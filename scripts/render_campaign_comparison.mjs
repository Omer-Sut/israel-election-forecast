/** Rebuild durable E003 plots/CSV from the compact hosted comparison, no fitting. */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { gzipSync, gunzipSync } from 'node:zlib';
import { trendPlot, stagePlot } from './screening_diagnostics.mjs';

export function render(folder) {
  const raw=path.join(folder,'comparison.json'), archive=raw+'.gz';
  const text=fs.existsSync(raw)?fs.readFileSync(raw,'utf8'):gunzipSync(fs.readFileSync(archive)).toString('utf8');
  const d=JSON.parse(text);
  if(!d.reference_reproduced||d.execution.cloud_tests!==46)throw Error('Expected verified E003 execution');
  fs.writeFileSync(archive,gzipSync(text,{level:9}));
  const rows=['variant,election,role,training_elections,method,stage,absolute_seat_error,delta_from_matching_mean'];
  const md=['# E003: data changes with fixed models','',
    'All 46 hosted tests and eight variant runs (including repeats) passed. Original reference scores reproduced. No model selected.',
    '', '| Variant | Election | Method | Full projected | 25% projected | Integer |',
    '| --- | --- | --- | ---: | ---: | ---: |'];
  for(const [variant,v] of Object.entries(d.variants)){
    fs.writeFileSync(path.join(folder,variant+'-history.svg'),trendPlot(v));
    fs.writeFileSync(path.join(folder,variant+'-stages.svg'),stagePlot(v));
    for(const c of v.cases)for(const [name,m] of Object.entries(c.methods)){
      for(const [stage,s] of Object.entries(m.stages??{}))rows.push([variant,c.election_id,c.role,c.training_elections.length,name,stage,s.error,s.delta_from_mean].join(','));
      if(c.role==='comparison'&&m.stages)md.push(`| ${variant} | ${c.election_id} | ${name} | ${m.stages.projected?.error.toFixed(3)??'—'} | ${m.stages.shrunk_projected?.error.toFixed(3)??'—'} | ${m.stages.integer.error} |`);
    }
  }
  md.push('',...d.limitations.map(x=>'- '+x),'',
    'Source: verified hosted run39741972606, implementation31b58712593b3db492b20e27ef3fb1728baaf858. All variant prediction CSVs repeat identically.',
    'Compact score/representation/provenance data: comparison.json.gz. Full inputs/predictions are rebuildable from the committed audit/code and downloadable from the run artifact.','');
  fs.writeFileSync(path.join(folder,'scores.csv'),rows.join('\n')+'\n');
  fs.writeFileSync(path.join(folder,'summary.md'),md.join('\n'));
  const html=`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Campaign-history comparison</title><style>body{font:16px/1.6 system-ui,sans-serif;max-width:1100px;margin:30px auto;padding:0 18px;color:#21324b}img{max-width:100%;height:auto}h1{font-size:28px}h2{font-size:22px}a{color:#245ab0}</style><h1>Does richer campaign history help?</h1><p>Three verified earlier releases; identical latest-group anchors, model settings, outcomes and forecast cutoffs. All four variants passed hosted tests and deterministic reruns. No final model selected.</p><p>The new history activates trends in three earlier campaigns. Results change, but no candidate beats the final 20/12 reference errors on 2021/2022. The combined data changes bring two ensemble configurations to a 2021 tie; some forests worsen.</p><h2>Expanded history versus the original history</h2><p>Each panel shows a fixed configuration across eligible elections. Below zero improves the corresponding poll mean. Earlier folds have fewer training elections; missing fits remain gaps. These are inspected historical outcomes, not new blind tests.</p><h3>Original reference history</h3><img src="reference-history.svg" alt="Original E002 historical performance, four processing stages"><h3>Three added repeated releases</h3><img src="expanded_history-history.svg" alt="Expanded history performance, four processing stages"><h3>Added history plus publication-age assumption</h3><img src="expanded_publication_age-history.svg" alt="Combined sensitivity historical performance, four stages"><p><a href="publication_age-history.svg">Publication-age only</a> · <a href="scores.csv">All stage scores</a> · <a href="summary.md">Full comparison table</a> · <a href="comparison.json.gz">Compact provenance and diagnostics</a></p><p><a href="https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39741972606">Verified hosted execution and full downloadable artifact</a>. The artifact expires after30days; committed audit/code and compact results support reproduction.</p></html>\n`;
  fs.writeFileSync(path.join(folder,'index.html'),html);
  return {variants:Object.keys(d.variants).length,archiveBytes:fs.statSync(archive).size};
}
if(typeof process!=='undefined'&&process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))console.log(render(path.resolve(process.argv[2]??'reports/campaign-history-2026-10-22')));
