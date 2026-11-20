import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
const runtimeRoot='C:/Users/Erik/.cache/codex-runtimes/codex-primary-runtime/dependencies/node';
const require=createRequire(path.join(runtimeRoot,'authoring-entry.cjs'));
const {Workbook}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const here=path.dirname(fileURLToPath(import.meta.url));
const data=JSON.parse(await fs.readFile(path.join(here,'TABLAS_DATOS_MI02.json'),'utf8'));
const output=path.join(here,'PAQUETE_ANALISIS_CANDIDATO_02');
const verifications=[];
for(const table of data.tables){
  const wb=Workbook.create();const ws=wb.worksheets.add('Datos');
  const matrix=[table.headers,...table.rows].map(r=>r.map(v=>v===null||v===undefined?'':v));
  const range=ws.getRangeByIndexes(0,0,matrix.length,matrix[0].length);range.values=matrix;
  await wb.recalculate();const actual=range.values;
  if(JSON.stringify(actual)!==JSON.stringify(matrix))throw new Error('Typed cell mismatch '+table.filename);
  const inspection=await wb.inspect({select:'$.sheets[*]',include:['name','range']});
  if(!inspection.records?.length)throw new Error('Semantic inspection missing '+table.filename);
  const csv='\ufeff'+actual.map(r=>r.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(',')).join('\r\n')+'\r\n';
  await fs.writeFile(path.join(output,table.filename),csv,'utf8');
  verifications.push({file:table.filename,rows:matrix.length-1,columns:matrix[0].length,typed_values_equal:true,inspection:inspection.records,encoding:'UTF8 BOM, quoted RFC4180, CRLF',formula_columns:0,native_ticks:0});
  if(table.filename==='CAPACIDADES_POR_VIDA.csv'){
    const view=ws.getRange('A1:E7');view.format.columnWidthPx=180;view.format.rowHeightPx=90;view.format.wrapText=true;ws.getRange('D1:E7').format.columnWidthPx=80;ws.getRange('A1:E1').format.rowHeightPx=46;
    try{
      const preview=await wb.render({sheetName:'Datos',range:'A1:E7',scale:1.5,format:'png'});
      await fs.writeFile(path.join(here,'VISTA_QA_TABLA_MI02.png'),new Uint8Array(await preview.arrayBuffer()));
    }catch(error){await fs.writeFile(path.join(here,'VISTA_QA_TABLA_MI02_ERROR.txt'),String(error),'utf8');}
  }
}
await fs.writeFile(path.join(output,'VERIFICACION_TABLAS.json'),JSON.stringify(verifications,null,2),'utf8');
console.log(JSON.stringify(verifications.map(({file,rows,columns,typed_values_equal})=>({file,rows,columns,typed_values_equal}))));
