import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook } from '@oai/artifact-tool';

const [input,outDir]=process.argv.slice(2);
const values=JSON.parse(await fs.readFile(input,'utf8'));
const workbook=Workbook.create();
const checks=[];
for (const [filename,matrix] of Object.entries(values)) {
  const sheet=workbook.worksheets.add(filename.startsWith('MAPA')?'Información y acceso':'Vidas y cortes');
  const range=sheet.getRangeByIndexes(0,0,matrix.length,matrix[0].length);
  range.values=matrix;
  workbook.recalculate();
  const roundtrip=range.values;
  if (JSON.stringify(roundtrip)!==JSON.stringify(matrix)) throw new Error('Table value roundtrip changed: '+filename);
  // Requested deliverables are flat CSV. No presentation formatting or hidden
  // worksheets are needed; all interpretation flags and source hashes are data.
  const quote=v=>{const s=v==null?'':String(v);return /[",\r\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;};
  await fs.writeFile(path.join(outDir,filename),'\uFEFF'+roundtrip.map(row=>row.map(quote).join(',')).join('\r\n')+'\r\n','utf8');
  const inspected=await workbook.inspect({kind:'region',sheetId:sheet.name,range:'A1:G3',maxChars:3000});
  checks.push({filename,rows:matrix.length-1,columns:matrix[0].length,exactValueRoundtrip:true,inspection:inspected.ndjson??inspected});
}
await fs.writeFile(path.join(outDir,'VERIFICACION_TABLAS.json'),JSON.stringify({authoring:'artifact-tool',format:'CSV UTF-8 BOM RFC4180',checks},null,2)+'\n','utf8');
console.log(JSON.stringify(checks.map(({filename,rows,columns})=>({filename,rows,columns}))));
