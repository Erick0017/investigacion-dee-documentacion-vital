import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook } from '@oai/artifact-tool';
const root=process.argv[2];
const input=JSON.parse(await fs.readFile(path.join(root,'laboratorio/campanas/CONSOLIDACION_1_1/TABLAS_PARA_EXPORTAR.json'),'utf8'));
if(process.argv.includes('--help-csv')){
  const wb=Workbook.create();console.log(wb.help('workbook.toCSV',{include:'index,examples,notes',maxChars:4500}).ndjson);process.exit(0);
}
for(const [name,rows]of Object.entries(input)){
  const wb=Workbook.create();const sheet=wb.worksheets.add('Datos');
  const keys=Object.keys(rows[0]);const matrix=[keys,...rows.map(r=>keys.map(k=>r[k]??''))];
  sheet.getRangeByIndexes(0,0,matrix.length,keys.length).values=matrix;
  wb.recalculate();
  const observed=sheet.getRangeByIndexes(0,0,matrix.length,keys.length).values;
  if(JSON.stringify(observed)!==JSON.stringify(matrix))throw Error('Matrix identity failed: '+name);
  console.log((await wb.inspect({kind:'table',range:'Datos!A1:D4',include:'values,formulas',tableMaxRows:4,tableMaxCols:4,maxChars:1800})).ndjson);
  // CSV serialization is deliberately plain and reversible. The table was
  // authored and verified with Artifact Tool; CSV carries no visual styles.
  const csv=matrix.map(row=>row.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(',')).join('\r\n')+'\r\n';
  const dest=path.join(root,'sistema/documentacion',name);await fs.writeFile(dest,'\ufeff'+csv,'utf8');
  console.log(JSON.stringify({file:dest,rows:rows.length,columns:keys.length,exactMatrixRoundTrip:true}));
}
