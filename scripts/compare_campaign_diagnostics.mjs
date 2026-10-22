/** Compare four predeclared data variants; fits are performed only by the Python runner. */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from './screening_diagnostics.mjs';

export function compare(folder) {
  const variants=['reference','publication_age','expanded_history','expanded_publication_age'];
  const summaries={};
  for(const variant of variants){
    const reportPath=path.join(folder,variant,'results/experiments.json');
    const report=JSON.parse(fs.readFileSync(reportPath,'utf8'));
    const d=build(reportPath,path.join(folder,variant,'diagnostics'));
    summaries[variant]={runtime_seconds:report.runtime_seconds,provenance:report.input_and_code_sha256,
      cases:d.cases.map(c=>({...c,methods:Object.fromEntries(Object.entries(c.methods).map(([name,m])=>[name,
        {...m,stages:m.stages?Object.fromEntries(Object.entries(m.stages).map(([stage,s])=>[stage,
          {error:s.error,delta_from_mean:s.delta_from_mean,distance_from_mean:s.distance_from_mean}])):null}]))}))};
  }
  const frozen=JSON.parse(fs.readFileSync(new URL('../reports/screening-six-elections-2026-10-21/experiments.json',import.meta.url),'utf8'));
  for(const c of summaries.reference.cases){
    const old=frozen.cases.find(x=>x.election_id===c.election_id);
    for(const [name,m] of Object.entries(c.methods))if(m.stages&&m.stages.integer.error!==old.methods[name].score.total_absolute_seat_error)throw Error('Reference reproduction mismatch');
  }
  const result={status:'E003_data_sensitivity_no_model_selected',reference_reproduced:true,
    variants:summaries,limitations:['Three added original-source releases, not blanket certification of the bulk index.',
      '2015 remains without repeated releases; source access failures are recorded in the audit.',
      'All comparisons reuse previously inspected election outcomes; descriptive sensitivity, not new blind evidence.',
      'Latest-group anchors, outcomes, model grid, correction fraction and cutoffs unchanged.']};
  fs.writeFileSync(path.join(folder,'comparison.json'),JSON.stringify(result,null,2)+'\n');
  const lines=['# E003 campaign-history sensitivities','',
    'Unchanged model grid and 25% correction. All latest-group anchors are preserved. Lower errors are better.',
    'Reference is a fresh fit of E002; its saved integer errors reproduce. No final method selected.','',
    '| Variant | Election | Method | Full projected error | 25% projected error | Integer error |',
    '| --- | --- | --- | ---: | ---: | ---: |'];
  for(const [variant,s] of Object.entries(summaries))for(const c of s.cases.filter(c=>c.role==='comparison'))for(const [name,m] of Object.entries(c.methods)){
    if(!m.stages)continue;lines.push(`| ${variant} | ${c.election_id} | ${name} | ${m.stages.projected?.error.toFixed(3)??'—'} | ${m.stages.shrunk_projected?.error.toFixed(3)??'—'} | ${m.stages.integer.error} |`);
  }
  lines.push('','Earlier history and full provenance are in comparison.json. Per-list predictions and source selection are in each variant artifact.','',...result.limitations.map(x=>'- '+x),'');
  fs.writeFileSync(path.join(folder,'summary.md'),lines.join('\n'));
  console.log('E003_COMPARISON_JSON='+JSON.stringify(result));
  return result;
}
if(typeof process!=='undefined'&&process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))compare(path.resolve(process.argv[2]??'output/campaign-history'));
