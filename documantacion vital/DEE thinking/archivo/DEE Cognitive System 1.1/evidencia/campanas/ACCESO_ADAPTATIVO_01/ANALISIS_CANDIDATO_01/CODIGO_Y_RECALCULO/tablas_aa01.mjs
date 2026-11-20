import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook} from '@oai/artifact-tool';
const root=process.argv[2];
const input=JSON.parse(await fs.readFile(path.join(root,'CODIGO_Y_RECALCULO','TABLAS_DATOS.json'),'utf8'));
const specs=[
 ['trials','Ensayos','TABLA_TODOS_LOS_ENSAYOS.csv',['experimento','vida','alcance_ejecucion','tick_inicial','tick_final','evaluaciones_logicas','evaluaciones_con_firma','evaluaciones_sin_firma','correctas_con_contrato_verdad','incorrectas_con_contrato_verdad','sin_contrato_verdad_semantica','IDs_materiales_explicitos','aplicados','rechazados_en_aplicacion','pendientes','recibo_final_no_incluido','fallo_instrumental','codigo_proceso','primario_original','sha256_primario_original','consultas_logicas_solicitadas','solicitadas_con_firma','solicitadas_sin_firma']],
 ['capabilities','Funciones por vida','CAPACIDADES_POR_VIDA.csv',['vida','perfil','tick_puntero_actual','funcion_evaluada','contexto','tick_ultima_lectura','firmas_observadas','correcta_en_tarea','alcance_no_garantia_actual_ilimitada','experimento','localizador','snapshot_actual','sha256_snapshot_actual']],
 ['recovery','Retencion y acceso','RECUPERACION_RETENCION_REAPRENDIZAJE.csv',['experimento','vida','brazo','lectura','tick','codigos_observados','objetivo_si_hay_contrato','correcta_en_tarea','respondida_con_firma','codigos_conflictivos','localizador','primario_JSON_descomprimido','sha256_JSON_descomprimido']]
];
const workbook=Workbook.create();const checks=[];
function csvCell(v){if(v===null||v===undefined)return'';const t=String(v);return /[",\r\n]/.test(t)?'"'+t.replaceAll('"','""')+'"':t;}
for(const[key,title,file,headers]of specs){
 const values=[headers,...input[key].map(row=>row.map(v=>v??null))];
 if(values.some(row=>row.length!==headers.length))throw new Error('Column mismatch '+key);
 const sheet=workbook.worksheets.add(title);const range=sheet.getRangeByIndexes(0,0,values.length,headers.length);range.values=values;
 sheet.freezePanes.freezeRows(1);sheet.getRangeByIndexes(0,0,1,headers.length).format.font.bold=true;
 const actual=range.values;
 if(JSON.stringify(actual)!==JSON.stringify(values))throw new Error('Authoring changed source values '+key);
 await fs.writeFile(path.join(root,file),'\uFEFF'+actual.map(row=>row.map(csvCell).join(',')).join('\r\n')+'\r\n','utf8');
 checks.push({file,rows:values.length-1,columns:headers.length,exact_authoring_values:true,raw_uint64_not_in_numeric_cells:true});
}
workbook.recalculate();
const inspect=await workbook.inspect({kind:'sheet',include:'id,name',maxChars:2000});
await fs.writeFile(path.join(root,'CODIGO_Y_RECALCULO','VERIFICACION_TABLAS.json'),JSON.stringify({authoring:'Bundled @oai/artifact-tool; flat scientific tables, no workbook or extra outputs requested',checks,inspection:inspect},null,2)+'\n');
console.log(JSON.stringify(checks));
