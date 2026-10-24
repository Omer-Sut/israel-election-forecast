"""Bounded linear/fractional-logit time-series screen with chronological selection."""
import argparse
import base64
import csv
from datetime import date
import gzip
import hashlib
from html import escape
import json
import math
from pathlib import Path
import statistics
import sys

if __package__ in (None,''):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import baseline, turnout_history

ROOT=baseline.ROOT
CONFIG=ROOT/'config/turnout-models.json'
REFERENCES=('previous_election','last_three_mean','last_three_median')


def features(earlier,target_date):
    if len(earlier)<3:raise ValueError('Three earlier outcomes required')
    target=date.fromisoformat(target_date)
    if any(date.fromisoformat(r['election_date'])>=target for r in earlier):
        raise ValueError('Target/future outcome in feature history')
    values=[r['turnout_pct'] for r in earlier];a,b,c=values[-3:]
    previous_gap=(date.fromisoformat(earlier[-1]['election_date'])-date.fromisoformat(earlier[-2]['election_date'])).days/365.2425
    gap=(target-date.fromisoformat(earlier[-1]['election_date'])).days/365.2425
    if previous_gap<=0 or gap<=0:raise ValueError('Dates must increase')
    all_values={'lag1':c,'lag2':b,'lag3':a,'change1':c-b,'change2_mean':(c-a)/2,
        'mean3':statistics.mean(values[-3:]),'gap_years':gap,'previous_gap_years':previous_gap,
        'calendar_decades':(target.year-2000)/10,'post2000':float(target.year>=2000),
        'annual_change':(c-b)/previous_gap,'expanding_mean':statistics.mean(values)}
    groups={'ar1':['lag1'],'ar3':['lag1','lag2','lag3'],
        'level_momentum':['lag1','change1','change2_mean'],
        'smooth_gap':['mean3','change1','gap_years'],
        'spacing':['lag1','gap_years','previous_gap_years'],
        'era_trend':['lag1','calendar_decades','post2000'],
        'annual_momentum':['lag1','annual_change','gap_years'],
        'expanding_level':['lag1','expanding_mean','mean3']}
    return {name:{key:all_values[key] for key in keys} for name,keys in groups.items()}


def configurations(config):
    result=[]
    for feature in config['feature_sets']:
        for window in config['training_windows']:
            for family,alphas in [('linear_level',config['linear_alphas']),
                    ('linear_change',config['linear_alphas']),
                    ('fractional_logit',config['fractional_logit_alphas'])]:
                for alpha in alphas:
                    ident=f"{family}__{feature}__w{window or 'all'}__a{alpha:g}"
                    result.append({'id':ident,'family':family,'features':feature,'window':window,'alpha':alpha})
    return result


def fit_predict(examples,target_features,previous_turnout,candidate):
    """One election=one equally weighted row; not millions of Bernoulli trials."""
    import numpy as np
    from scipy.optimize import minimize
    from scipy.special import expit
    names=list(target_features)
    x=np.asarray([[r['features'][k] for k in names] for r in examples],dtype=float)
    y=np.asarray([r['turnout_pct']/100 for r in examples])
    if candidate['family']=='linear_change':
        y-=np.asarray([r['previous_turnout']/100 for r in examples])
    center=x.mean(axis=0);scale=x.std(axis=0);scale[scale<1e-12]=1
    z=np.column_stack([np.ones(len(x)),(x-center)/scale])
    target=np.r_[1.,(np.asarray([target_features[k] for k in names])-center)/scale]
    penalty=np.diag([0.]+[candidate['alpha']]*len(names))
    status='converged';message='closed_form_lstsq';gradient=None
    if candidate['family']=='fractional_logit':
        def objective(beta):
            eta=z@beta
            loss=np.mean(np.logaddexp(0,eta)-y*eta)+.5*float(beta@penalty@beta)
            jac=z.T@(expit(eta)-y)/len(y)+penalty@beta
            return loss,jac
        initial=np.zeros(z.shape[1]);initial[0]=math.log(float(y.mean())/(1-float(y.mean())))
        fitted=minimize(objective,initial,jac=True,method='L-BFGS-B',
            options={'maxiter':1000,'ftol':1e-13,'gtol':1e-9,'maxls':50})
        beta=fitted.x;gradient=float(np.max(np.abs(objective(beta)[1])))
        if not fitted.success and gradient>1e-7:status='not_converged'
        message=str(fitted.message)
        prediction=100*float(expit(target@beta))
    else:
        # Minimize mean squared fraction error /2 + alpha*||slopes||²/2.
        augmentation=np.diag(np.sqrt(np.diag(penalty)*len(y)))
        beta=np.linalg.lstsq(np.vstack([z,augmentation]),np.r_[y,np.zeros(z.shape[1])],rcond=None)[0]
        prediction=100*float(target@beta)
        if candidate['family']=='linear_change':prediction+=previous_turnout
    if not math.isfinite(prediction):status='nonfinite_prediction'
    factor=1 if candidate['family']=='fractional_logit' else 100
    raw_slopes=factor*beta[1:]/scale
    raw_intercept=factor*(beta[0]-np.sum(beta[1:]*center/scale))
    detail={'status':status,'optimizer_message':message,'gradient_max_abs':gradient,
        'training_knessets':[r['knesset'] for r in examples],
        'feature_names':names,'training_centers':center.tolist(),'training_scales':scale.tolist(),
        'standardized_coefficients':beta.tolist(),
        'raw_intercept':float(raw_intercept),'raw_coefficients':dict(zip(names,map(float,raw_slopes))),
        'formula':'100*sigmoid(raw_intercept + raw_slopes*x)' if candidate['family']=='fractional_logit'
            else 'raw_intercept + raw_slopes*x'+(' + previous_turnout' if candidate['family']=='linear_change' else '')}
    return prediction,detail


def allowed(value,contract):
    bounds=contract['turnout_field']
    return math.isfinite(value) and bounds['minimum']<=value<=bounds['maximum']


def choose(past_records,current,minimum=3,lookback=6,families=None):
    """Tune only on earlier OOF outcomes; current contains no target outcome."""
    earlier=sorted({r['knesset'] for r in past_records})
    used=earlier[-lookback:] if lookback else earlier
    if len(used)<minimum:
        return {'selected':'previous_election','status':'warmup_reference','validation_knessets':used,'validation_mae':None}
    scores=[]
    for ident,now in current.items():
        if not now['eligible'] or (families and now['family'] not in families and now['family']!='reference'):continue
        subset=[r for r in past_records if r['id']==ident and r['knesset'] in used]
        if len(subset)!=len(used) or not all(r['eligible'] for r in subset):continue
        score=statistics.mean(r['absolute_error_pp'] for r in subset)
        # Numerical ties favor references, then fixed ID. No hindsight tie-break.
        scores.append((round(score,8),0 if now['family']=='reference' else 1,ident,score))
    if not scores:raise ValueError('No complete admissible chronological candidate')
    winner=min(scores)
    return {'selected':winner[2],'status':'past_only_selection','validation_knessets':used,'validation_mae':winner[3]}


def build(config=None,rows=None):
    import numpy as np
    import scipy
    config=config or baseline.load_json(CONFIG)
    rows=rows or baseline.load_json(ROOT/config['history_path'])['elections']
    contract=baseline.load_json(ROOT/'config/submission-fields.json')
    candidates=configurations(config)
    if len({c['id'] for c in candidates})!=len(candidates):raise ValueError('Duplicate configurations')
    feature_rows={i:features(rows[:i],r['election_date']) for i,r in enumerate(rows) if i>=3}
    policy_specs={'all_recent6':(6,None),'all_expanding':(None,None),
                  'linear_recent6':(6,{'linear_level','linear_change'}),
                  'glm_recent6':(6,{'fractional_logit'})}
    predictions=[];selected=[];current_fits={}
    for i in range(3,len(rows)+1):
        future=i==len(rows)
        if i-3<config['minimum_training_elections']:continue
        target_date=config['forecast_election_date'] if future else rows[i]['election_date']
        if future and date.fromisoformat(config['forecast_cutoff'])>=date.fromisoformat(target_date):
            raise ValueError('Forecast cutoff must precede election')
        current_features=features(rows[:i],target_date)
        current={}
        for m,value in turnout_history.forecasts(rows[:i]).items():
            current[m]={'prediction_pct':value,'family':'reference','eligible':allowed(value,contract),
                        'fit':{'status':'reference','training_knessets':[r['knesset'] for r in rows[:i]]}}
        for c in candidates:
            indices=list(range(3,i))
            if c['window']:indices=indices[-c['window']:]
            examples=[{'knesset':rows[j]['knesset'],'turnout_pct':rows[j]['turnout_pct'],
                'previous_turnout':rows[j-1]['turnout_pct'],'features':feature_rows[j][c['features']]} for j in indices]
            value,detail=fit_predict(examples,current_features[c['features']],rows[i-1]['turnout_pct'],c)
            current[c['id']]={'prediction_pct':value,'family':c['family'],
                'eligible':detail['status']=='converged' and allowed(value,contract),'fit':detail}
        # Select BEFORE observing/appending the target truth.
        selections={name:choose(predictions,current,config['minimum_selection_folds'],lookback,families)
                    for name,(lookback,families) in policy_specs.items()}
        if future:
            current_fits=current;current_selection=selections;break
        truth=rows[i]['turnout_pct']
        for name,selection in selections.items():
            value=current[selection['selected']]['prediction_pct']
            selected.append({'policy':name,'knesset':rows[i]['knesset'],'election_date':target_date,
                **selection,'prediction_pct':value,'actual_pct':truth,'absolute_error_pp':abs(value-truth)})
        for ident,item in current.items():
            predictions.append({'id':ident,'knesset':rows[i]['knesset'],'election_date':target_date,
                'family':item['family'],'prediction_pct':item['prediction_pct'],'actual_pct':truth,
                'absolute_error_pp':abs(item['prediction_pct']-truth),'eligible':item['eligible'],
                'fit_status':item['fit']['status'],'training_knessets':item['fit']['training_knessets']})
    def metrics(records):
        recent=[r for r in records if r['knesset']>=20]
        blocks=[[r for r in recent if r['knesset']==20],
                [r for r in recent if 21<=r['knesset']<=24],[r for r in recent if r['knesset']==25]]
        return {'folds':len(records),'recent_folds':len(recent),
            'all_mae':statistics.mean(r['absolute_error_pp'] for r in records),
            'recent_mae':statistics.mean(r['absolute_error_pp'] for r in recent),
            'recent_block_mae':statistics.mean(statistics.mean(r['absolute_error_pp'] for r in b) for b in blocks),
            'recent_worst':max(r['absolute_error_pp'] for r in recent),'invalid_folds':sum(not r.get('eligible',True) for r in records)}
    scores={ident:{**metrics([r for r in predictions if r['id']==ident]),
        'current_prediction_pct':now['prediction_pct'],'current_eligible':now['eligible'],'family':now['family']}
        for ident,now in current_fits.items()}
    policy_scores={name:{**metrics([r for r in selected if r['policy']==name]),
        'current_selection':current_selection[name],
        'current_prediction_pct':current_fits[current_selection[name]['selected']]['prediction_pct']}
        for name in policy_specs}
    grid_ranking=sorted([k for k,v in scores.items() if v['invalid_folds']==0 and v['current_eligible']],
                        key=lambda k:(round(scores[k]['recent_mae'],8),k))
    signatures={tuple(round(r['prediction_pct'],7) for r in predictions if r['id']==c['id']) for c in candidates}
    return {'config':config,'configuration_count':len(candidates),'unique_historical_prediction_vectors_7dp':len(signatures),
        'configurations':candidates,'historical_predictions':predictions,'nested_selections':selected,
        'scores':scores,'policy_scores':policy_scores,'hindsight_recent_ranking':grid_ranking,
        'current_fits':current_fits,'current_features':features(rows,config['forecast_election_date']),
        'current_form_bounds':[contract['turnout_field']['minimum'],contract['turnout_field']['maximum']],
        'environment':{'numpy':np.__version__,'scipy':scipy.__version__,'seed':'not_applicable_deterministic'},
        'decision':'Exploratory comparison only. No forecast replacement or current-poll/war adjustment adopted.',
        'limitations':['Only25 outcomes and22 lag-complete rows, with16 outer evaluation elections.',
            'No untouched holdout: historical outcomes and the post2000 break were already inspected.',
            'Many configurations are equivalent or correlated; configuration count is not independent evidence.',
            'Four2019–2021 elections are correlated; block sensitivity reported separately.',
            'Retrospective source vintages; strictly earlier numerical outcomes, not certified real-time reconstruction.',
            'Fractional-logit quasi-likelihood treats elections equally; ballots are not independent model trials.',
            'Current war/poll-intention covariates omitted because comparable audited inputs are insufficient.']}


def write(report,out):
    out.mkdir(parents=True,exist_ok=True)
    def save(name,text):(out/name).write_text(text,encoding='utf-8',newline='\n')
    save('results.json',json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    with (out/'predictions.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['id','knesset','date','prediction_pct','actual_pct','error_pp','eligible'])
        for r in report['historical_predictions']:w.writerow([r['id'],r['knesset'],r['election_date'],f"{r['prediction_pct']:.6f}",f"{r['actual_pct']:.6f}",f"{r['absolute_error_pp']:.6f}",r['eligible']])
    with (out/'configurations.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['id','family','recent_mae_pp','all_mae_pp','block_mae_pp','recent_worst_pp','next_prediction_pct','invalid_folds','current_eligible'])
        for ident,v in report['scores'].items():w.writerow([ident,v['family'],*[f'{v[k]:.6f}' for k in ('recent_mae','all_mae','recent_block_mae','recent_worst','current_prediction_pct')],v['invalid_folds'],v['current_eligible']])
    lines=['# Turnout regression and GLM time-series screen','',
        f"**{report['configuration_count']} fitted configurations; no current forecast change adopted.** All estimates are national turnout percentages; errors are percentage points.", '',
        '## What was fitted?','',
        'Eight feature sets cover AR1/AR3 lags, changes, three-election means, election gaps, annualized momentum, expanding means and a calendar/post2000 sensitivity. Three fitting windows use all earlier lag-complete elections, the last12 or last8. Linear models predict either the level or the change from the previous election, with ridge alpha0/.01/.1/1; fractional-logit GLMs use alpha.001/.01/.1. Every training row and feature uses only earlier election outcomes. Scaling is fitted on the training rows, and intercepts are not penalized.', '',
        'Linear objective: mean((y−Xb)^2)/2 + alpha*||slopes||²/2, with y=T/100 or the turnout change/100. The latter is a regularized correction around previous turnout. Fractional-logit objective: mean(log(1+exp(Xb))−(T/100)*Xb) + alpha*||slopes||²/2; prediction=100*sigmoid(Xb). Each election has equal weight. This is fractional-response quasi-likelihood, not a binomial experiment with millions of independent voters; no naive voter-count standard errors are reported.', '',
        'Coefficients, training IDs, training means/scales, optimizer status and feature values are saved. Unconstrained out-of-range estimates remain visible; they are excluded from point-selection eligibility using the configured inclusive40–100 bounds, never silently clipped. Nonconverged fits are also excluded.', '',
        '## Chronological model selection','',
        'Six earlier lag-complete rows are required to fit a candidate:16 common outer elections from1981–2022. At each target, choose the configuration using only its previously completed out-of-fold errors, either the last6 or all earlier folds. At least3 earlier folds are required; initial selector folds use previous-election persistence. References remain in every selection pool so the selector can decline a regression. Current admissibility is checked before selection. Ties rounded at8 decimal places favor references, then a fixed ID. No target truth is supplied to selection.', '',
        '| Past-only rule/reference | Recent six MAE | All16 MAE | Three-block MAE | Next estimate |',
        '| --- | ---: | ---: | ---: | ---: |']
    for ident in REFERENCES:
        v=report['scores'][ident];lines.append(f"| {ident} | {v['recent_mae']:.3f} | {v['all_mae']:.3f} | {v['recent_block_mae']:.3f} | {v['current_prediction_pct']:.2f}% |")
    for ident,v in report['policy_scores'].items():
        lines.append(f"| nested:{ident} | {v['recent_mae']:.3f} | {v['all_mae']:.3f} | {v['recent_block_mae']:.3f} | {v['current_prediction_pct']:.2f}% |")
    lines += ['', 'The block metric gives equal weight to2015, the2019–2021 cluster and2022. A good-looking fixed configuration ranked on these outcomes is a hindsight discovery; its score must not be confused with the past-only selectors above. These inspected data are not a fresh holdout.', '',
        '![Chronological selection errors](chronological-errors.svg)','',
        '![Predictions and historical errors](model-stability.svg)','',
        '## Hindsight ranking: descriptive, not selected forecasting skill','',
        '| Configuration | Recent MAE | All16 MAE | Recent worst | Next estimate |','| --- | ---: | ---: | ---: | ---: |']
    for ident in report['hindsight_recent_ranking'][:12]:
        v=report['scores'][ident];lines.append(f"| {ident} | {v['recent_mae']:.3f} | {v['all_mae']:.3f} | {v['recent_worst']:.3f} | {v['current_prediction_pct']:.2f}% |")
    lines += ['',f"There are {report['unique_historical_prediction_vectors_7dp']} distinct historical prediction vectors at7-decimal precision among {report['configuration_count']} configurations. OLS on equivalent feature spans and some level/change parameterizations can coincide; this is expected algebra, not additional independent validation.", '',
        '## What would the chronological selectors use now?','']
    for name,v in report['policy_scores'].items():
        sel=v['current_selection'];lines.append(f"- {name}: {v['current_prediction_pct']:.2f}%, selecting `{sel['selected']}` from earlier OOF elections {sel['validation_knessets']}.")
    lines += ['', 'The scatter shows sensitivity across configurations, not a confidence/prediction interval. A stable next estimate is not proof of accuracy. No automatic replacement of the70.63% working placeholder is made by a many-configuration screen; review the chronological errors and stability before adopting one.', '',
        '## Limits','']+['- '+x for x in report['limitations']]
    lines += ['', 'Source history and conflict/denominator caveats: [E014 analysis](../turnout-history-2026-10-24/analysis.md). The next-election date is the competition-provided2026-10-27, not a new independent election-date verification. No same-election turnout intentions or later outcomes enter fits.', '',
        'Reproduce: install requirements-turnout.txt on a hosted CPU and run `python scripts/turnout_models.py`. NumPy/SciPy versions, all configuration outputs and input hashes are saved. No additional dependencies enter the standard-library baseline. The workflow compares numeric values within absolute1e-7, with exact configuration/selection identities and exact displayed plots/text.','']
    save('analysis.md','\n'.join(lines))
    draw(report,out)
    paths=[CONFIG,ROOT/report['config']['history_path'],Path(__file__),ROOT/'scripts/turnout_history.py',
        ROOT/'config/submission-fields.json',ROOT/'requirements-turnout.txt',ROOT/'scripts/compare_turnout_models.py']
    save('inputs-manifest.json',json.dumps({str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')


def draw(report,out):
    candidates=[(k,v) for k,v in report['scores'].items() if v['family']!='reference' and v['current_eligible'] and not v['invalid_folds']]
    colors={'linear_level':'#216aa4','linear_change':'#298269','fractional_logit':'#b87922'}
    xmax=max(5,max(v['recent_mae'] for k,v in candidates));xmin=0
    ymin=min(60,min(v['current_prediction_pct'] for k,v in candidates))-1
    ymax=max(80,max(v['current_prediction_pct'] for k,v in candidates))+1
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="620" viewBox="0 0 1100 620"><rect width="1100" height="620" fill="white"/><g font-family="Arial,sans-serif" fill="#18324a">',
        '<text x="25" y="30" font-size="22">Turnout models: historical error versus next-election prediction</text>',
        '<text x="25" y="55" font-size="13">Each dot is a configuration. Hindsight recent-six error; dispersion is not predictive uncertainty.</text>']
    def xy(error,pred):return 90+error/xmax*930,510-(pred-ymin)/(ymax-ymin)*400
    for j in range(6):
        error=xmax*j/5;x,y=xy(error,ymin)
        parts.append(f'<path d="M{x:.2f},90V510" stroke="#e1e6ea"/><text x="{x-9:.2f}" y="535" font-size="12">{error:.1f}</text>')
    for j in range(6):
        p=ymin+(ymax-ymin)*j/5;x,y=xy(0,p)
        parts.append(f'<path d="M90,{y:.2f}H1020" stroke="#e1e6ea"/><text x="30" y="{y+4:.2f}" font-size="12">{p:.1f}%</text>')
    for ident,v in candidates:
        x,y=xy(v['recent_mae'],v['current_prediction_pct'])
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" fill="{colors[v["family"]]}" opacity=".55"><title>{escape(ident)}: MAE{v["recent_mae"]:.3f}, next{v["current_prediction_pct"]:.2f}%</title></circle>')
    for ident in REFERENCES:
        v=report['scores'][ident];x,y=xy(v['recent_mae'],v['current_prediction_pct'])
        parts.append(f'<rect x="{x-4:.2f}" y="{y-4:.2f}" width="8" height="8" fill="#152534"><title>{ident}</title></rect>')
    parts.append('<text x="340" y="560" font-size="14">Mean absolute error on six recent elections (percentage points)</text>')
    for j,(name,color) in enumerate(colors.items()):parts.append(f'<text x="{25+330*j}" y="590" fill="{color}" font-size="15">{name}</text>')
    parts.append('<text x="25" y="612" font-size="12">Black squares: simple references. Inadmissible/nonconverged configurations excluded from this plot, preserved in results.</text></g></svg>')
    (out/'model-stability.svg').write_text('\n'.join(parts)+'\n',encoding='utf-8',newline='\n')
    recent=sorted({r['knesset'] for r in report['historical_predictions'] if r['knesset']>=20})
    series={}
    for name in ('previous_election','last_three_mean'):
        series[name]=[r for r in report['historical_predictions'] if r['id']==name and r['knesset'] in recent]
    for name in ('all_recent6','glm_recent6'):
        series['nested:'+name]=[r for r in report['nested_selections'] if r['policy']==name and r['knesset'] in recent]
    maximum=max(8,max(r['absolute_error_pp'] for values in series.values() for r in values))*1.1
    p=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="550" viewBox="0 0 1100 550"><rect width="1100" height="550" fill="white"/><g font-family="Arial,sans-serif" fill="#18324a">',
       '<text x="25" y="30" font-size="22">Turnout errors: model choice made before each target election</text>',
       '<text x="25" y="55" font-size="13">Six recent outcomes, including the correlated 2019–2021 cluster. Lower error is better.</text>']
    palette=['#216aa4','#298269','#b87922','#a15aa3']
    for j in range(5):
        v=maximum*j/4;y=440-v/maximum*340
        p.append(f'<path d="M90,{y:.2f}H1030" stroke="#e1e6ea"/><text x="25" y="{y+4:.2f}" font-size="12">{v:.1f}pp</text>')
    for i,(name,values) in enumerate(series.items()):
        values=sorted(values,key=lambda r:r['knesset'])
        pts=[(120+j*175,440-r['absolute_error_pp']/maximum*340) for j,r in enumerate(values)]
        p.append('<polyline points="'+' '.join(f'{x},{y:.2f}' for x,y in pts)+f'" fill="none" stroke="{palette[i]}" stroke-width="2"/>')
        for (x,y),r in zip(pts,values):p.append(f'<circle cx="{x}" cy="{y:.2f}" r="4" fill="{palette[i]}"><title>{escape(name)}: {r["absolute_error_pp"]:.3f}pp</title></circle>')
        p.append(f'<text x="{25+(i%2)*540}" y="{500+(i//2)*27}" fill="{palette[i]}" font-size="14">{escape(name)}</text>')
    for j,r in enumerate(series['previous_election']):p.append(f'<text x="{85+j*175}" y="465" font-size="12">{r["election_date"]}</text>')
    p.append('</g></svg>')
    (out/'chronological-errors.svg').write_text('\n'.join(p)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,default=ROOT/'output/turnout-models')
    args=parser.parse_args();write(build(),args.out_dir)
    files={p.name:p.read_text(encoding='utf-8') for p in sorted(args.out_dir.iterdir()) if p.is_file()}
    encoded=base64.b64encode(gzip.compress(json.dumps(files,ensure_ascii=False).encode())).decode()
    print('E015_FILES_BASE64_BEGIN')
    for i in range(0,len(encoded),8000):print(encoded[i:i+8000])
    print('E015_FILES_BASE64_END');print(files['analysis.md'])
