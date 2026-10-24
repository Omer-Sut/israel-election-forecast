// E009: descriptive source-coverage sensitivity; no fitting or forecast selection.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
export const firm=p=>p.pollster_group==='midgam_rc'?'midgam':p.pollster_group;
const sum=a=>a.reduce((s,x)=>s+x,0);
const loss=(a,b)=>sum(a.map((v,i)=>Math.abs(v-b[i])));
const clean=x=>Number(x.toFixed(10));
const assert=(condition,message)=>{if(!condition)throw Error(message);};

export function validate(p,ids){
  assert(p.seat_projection_complete!==false,'Incomplete allocation');
  assert(Object.keys(p.reported_seats).every(id=>ids.includes(id)),'Unknown historical list');
  const v=ids.map(id=>p.reported_seats[id]??0);
  assert(v.every(x=>Number.isInteger(x)&&x>=0)&&sum(v)===120,'Invalid seat allocation');
  return v;
}
export function latest(polls,cutoff){
  const groups=new Map();
  for(const p of polls){
    const available=[p.published_on,p.available_on,p.source_updated_on].filter(Boolean).sort().at(-1);
    if(available>cutoff)continue;
    const age=(Date.parse(cutoff)-Date.parse(p.fieldwork_end??p.published_on))/86400000;
    assert(Number.isFinite(age),'Invalid date');
    if(age<0||age>14)continue;
    const key=firm(p),old=groups.get(key);
    if(!old||p.published_on>old.published_on)groups.set(key,p);
    else if(p.published_on===old.published_on&&p.id!==old.id)throw Error('Ambiguous same-firm same-day releases');
  }
  return [...groups.values()].sort((a,b)=>firm(a).localeCompare(firm(b),'en'));
}
export function roundedMean(vectors){
  assert(vectors.length>0,'No polls');
  const n=vectors.length,sums=vectors[0].map((_,i)=>sum(vectors.map(v=>v[i])));
  const result=sums.map(s=>Math.floor(s/n));
  const order=sums.map((_,i)=>i).sort((i,j)=>(sums[j]%n)-(sums[i]%n)||i-j);
  for(const i of order.slice(0,120-sum(result)))result[i]++;
  return result;
}
export function evaluate(polls,ids,truth){
  assert(polls.length>0,'Empty panel');
  assert(new Set(polls.map(firm)).size===polls.length,'Duplicate firm');
  const vectors=polls.map(p=>validate(p,ids));
  const mean=ids.map((_,i)=>sum(vectors.map(v=>v[i]))/vectors.length);
  const rounded=roundedMean(vectors),errors=vectors.map(v=>loss(v,truth));
  const avg=sum(errors)/errors.length;
  return {n:polls.length,firms:polls.map(firm),poll_ids:polls.map(p=>p.id),
    mean:mean.map(clean),rounded,continuous_error:clean(loss(mean,truth)),integer_error:loss(rounded,truth),
    per_poll_errors:errors,mean_poll_error:clean(avg),population_variance_poll_error:clean(sum(errors.map(e=>(e-avg)**2))/errors.length),
    cancellation:clean(avg-loss(mean,truth)),
    parties:ids.map((id,i)=>({id,actual:truth[i],mean:clean(mean[i]),rounded:rounded[i],
      continuous_signed_error:clean(mean[i]-truth[i]),integer_signed_error:rounded[i]-truth[i],
      min_poll:Math.min(...vectors.map(v=>v[i])),max_poll:Math.max(...vectors.map(v=>v[i])),
      above:vectors.filter(v=>v[i]>truth[i]).length,below:vectors.filter(v=>v[i]<truth[i]).length,equal:vectors.filter(v=>v[i]===truth[i]).length}))};
}

export async function run(out=path.join(ROOT,'output/final-poll-coverage')){
  const auditPath='data/snapshots/final-poll-coverage-2026-10-24/audit.json';
  const inputPaths=[auditPath,'data/snapshots/historical-2026-10-21/outcomes.json',...['2021','2022'].map(y=>`data/snapshots/historical-2026-10-21/polls-${y}.json`),
    'reports/poll-metadata-trial-2026-10-23/results.json'];
  const inputs={};for(const p of inputPaths)inputs[p]=JSON.parse((await fs.readFile(path.join(ROOT,p),'utf8')).replace(/^\uFEFF/,''));
  const audit=inputs[auditPath],outcomes=inputs[inputPaths[1]].elections,oldScores=inputs[inputPaths[4]].scores;
  const data={experiment:'E009',status:'retrospective_diagnostic_no_model_selection',source_policy:audit.vintage_limit,elections:[]};
  const panels=[];
  for(const year of [2021,2022]){
    const s=inputs[`data/snapshots/historical-2026-10-21/polls-${year}.json`];
    const ids=s.lists.map(l=>l.id).sort(),truth=ids.map(id=>outcomes[s.election_id].seat_results[id]);
    assert(truth.every(Number.isInteger)&&sum(truth)===120,'Invalid outcomes');
    const cutoff=new Date(Date.parse(s.election_date)-86400000).toISOString().slice(0,10);
    const base=latest(s.polls,cutoff).map(p=>({...p,source_tier:'original_publisher'}));
    const extra=audit.additions.filter(p=>p.election_id===s.election_id);
    for(const p of extra)validate(p,ids);
    const expanded=latest([...base,...extra],cutoff);
    const original=expanded.filter(p=>p.source_tier==='original_publisher');
    panels.push({year,s,ids,truth,cutoff,base,expanded,original});
  }
  const common=(key)=>panels[0][key].map(firm).filter(f=>panels[1][key].some(p=>firm(p)===f));
  for(const p of panels){
    const variants={original_three:p.base,original_publisher_only:p.original,
      original_plus_republication:p.expanded.filter(x=>x.source_tier!=='contemporaneous_secondary'),
      expanded_reported:p.expanded,matched_original_publishers:p.original.filter(x=>common('original').includes(firm(x))),
      matched_reported:p.expanded.filter(x=>common('expanded').includes(firm(x))),
      matched_without_direct:p.expanded.filter(x=>common('expanded').includes(firm(x))&&firm(x)!=='direct_polls')};
    const results=Object.fromEntries(Object.entries(variants).map(([name,polls])=>[name,evaluate(polls,p.ids,p.truth)]));
    const prior=oldScores.find(s=>s.election===p.s.election_id&&s.fraction===0);
    assert(JSON.stringify(prior.party_ids)===JSON.stringify(p.ids),'Historical field order changed');
    assert(JSON.stringify(prior.integer_prediction)===JSON.stringify(results.original_three.rounded),'Frozen reference differs');
    assert(Math.abs(prior.continuous_error-results.original_three.continuous_error)<1e-8,'Continuous reference differs');
    data.elections.push({year:p.year,election_id:p.s.election_id,cutoff:p.cutoff,labels:p.s.lists,results,
      sources:p.expanded.map(x=>({id:x.id,firm:firm(x),tier:x.source_tier,url:x.source_url,published_on:x.published_on,sample_size:x.sample_size,
        lead_days:(Date.parse(p.s.election_date)-Date.parse(x.published_on))/86400000})),
      leave_one_firm_out:p.expanded.map(x=>({omitted:firm(x),...evaluate(p.expanded.filter(y=>y!==x),p.ids,p.truth)}))});
  }
  data.gaps=Object.keys(data.elections[0].results).map(name=>({variant:name,
    continuous:clean(data.elections[0].results[name].continuous_error-data.elections[1].results[name].continuous_error),
    integer:data.elections[0].results[name].integer_error-data.elections[1].results[name].integer_error}));
  await fs.mkdir(out,{recursive:true});
  await fs.writeFile(path.join(out,'results.json'),JSON.stringify(data,null,2)+'\n');
  const summary=['# Final-poll coverage sensitivity (E009)','',
    'Source-tiered retrospective comparison; outcomes already inspected. No model fitting, forecast selection or promotion of secondary records into training. Lower total absolute seat error is better.','',
    '| Panel | Firms 2021 / 2022 | Continuous error 2021 / 2022 | Integer error 2021 / 2022 |',
    '| --- | --- | --- | --- |'];
  for(const name of Object.keys(data.elections[0].results)){
    const [a,b]=data.elections.map(e=>e.results[name]);
    summary.push(`| ${name} | ${a.n} / ${b.n} | ${a.continuous_error.toFixed(3)} / ${b.continuous_error.toFixed(3)} | ${a.integer_error} / ${b.integer_error} |`);
  }
  summary.push('','Population variance describes the small set of final-poll errors, not calibrated uncertainty. Equal polling-firm weights; latest eligible publication per firm. Common firms do not guarantee unchanged methodology.','',
    'Smith remains excluded: incomplete retrieved primary2021 allocation, final2022 publisher source unverified. Direct2021 may include trend adjustment; matched_without_direct removes Direct in both years. No proof that remaining errors are caused by late movement rather than polling bias.','',
    '![Coverage and party errors](comparison.svg)','');
  await fs.writeFile(path.join(out,'summary.md'),summary.join('\n'));
  await fs.writeFile(path.join(out,'comparison.svg'),chart(data));
  const hashes={};for(const p of [...inputPaths,'scripts/final_poll_coverage.mjs'])hashes[p]=createHash('sha256').update(await fs.readFile(path.join(ROOT,p))).digest('hex');
  await fs.writeFile(path.join(out,'inputs-manifest.json'),JSON.stringify({experiment:'E009',hashes},null,2)+'\n');
  return data;
}
export function chart(data){
  const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;');
  const parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="1000" viewBox="0 0 1100 1000">',
    '<rect width="1100" height="1000" fill="white"/><g font-family="Arial,sans-serif" fill="#17324d">',
    '<text x="25" y="35" font-size="23">Does broader final-poll coverage explain the 2021 error?</text>',
    '<text x="25" y="62" font-size="15">Continuous total absolute seat error; lower is better. Secondary-source sensitivity is explicit.</text>'];
  const variants=[['original_three','Original 3 firms'],['expanded_reported','Expanded reported (6 firms)'],['matched_original_publishers','Matched original sources (3)'],['matched_without_direct','Matched without Direct (5)']];
  for(let i=0;i<variants.length;i++){
    const [key,label]=variants[i],y=112+i*65;
    parts.push(`<text x="25" y="${y+12}" font-size="15">${label}</text>`);
    for(let j=0;j<2;j++){const v=data.elections[j].results[key].continuous_error;
      parts.push(`<rect x="305" y="${y+j*23}" width="${v*25}" height="19" fill="${j?'#cf7b22':'#246aa5'}"/><text x="${312+v*25}" y="${y+j*23+15}" font-size="14">${data.elections[j].year}: ${v.toFixed(2)}</text>`);}
  }
  parts.push('<text x="25" y="405" font-size="19">Expanded panel: signed party error before rounding</text>',
    '<text x="25" y="430" font-size="14">Left = underestimated; right = overestimated. Each panel includes all modeled lists.</text>');
  for(let j=0;j<2;j++){
    const e=data.elections[j],left=j*550,zero=left+330;
    parts.push(`<text x="${left+25}" y="465" font-size="18">${e.year} — six firms, mixed source tiers</text>`);
    const rows=[...e.results.expanded_reported.parties].sort((a,b)=>Math.abs(b.continuous_signed_error)-Math.abs(a.continuous_signed_error));
    for(let i=0;i<rows.length;i++){
      const r=rows[i],v=r.continuous_signed_error,y=495+i*27,label=e.labels.find(l=>l.id===r.id).label_en.replace('Religious Zionism / Otzma / Noam','Religious Zionism alliance').replace('Joint List (Hadash, Taal, Balad)','Joint List');
      parts.push(`<text x="${left+25}" y="${y+14}" font-size="12">${esc(label)}</text><rect x="${zero+Math.min(0,v)*25}" y="${y}" width="${Math.abs(v)*25}" height="18" fill="${v<0?'#246aa5':'#cf7b22'}"/><text x="${zero+Math.max(0,v)*25+5}" y="${y+14}" font-size="12">${v.toFixed(2)}</text>`);
    }
    parts.push(`<path d="M${zero},485V940" stroke="#546878"/>`);
  }
  parts.push('<text x="25" y="978" font-size="13">Two previously inspected elections; this is a coverage diagnostic, not causal identification or a model ranking.</text></g></svg>');
  return parts.join('\n')+'\n';
}
if(typeof process!=='undefined'&&process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const data=await run(process.argv[2]?path.resolve(process.argv[2]):undefined);
  console.log(JSON.stringify(data.gaps,null,2));
}
