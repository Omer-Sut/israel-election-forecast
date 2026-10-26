"""E021: finite scenario-model minimax-regret search; no model/API calls."""
import argparse
from collections import Counter
import csv
from fractions import Fraction
import hashlib
from html import escape
import itertools
import json
import math
from pathlib import Path
import statistics
import sys
import time

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import baseline, forecast_review, threshold_trial as tt

ROOT = baseline.ROOT
CONFIG = ROOT/'config/numerical-search.json'


def fixed_fields(case):
    return {case['ids'].index('other_qualifying_lists'): 0} if 'other_qualifying_lists' in case['ids'] else {}


def validate(vector, reference, budget, fixed, total=120, minimum=3):
    if len(vector) != len(reference) or any(type(v) is not int or v < 0 or 0 < v < minimum for v in vector) or sum(vector) != total:
        raise ValueError('Invalid integer/total/positive-seat constraints')
    if any(vector[i] != v for i, v in fixed.items()):
        raise ValueError('Fixed individual-list/roster scope violated')
    if budget is not None and sum(abs(a-b) for a,b in zip(vector, reference)) > budget:
        raise ValueError('Adjustment budget violated')


def scenario_models(case, config):
    """Only inputs used here; outcomes are joined for scoring after optimization."""
    polls = [list(v) for v in case['vectors']]; n = len(polls); fixed = fixed_fields(case)
    reference = forecast_review.constrained_decision(polls, fixed=fixed)
    models = []; scenarios = list(polls)
    def add(name, weights):
        weights = {i: Fraction(w) for i,w in weights.items() if w}
        if sum(weights.values()) != 1 or any(w < 0 for w in weights.values()):
            raise ValueError('Invalid model weights')
        models.append({'name': name, 'weights': weights})
    empirical = {i: Fraction(1,n) for i in range(n)}
    add('empirical', empirical)
    if n > 1:
        for omitted in range(n):
            add('leave_firm_'+str(omitted), {i: Fraction(1,n-1) for i in range(n) if i != omitted})
    candidates = []
    for i, key in enumerate(case['ids']):
        column = [v[i] for v in polls]; fraction = sum(v>0 for v in column)/n
        if i not in fixed and 0 < fraction < 1 and statistics.mean(column) <= 6 and max(column) <= 8:
            candidates.append((abs(fraction-.5), key, i))
    candidates = [i for _,_,i in sorted(candidates)[:config['maximum_threshold_candidates']]]
    # Conditional vectors use the same allocator and inputs; no vote reconstruction.
    for positive in config['threshold_positive_branches']:
        patterns = {}
        for bits in itertools.product((0,1), repeat=len(candidates)):
            if not candidates: continue
            conditions = {**fixed, **{i: positive*bit for i,bit in zip(candidates,bits)}}
            vector = forecast_review.constrained_decision(polls, fixed=conditions)
            patterns[bits] = len(scenarios); scenarios.append(vector)
        if not patterns: continue
        for probabilities in itertools.product(config['threshold_assumed_pass_weights'], repeat=len(candidates)):
            blend = Fraction(config['threshold_model_mixture']); weights = {i: (1-blend)*w for i,w in empirical.items()}
            for bits, index in patterns.items():
                p = math.prod(Fraction(q) if bit else 1-Fraction(q) for bit,q in zip(bits,probabilities))
                weights[index] = blend*p
            add('threshold_'+str(positive)+'_'+'_'.join(probabilities), weights)
    stress = []
    largest = sorted((i for i in range(len(reference)) if i not in fixed), key=lambda i: (-case['anchor'][i], case['ids'][i]))[:2]
    for i in largest:
        for change in config['largest_party_stress_seats']:
            value = reference[i]+change
            if value < 0 or value > 120 or 0 < value < 3: continue
            vector = forecast_review.constrained_decision(polls, fixed={**fixed, i:value})
            stress.append(len(scenarios)); scenarios.append(vector)
    if stress:
        for q in config['stress_mixture_weights']:
            blend = Fraction(q); weights = {i: (1-blend)*w for i,w in empirical.items()}
            weights.update({i: blend/len(stress) for i in stress}); add('balanced_transfer_stress_'+q, weights)
    for vector in scenarios[n:]: validate(vector, reference, None, fixed)
    scale = math.lcm(*(w.denominator for m in models for w in m['weights'].values()))
    if scale > 10**7: raise ValueError('Unexpected rational objective scale')
    return {'reference': reference, 'scenarios': scenarios, 'models': models, 'scale': scale,
        'threshold_candidates': [case['ids'][i] for i in candidates], 'fixed': fixed}


def problem(case, family, budget, total=120, minimum=3):
    import numpy as np
    slots = []; groups = []
    for i, anchor in enumerate(family['reference']):
        choices = [family['fixed'][i]] if i in family['fixed'] else [0]+list(range(minimum,total+1))
        choices = [v for v in choices if budget is None or abs(v-anchor) <= budget]
        groups.append(list(range(len(slots), len(slots)+len(choices))))
        slots += [(i,v) for v in choices]
    costs = np.zeros((len(family['models']), len(slots)), dtype=np.int64)
    for m, model in enumerate(family['models']):
        for s, weight in model['weights'].items():
            w = int(weight*family['scale'])
            costs[m] += np.array([w*abs(v-family['scenarios'][s][i]) for i,v in slots], dtype=np.int64)
    return {'slots': slots, 'groups': groups, 'costs': costs, 'family': family, 'budget': budget, 'total': total}


def highs(p, objective=None, oracles=None, seconds=15):
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import coo_matrix
    slots = p['slots']; count = len(slots); rr=[]; cc=[]; vv=[]; lower=[]; upper=[]
    def row(entries, lo, hi):
        index = len(lower); lower.append(lo); upper.append(hi)
        for c,v in entries:
            if v: rr.append(index); cc.append(c); vv.append(v)
    for indices in p['groups']: row([(k,1) for k in indices], 1, 1)
    row([(k,v) for k,(i,v) in enumerate(slots)], p['total'], p['total'])
    if p['budget'] is not None:
        row([(k,abs(v-p['family']['reference'][i])) for k,(i,v) in enumerate(slots)], -np.inf, p['budget'])
    if oracles is not None:
        for costs, oracle in zip(p['costs'],oracles):
            row([(k,int(v)) for k,v in enumerate(costs)]+[(count,-1)], -np.inf, oracle)
    a = coo_matrix((vv,(rr,cc)), shape=(len(lower),count+1)).tocsc()
    c = np.r_[np.zeros(count),1.] if objective is None else np.r_[objective,0.]
    solved = milp(c, integrality=np.r_[np.ones(count),0], bounds=Bounds(np.zeros(count+1), np.r_[np.ones(count),np.inf]),
        constraints=LinearConstraint(a,lower,upper), options={'time_limit':seconds,'mip_rel_gap':0.})
    finite = lambda v: float(v) if v is not None and math.isfinite(float(v)) else None
    result = {'status': int(solved.status), 'optimal': solved.status==0, 'message': str(solved.message),
        'gap': finite(getattr(solved,'mip_gap',None)),
        'lower_bound': finite(getattr(solved,'mip_dual_bound',None))}
    if solved.x is not None:
        vector = [0]*len(p['groups'])
        for indices in p['groups']:
            selected = [k for k in indices if solved.x[k] > .5]
            if len(selected)!=1: raise ValueError('Nonintegral one-hot result')
            i,v = slots[selected[0]]; vector[i]=v
        validate(vector, p['family']['reference'], p['budget'], p['family']['fixed'], p['total'])
        y = np.array([int(vector[i]==v) for i,v in slots],dtype=np.int64)
        value = int(max(p['costs']@y-np.array(oracles))) if oracles is not None else int(np.asarray(objective)@y)
        if abs(float(solved.fun)-value)>1e-4: raise ValueError('Solver objective does not match exact integer recomputation')
        result.update(seats=vector, value_scaled=value)
    return result


def cp_model(p, oracles, cap=None, conditions=None):
    from ortools.sat.python import cp_model as cp
    model=cp.CpModel(); y=[model.new_bool_var('y'+str(k)) for k in range(len(p['slots']))]
    for group in p['groups']: model.add(sum(y[k] for k in group)==1)
    seats=[sum(p['slots'][k][1]*y[k] for k in group) for group in p['groups']]
    model.add(sum(seats)==p['total'])
    if p['budget'] is not None:
        model.add(sum(abs(v-p['family']['reference'][i])*y[k] for k,(i,v) in enumerate(p['slots'])) <= p['budget'])
    for i,v in (conditions or {}).items(): model.add(seats[i]==v)
    bound=max(1,int(p['costs'].max())*len(p['groups']))
    t=model.new_int_var(0,bound,'regret') if cap is None else None
    for costs, oracle in zip(p['costs'],oracles):
        expression=sum(int(v)*y[k] for k,v in enumerate(costs) if v)
        model.add(expression <= int(oracle)+(t if t is not None else int(cap)))
    if t is not None: model.minimize(t)
    return model, y, seats, t


def cp_solve(p, oracles, config, conditions=None):
    from ortools.sat.python import cp_model as cp
    model,y,seats,t=cp_model(p,oracles,conditions=conditions); solver=cp.CpSolver()
    solver.parameters.max_time_in_seconds=config['cp_seconds']; solver.parameters.num_search_workers=1
    solver.parameters.random_seed=config['seed']; status=solver.solve(model)
    result={'status':solver.status_name(status),'optimal':status==cp.OPTIMAL,'lower_bound':solver.best_objective_bound}
    if status in (cp.OPTIMAL,cp.FEASIBLE):
        vector=[int(solver.value(v)) for v in seats]
        validate(vector,p['family']['reference'],p['budget'],p['family']['fixed'],p['total'])
        exact=max(sum(int(c)*int(vector[i]==v) for c,(i,v) in zip(cost,p['slots']))-oracle for cost,oracle in zip(p['costs'],oracles))
        if exact!=int(round(solver.objective_value)): raise ValueError('CP objective recomputation failed')
        result.update(seats=vector,value_scaled=exact)
    return result


def enumerate_near(p, oracles, optimum, config):
    from ortools.sat.python import cp_model as cp
    cap=optimum+config['near_optimal_regret_seats']*p['family']['scale']
    model,y,seats,_=cp_model(p,oracles,cap=cap)
    class Capture(cp.CpSolverSolutionCallback):
        def __init__(self): super().__init__(); self.vectors=[]; self.capped=False
        def on_solution_callback(self):
            vector=[int(self.value(v)) for v in seats]
            validate(vector,p['family']['reference'],p['budget'],p['family']['fixed'],p['total'])
            self.vectors.append(vector)
            if len(self.vectors)>=config['maximum_near_optimal_vectors']: self.capped=True; self.stop_search()
    capture=Capture(); solver=cp.CpSolver(); solver.parameters.enumerate_all_solutions=True
    solver.parameters.max_time_in_seconds=config['enumeration_seconds']; solver.parameters.num_search_workers=1
    solver.parameters.random_seed=config['seed']; status=solver.solve(model,capture)
    return {'status':solver.status_name(status),'cap_scaled':cap,'vectors':capture.vectors,'count_capped':capture.capped,
        'interpretation':'Bounded deterministic enumeration, not random sampling or electoral probabilities.'}


def serial_family(family):
    return {**family,'models':[{'name':m['name'],'weights':{str(k):str(v) for k,v in m['weights'].items()}} for m in family['models']]}


def execute(config, out):
    started=time.monotonic(); deadline=started+60*config['soft_deadline_minutes']
    cases=[tt.current_case()]+tt.historical_cases(baseline.load_json(tt.CONFIG))
    report={'config':config,'commit':__import__('os').environ.get('GITHUB_SHA'),'status':'running','cases':[],
        'forecast_changed':False,'turnout':'69.86','interpretation':'Sensitivity experiment. No auto-adoption or calibrated probabilities.'}
    def checkpoint():
        report['elapsed_seconds']=round(time.monotonic()-started,3); write(report,out)
    checkpoint()
    for case in cases:
        if time.monotonic()>deadline: report['status']='partial_soft_deadline'; break
        family=scenario_models(case,config); cells=[]
        control=tt.controls(case)
        # Scope matches the solver, including the current individual-other gate.
        for item in control.values(): validate(item['seats'],family['reference'],None,family['fixed'])
        record={'election':case['election_id'],'period':case.get('period','current'),'cutoff':case['cutoff'],
            'party_ids':case['ids'],'family':serial_family(family),'selected_poll_ids':[p['id'] for p in case['selected_polls']],
            'controls':{k:{'seats':v['seats']} for k,v in control.items()},'cells':cells}
        if 'actual' in case:
            record['actual']=case['actual']
            for item in record['controls'].values(): item['seat_l1']=sum(abs(v-case['actual'][k]) for k,v in zip(case['ids'],item['seats']))
        report['cases'].append(record); checkpoint()
        for budget in config['budgets']:
            if time.monotonic()>deadline: report['status']='partial_soft_deadline'; break
            p=problem(case,family,budget); cell={'budget':budget,'status':'oracles','oracles':[]}; cells.append(cell)
            print(f"START {case['election_id']} budget={budget}, models={len(family['models'])}",flush=True)
            for costs,model in zip(p['costs'],family['models']):
                if time.monotonic()>deadline: break
                solved=highs(p,objective=costs,seconds=config['solver_seconds']); cell['oracles'].append({'model':model['name'],**solved})
                checkpoint()
                if not solved['optimal']: break
            if len(cell['oracles'])!=len(family['models']) or not all(r['optimal'] for r in cell['oracles']):
                cell['status']='incomplete_oracle_certificates'; checkpoint(); continue
            oracles=[r['value_scaled'] for r in cell['oracles']]
            cell['highs']=highs(p,oracles=oracles,seconds=config['solver_seconds'])
            cell['status']='complete' if cell['highs']['optimal'] else 'uncertified_robust_solution'
            if 'actual' in case and 'seats' in cell['highs']:
                cell['seat_l1']=sum(abs(v-case['actual'][k]) for k,v in zip(case['ids'],cell['highs']['seats']))
            if case['election_id']=='current_2026' or budget==12:
                cell['cp_sat']=cp_solve(p,oracles,config)
                if cell['highs']['optimal'] and cell['cp_sat']['optimal'] and cell['highs']['value_scaled']!=cell['cp_sat']['value_scaled']:
                    raise ValueError('Independent solvers disagree on certified regret')
            if case['election_id']=='current_2026' and cell['highs']['optimal']:
                cell['near_optimal']=enumerate_near(p,oracles,cell['highs']['value_scaled'],config)
                focus=[case['ids'].index(k) for k in config['current_focus']]
                cell['focus_conditions']=[]
                for values in itertools.product((0,3,4),repeat=len(focus)):
                    if time.monotonic()>deadline: break
                    result=cp_solve(p,oracles,config,dict(zip(focus,values)))
                    cell['focus_conditions'].append({'values':list(values),**result}); checkpoint()
            checkpoint(); print(f"DONE {case['election_id']} budget={budget} {cell['status']}",flush=True)
    else:
        if report['status']=='running': report['status']='completed'
    if any(c['status']!='complete' for r in report['cases'] for c in r['cells']): report['status']='completed_with_incomplete_cells' if report['status']=='completed' else report['status']
    checkpoint(); return report


def write(report,out):
    out.mkdir(parents=True,exist_ok=True)
    def save(name,value):
        path=out/name; temporary=out/(name+'.tmp'); temporary.write_text(value,encoding='utf-8',newline='\n'); temporary.replace(path)
    save('checkpoint.json',json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    lines=['# Numerical search E021 — START HERE','',f"Status: **{report['status']}**. Elapsed: {report.get('elapsed_seconds',0):.0f} seconds.",'',
        '**Research only: adopted forecast and turnout69.86% are unchanged.** Scenario weights, thresholds and stress magnitudes are assumptions; enumeration counts are not probabilities.','',
        '| Campaign | Budget | Solver status | Seat error (history only) | Worst regret (assumed models) |','|---|---:|---|---:|---:|']
    for r in report['cases']:
        for c in r['cells']:
            value=c.get('highs',{}).get('value_scaled'); regret='—' if value is None else f"{value/r['family']['scale']:.4f}"
            lines.append(f"|{r['election']}|{c['budget'] if c['budget'] is not None else 'unrestricted'}|{c['status']}|{c.get('seat_l1','—')}|{regret}|")
    lines+=['','## Historical comparison','', '| Method | Complete campaigns | Mean seat L1 | Equal-period L1 |','|---|---:|---:|---:|']
    summaries={}
    history=[r for r in report['cases'] if 'actual' in r]
    for budget in report['config']['budgets']:
        pairs=[(r,c) for r in history for c in r['cells'] if c['budget']==budget and c['status']=='complete' and 'seat_l1' in c]
        methods={'robust_regret':[c['seat_l1'] for r,c in pairs]}
        methods.update({name:[r['controls'][name]['seat_l1'] for r,c in pairs] for name in tt.CONTROLS})
        for name,values in methods.items():
            if not values: continue
            mean=statistics.mean(values); periods=sorted({r['period'] for r,c in pairs})
            block=statistics.mean(statistics.mean(v for (r,c),v in zip(pairs,values) if r['period']==p) for p in periods)
            key=name+'_budget_'+str(budget); summaries[key]={'campaigns':len(values),'mean_l1':mean,'equal_period_l1':block}
            lines.append(f'|{key}|{len(values)}|{mean:.3f}|{block:.3f}|')
    lines+=['','Controls are scored on the same completed campaigns as each challenger. Budgets reference each campaign’s constrained mean. No historical party aliases, fitted corrections, or new holdout claim.','',
        '## Files','', '- `checkpoint.json`: full assumptions, model weights, solver certificates, historical scores and partial results.',
        '- `summary.json`: compact comparison and current alternatives.', '- `current-candidates.csv`: main and enumerated current vectors; counts are not probabilities.',
        '- `comparison.svg` and `focus.svg`: plots; open them in a browser.', '- `inputs-manifest.json`: code and data hashes.','',
        'Current and historical panels differ in firm count and forecast horizon. Source freeze/official mappings and full current vote shares/agreements remain incomplete. Other current qualifiers fixed0 as a roster assumption. No exact current Bader–Ofer or calibrated uncertainty claim.','',
        '## Next session','', 'Open this folder and read START_HERE.md. Review complete historical comparisons before changing the adopted forecast. Incomplete/feasible/time-limited solutions are labelled, not certified optima. Full files are artifact-only; commit only a reviewed compact report later.']
    save('START_HERE.md','\n'.join(lines)+'\n')
    current=next((r for r in report['cases'] if r['election']=='current_2026'),None)
    compact={'status':report['status'],'elapsed_seconds':report.get('elapsed_seconds'), 'historical':summaries,
        'current':None if current is None else {'party_ids':current['party_ids'],'reference':current['family']['reference'],
            'scale':current['family']['scale'],'cells':[{k:v for k,v in c.items() if k not in ('oracles','near_optimal')} for c in current['cells']]},'forecast_changed':False}
    save('summary.json',json.dumps(compact,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    if current:
        with (out/'current-candidates.csv').open('w',encoding='utf-8',newline='') as f:
            writer=csv.writer(f,lineterminator='\n'); writer.writerow(['budget','kind']+current['party_ids'])
            writer.writerow(['reference','adopted_mean']+current['family']['reference'])
            for c in current['cells']:
                if 'seats' in c.get('highs',{}): writer.writerow([c['budget'],'robust']+c['highs']['seats'])
                for v in c.get('near_optimal',{}).get('vectors',[]): writer.writerow([c['budget'],'near_optimal_not_probability']+v)
    plot(report,out)


def plot(report,out):
    for kind in ('comparison','focus'):
        p=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="650" viewBox="0 0 1120 650"><rect width="1120" height="650" fill="white"/><g font-family="Arial,sans-serif" fill="#21384b">',
            f'<text x="25" y="30" font-size="23">E021: {kind} — {escape(report["status"])}</text>',
            '<text x="25" y="58" font-size="14">Sensitivity diagnostics; no calibrated probabilities or automatic forecast adoption.</text>']
        if kind=='comparison':
            for j,budget in enumerate(report['config']['budgets']):
                rows=[(r,c) for r in report['cases'] if 'actual' in r for c in r['cells'] if c['budget']==budget and 'seat_l1' in c and c['status']=='complete']
                for k,(name,color) in enumerate([('robust','#8a4284'),(tt.CONTROLS[0],'#246e9b')]):
                    points=[]
                    for i,(r,c) in enumerate(rows):
                        error=c['seat_l1'] if name=='robust' else r['controls'][name]['seat_l1']; x=90+i*160; y=170+j*140-error*2
                        points.append(f'{x},{y}'); p.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"><title>{r["election"]}: {error}</title></circle>')
                    p.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2"/>')
                p.append(f'<text x="25" y="{210+j*140}" font-size="14">Budget {budget}: purple robust / blue constrained mean; lower seat error plots higher.</text>')
        else:
            current=next((r for r in report['cases'] if r['election']=='current_2026'),None)
            if current:
                focus=[current['party_ids'].index(k) for k in report['config']['current_focus']]
                colors=['#246e9b','#b47822','#8a4284']
                for j,c in enumerate(current['cells']):
                    counts=Counter((v[focus[0]],v[focus[1]]) for v in c.get('near_optimal',{}).get('vectors',[]))
                    for (a,b),n in counts.items():
                        x=100+a*60+j*7; y=490-b*60-j*7
                        p.append(f'<circle cx="{x}" cy="{y}" r="{min(18,4+math.sqrt(n)):.2f}" fill="{colors[j]}"><title>budget={c["budget"]}; Reservists={a}, Amcha={b}; enumerated={n} (not probability)</title></circle>')
                    p.append(f'<text x="{25+j*350}" y="575" fill="{colors[j]}" font-size="14">Budget {c["budget"]}: bounded enumeration</text>')
                p.append('<text x="400" y="530" font-size="16">Reservists seats →</text><text x="25" y="100" font-size="16">Amcha seats ↑</text>')
        p.append('<text x="25" y="625" font-size="13">Partial output is updated at checkpoints. Read START_HERE.md and solver statuses before interpreting.</text></g></svg>')
        (out/(kind+'.svg')).write_text('\n'.join(p)+'\n',encoding='utf-8',newline='\n')


def manifest(out):
    hc=baseline.load_json(ROOT/baseline.load_json(tt.CONFIG)['historical_config'])
    paths=['scripts/numerical_search.py','config/numerical-search.json','requirements-numerical-search.txt','scripts/threshold_trial.py',
        'scripts/forecast_review.py','scripts/baseline.py','scripts/experiments.py','scripts/backtest.py','config/threshold-trial.json',
        baseline.load_json(tt.CONFIG)['historical_config'],hc['outcomes_path'],'config/forecast-review.json','config/poll-mappings.json',
        'config/submission-fields.json','data/snapshots/polls-2026-10-24.json','reports/forecast-decision-2026-10-25/forecast.json']+[e['polls_path'] for e in hc['elections']]
    (out/'inputs-manifest.json').write_text(json.dumps({p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(set(paths))},indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--out-dir',type=Path,default=ROOT/'output/numerical-search-2026-10-26')
    args=parser.parse_args(); args.out_dir.mkdir(parents=True,exist_ok=True); manifest(args.out_dir)
    try: execute(baseline.load_json(CONFIG),args.out_dir)
    except Exception as error:
        (args.out_dir/'FAILURE.txt').write_text(type(error).__name__+': '+str(error)+'\nCheck checkpoint.json for partial results. Forecast unchanged.\n',encoding='utf-8')
        raise
