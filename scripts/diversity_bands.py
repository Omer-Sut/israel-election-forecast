"""E022: minimum-width scenario bands and diverse feasible alternatives; no AI calls."""
import argparse
import copy
import csv
from fractions import Fraction
import hashlib
from html import escape
import json
from pathlib import Path
import statistics
import sys
import time

if __package__ in (None,''):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import baseline, numerical_search as ns

ROOT=baseline.ROOT
CONFIG=ROOT/'config/diversity-bands.json'


def legal(vector,total=120):
    return sum(vector)==total and all(type(v) is int and (v==0 or 3<=v<=total) for v in vector)


def int_weight(value,scale):
    value=Fraction(value)*scale
    if value.denominator!=1: raise ValueError('Inexact model weight')
    return value.numerator


def covered_mass(case,lower,upper,total=120):
    family=case['family']
    covered=[legal(v,total) and all(a<=x<=b for a,x,b in zip(lower,v,upper)) for v in family['scenarios']]
    return [sum(int_weight(w,family['scale']) for k,w in m['weights'].items() if covered[int(k)]) for m in family['models']]


def region_count(lower,upper,fixed=None,total=120):
    states={0:1}; fixed=fixed or {}
    for i,(lo,hi) in enumerate(zip(lower,upper)):
        choices=[int(fixed[i])] if i in fixed else [v for v in range(lo,hi+1) if v==0 or v>=3]
        choices=[v for v in choices if lo<=v<=hi]; following={}
        for assigned,count in states.items():
            for value in choices:
                if assigned+value<=total: following[assigned+value]=following.get(assigned+value,0)+count
        states=following
    return states.get(total,0)


def minimum_width(case,coverage,config,total=120):
    from ortools.sat.python import cp_model as cp
    if not 0<Fraction(coverage)<1: raise ValueError('Coverage must lie strictly between zero and one')
    family=case['family']; reference=family['reference']; width=len(reference)
    if not legal(reference,total): raise ValueError('Invalid anchor')
    model=cp.CpModel(); allowed=[0]+list(range(3,total+1))
    lower=[model.new_int_var_from_domain(cp.Domain.from_values([v for v in allowed if v<=r]),'L'+str(i)) for i,r in enumerate(reference)]
    upper=[model.new_int_var_from_domain(cp.Domain.from_values([v for v in allowed if v>=r]),'U'+str(i)) for i,r in enumerate(reference)]
    for key,value in family.get('fixed',{}).items():
        model.add(lower[int(key)]==value); model.add(upper[int(key)]==value)
    included=[model.new_bool_var('covered'+str(s)) for s in range(len(family['scenarios']))]
    for s,vector in enumerate(family['scenarios']):
        if not legal(vector,total): model.add(included[s]==0); continue
        for i,value in enumerate(vector):
            model.add(lower[i]<=value).only_enforce_if(included[s]); model.add(upper[i]>=value).only_enforce_if(included[s])
    target=Fraction(coverage)*family['scale']; required=(target.numerator+target.denominator-1)//target.denominator
    for item in family['models']:
        model.add(sum(int_weight(w,family['scale'])*included[int(k)] for k,w in item['weights'].items())>=required)
    objective=sum(u-l for l,u in zip(lower,upper)); model.minimize(objective)
    def solver():
        s=cp.CpSolver(); s.parameters.max_time_in_seconds=config['solver_seconds']; s.parameters.num_search_workers=1; s.parameters.random_seed=config['seed']; return s
    first=solver(); status=first.solve(model)
    result={'status':first.status_name(status),'primary_optimal':status==cp.OPTIMAL,'coverage_target':str(coverage),
        'primary_lower_bound':first.best_objective_bound,'label':'scenario coverage, not calibrated confidence'}
    if status not in (cp.OPTIMAL,cp.FEASIBLE): return result
    lo=[int(first.value(v)) for v in lower]; hi=[int(first.value(v)) for v in upper]; optimal_width=sum(b-a for a,b in zip(lo,hi))
    # Frozen secondary rule; no historical outcomes appear in either optimization.
    model.add(objective==optimal_width); deviations=[]
    for i,r in enumerate(reference):
        a=model.new_int_var(0,2*total,'center'+str(i)); model.add_abs_equality(a,lower[i]+upper[i]-2*r); deviations.append(a)
    model.minimize(sum(deviations)); second=solver(); second_status=second.solve(model)
    if second_status in (cp.OPTIMAL,cp.FEASIBLE): lo=[int(second.value(v)) for v in lower]; hi=[int(second.value(v)) for v in upper]
    mass=covered_mass(case,lo,hi,total)
    if min(mass)<required or sum(b-a for a,b in zip(lo,hi))!=optimal_width: raise ValueError('Band certificate recomputation failed')
    result.update(lower=lo,upper=hi,total_width=optimal_width,secondary_status=second.status_name(second_status),
        model_coverage=[str(Fraction(v,family['scale'])) for v in mass],minimum_model_coverage=float(Fraction(min(mass),family['scale'])),
        feasible_vector_count=str(region_count(lo,hi,{int(k):v for k,v in family.get('fixed',{}).items()},total)))
    return result


def score_band(lower,upper,actual,coverage):
    distances=[max(a-y,y-b,0) for a,b,y in zip(lower,upper,actual)]
    width=sum(b-a for a,b in zip(lower,upper)); penalty=Fraction(2)/(1-Fraction(coverage))
    return {'total_width':width,'joint_covered':not any(distances),'parties_covered':sum(v==0 for v in distances),
        'party_count':len(actual),'maximum_miss':max(distances,default=0),
        'sum_marginal_interval_score':float(width+penalty*sum(distances))}


def earlier_inflation(previous_misses,coverage):
    n=len(previous_misses); rank=Fraction(coverage)*(n+1); rank=(rank.numerator+rank.denominator-1)//rank.denominator
    if rank>n: return {'status':'unavailable_insufficient_campaigns','earlier_campaigns':n,'rank':rank,'inflation':None}
    return {'status':'available_assumption_diagnostic','earlier_campaigns':n,'rank':rank,'inflation':sorted(previous_misses)[rank-1],
        'limitation':'Exchangeability unverified; repeated campaigns and prior inspection prevent a calibrated guarantee.'}


def inflate(lower,upper,amount,fixed=None,total=120):
    lo=[];hi=[];fixed=fixed or {}
    for i,(a,b) in enumerate(zip(lower,upper)):
        if i in fixed: lo.append(fixed[i]);hi.append(fixed[i]);continue
        x=max(0,a-amount); y=min(total,b+amount)
        lo.append(3 if 0<x<3 else x); hi.append(0 if 0<y<3 else y)
    return lo,hi


def restore_family(case):
    family=copy.deepcopy(case['family']);family['fixed']={int(k):v for k,v in family['fixed'].items()}
    for item in family['models']: item['weights']={int(k):Fraction(w) for k,w in item['weights'].items()}
    return family


def exact_regret(p,oracles,vector):
    return max(sum(int(c)*int(vector[i]==v) for c,(i,v) in zip(costs,p['slots']))-oracle for costs,oracle in zip(p['costs'],oracles))


def diverse_vectors(case,budget,tolerance,config,deadline=None):
    from ortools.sat.python import cp_model as cp
    family=restore_family(case); original=next(c for c in case['cells'] if c['budget']==budget)
    if not original['highs']['optimal'] or not all(c['optimal'] for c in original['oracles']): raise ValueError('Uncertified E021 input')
    p=ns.problem(case,family,budget);oracles=[r['value_scaled'] for r in original['oracles']]
    cap=original['highs']['value_scaled']+tolerance*family['scale'];kept=[family['reference']]
    if exact_regret(p,oracles,kept[0])>cap: raise ValueError('Anchor outside chosen regret band')
    result={'budget':budget,'tolerance':tolerance,'status':'running','vectors':kept,'steps':[],
        'label':'Sequential greedy max-min diversity; not a globally optimal batch or random sample.'}
    while len(kept)<config['maximum_diverse_vectors']:
        if deadline is not None and time.monotonic()>deadline: result['status']='partial_soft_deadline';break
        model,y,seats,_=ns.cp_model(p,oracles,cap=cap); distance=model.new_int_var(0,240,'minimum_distance')
        for old in kept: model.add(distance<=sum(abs(v-old[i])*y[k] for k,(i,v) in enumerate(p['slots'])))
        model.maximize(distance); solver=cp.CpSolver(); solver.parameters.max_time_in_seconds=config['solver_seconds']
        solver.parameters.num_search_workers=1;solver.parameters.random_seed=config['seed'];status=solver.solve(model)
        step={'status':solver.status_name(status),'optimal_step':status==cp.OPTIMAL,'upper_bound':solver.best_objective_bound}
        result['steps'].append(step)
        if status not in (cp.OPTIMAL,cp.FEASIBLE): result['status']='incomplete_search';break
        vector=[int(solver.value(v)) for v in seats];actual=min(sum(abs(a-b) for a,b in zip(vector,old)) for old in kept)
        ns.validate(vector,family['reference'],budget,family['fixed'])
        regret=exact_regret(p,oracles,vector)
        if regret>cap: raise ValueError('Diversity vector outside regret band')
        if status==cp.OPTIMAL and actual!=int(round(solver.objective_value)): raise ValueError('Diversity objective mismatch')
        step.update(actual_minimum_l1=actual,regret_scaled=regret)
        if actual==0:
            result['status']='exhausted' if status==cp.OPTIMAL else 'incomplete_search';break
        kept.append(vector)
    else: result['status']='requested_count_reached'
    result['all_steps_optimal']=all(s['optimal_step'] for s in result['steps'])
    result['minimum_pairwise_l1']=min((sum(abs(a-b) for a,b in zip(v,w)) for i,v in enumerate(kept) for w in kept[:i]),default=None)
    return result


def execute(source,config,out):
    started=time.monotonic(); deadline=started+60*config['soft_deadline_minutes']
    result={'status':'running','config':config,'forecast_changed':False,'turnout':'69.86','bands':[],'diversity':[],
        'labels':config['labels'],'source_run':config['source_run']}
    def checkpoint(): result['elapsed_seconds']=round(time.monotonic()-started,3);write(result,out)
    histories=sorted([c for c in source['cases'] if 'actual' in c],key=lambda c:c['cutoff'])
    current=next(c for c in source['cases'] if c['election']=='current_2026')
    prior={str(q):[] for q in config['scenario_joint_coverage']};prior_ids={str(q):[] for q in config['scenario_joint_coverage']}
    checkpoint()
    for case in histories+[current]:
        if time.monotonic()>deadline: result['status']='partial_soft_deadline';break
        entry={'election':case['election'],'cutoff':case['cutoff'],'party_ids':case['party_ids'],'reference':case['family']['reference'],'levels':[]};result['bands'].append(entry)
        for q in config['scenario_joint_coverage']:
            if time.monotonic()>deadline: result['status']='partial_soft_deadline';break
            print(f'BANDS {case["election"]} level={q}',flush=True)
            band=minimum_width(case,q,config); item={'level':q,'raw':band};entry['levels'].append(item)
            if 'lower' not in band: checkpoint();continue
            calibration=earlier_inflation(prior[q],q);calibration['earlier_campaign_ids']=list(prior_ids[q]);item['inflation_diagnostic']=calibration
            if calibration['inflation'] is not None:
                lo,hi=inflate(band['lower'],band['upper'],calibration['inflation'],{int(k):v for k,v in case['family']['fixed'].items()})
                calibration.update(lower=lo,upper=hi,total_width=sum(b-a for a,b in zip(lo,hi)),feasible_vector_count=str(region_count(lo,hi,{int(k):v for k,v in case['family']['fixed'].items()})))
            n=len(case['selected_poll_ids']); polls=case['family']['scenarios'][:n]
            envelope=([min(v[i] for v in polls) for i in range(len(case['party_ids']))],[max(v[i] for v in polls) for i in range(len(case['party_ids']))])
            item['poll_envelope']={'lower':envelope[0],'upper':envelope[1],'label':'Poll-disagreement envelope; no calibrated probability'}
            # Only now join the target outcome; it cannot affect raw bands or inflation.
            if 'actual' in case:
                truth=[case['actual'][k] for k in case['party_ids']]
                item['raw_scores']=score_band(band['lower'],band['upper'],truth,q)
                item['poll_envelope_scores']=score_band(*envelope,truth,q)
                if calibration['inflation'] is not None: item['inflation_scores']=score_band(calibration['lower'],calibration['upper'],truth,q)
                if band['primary_optimal']:prior[q].append(item['raw_scores']['maximum_miss']);prior_ids[q].append(case['election'])
            checkpoint()
    if result['status']=='running':
        for budget in config['diversity_budgets']:
            for tolerance in config['regret_tolerances']:
                if time.monotonic()>deadline: result['status']='partial_soft_deadline';break
                print(f'DIVERSITY budget={budget} tolerance={tolerance}',flush=True)
                result['diversity'].append(diverse_vectors(current,budget,tolerance,config,deadline));checkpoint()
            if result['status']!='running':break
    if result['status']=='running': result['status']='completed'
    if any(not x['raw']['primary_optimal'] for r in result['bands'] for x in r['levels']) and result['status']=='completed':result['status']='completed_with_uncertified_bands'
    if any(d['status'] not in ('requested_count_reached','exhausted') or not d['all_steps_optimal'] for d in result['diversity']) and result['status']=='completed':result['status']='completed_with_partial_diversity'
    checkpoint();return result


def write(result,out):
    out.mkdir(parents=True,exist_ok=True)
    def save(name,text):
        temp=out/(name+'.tmp');temp.write_text(text,encoding='utf-8',newline='\n');temp.replace(out/name)
    save('results.json',json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    lines=['# E022 diversity and prediction-band diagnostics — START HERE','',f"Status: **{result['status']}**; elapsed {result.get('elapsed_seconds',0):.0f}s.",'',
        '**Forecast unchanged. These are scenario-coverage bands and assumption diagnostics, not calibrated confidence intervals.**','',
        '## Historical band diagnostics','', '| Campaign | Scenario target | Minimum width status | Width | Actual whole-election covered? | Marginal interval-score sum | Inflation diagnostic |', '|---|---|---|---:|---|---:|---|']
    for r in result['bands']:
        for x in r['levels']:
            s=x.get('raw_scores',{});b=x['raw'];inf=x.get('inflation_diagnostic',{})
            lines.append(f"|{r['election']}|{x['level']}|{b['status']}|{b.get('total_width','—')}|{s.get('joint_covered','current: unknown')}|{s.get('sum_marginal_interval_score','—')}|{inf.get('status','unavailable')}|")
    lines+=['','Joint scenario coverage is imposed separately for every assumed E021 model. The interval score sums univariate scores and is an auxiliary marginal diagnostic, not a proper joint-region score or proof of joint calibration. Narrow model bands can miss actual elections. Interval bounds are intersected with integer/total120/zero-or3plus constraints; coordinate endpoints cannot be combined freely.','',
        'The inflation rank uses only earlier whole-election misses: ceil((n+1)×target). If the required rank exceeds n, no finite estimate is reported. Six earlier elections are insufficient for a finite90%rank; exchangeability is also unverified. Parties are not treated as independent calibration samples.','',
        '## Diverse current alternatives','', '| Budget | Regret tolerance | Vectors | Status | All greedy steps optimal? | Minimum pairwise L1 |','|---|---:|---:|---|---|---:|']
    for d in result['diversity']:lines.append(f"|{d['budget']}|{d['tolerance']}|{len(d['vectors'])}|{d['status']}|{d['all_steps_optimal']}|{d['minimum_pairwise_l1']}|")
    lines+=['','Greedy max-min means each added vector is chosen far from the previously selected set. It is not proof that the final batch is globally most diverse. Tolerance3 deliberately admits forecasts with worse assumed regret than tolerance1. Neither diversity nor counts imply electoral probability or improved seat accuracy.','',
        'Files: results.json, diversity.csv, current-bands.svg, diversity.svg, inputs-manifest.json and run.log. Read solver statuses and unavailable calibration entries. Full outputs remain artifact-only; no auto-adoption, commit, merge or competition submission.']
    save('START_HERE.md','\n'.join(lines)+'\n')
    current=next((c for c in result['bands'] if c['election']=='current_2026'),None)
    if current:
        with (out/'diversity.csv').open('w',encoding='utf-8',newline='') as f:
            writer=csv.writer(f,lineterminator='\n');writer.writerow(['budget','regret_tolerance','sequence']+current['party_ids'])
            for d in result['diversity']:
                for i,v in enumerate(d['vectors']):writer.writerow([d['budget'],d['tolerance'],i]+v)
    plot(result,out)


def plot(result,out):
    current=next((c for c in result['bands'] if c['election']=='current_2026'),None)
    head='<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="800" viewBox="0 0 1180 800"><rect width="1180" height="800" fill="white"/><g font-family="Arial,sans-serif" fill="#21384b">'
    p=[head,'<text x="25" y="32" font-size="23">E022: current scenario bands — not confidence intervals</text>']
    if current:
        sets=[(x['level'],x['raw']) for x in current['levels'] if 'lower' in x['raw']]
        scale=max([30]+[max(b['upper']) for label,b in sets]);colors=['#246e9b','#8a4284']
        for i,key in enumerate(current['party_ids']):
            y=95+i*39;p.append(f'<text x="20" y="{y+4}" font-size="13">{escape(key)}</text>')
            for j,(label,b) in enumerate(sets):
                x1=260+800*b['lower'][i]/scale;x2=260+800*b['upper'][i]/scale
                p.append(f'<path d="M{x1:.2f},{y+j*7}H{x2:.2f}" stroke="{colors[j%2]}" stroke-width="5"><title>{label}: {b["lower"][i]}..{b["upper"][i]}</title></path>')
            x=260+800*current['reference'][i]/scale;p.append(f'<circle cx="{x:.2f}" cy="{y+3}" r="3" fill="#222"/>')
        p.append('<text x="25" y="730" font-size="14">Blue80% / purple90% refer to assumed joint scenario mass, not validated election coverage.</text>')
    p.append('<text x="25" y="770" font-size="13">Raw model bands shown; historical inflation diagnostics and unavailable levels are in START_HERE.md/results.json.</text></g></svg>')
    (out/'current-bands.svg').write_text('\n'.join(p)+'\n',encoding='utf-8')
    q=[head,'<text x="25" y="32" font-size="23">E022: diverse current forecasts — not probabilities</text>']
    if current:
        indices=[current['party_ids'].index(k) for k in result['config']['current_focus']];colors=['#246e9b','#8a4284','#b47822','#278267']
        for j,d in enumerate(result['diversity']):
            for v in d['vectors']:
                x=130+v[indices[0]]*90+j*4;y=590-v[indices[1]]*90-j*4
                q.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{colors[j%4]}"><title>Budget{d["budget"]}, tolerance{d["tolerance"]}: {v[indices[0]]}/{v[indices[1]]}</title></circle>')
            q.append(f'<text x="25" y="{660+j*24}" fill="{colors[j%4]}" font-size="14">Budget{d["budget"]}, tolerance{d["tolerance"]}: {len(d["vectors"])}greedy representatives</text>')
        q.append('<text x="25" y="90" font-size="16">Amcha seats ↑</text><text x="400" y="620" font-size="16">Reservists seats →</text>')
    q.append('</g></svg>');(out/'diversity.svg').write_text('\n'.join(q)+'\n',encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source-dir',type=Path,required=True);parser.add_argument('--out-dir',type=Path,default=ROOT/'output/diversity-bands-2026-10-26')
    args=parser.parse_args();config=baseline.load_json(CONFIG);raw=(args.source_dir/'checkpoint.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=config['source_checkpoint_sha256']:raise ValueError('Source checkpoint hash does not match audited E021 run')
    args.out_dir.mkdir(parents=True,exist_ok=True)
    paths=['scripts/diversity_bands.py','config/diversity-bands.json','scripts/numerical_search.py','requirements-numerical-search.txt','reports/forecast-decision-2026-10-25/forecast.json']
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths};hashes['E021/checkpoint.json']=hashlib.sha256(raw).hexdigest()
    (args.out_dir/'inputs-manifest.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
    try:execute(json.loads(raw),config,args.out_dir)
    except Exception as e:
        (args.out_dir/'FAILURE.txt').write_text(type(e).__name__+': '+str(e)+'\nInspect results.json for partial checkpoints. Forecast unchanged.\n',encoding='utf-8');raise
