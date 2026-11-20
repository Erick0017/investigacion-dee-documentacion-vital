import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook} from '@oai/artifact-tool';
const lab=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(lab,'../../..');
const ev=path.join(root,'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02');
const input=JSON.parse(await fs.readFile(path.join(ev,'TABLAS_DATOS.json'),'utf8'));
const wb=Workbook.create();
for(let i=0;i<input.tables.length;i++){
  const t=input.tables[i];const sh=wb.worksheets.add('Datos_'+(i+1));
  const matrix=[t.columns,...t.rows];
  sh.getRangeByIndexes(0,0,matrix.length,t.columns.length).values=matrix;
}
wb.recalculate();
const records=[];
function cell(s){return '"'+String(s??'').replaceAll('"','""')+'"';}
for(let i=0;i<input.tables.length;i++){
  const t=input.tables[i],sh=wb.worksheets.getItemAt(i);
  const expected=[t.columns,...t.rows];
  const actual=sh.getRangeByIndexes(0,0,expected.length,t.columns.length).values;
  if(JSON.stringify(actual)!==JSON.stringify(expected))throw new Error('Exact text-cell readback mismatch: '+t.file);
  const text='\uFEFF'+actual.map(row=>row.map(cell).join(',')).join('\r\n')+'\r\n';
  const out=path.join(ev,'EXPORTACION',t.file);await fs.writeFile(out,text,'utf8');
  records.push({file:t.file,rows:t.rows.length,columns:t.columns.length,bytes:Buffer.byteLength(text),exactStringsVerified:true});
}
const inspection=await wb.inspect({kind:'sheet',include:'id,name',maxChars:1800});
await fs.writeFile(path.join(ev,'VERIFICACION_TABLAS.json'),JSON.stringify({method:'artifact-tool Workbook block authoring, one recalc, exact string readback, RFC4180 UTF8 BOM CSV',tables:records,inspection,native_ticks:0},null,2),'utf8');
console.log(JSON.stringify(records));
