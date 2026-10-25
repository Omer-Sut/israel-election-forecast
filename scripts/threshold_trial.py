"""E018: past-only representation learner and constrained expected-seat-loss decisions."""
import argparse
import base64
from collections import Counter
from datetime import date, timedelta
import gzip
import hashlib
from html import escape
import json
import math
from pathlib import Path
import statistics
import sys

if __package__ in (None, ''):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import baseline, experiments, forecast_review

ROOT=baseline.ROOT
CONFIG=ROOT/'config/threshold-trial.json'
CONTROLS=('square_0or3','absolute_0or3')


def candidate_rows(case, config):
    result=[]
    for i,key in enumerate(case['ids']):
        column=[v[i] for v in case['vectors']]
        positive=[v for v in column if v>0]
        eligible=bool(positive) and statistics.mean(column)<=config['candidate_mean_max'] and max(column)<=config['candidate_poll_max']
        result.append({'id':key,'index':i,'poll_seats':column,'candidate':eligible,
            'features':[len(positive)/len(column),statistics.mean(positive)] if positive else None,
            'positive_seats':[max(config['minimum_positive_seats'],v) for v in positive]})
    return result


def training_rows(cases, config):
    rows=[]
    for case in cases:
        candidates=[r for r in candidate_rows(case,config) if r['candidate']]
        for row in candidates:
            rows.append({**row,'election':case['election_id'],
                'represented':int(case['actual'][row['id']]>0),'weight':1/len(candidates)})
    return rows


def fit_probabilities(rows, targets, alpha):
    import numpy as np
    from scipy.special import expit
    if not rows:
        raise ValueError('No earlier candidate rows')
    x=np.asarray([r['features'] for r in rows],dtype=float)
    y=np.asarray([r['represented'] for r in rows],dtype=float)
    weights=np.asarray([r['weight'] for r in rows],dtype=float);weights/=weights.sum()
    center=weights@x;scale=np.sqrt(weights@((x-center)**2));scale[scale<1e-12]=1.
    z=np.column_stack([np.ones(len(x)),(x-center)/scale])
    mass=float(weights@y);penalty=np.diag([0.,alpha,alpha]);gradient=0.
    if len(set(y.tolist()))==1:
        campaigns=len({r['election'] for r in rows})
        probability=(mass*campaigns+.5)/(campaigns+1)
        beta=np.array([math.log(probability/(1-probability)),0.,0.]);status='single_class_smoothed_intercept'
    else:
        beta=np.array([math.log(mass/(1-mass)),0.,0.]);status='converged'
        def objective(b):
            eta=z@b;prob=expit(eta)
            return (float(weights@(np.logaddexp(0,eta)-y*eta)+.5*b@penalty@b),
                z.T@(weights*(prob-y))+penalty@b,
                z.T@((weights*prob*(1-prob))[:,None]*z)+penalty)
        for iteration in range(80):
            loss,jac,hessian=objective(beta)
            if np.max(np.abs(jac))<1e-13:break
            direction=np.linalg.solve(hessian,jac);step=1.
            while step>2**-30:
                trial=beta-step*direction;new_loss,new_jac,_=objective(trial)
                if (new_loss<=loss-1e-4*step*float(jac@direction) or
                    (abs(new_loss-loss)<1e-15 and np.max(np.abs(new_jac))<np.max(np.abs(jac)))):break
                step*=.5
            beta=trial
        gradient=float(np.max(np.abs(objective(beta)[1])))
        if gradient>1e-10:raise ValueError('Threshold logistic fit failed convergence')
    prediction={r['id']:float(expit(np.r_[1.,(np.asarray(r['features'])-center)/scale]@beta)) for r in targets if r['candidate']}
    return prediction,{'status':status,'alpha':alpha,'gradient_max':gradient,
        'training_campaigns':sorted({r['election'] for r in rows}),
        'training_rows':[{'election':r['election'],'id':r['id'],'represented':r['represented'],'weight':float(w)} for r,w in zip(rows,weights)],
        'centers':center.tolist(),'scales':scale.tolist(),'coefficients':beta.tolist(),
        'feature_names':['fraction_firms_projecting_seats','mean_positive_projection']}


def expected_loss_decision(distributions, anchor, total=120, minimum=3, fixed=None):
    fixed=fixed or {};states={0:(0.,0.,())}
    for i,dist in enumerate(distributions):
        if not dist or any(not math.isfinite(w) or w<0 or not math.isfinite(v) or v<0 for v,w in dist) or abs(sum(w for v,w in dist)-1)>1e-9:
            raise ValueError('Invalid marginal seat distribution')
        values=[fixed[i]] if i in fixed else [0]+list(range(minimum,total+1))
        costs={v:sum(w*abs(v-point) for point,w in dist) for v in values}
        next_states={}
        for allocated,prior in states.items():
            for value in values:
                if allocated+value>total:continue
                candidate=(prior[0]+costs[value],prior[1]+(value-anchor[i])**2,prior[2]+(value,))
                key=lambda r:(round(r[0],10),round(r[1],10),r[2])
                if allocated+value not in next_states or key(candidate)<key(next_states[allocated+value]):
                    next_states[allocated+value]=candidate
        states=next_states
    if total not in states:raise ValueError('Infeasible expected-loss decision')
    return list(states[total][2])


def predict(case, past, config, alpha):
    targets=candidate_rows(case,config);train=training_rows(past,config)
    campaigns={r['election'] for r in train}
    if len(campaigns)<config['minimum_training_campaigns']:return None
    probs,fit=fit_probabilities(train,targets,alpha)
    distributions=[]
    for row in targets:
        if row['candidate']:
            p=probs[row['id']];positive=row['positive_seats']
            dist=[(0.,1-p)]+[(v,p/len(positive)) for v in positive]
        else:
            dist=[(v,1/len(row['poll_seats'])) for v in row['poll_seats']]
        distributions.append(dist)
    fixed={case['ids'].index('other_qualifying_lists'):0} if 'other_qualifying_lists' in case['ids'] else {}
    seats=expected_loss_decision(distributions,case['anchor'],minimum=config['minimum_positive_seats'],fixed=fixed)
    return {'seats':seats,'probabilities':probs,'fit':fit,
        'marginals':{r['id']:d for r,d in zip(targets,distributions)}}


def controls(case):
    fixed={case['ids'].index('other_qualifying_lists'):0} if 'other_qualifying_lists' in case['ids'] else {}
    return {ident:{'seats':forecast_review.constrained_decision(case['vectors'],minimum=3,
        objective=objective,fixed=fixed),'probabilities':{},'fit':{'status':'control'}}
        for ident,objective in zip(CONTROLS,('square','absolute'))}


def select(past, now, minimum=2):
    campaigns=sorted({r['election_date'] for r in past if r['learned_available']})
    if len(campaigns)<minimum:return {'id':CONTROLS[0],'status':'warmup_control','validation_dates':campaigns}
    scores=[]
    for ident in now:
        rows=[r for r in past if r['election_date'] in campaigns and r['method']==ident]
        if len(rows)!=len(campaigns):continue
        scores.append((statistics.mean(r['seat_l1'] for r in rows),int(ident not in CONTROLS),ident))
    return {'id':min(scores)[2],'status':'earlier_campaign_selection','validation_dates':campaigns}


def historical_cases(config):
    historical=baseline.load_json(ROOT/config['historical_config'])
    outcomes=baseline.load_json(ROOT/historical['outcomes_path'])['elections'];cases=[]
    for spec in historical['elections']:
        snapshot=baseline.load_json(ROOT/spec['polls_path'])
        cutoff=(date.fromisoformat(snapshot['election_date'])-timedelta(days=1)).isoformat()
        case=experiments.build_case(snapshot,cutoff,historical['poll_window_days'],historical['minimum_groups'])
        case['actual']=outcomes[spec['id']]['seat_results'];case['period']=spec['period'];cases.append(case)
    return cases


def current_case():
    review=forecast_review.build_review()
    return {'election_id':'current_2026','election_date':'2026-10-27','cutoff':review['as_of_date'],
        'ids':review['fields'],'vectors':review['vectors'],'anchor':review['continuous_mean'],
        'selected_polls':review['selected_polls']}


def score(case, item, targets):
    truth=[case['actual'][key] for key in case['ids']]
    false_positive=[key for key,a,b in zip(case['ids'],item['seats'],truth) if a>0 and b==0]
    false_negative=[key for key,a,b in zip(case['ids'],item['seats'],truth) if a==0 and b>0]
    probabilistic=[]
    for row in targets:
        if row['id'] not in item['probabilities']:continue
        p=item['probabilities'][row['id']];y=int(case['actual'][row['id']]>0)
        probabilistic.append({'id':row['id'],'p':p,'represented':y,'brier':(p-y)**2,
            'log_loss':-math.log(max(1e-15,p if y else 1-p))})
    return {'seat_l1':sum(abs(a-b) for a,b in zip(item['seats'],truth)),
        'false_positive':false_positive,'false_negative':false_negative,
        'candidate_probability_scores':probabilistic,
        'candidate_brier':statistics.mean(r['brier'] for r in probabilistic) if probabilistic else None,
        'candidate_log_loss':statistics.mean(r['log_loss'] for r in probabilistic) if probabilistic else None}


def build(config=None,cases=None):
    config=config or baseline.load_json(CONFIG);cases=historical_cases(config) if cases is None else cases
    records=[];selections=[];coverage=[];past=[];current={}
    for case in cases+[current_case()]:
        future='actual' not in case
        if any(c['election_date']>=case['election_date'] for c in past):raise ValueError('Future campaign in training')
        now=controls(case);targets=candidate_rows(case,config)
        for alpha in config['alphas']:
            item=predict(case,past,config,alpha)
            if item is not None:now[f'hurdle_a{alpha:g}']=item
        learned=any(k not in CONTROLS for k in now)
        choice=select(records,now,config['minimum_selection_campaigns'])
        if future:
            current={'case':{k:case[k] for k in ('election_id','cutoff','ids','anchor')},
                'selected_polls':[{k:p.get(k) for k in ('id','pollster_group','source_url','published_on')} for p in case['selected_polls']],
                'targets':targets,'methods':now,'selection':choice};break
        coverage.append({'election':case['election_id'],'election_date':case['election_date'],
            'candidate_ids':[r['id'] for r in targets if r['candidate']],
            'positive_projected_count':sum(any(v>0 for v in r['poll_seats']) for r in targets),
            'all_zero_winners':[r['id'] for r in targets if not any(r['poll_seats']) and case['actual'][r['id']]>0],
            'selected_poll_ids':[p['id'] for p in case['selected_polls']]})
        for ident,item in now.items():
            records.append({'election':case['election_id'],'election_date':case['election_date'],
                'period':case['period'],'party_ids':case['ids'],'actual':case['actual'],
                'method':ident,'learned_available':learned,**item,**score(case,item,targets)})
        selected=next(r for r in records if r['election']==case['election_id'] and r['method']==choice['id'])
        selections.append({'election':case['election_id'],'election_date':case['election_date'],
            **choice,'seat_l1':selected['seat_l1'],'false_positive':selected['false_positive'],'false_negative':selected['false_negative']})
        past.append(case)
    summaries={}
    for ident in current['methods']:
        rows=[r for r in records if r['method']==ident and r['learned_available']]
        periods=sorted({r['period'] for r in rows})
        summaries[ident]={'folds':len(rows),'mean_seat_l1':statistics.mean(r['seat_l1'] for r in rows),
            'equal_period_seat_l1':statistics.mean(statistics.mean(r['seat_l1'] for r in rows if r['period']==p) for p in periods),
            'false_positives':sum(len(r['false_positive']) for r in rows),
            'false_negatives':sum(len(r['false_negative']) for r in rows),
            'mean_campaign_brier':statistics.mean(r['candidate_brier'] for r in rows if r['candidate_brier'] is not None) if ident not in CONTROLS else None}
    audit=baseline.load_json(ROOT/config['current_percentage_audit'])
    if {p['poll_id'] for p in audit['polls']}!={p['id'] for p in current['selected_polls']}:
        raise ValueError('Current percentage audit does not match selected releases')
    focus_percentages=[{'poll_id':p['poll_id'],'source_url':p['source_url'],
        'percentages':{key:p['reported_vote_percentages'].get(key) for key in config['current_focus']},
        'reported_seats':{key:p['borderline_seats'].get(key) for key in config['current_focus']}}
        for p in audit['polls']]
    return {'config':config,'records':records,'selections':selections,'coverage':coverage,
        'summaries':summaries,'current':current,'current_reported_percentages':focus_percentages,
        'decision':'Research only; adopted forecast/turnout unchanged. No calibrated threshold probabilities claimed.',
        'limitations':['Six inspected campaigns, four learned outer folds; party rows are dependent.',
            'Training candidate roster requires at least one positive projection; all-zero lists are not modelled probabilities.',
            'Current has seven firms; history has three. Firm count/fraction precision shift is uncalibrated.',
            'Conditional positive support is a limited empirical poll distribution, not a complete seat scenario.',
            'Current below-threshold percentages are descriptive, not historical training features.',
            'Marginal expected-loss decision is not a feasible joint vote/allocation simulation.']}


def write(report,out):
    out.mkdir(parents=True,exist_ok=True)
    def save(name,text):(out/name).write_text(text,encoding='utf-8',newline='\n')
    save('results.json',json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    lines=['# E018: threshold-aware seat research','',report['decision'],'',
        '| Method | Four-fold mean seat error | Equal-period error | False positives | False negatives | Brier* |',
        '|---|---:|---:|---:|---:|---:|']
    for ident,s in report['summaries'].items():
        b='—' if s['mean_campaign_brier'] is None else f"{s['mean_campaign_brier']:.3f}"
        lines.append(f"| {ident} | {s['mean_seat_l1']:.3f} | {s['equal_period_seat_l1']:.3f} | {s['false_positives']} | {s['false_negatives']} | {b} |")
    lines+=['','*Brier averages each campaign equally over its modelled candidate lists; not all lists. Controls have no learned probability forecast. Lower is better.2019–21 is one period,2022 another;2015/April2019 warm up learning. No untouched holdout.','',
        '## Current focus: exploratory model outputs','',
        '| Method | Reservists seats | Model p(represented) | Amcha seats | Model p(represented) |',
        '|---|---:|---:|---:|---:|']
    ids=report['current']['case']['ids']
    for ident,item in report['current']['methods'].items():
        cells=[]
        for key in report['config']['current_focus']:
            p=item['probabilities'].get(key)
            cells += [str(item['seats'][ids.index(key)]),'—' if p is None else f'{p:.3f}']
        lines.append('| '+ident+' | '+' | '.join(cells)+' |')
    lines+=['',f"Earlier-campaign selector: {report['current']['selection']}",'',
        'These numerical probability forecasts are not certified crossing probabilities. Poll pass frequency is an input, not a probability interpretation. Current source percentage evidence is retained separately in results.json with missing values and URLs. No new sources promoted.','',
        '![Historical error and current sensitivity](threshold-diagnostics.svg)','','## Limitations','']
    lines+=['- '+s for s in report['limitations']]
    save('analysis.md','\n'.join(lines)+'\n')
    historical=baseline.load_json(ROOT/report['config']['historical_config'])
    paths=['scripts/threshold_trial.py','config/threshold-trial.json','scripts/experiments.py','scripts/forecast_review.py',
        'scripts/baseline.py','scripts/backtest.py',report['config']['historical_config'],historical['outcomes_path'],
        report['config']['current_percentage_audit'],'data/snapshots/polls-2026-10-24.json','config/forecast-review.json',
        'config/poll-mappings.json','config/submission-fields.json','requirements-turnout.txt','reports/forecast-decision-2026-10-25/forecast.json']
    paths+=[s['polls_path'] for s in historical['elections']]
    save('inputs-manifest.json',json.dumps({p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(set(paths))},indent=2)+'\n')
    plot(report,out)


def plot(report,out):
    colors=['#33485c','#777777','#2279ac','#b97919','#98589d']
    methods=list(report['summaries']);dates=sorted({r['election_date'] for r in report['records'] if r['learned_available']})
    maximum=max(24,max(r['seat_l1'] for r in report['records'] if r['learned_available']))*1.1
    p=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="820" viewBox="0 0 1120 820"><rect width="1120" height="820" fill="white"/><g font-family="Arial,sans-serif" fill="#17334a">',
        '<text x="25" y="30" font-size="22">Threshold trial: historical errors and current model sensitivity</text>',
        '<text x="25" y="55" font-size="13">Exploratory forecasts, not calibrated crossing probabilities. Adopted forecast unchanged.</text>']
    for j in range(5):
        y=350-250*j/4;v=maximum*j/4
        p.append(f'<path d="M85,{y}H1050" stroke="#e0e5ea"/><text x="25" y="{y+4}" font-size="12">{v:.0f}</text>')
    for i,method in enumerate(methods):
        records=[r for r in report['records'] if r['method']==method and r['election_date'] in dates]
        pts=[(130+280*dates.index(r['election_date']),350-r['seat_l1']/maximum*250) for r in records]
        p.append('<polyline points="'+' '.join(f'{x},{y:.2f}' for x,y in pts)+f'" fill="none" stroke="{colors[i]}" stroke-width="2"/>')
        for x,y in pts:p.append(f'<circle cx="{x}" cy="{y:.2f}" r="4" fill="{colors[i]}"/>')
        p.append(f'<text x="{25+(i%3)*365}" y="{410+25*(i//3)}" font-size="13" fill="{colors[i]}">{escape(method)}</text>')
    for i,d in enumerate(dates):p.append(f'<text x="{95+280*i}" y="375" font-size="12">{d}</text>')
    p.append('<text x="25" y="485" font-size="19">Current focus: estimated representation probability by fixed penalty</text>')
    for j,key in enumerate(report['config']['current_focus']):
        y=550+85*j;p.append(f'<text x="25" y="{y+4}" font-size="15">{escape(key)}</text><path d="M320,{y}H1020" stroke="#ccd6dd"/>')
        for i,method in enumerate(methods):
            probability=report['current']['methods'][method]['probabilities'].get(key)
            if probability is None:continue
            x=320+700*probability;dy=(i-3)*10
            p.append(f'<circle cx="{x:.2f}" cy="{y+dy}" r="5" fill="{colors[i]}"><title>{escape(method)}: {probability:.4f}</title></circle>')
    for j in range(6):p.append(f'<text x="{310+140*j}" y="700" font-size="12">{j/5:.1f}</text>')
    p.append('<text x="25" y="750" font-size="13">Dots vary regularization only. Same current inputs; historical three-firm to current seven-firm shift remains uncalibrated.</text><text x="25" y="778" font-size="13">A numerical p is a model estimate, not evidence that historical calibration is reliable.</text></g></svg>')
    (out/'threshold-diagnostics.svg').write_text('\n'.join(p)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,default=ROOT/'output/threshold-trial')
    args=parser.parse_args();write(build(),args.out_dir)
    files={p.name:p.read_text(encoding='utf-8') for p in sorted(args.out_dir.iterdir()) if p.is_file()}
    encoded=base64.b64encode(gzip.compress(json.dumps(files,ensure_ascii=False).encode())).decode()
    print('E018_FILES_BASE64_BEGIN')
    for i in range(0,len(encoded),8000):print(encoded[i:i+8000])
    print('E018_FILES_BASE64_END');print(files['analysis.md'])
