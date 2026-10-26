/** Offline diagnostics of saved predictions; no model fitting or parameter selection.
 * Run: node scripts/screening_diagnostics.mjs --out-dir output/screening-diagnostics
 * Uses only Node built-ins. The forecasting pipelines remain Python-only.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { gzipSync } from 'node:zlib';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DEFAULT_REPORT = 'reports/screening-six-elections-2026-10-21/experiments.json';
const STAGES = ['raw', 'projected', 'shrunk_projected', 'integer'];
const LABELS = ['Full correction, unconstrained', 'Full correction, sum 120', '25% correction, sum 120', '25% correction, rounded'];
// Fixed representatives, not winners chosen from the evaluation scores.
const REPRESENTATIVES = ['recency_7', 'ridge_10', 'forest_3_5', 'xgb_2_50', 'dynamic_01', 'ensemble_1'];
const ELECTIONS = ['2015', 'Apr 2019', 'Sep 2019', '2020', '2021', '2022'];
const COLORS = ['#3067c5', '#8b51ad', '#b56a16', '#177c70'];
const read = p => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const close = (a, b) => Math.abs(a - b) < 1e-8;
const esc = x => String(x).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');

export function project(values, total = 120) {
  if (!values.length || values.some(v => !Number.isFinite(v)) || !Number.isInteger(total) || total <= 0) throw Error('Invalid simplex inputs');
  const sorted = [...values].sort((a, b) => b - a);
  let cumulative = 0, theta;
  sorted.forEach((v, i) => { cumulative += v; const t = (cumulative - total) / (i + 1); if (v > t) theta = t; });
  return values.map(v => Math.max(v - theta, 0));
}

export function integerSeats(values) {
  const p = project(values), result = p.map(Math.floor);
  const remaining = 120 - result.reduce((s, v) => s + v, 0);
  p.map((_, i) => i).sort((a, b) => (p[b] - result[b]) - (p[a] - result[a]) || a - b)
    .slice(0, remaining).forEach(i => result[i]++);
  return result;
}

export function absoluteError(values, actual) {
  if (values.length !== actual.length || values.some(v => !Number.isFinite(v))) throw Error('Invalid vector');
  return values.reduce((s, v, i) => s + Math.abs(v - actual[i]), 0);
}

export function diagnose(report, outcomes) {
  const families = Object.fromEntries(report.configuration.models.map(m => [m.id, m.family]));
  const cases = report.cases.map(c => {
    const target = outcomes.elections[c.election_id];
    if (!target || target.election_date !== c.election_date || c.ids.length !== Object.keys(target.seat_results).length || c.ids.some(k => !(k in target.seat_results))) throw Error('Outcome coverage mismatch');
    const actual = c.ids.map(k => target.seat_results[k]);
    if (actual.some(v => !Number.isInteger(v) || v < 0) || actual.reduce((s, v) => s + v, 0) !== 120) throw Error('Invalid outcome');
    const ref = c.ids.map(k => c.methods.rounded_mean_reference.seats[k]);
    const referenceErrors = {continuous: absoluteError(c.anchor, actual), integer: absoluteError(ref, actual)};
    const methods = Object.fromEntries(Object.entries(c.methods).map(([name, m]) => {
      if (!m.seats) return [name, {status: m.status, reason: m.reason, stages: null}];
      if (Object.keys(m.seats).length !== c.ids.length || c.ids.some(k => !(k in m.seats))) throw Error('Prediction coverage mismatch');
      const saved = c.ids.map(k => m.seats[k]);
      if (saved.some(v => !Number.isInteger(v) || v < 0) || saved.reduce((s, v) => s + v, 0) !== 120) throw Error('Invalid saved allocation');
      const loss = absoluteError(saved, actual);
      if (!close(loss, m.score.total_absolute_seat_error) || c.ids.some((id, i) => !close(saved[i] - actual[i], m.score.signed_error_by_list[id]))) throw Error(`Saved score mismatch: ${name}`);
      let vectors = {integer: saved};
      if (m.continuous_unshrunk) {
        const raw = m.continuous_unshrunk;
        const shrunk = c.anchor.map((v, i) => v + report.configuration.correction_fraction * (raw[i] - v));
        if (shrunk.some((v, i) => !close(v, m.continuous_shrunk[i]))) throw Error('Saved shrinkage mismatch');
        if (integerSeats(shrunk).some((v, i) => v !== saved[i])) throw Error('Saved rounding mismatch');
        vectors = {raw, projected: project(raw), shrunk_projected: project(shrunk), integer: saved};
      } else if (name === 'rounded_mean_reference') {
        vectors = {raw: c.anchor, projected: project(c.anchor), shrunk_projected: project(c.anchor), integer: saved};
      }
      const stages = Object.fromEntries(Object.entries(vectors).map(([stage, v]) => [stage, {
        error: absoluteError(v, actual),
        delta_from_mean: absoluteError(v, actual) - (stage === 'integer' ? referenceErrors.integer : referenceErrors.continuous),
        distance_from_mean: absoluteError(v, stage === 'integer' ? ref : c.anchor),
        by_list: Object.fromEntries(c.ids.map((id, i) => [id, {prediction: v[i], actual: actual[i], signed_error: v[i] - actual[i]}]))
      }]));
      return [name, {family: families[name] ?? 'reference', status: m.status, stages,
        identical_integer_to_mean: saved.every((v, i) => v === ref[i]),
        representation_false_positives: c.ids.filter((id, i) => saved[i] > 0 && actual[i] === 0),
        representation_false_negatives: c.ids.filter((id, i) => saved[i] === 0 && actual[i] > 0)}];
    }));
    return {election_id: c.election_id, election_date: c.election_date, horizon_days: c.horizon_days,
      role: c.evaluation_role, training_elections: c.training_elections,
      reference_errors: referenceErrors, selected_groups: c.selected_polls.length,
      eligible_releases: c.history_poll_ids.length,
      trend_missing_rows: Object.values(c.features_by_list).filter(f => f.trend_missing === 1).length,
      party_rows: c.ids.length, methods};
  });
  return {status: 'descriptive_saved_prediction_diagnostics_no_refitting',
    correction_fraction: report.configuration.correction_fraction, cases,
    limits: ['Continuous errors are diagnostic; final integer absolute seat error remains the competition metric.',
      'Earlier folds have fewer training elections. Compare methods only on shared available cases.',
      'Earlier OOF outcomes train later ensembles; these are not additional untouched ensemble tests.',
      'Already inspected outcomes; no parameter selection or new validation evidence claimed.',
      'No synthetic outcomes, newly audited polls, or current forecasts enter this report.']};
}

function svgStart(width, height, title, description) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img"><title>${esc(title)}</title><desc>${esc(description)}</desc><style>text{font-family:Arial,sans-serif;fill:#21324b;font-size:13px}.title{font-size:19px;font-weight:600}.small{font-size:12px}.grid{stroke:#e0e6ef;stroke-width:1}</style><rect width="100%" height="100%" fill="#fff"/>`;
}

export function trendPlot(diagnostics) {
  const width = 1080, height = 1150, panelWidth = 520, panelHeight = 330;
  let svg = svgStart(width, height, 'Where model differences disappear', 'Six fixed model configurations across six elections; error relative to the poll mean. Below zero is better. Missing fits are gaps. Equal spacing denotes elections, not elapsed time.');
  svg += '<text x="26" y="32" class="title">Error relative to poll mean, before and after rounding</text><text x="26" y="57">Below zero is better · fixed configurations · missing fits are gaps · T−1 throughout</text>';
  LABELS.forEach((label, i) => { svg += `<line x1="26" x2="46" y1="${84+i*18}" y2="${84+i*18}" stroke="${COLORS[i]}" stroke-width="2.5"/><text x="54" y="${88+i*18}" class="small">${esc(label)}</text>`; });
  REPRESENTATIVES.forEach((name, p) => {
    const ox = 15 + (p % 2) * 540, oy = 160 + Math.floor(p / 2) * panelHeight;
    const left = ox + 62, right = ox + panelWidth - 12, top = oy + 38, bottom = oy + 256;
    const all = diagnostics.cases.flatMap(c => STAGES.map(s => c.methods[name]?.stages?.[s]?.delta_from_mean).filter(v => v !== undefined));
    // Shared y scale across panels and all displayed stages.
    const every = diagnostics.cases.flatMap(c => REPRESENTATIVES.flatMap(n => STAGES.map(s => c.methods[n]?.stages?.[s]?.delta_from_mean).filter(v => v !== undefined)));
    const lo = Math.floor(Math.min(0, ...every) / 5) * 5 - 1, hi = Math.ceil(Math.max(0, ...every) / 5) * 5 + 1;
    const x = i => left + 8 + i * (right - left - 16) / 5, y = v => bottom - (v-lo) / (hi-lo) * (bottom-top);
    svg += `<text x="${ox+12}" y="${oy+20}" font-weight="600">${esc(name)}</text>`;
    for (let tick = Math.ceil(lo/5)*5; tick <= hi; tick += 5) svg += `<line class="grid" x1="${left}" x2="${right}" y1="${y(tick)}" y2="${y(tick)}"/><text x="${left-9}" y="${y(tick)+4}" text-anchor="end">${tick}</text>`;
    svg += `<line x1="${left}" x2="${right}" y1="${y(0)}" y2="${y(0)}" stroke="#6e7f95"/><text transform="translate(${ox+17},${(top+bottom)/2}) rotate(-90)" text-anchor="middle" class="small">Δ absolute seat error</text>`;
    ELECTIONS.forEach((label, i) => { svg += `<text x="${x(i)}" y="${bottom+23}" text-anchor="middle" class="small">${esc(label)}</text>`; });
    STAGES.forEach((stage, si) => {
      let points = [];
      const flush = () => { if(points.length) svg += `<polyline fill="none" stroke="${COLORS[si]}" stroke-width="2" ${si===3?'stroke-dasharray="5 3"':''} points="${points.join(' ')}"/>`; points=[]; };
      diagnostics.cases.forEach((c, i) => { const v = c.methods[name]?.stages?.[stage]?.delta_from_mean; if(v===undefined){flush();return;} points.push(`${x(i)},${y(v)}`); }); flush();
      diagnostics.cases.forEach((c, i) => { const v=c.methods[name]?.stages?.[stage]?.delta_from_mean;if(v!==undefined)svg+=`<circle cx="${x(i)}" cy="${y(v)}" r="${si===3?3.8:2.5}" fill="${COLORS[si]}"><title>${esc(name)} / ${ELECTIONS[i]} / ${LABELS[si]}: ${v.toFixed(3)}</title></circle>`; });
    });
    svg += `<text x="${left}" y="${bottom+47}" class="small">${all.length ? '2015–2020: training / OOF history · 2021–2022: comparison' : 'No eligible fits'}</text>`;
  });
  return svg+'</svg>\n';
}

export function stagePlot(d) {
  let svg=svgStart(1080,760,'All candidates before rounding','Projected continuous and final integer error for all 18 candidates in 2021 and 2022. Line segments group configurations by family; they are not time trends.');
  svg+='<text x="24" y="32" class="title">All configurations: continuous differences versus rounded ties</text>';
  const stages=['projected','shrunk_projected','integer'];
  stages.forEach((s,i)=>{svg+=`<line x1="24" x2="44" y1="${62+i*20}" y2="${62+i*20}" stroke="${COLORS[i+1]}" stroke-width="3"/><text x="52" y="${66+i*20}">${esc(LABELS[STAGES.indexOf(s)])}</text>`;});
  const cases=d.cases.filter(c=>c.role==='comparison');
  const names=Object.keys(cases[0].methods).filter(n=>cases[0].methods[n].family!=='reference');
  const max=Math.ceil(Math.max(...cases.flatMap(c=>names.flatMap(n=>stages.map(s=>c.methods[n].stages[s].error))),...cases.map(c=>c.reference_errors.continuous))/5)*5;
  cases.forEach((c,p)=>{
    const left=70, right=1000, top=145+p*300, bottom=top+165;
    const x=i=>left+10+i*(right-left-20)/(names.length-1),y=v=>bottom-v/max*(bottom-top);
    svg+=`<text x="24" y="${top-12}" font-weight="600">${c.election_id.includes('2021')?'2021':'2022'} · ${c.training_elections.length} earlier training elections</text>`;
    for(let t=0;t<=max;t+=5)svg+=`<line class="grid" x1="${left}" x2="${right}" y1="${y(t)}" y2="${y(t)}"/><text x="${left-10}" y="${y(t)+4}" text-anchor="end">${t}</text>`;
    svg+=`<text transform="translate(21,${(top+bottom)/2}) rotate(-90)" text-anchor="middle">Absolute seat error</text>`;
    for(const [v,dash] of [[c.reference_errors.continuous,'2 3'],[c.reference_errors.integer,'7 4']])svg+=`<line x1="${left}" x2="${right}" y1="${y(v)}" y2="${y(v)}" stroke="#68788e" stroke-dasharray="${dash}"/>`;
    names.forEach((name,i)=>{svg+=`<text transform="translate(${x(i)},${bottom+14}) rotate(50)" class="small">${esc(name)}</text>`;});
    stages.forEach((s,si)=>{
      // Split at family boundaries: no claim that adjacent configurations form a trajectory.
      let previousFamily=null,points=[];
      const flush=()=>{if(points.length)svg+=`<polyline points="${points.join(' ')}" fill="none" stroke="${COLORS[si+1]}" stroke-width="2"/>`;points=[];};
      names.forEach((n,i)=>{const family=c.methods[n].family;if(family!==previousFamily)flush();previousFamily=family;points.push(`${x(i)},${y(c.methods[n].stages[s].error)}`);});flush();
      names.forEach((n,i)=>{const v=c.methods[n].stages[s].error;svg+=`<circle cx="${x(i)}" cy="${y(v)}" r="3.2" fill="${COLORS[si+1]}"><title>${esc(n)} / ${s}: ${v.toFixed(3)}</title></circle>`;});
    });
  });
  return svg+'<text x="24" y="748" class="small">Gray guides: continuous mean (dotted), rounded mean (dashed). Candidate order is configuration order, not rank.</text></svg>\n';
}

export function build(reportPath=path.join(ROOT,DEFAULT_REPORT), outDir=path.join(ROOT,'output/screening-diagnostics')) {
  const report=read(reportPath),configPath=path.join(ROOT,report.configuration.historical_config);
  const config=read(configPath), outcomePath=path.join(ROOT,config.outcomes_path);
  const d=diagnose(report,read(outcomePath));
  d.provenance=Object.fromEntries([reportPath,configPath,outcomePath,fileURLToPath(import.meta.url)].map(p=>[path.relative(ROOT,p).replaceAll('\\','/'),hash(p)]));
  fs.mkdirSync(outDir,{recursive:true});
  const json=JSON.stringify(d,null,2)+'\n';
  fs.writeFileSync(path.join(outDir,'diagnostics.json'),json);
  fs.writeFileSync(path.join(outDir,'diagnostics.json.gz'),gzipSync(json,{level:9}));
  fs.writeFileSync(path.join(outDir,'history.svg'),trendPlot(d));
  fs.writeFileSync(path.join(outDir,'stages.svg'),stagePlot(d));
  const rows=['election,role,training_elections,method,status,stage,absolute_seat_error,delta_from_matching_mean'];
  for(const c of d.cases)for(const [name,m] of Object.entries(c.methods))for(const [s,v] of Object.entries(m.stages??{}))rows.push([c.election_id,c.role,c.training_elections.length,name,m.status,s,v.error,v.delta_from_mean].join(','));
  fs.writeFileSync(path.join(outDir,'scores.csv'),rows.join('\n')+'\n');
  const comparisons=d.cases.filter(c=>c.role==='comparison').map(c=>{
    const candidates=Object.values(c.methods).filter(m=>m.family!=='reference'&&m.stages);
    return `<li>${esc(c.election_id)}: ${candidates.filter(m=>m.identical_integer_to_mean).length}/${candidates.length} candidates reproduce the mean allocation.</li>`;
  }).join('');
  const html=`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Screening diagnostics</title><style>body{font:16px/1.6 system-ui,sans-serif;color:#21324b;max-width:1100px;margin:32px auto;padding:0 18px}img{width:100%;height:auto}h1{font-size:28px}h2{font-size:22px}a{color:#245ab0}li{margin:8px 0}.plot{overflow:auto}.plot img{min-width:850px}code{background:#eef2f7;padding:2px 5px}</style><h1>What the screening scores hide</h1><p>Saved E002 predictions only. No refitting, new polls, parameter selection or 2026 forecast change. Lower absolute seat error is better. Continuous scores diagnose the model; integer scores determine competition performance.</p><ul>${comparisons}</ul><h2>Performance across historical elections</h2><p>Each panel shows a fixed configuration. Zero means matching the mean's error; below zero improves it. Continuous stages compare with the continuous mean, integer stages with the rounded mean. Earlier folds have less training data. The learned ensemble starts only in 2021; earlier OOF outcomes fit its later weights.</p><div class="plot"><img src="history.svg" alt="Six model panels showing raw, projected, shrunken and integer error relative to the mean across eligible elections"></div><h2>All configurations on the two comparison elections</h2><p>The three stages show how different continuous predictions collapse into rounded ties. Connecting segments stay within model families and do not represent elapsed time.</p><div class="plot"><img src="stages.svg" alt="All 18 candidate configurations before and after rounding in 2021 and 2022"></div><h2>Interpretation and limits</h2><ul>${d.limits.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><p>All saved final scores were checked directly against the outcome snapshot. Saved shrinkage and rounded allocations were independently reproduced. Raw unconstrained predictions can violate seat totals; projected stages are the coherent continuous comparisons.</p><p><a href="scores.csv">All stage scores</a> · <a href="diagnostics.json">Per-list diagnostics and provenance</a></p></html>\n`;
  fs.writeFileSync(path.join(outDir,'index.html'),html.replace('href="diagnostics.json"','href="diagnostics.json.gz"'));
  return d;
}

if(typeof process !== 'undefined' && process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const args=process.argv.slice(2);let reportPath=path.join(ROOT,DEFAULT_REPORT),outDir=path.join(ROOT,'output/screening-diagnostics');
  while(args.length){const flag=args.shift(),value=args.shift();if(!value||!['--report','--out-dir'].includes(flag))throw Error('Use --report PATH or --out-dir PATH');if(flag==='--report')reportPath=path.resolve(value);else outDir=path.resolve(value);}
  const result=build(reportPath,outDir);console.log(`Checked ${result.cases.length} historical cases; wrote plots, CSV and per-list diagnostics to ${outDir}. No models refitted.`);
}
