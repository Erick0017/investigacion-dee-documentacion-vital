// CSV authoring from exact source rows through bundled Artifact Tool.
// Two machine-readable CSVs requested; no XLSX variant or Native execution.
import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
import crypto from 'node:crypto';
const h=path.dirname(fileURLToPath(import.meta.url)),p=path.dirname(h);
const work='C:/Users/Erik/.codex/visualizations/2026/09/11/01a0921e-4727-7f93-8ad0-0b605c9afe96/pi09_maps_C2';
const bundled=createRequire(path.join(work,'artifact_context.cjs'));
const { Workbook }=await import(pathToFileURL(bundled.resolve('@oai/artifact-tool')).href);
const source=path.join(h,'DATOS_MATRICES_C2_PI09_R01.json');
const data=JSON.parse(await fs.readFile(source,'utf8'));
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const wb=Workbook.create(),works=[];
for(const table of data.tables){
  const rows=[table.headers,...table.rows];
  if(!rows.every(r=>r.length===table.headers.length))throw Error('Ragged source table');
  const sheet=wb.worksheets.add(table.name),range=sheet.getRangeByIndexes(0,0,rows.length,table.headers.length);
  range.values=rows;range.format.font={name:'Arial',size:11};range.format.wrapText=true;
  sheet.showGridLines=false;
  sheet.getRangeByIndexes(0,0,1,table.headers.length).format={fill:'#243746',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:30};
  sheet.getRangeByIndexes(1,0,rows.length-1,table.headers.length).format.rowHeight=56;
  sheet.getRangeByIndexes(0,0,rows.length,1).format.columnWidthPx=190;
  sheet.getRangeByIndexes(0,1,rows.length,1).format.columnWidthPx=230;
  sheet.getRangeByIndexes(0,2,rows.length,2).format.columnWidthPx=330;
  sheet.getRangeByIndexes(0,4,rows.length,1).format.columnWidthPx=220;
  works.push({table,rows,sheet,range});
}
wb.recalculate();
await fs.mkdir(path.join(p,'mapas'),{recursive:true});const proofs=[];
for(const {table,rows,sheet,range}of works){
  const actual=range.values;
  if(JSON.stringify(actual)!==JSON.stringify(rows))throw Error('Typed Artifact values differ from explicit source');
  const inspect=await wb.inspect({kind:'table',range:table.name+'!A1:E6',include:'values,formulas',tableMaxRows:6,tableMaxCols:5,maxChars:2200});
  await fs.writeFile(path.join(work,table.name+'_inspeccion.ndjson'),inspect.ndjson);
  const csv=actual.map(row=>row.map(v=>{const text=v===null?'':String(v);return /[",\r\n]/.test(text)?'"'+text.replaceAll('"','""')+'"':text;}).join(',')).join('\r\n')+'\r\n';
  const output=path.join(p,'mapas',table.filename);
  try{const old=await fs.readFile(output);const backup=path.join(p,'mapas','revisiones',table.filename+'.'+hash(old).slice(0,12));await fs.mkdir(path.dirname(backup),{recursive:true});try{await fs.writeFile(backup,old,{flag:'wx'});}catch(e){if(e.code!=='EEXIST')throw e;}}catch(e){if(e.code!=='ENOENT')throw e;}
  await fs.writeFile(output,'\uFEFF'+csv,'utf8');
  const saved=await fs.readFile(output);
  const preview=await wb.render({sheetName:table.name,range:'A1:E6',scale:1,format:'png'});
  await fs.writeFile(path.join(work,table.name+'_preview.png'),new Uint8Array(await preview.arrayBuffer()));
  proofs.push({path:output,sha256:hash(saved),bytes:saved.length,rows:rows.length-1,columns:table.headers.length});
}
const proof={schema:'DEE.PI09.C2.capability_and_gap_CSV.artifact_authorship.R01',recorded_utc:new Date().toISOString(),Native_executed:false,DEE_imported:false,SQLite_or_live_world_read:false,source_json:{path:source,sha256:hash(await fs.readFile(source))},outputs:proofs,typed_values_readback_exact:true,format:'CSV_UTF8_BOM',unexecuted_or_unclosed_cases_remain_missing:true,preview_scope:'First5columns/6rows only; CSV is unformatted data and this is no Word visual QA'};
const out=path.join(p,'control','MATRICES_C2_PI09_R01_AUTORIA.json');
await fs.writeFile(out,JSON.stringify(proof,null,2)+'\n','utf8');
console.log(JSON.stringify(proof));
