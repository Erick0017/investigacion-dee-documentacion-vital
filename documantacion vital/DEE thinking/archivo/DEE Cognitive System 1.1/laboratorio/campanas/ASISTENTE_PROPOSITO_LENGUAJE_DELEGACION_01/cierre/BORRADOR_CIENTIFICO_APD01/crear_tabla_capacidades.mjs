import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook} from '@oai/artifact-tool';
const here=path.dirname(fileURLToPath(import.meta.url));
const wb=Workbook.create();
if(process.argv.includes('--help-csv')){
  console.log(wb.help('csv',{search:'csv|CSV|Csv',include:'index,examples,notes',maxChars:4000}).ndjson);
}else{
  const data=JSON.parse(await fs.readFile(path.join(here,'DATOS_TABLA_CAPACIDADES.json'),'utf8'));
  const sheet=wb.worksheets.add('Capacidades');
  const grid=[data.columns,...data.rows];
  sheet.getRange('A1').write(grid);sheet.showGridLines=false;
  sheet.freezePanes.freezeRows(1);sheet.freezePanes.freezeColumns(1);
  sheet.getRange(`A1:G${grid.length}`).format.font={name:'Arial',size:10};
  sheet.getRange(`A1:G${grid.length}`).format.wrapText=true;
  sheet.getRange(`A1:G${grid.length}`).format.rowHeight=36;
  sheet.getRange(`A1:A${grid.length}`).format.columnWidth=36;
  sheet.getRange(`B1:C${grid.length}`).format.columnWidth=16;
  sheet.getRange(`D1:E${grid.length}`).format.columnWidth=42;
  sheet.getRange(`F1:G${grid.length}`).format.columnWidth=14;
  sheet.getRange('A1:G1').format.fill='#273442';
  sheet.getRange('A1:G1').format.font={name:'Arial',size:10,bold:true,color:'#FFFFFF'};
  wb.recalculate();
  const inspected=await wb.inspect({kind:'table',range:'Capacidades!A1:G8',include:'values,formulas',tableMaxRows:8,tableMaxCols:7,maxChars:3000});
  console.log(inspected.ndjson);
  const actual=sheet.getRangeByIndexes(0,0,grid.length,data.columns.length).values;
  if(JSON.stringify(actual)!==JSON.stringify(grid))throw new Error('Artifact authored values differ from source cells');
  sheet.freezePanes.unfreeze();
  const preview=await wb.render({sheetName:'Capacidades',range:`A1:G${grid.length}`,scale:1,format:'png'});
  await fs.writeFile(path.join(here,'QA_TABLA_COMPLETA.png'),new Uint8Array(await preview.arrayBuffer()),{flag:'wx'});
  if(process.argv.includes('--qa-only'))console.log(JSON.stringify({visual_qa_only:true,CSV_not_rewritten:true,native_ticks:0}));
  if(!process.argv.includes('--qa-only')){
  // Plain CSV is the requested machine-readable table, not an extra workbook.
  const quote=v=>v===null?'':`"${String(v).replaceAll('"','""')}"`;
  const csv=actual.map(row=>row.map(quote).join(',')).join('\r\n')+'\r\n';
  const target=path.join(here,'CAPACIDADES_POR_VIDA.csv');
  await fs.writeFile(target,'\ufeff'+csv,{flag:'wx'});
  const imported=await Workbook.fromCSV(csv,{sheetName:'Reimportado'});
  const reimport=imported.worksheets.getItemAt(0).getRangeByIndexes(0,0,grid.length,data.columns.length).values;
  for(let i=0;i<grid.length;i++)for(let j=0;j<data.columns.length;j++){
    if(String(reimport[i][j]??'')!==String(grid[i][j]??''))throw new Error(`CSV round-trip differs at${i},${j}`);
  }
  console.log(JSON.stringify({csv:target,rows:grid.length-1,columns:data.columns.length,roundtrip:true,native_ticks:0}));
  }
}
