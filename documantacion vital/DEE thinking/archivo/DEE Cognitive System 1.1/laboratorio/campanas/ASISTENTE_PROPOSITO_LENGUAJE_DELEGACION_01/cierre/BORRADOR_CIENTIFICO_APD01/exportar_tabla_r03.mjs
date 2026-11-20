// Bundled artifact runtime; absolute dependency entry avoids a node_modules junction.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook} from 'file:///C:/Users/Erik/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const finalR04=process.argv.includes('--final-r04');
const fullProof=process.argv.includes('--full-proof');
const data=JSON.parse(await fs.readFile(path.join(here,'DATOS_TABLA_CAPACIDADES.json'),'utf8'));
const backup=path.join(here,'_VERSIONES_INSTRUMENTALES','PRE_R03','CAPACIDADES_POR_VIDA.csv');
await fs.access(backup);
const wb=Workbook.create();
const sheet=wb.worksheets.add('Capacidades');
const grid=[data.columns,...data.rows];
sheet.getRange('A1').write(grid);
wb.recalculate();
const actual=sheet.getRangeByIndexes(0,0,grid.length,data.columns.length).values;
if(JSON.stringify(actual)!==JSON.stringify(grid))throw new Error('Authored cells differ from factual source');
const quote=v=>v===null?'':`"${String(v).replaceAll('"','""')}"`;
const csv=actual.map(row=>row.map(quote).join(',')).join('\r\n')+'\r\n';
const imported=await Workbook.fromCSV(csv,{sheetName:'Reimportado'});
const roundtrip=imported.worksheets.getItemAt(0).getRangeByIndexes(0,0,grid.length,data.columns.length).values;
for(let r=0;r<grid.length;r++)for(let c=0;c<data.columns.length;c++){
  if(String(roundtrip[r][c]??'')!==String(grid[r][c]??''))throw new Error(`Roundtrip changed${r},${c}`);
}
await fs.writeFile(path.join(here,'CAPACIDADES_POR_VIDA.csv'),'\ufeff'+csv);
sheet.showGridLines=false;
sheet.getRange(`A1:G${grid.length}`).format.font={name:'Arial',size:10};
sheet.getRange(`A1:G${grid.length}`).format.wrapText=true;
sheet.getRange(`A1:G${grid.length}`).format.rowHeight=48;
sheet.getRange(`A1:A${grid.length}`).format.columnWidth=27;
sheet.getRange(`B1:C${grid.length}`).format.columnWidth=16;
sheet.getRange(`D1:E${grid.length}`).format.columnWidth=42;
sheet.getRange(`F1:G${grid.length}`).format.columnWidth=14;
sheet.getRange('A1:G1').format.fill='#273442';
sheet.getRange('A1:G1').format.font={name:'Arial',size:10,bold:true,color:'#FFFFFF'};
const image=await wb.render({sheetName:'Capacidades',range:`A${fullProof?103:finalR04?80:60}:G${grid.length}`,scale:1,format:'png'});
await fs.writeFile(path.join(here,fullProof?'QA_TABLA_FULL_COPIA.png':finalR04?'QA_TABLA_FINAL_R04.png':'QA_TABLA_R03.png'),new Uint8Array(await image.arrayBuffer()));
console.log(JSON.stringify({rows:data.rows.length,columns:data.columns.length,artifact_cells_exact:true,roundtrip:true,native_ticks:0,junction_created:false}));
