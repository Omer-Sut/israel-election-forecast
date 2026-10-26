// Post-run audit only. No fitting, solver execution, model calls or forecast writes.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import crypto from 'node:crypto';

const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
export async function analyze(input=path.join(root,'output/numerical-search-2026-10-26'),out=path.join(root,'output/e021-analysis')){
input=path.resolve(input);out=path.resolve(out);
await fs.mkdir(out,{recursive:true});
const raw=await fs.readFile(path.join(input,'checkpoint.json'),'utf8');
const report=JSON.parse(raw);
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const assert=(condition,message)=>{if(!condition)throw Error(message);};
const total=v=>v.reduce((a,b)=>a+b,0);
const l1=(a,b)=>total(a.map((v,i)=>Math.abs(v-b[i])));
const mean=v=>total(v)/v.length;
const safe=n=>{const x=Number(n);assert(Number.isSafeInteger(x),'Unsafe exact integer');return x;};
function weight(w,scale){const [a,b=1n]=w.split('/').map(BigInt);const x=a*BigInt(scale);assert(x%b===0n,'Noninteger weight scale');return x/b;}
function losses(c,v){return c.family.models.map(m=>safe(Object.entries(m.weights).reduce((s,[i,w])=>s+weight(w,c.family.scale)*BigInt(l1(v,c.family.scenarios[Number(i)])),0n)));}
function feasible(c,v,budget){
  assert(v.length===c.party_ids.length&&total(v)===120,'Incorrect vector shape/total');
  assert(v.every(x=>Number.isInteger(x)&&x>=0&&(x===0||x>=3)),'Invalid individual seats');
  for(const [i,x]of Object.entries(c.family.fixed))assert(v[Number(i)]===x,'Fixed roster scope violated');
  assert(budget===null||l1(v,c.family.reference)<=budget,'Budget violated');
}
function regret(c,cell,v){const values=losses(c,v);return Math.max(...values.map((x,i)=>x-cell.oracles[i].value_scaled));}
const audit={status:report.status,elapsed_seconds:report.elapsed_seconds,cases:report.cases.length,
  cells:0,certified_oracles:0,certified_robust_cells:0,independent_checks:[],conditional_statuses:{},historical:[],current:[],forecast_changed:false};
assert(report.status==='completed','Original search is incomplete');
for(const c of report.cases){
  for(const m of c.family.models)assert(Object.values(m.weights).reduce((s,w)=>s+weight(w,c.family.scale),0n)===BigInt(c.family.scale),'Weights do not total one');
  for(const cell of c.cells){
    audit.cells++;assert(cell.status==='complete','Incomplete cell');
    assert(cell.oracles.length===c.family.models.length,'Missing model oracle');
    for(let i=0;i<cell.oracles.length;i++){
      const o=cell.oracles[i];feasible(c,o.seats,cell.budget);
      assert(o.optimal&&o.gap===0,'Uncertified oracle');
      assert(losses(c,o.seats)[i]===o.value_scaled,'Oracle objective recomputation mismatch');
      assert(Math.abs(o.lower_bound-o.value_scaled)<1e-4,'Oracle primal/bound mismatch');audit.certified_oracles++;
    }
    feasible(c,cell.highs.seats,cell.budget);
    assert(cell.highs.optimal&&cell.highs.gap===0,'Uncertified robust solution');
    assert(regret(c,cell,cell.highs.seats)===cell.highs.value_scaled,'Robust objective mismatch');
    assert(Math.abs(cell.highs.lower_bound-cell.highs.value_scaled)<1e-4,'Robust primal/bound mismatch');audit.certified_robust_cells++;
    if(cell.cp_sat){
      feasible(c,cell.cp_sat.seats,cell.budget);assert(cell.cp_sat.optimal,'CP check not optimal');
      assert(regret(c,cell,cell.cp_sat.seats)===cell.cp_sat.value_scaled,'CP objective mismatch');
      assert(cell.cp_sat.value_scaled===cell.highs.value_scaled,'Independent objective disagreement');
      assert(Math.abs(cell.cp_sat.lower_bound-cell.cp_sat.value_scaled)<1e-4,'CP bound mismatch');
      audit.independent_checks.push({election:c.election,budget:cell.budget,same_vector:JSON.stringify(cell.cp_sat.seats)===JSON.stringify(cell.highs.seats)});
    }
    for(const item of cell.focus_conditions||[]){
      audit.conditional_statuses[item.status]=(audit.conditional_statuses[item.status]||0)+1;
      if(item.status==='INFEASIBLE')continue;
      assert(item.optimal,'Conditional not certified');feasible(c,item.seats,cell.budget);
      for(let i=0;i<report.config.current_focus.length;i++)assert(item.seats[c.party_ids.indexOf(report.config.current_focus[i])]===item.values[i],'Conditional choice mismatch');
      assert(regret(c,cell,item.seats)===item.value_scaled,'Conditional objective mismatch');
    }
  }
  if(c.actual){
    const truth=c.party_ids.map(k=>c.actual[k]);
    audit.historical.push({election:c.election,period:c.period,mean_error:l1(c.controls.square_0or3.seats,truth),
      l1_error:l1(c.controls.absolute_0or3.seats,truth),cells:c.cells.map(cell=>({budget:cell.budget,
        highs_error:l1(cell.highs.seats,truth),cp_error:cell.cp_sat?l1(cell.cp_sat.seats,truth):null}))});
  }else{
    for(const cell of c.cells){
      const near=cell.near_optimal;assert(near.status==='OPTIMAL'&&!near.count_capped,'Enumeration did not finish');
      assert(new Set(near.vectors.map(v=>JSON.stringify(v))).size===near.vectors.length,'Duplicate enumerated vectors');
      for(const v of near.vectors){feasible(c,v,cell.budget);assert(regret(c,cell,v)<=near.cap_scaled,'Vector outside near-optimal band');}
      const exact=near.vectors.filter(v=>regret(c,cell,v)===cell.highs.value_scaled);
      audit.current.push({budget:cell.budget,optimum_regret:cell.highs.value_scaled/c.family.scale,
        reference_regret:regret(c,cell,c.family.reference)/c.family.scale,
        reference_gap:(regret(c,cell,c.family.reference)-cell.highs.value_scaled)/c.family.scale,
        near_count:near.vectors.length,exact_optimum_count:exact.length,
        exact_optima:exact,near_ranges:c.party_ids.map((id,i)=>({id,minimum:Math.min(...near.vectors.map(v=>v[i])),maximum:Math.max(...near.vectors.map(v=>v[i]))})),
        conditions:cell.focus_conditions.map(item=>({values:item.values,status:item.status,
          extra_regret:item.optimal?(item.value_scaled-cell.highs.value_scaled)/c.family.scale:null}))});
    }
  }
}
const history=audit.historical;
audit.averages={mean:mean(history.map(r=>r.mean_error)),l1:mean(history.map(r=>r.l1_error)),
  robust:report.config.budgets.map(b=>({budget:b,highs:mean(history.map(r=>r.cells.find(c=>c.budget===b).highs_error))})),
  cp_budget12:mean(history.map(r=>r.cells.find(c=>c.budget===12).cp_error))};
audit.provenance={run:40311428283,artifact:12645121746,artifact_zip_digest_from_api:'sha256:9f958c4cd1562b31f4ed4a70111bfc34c4ff3d871c7d4c448c2735a7c2338a2c',
  producer_head:'3d5d3190fc3616ed2049b07ac9ef74d5a63c2c4f',executed_commit:report.commit,
  checkpoint_sha256:hash(Buffer.from(raw)),postprocessor_sha256:hash(await fs.readFile(fileURLToPath(import.meta.url)))};
const adopted=await fs.readFile(path.join(root,'reports/forecast-decision-2026-10-25/forecast.json'));
audit.provenance.adopted_forecast_sha256=hash(adopted);
assert(hash(adopted)==='3a02e8c53ef2b85af839b6d048650c4a581ad64e6a24cae0bd9c316ab449ca97','Adopted forecast changed');
await fs.writeFile(path.join(out,'audit.json'),JSON.stringify(audit,null,2)+'\n');
for(const [source,dest]of [['summary.json','source-summary.json'],['inputs-manifest.json','source-inputs-manifest.json']])await fs.copyFile(path.join(input,source),path.join(out,dest));
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;');
function start(title,subtitle){return ['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="620" viewBox="0 0 1120 620"><rect width="1120" height="620" fill="white"/><g font-family="Arial,sans-serif" fill="#21384b">',`<text x="25" y="32" font-size="23">${esc(title)}</text>`,`<text x="25" y="62" font-size="14">${esc(subtitle)}</text>`];}
const p=start('E021: exact numerical optimization did not improve historical accuracy','Total absolute seat error; lower is better. Same six campaigns. Equal optima can give different forecasts.');
const labels=['2015','2019 Apr','2019 Sep','2020','2021','2022'];
for(let j=0;j<=5;j++){const y=430-j*62;p.push(`<path d="M70,${y}H1060" stroke="#dde4e8"/><text x="32" y="${y+4}" font-size="12">${j*8}</text>`);}
const series=[['Poll mean','#246e9b',r=>r.mean_error],['Robust budget6','#b47822',r=>r.cells.find(c=>c.budget===6).highs_error],['Robust budget12 HiGHS','#8a4284',r=>r.cells.find(c=>c.budget===12).highs_error],['Same optimum CP-SAT','#278267',r=>r.cells.find(c=>c.budget===12).cp_error]];
for(let j=0;j<series.length;j++){const [name,color,value]=series[j];let points=[];for(let i=0;i<history.length;i++){const x=100+i*180,y=430-value(history[i])*7.75;points.push(`${x},${y}`);p.push(`<circle cx="${x}" cy="${y}" r="${5-j*.5}" fill="${color}"><title>${name}: ${value(history[i])}</title></circle>`);}p.push(`<polyline points="${points.join(' ')}" fill="none" stroke="${color}" stroke-width="2"/>`,`<text x="${25+(j%2)*550}" y="${520+30*Math.floor(j/2)}" fill="${color}" font-size="15">${name}; mean ${mean(history.map(value)).toFixed(2)}</text>`);}
for(let i=0;i<labels.length;i++)p.push(`<text x="${75+i*180}" y="465" font-size="14">${labels[i]}</text>`);
p.push('<text x="25" y="600" font-size="13">2019–2021 outcomes are dependent; all campaigns previously inspected. No fresh holdout or adopted correction.</text></g></svg>');
await fs.writeFile(path.join(out,'historical-errors.svg'),p.join('\n')+'\n');
const current=report.cases.find(c=>!c.actual),cell=current.cells.find(c=>c.budget===12),base=cell.highs.value_scaled;
const q=start('E021: Reservists 4 remains close under the assumed objective','Budget12. Extra worst-model regret above optimum; these are not probabilities or actual-election error forecasts.');
const options=[['Res3 / Amcha0',[3,0]],['Res4 / Amcha0',[4,0]],['Res0 / Amcha0',[0,0]],['Res0 / Amcha3',[0,3]],['Res0 / Amcha4',[0,4]]];
for(let i=0;i<options.length;i++){const [label,values]=options[i],item=cell.focus_conditions.find(c=>JSON.stringify(c.values)===JSON.stringify(values));const gap=(item.value_scaled-base)/current.family.scale,x=90+i*205,height=gap*95;q.push(`<rect x="${x}" y="${430-height}" width="90" height="${Math.max(1,height)}" fill="${i===0?'#246e9b':'#8a4284'}"/><text x="${x+12}" y="${415-height}" font-size="16">${gap.toFixed(3)}</text><text x="${x-25}" y="465" font-size="13">${label}</text>`);}
q.push(`<text x="25" y="520" font-size="15">Adopted vector is also in the near-optimal set; its extra regret is ${audit.current.find(c=>c.budget===12).reference_gap.toFixed(3)}.</text>`,
 `<text x="25" y="555" font-size="14">${audit.current.find(c=>c.budget===12).near_count} vectors were fully enumerated within one regret unit. This is a model-defined band.</text>`,
 '<text x="25" y="600" font-size="13">Conditional bars fix the displayed pair exactly. They do not establish party crossing probabilities.</text></g></svg>');
await fs.writeFile(path.join(out,'threshold-regret.svg'),q.join('\n')+'\n');
console.log(JSON.stringify({status:'audit_passed',oracles:audit.certified_oracles,robust:audit.certified_robust_cells,cp_checks:audit.independent_checks.length,averages:audit.averages,current:audit.current.map(c=>({budget:c.budget,near:c.near_count,exact:c.exact_optimum_count,reference_gap:c.reference_gap})),out}));
return audit;
}
if(typeof process!=='undefined'&&process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))await analyze(process.argv[2],process.argv[3]);
