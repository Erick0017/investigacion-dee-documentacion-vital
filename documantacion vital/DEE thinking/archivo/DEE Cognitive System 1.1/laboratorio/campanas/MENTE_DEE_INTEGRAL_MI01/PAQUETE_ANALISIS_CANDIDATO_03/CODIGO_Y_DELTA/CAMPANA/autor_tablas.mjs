import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook } from '@oai/artifact-tool';
const here=path.dirname(fileURLToPath(import.meta.url));
const data=JSON.parse(await fs.readFile(path.join(here,'TABLAS_DATOS.json'),'utf8'));
const output=path.join(here,'EXPORTACION_ANALISIS');await fs.mkdir(output,{recursive:true});
const verifications=[];
for(const table of data.tables){
  const wb=Workbook.create();const ws=wb.worksheets.add('Datos');
  const matrix=[table.headers,...table.rows].map(r=>r.map(v=>String(v)));
  const range=ws.getRangeByIndexes(0,0,matrix.length,matrix[0].length);range.values=matrix;await wb.recalculate();
  const actual=range.values;if(JSON.stringify(actual)!==JSON.stringify(matrix))throw new Error('Cell mismatch '+table.filename);
  const view=await wb.inspect({select:'$.sheets[*]',include:['name','range']});
  const inspection=view.records;if(!inspection?.length)throw new Error('Semantic inspection missing '+table.filename);
  const csv='\ufeff'+actual.map(r=>r.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(',')).join('\r\n')+'\r\n';
  await fs.writeFile(path.join(output,table.filename),csv,'utf8');
  verifications.push({file:table.filename,rows:matrix.length-1,columns:matrix[0].length,all_cells_equal:true,inspection,encoding:'UTF8 BOM, quoted RFC4180 fields, CRLF',native_ticks:0});
}
await fs.writeFile(path.join(output,'VERIFICACION_TABLAS.json'),JSON.stringify(verifications,null,2),'utf8');
process.stdout.write(JSON.stringify(verifications.map(({file,rows,columns,all_cells_equal})=>({file,rows,columns,all_cells_equal})))+'\n');
