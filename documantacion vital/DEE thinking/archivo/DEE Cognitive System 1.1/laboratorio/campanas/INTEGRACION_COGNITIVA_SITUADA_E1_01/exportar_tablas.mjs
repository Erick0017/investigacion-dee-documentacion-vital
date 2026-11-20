import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook} from '@oai/artifact-tool';
const spec=JSON.parse(await fs.readFile(new URL('./TABLAS_INTERMEDIAS.json',import.meta.url),'utf8'));
await fs.mkdir(spec.out,{recursive:true});
const checks=[];
const field=v=>{const s=v===null||v===undefined?'':String(v);return /[",\r\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;};
for(const t of spec.tables){
  const wb=Workbook.create();const sh=wb.worksheets.add('Datos');
  const values=[t.headers,...t.rows].map(r=>r.map(v=>v===undefined?null:v));
  const rg=sh.getRangeByIndexes(0,0,values.length,t.headers.length);rg.values=values;
  await wb.recalculate();const restored=rg.values;
  if(JSON.stringify(restored)!==JSON.stringify(values))throw new Error('Artifact table changed a primary-derived field: '+t.name);
  const inspected=await wb.inspect({kind:'region',sheetId:'Datos',range:'A1:D3',maxChars:1100});
  await fs.writeFile(path.join(spec.out,t.name),'\ufeff'+restored.map(r=>r.map(field).join(',')).join('\r\n')+'\r\n','utf8');
  checks.push({file:t.name,dataRows:values.length-1,columns:t.headers.length,exact_cell_roundtrip:true,inspection:inspected.ndjson});
}
await fs.writeFile(new URL('./VERIFICACION_TABLAS_ARTIFACT.json',import.meta.url),JSON.stringify({author:'@oai/artifact-tool',format:'csv',uint64:'Exact strings, never JS Number conversion',checks},null,2)+'\n');
console.log(JSON.stringify(checks.map(({inspection,...c})=>c)));
