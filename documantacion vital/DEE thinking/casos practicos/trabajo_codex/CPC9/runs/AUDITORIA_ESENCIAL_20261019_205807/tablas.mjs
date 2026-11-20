import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook } from '@oai/artifact-tool';
const [input,output,qa]=process.argv.slice(2);
if(!input||!output||!qa)throw new Error('Usage: tablas.mjs TABLE_VALUES.json PACKAGE QA_FOLDER');
const source=JSON.parse(await fs.readFile(input,'utf8'));await fs.mkdir(qa,{recursive:true});
const workbook=Workbook.create();const all=[];
const col=n=>{let s='';for(;n>0;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
for(const [name,t]of Object.entries(source.tables)){
  const sheetName=name.startsWith('MATRIZ')?'Capacidades':name.startsWith('ESTADO')?'NSM65':name.startsWith('TRAYECTORIA')?'E1':'Origenes';
  const sheet=workbook.worksheets.add(sheetName);const values=[t.headers,...t.rows];
  if(values.some(r=>r.length!==t.headers.length))throw new Error('Nonrectangular table');
  if(values.some(r=>r.some(v=>typeof v!=='string'||v.startsWith('='))))throw new Error('Nonliteral/unsafe CSV value; do not silently alter it');
  const range=sheet.getRange(`A1:${col(t.headers.length)}${values.length}`);range.values=values;
  range.format.font={name:'Arial',size:10};sheet.getRange(`A1:${col(t.headers.length)}1`).format.font={name:'Arial',size:10,bold:true};sheet.freezePanes.freezeRows(1);
  all.push({name,sheet,range,values,t});
}
workbook.recalculate();
const summaries=[];
for(const x of all){
  const values=x.range.values;
  if(JSON.stringify(values)!==JSON.stringify(x.values))throw new Error('Artifact table changed literal scientific values');
  const csv=values.map(r=>r.map(v=>'"'+v.replaceAll('"','""')+'"').join(',')).join('\r\n')+'\r\n';
  await fs.writeFile(path.join(output,x.name),csv,{encoding:'utf8',flag:'wx'});
  const inspected=await workbook.inspect({kind:'table',range:`${x.sheet.name}!A1:F6`,include:'values,formulas',tableMaxRows:6,tableMaxCols:6,maxChars:1800});
  const preview=x.sheet.getRange('A1:F8');preview.format.columnWidthPx=150;preview.format.wrapText=true;preview.format.rowHeight=50;
  const blob=await workbook.render({sheetName:x.sheet.name,range:'A1:F8',scale:1,format:'png'});await fs.writeFile(path.join(qa,x.sheet.name+'.png'),new Uint8Array(await blob.arrayBuffer()));
  summaries.push({file:x.name,rows:x.t.rows.length,columns:x.t.headers.length,all_values_exact:true,inspection:inspected.ndjson});
}
await fs.writeFile(path.join(qa,'VERIFICACION_TABLAS.json'),JSON.stringify({status:'PASS',format:'UTF8 CSV with quoted literals; no XLSX generated',tables:summaries},null,2)+'\n');
console.log(JSON.stringify({status:'PASS',tables:summaries.map(({inspection,...r})=>r)}));
