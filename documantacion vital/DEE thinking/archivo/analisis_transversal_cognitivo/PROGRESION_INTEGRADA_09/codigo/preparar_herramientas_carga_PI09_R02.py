"""New adoption chain and same-ID STATE recovery; no Native/product writes."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(t,a,b):
 if t.count(a)!=1:raise ValueError('Exact source anchor changed '+a[:100])
 return t.replace(a,b)
def save(p,text):
 if p.exists():raise FileExistsError('Existing revision preserved')
 ast.parse(text);p.write_text(text,'utf8')
def main():
 source=H/'incorporar_PI09_misma_identidad_R04.py';target=H/'incorporar_PI09_misma_identidad_R05.py';text=source.read_text('utf-8-sig');start=text.index(' # Original preparation/decision stay immutable.');end=text.index(' reasoned=',start)
 text=text[:start]+''' # Preserve both failed administrative revisions and the original prepare.
 supplement_file=CONTROL/'CARGA_PREPARADA_PI09_APLICADA_R02.json';supplement=read(supplement_file);prior_file=CONTROL/'CARGA_PREPARADA_PI09_APLICADA_R01.json';prior=read(prior_file)
 if supplement.get('schema')!='DEE.PI09.prepared_load.administrative_supplement.applied.R02'or supplement.get('applied')is not True or supplement.get('critical_state_before_after_equal')is not True or supplement.get('Native_executed')is not False or supplement['preparation']['sha256']!=sha(PREPARED)or supplement['decision']['sha256']!=sha(file)or supplement['prior_supplement']['sha256']!=sha(prior_file):raise ValueError('Exact R02 administrative recovery supplement required')
 if prior['preparation']['sha256']!=sha(PREPARED)or prior['decision']['sha256']!=sha(file)or prior.get('applied')is not True:raise ValueError('Original R01 supplement proof changed')
 first=read(H/'CARGA_PREPARADA_PI09_R01_PROPUESTA/PLAN.json');second=read(H/'CARGA_PREPARADA_PI09_R02_PROPUESTA/PLAN.json')
 if prior['files']!=first['files']or supplement['files']!=second['files']:raise ValueError('Administrative deployment differs from reviewed plans')
 effective={r['file']:r['sha256']for r in prepared['deployed_code']}
 for patch in [*prior['files'],*supplement['files']]:
  if effective.get(patch['file'])!=patch['before_sha256']:raise ValueError('Administrative amendment beforeimage chain differs')
  effective[patch['file']]=patch['sha256']
  if sha(Path(patch['source']))!=patch['sha256']:raise ValueError('Reviewed administrative source changed')
 for name,digest in effective.items():
  if sha(S/name)!=digest:raise ValueError('Deployed source changed outside the two exact supplements')
 if {r['file']for r in supplement['files']}!={'app/mundo_genesis_apd05.py','capacidades/pi09_permiso_operativo_R01.py','capacidades/pi09_carga_preparada_R02.py'}:raise ValueError('Only exact full-payload administrative gate allowed')
''' +text[end:];save(target,text);rows=[{'file':target.name,'source_sha256':sha(source),'sha256':sha(target)}]
 source=H/'ejecutar_administracion_con_tope_PI09_R04.py';target=H/'ejecutar_administracion_con_tope_PI09_R05.py';text=source.read_text('utf-8-sig').replace('incorporar_PI09_misma_identidad_R04.py','incorporar_PI09_misma_identidad_R05.py');save(target,text);rows.append({'file':target.name,'source_sha256':sha(source),'sha256':sha(target)})
 source=H/'reabrir_producto_PI09_0_R03.py';target=H/'reabrir_producto_PI09_0_R04.py';text=source.read_text('utf-8-sig').replace('PI09_PRODUCT0_SELECTED_R03','PI09_PRODUCT0_SELECTED_R04').replace('PI09_PRODUCT0_UNSELECTED_R03','PI09_PRODUCT0_UNSELECTED_R04')
 function='''def recover_existing_state(owner,tag):
 identifier='PI09_PRODUCT0_UNSELECTED_R03_PI09'
 row=owner.q.get(identifier)
 if not row or row['status']not in('queued','completed')or json.loads(row['payload'])!={'operacion':'sesion','situaciones':[{'modo':'eci01-pi09-estado'}],'actuador':'closed','retorno':'omit'}:raise ValueError('Sólo se continúa el STATE ya admitido con su ID exacto; no se reenvía ni purga')
 controls=[]
 if row['status']=='queued':
  controls.append(public_control(tag,'recuperar_reanudar','reanudar'));owner.wait(identifier)
 answer,proof=cli(tag,'recuperar_resultado',['mente-unificada-resultado','--vida',LIFE,'--id',identifier]);controls.append(proof);controls.append(public_control(tag,'recuperar_pausar','pausar'))
 current=answer.get('request',{})
 if current.get('id')!=identifier or current.get('status')!='completed':raise ValueError('El STATE existente no terminó; conservar sin reenvío')
 primary=P/'ensayos'/(tag+'_PI09_EXISTING_STATE.json')
 with primary.open('x',encoding='utf8')as f:json.dump(current,f,ensure_ascii=False,indent=2);f.write('\\n')
 return json.loads(current['result']),controls,primary
'''
 text=once(text,'def main(a):',function+'def main(a):')
 before="   identifier=tag+'_'+label;value,public_cli=public_state(owner,tag,label,{'modo':mode});primary=P/'ensayos'/(identifier+'.json')"
 after="   if label=='PI09'and not a.seleccionado:value,public_cli,primary=recover_existing_state(owner,tag)\n   else:\n    identifier=tag+'_'+label;value,public_cli=public_state(owner,tag,label,{'modo':mode});primary=P/'ensayos'/(identifier+'.json')"
 text=once(text,before,after);save(target,text);rows.append({'file':target.name,'source_sha256':sha(source),'sha256':sha(target)})
 proof={'schema':'DEE.PI09.prepared_load.same_ID_recovery_tools.R02','Native_executed':False,'original_failed_sources_and_IDs_preserved':True,'existing_queued_STATE_id':'PI09_PRODUCT0_UNSELECTED_R03_PI09','existing_STATE_never_re_admitted':True,'files':rows}
 (H/'HERRAMIENTAS_CARGA_PREPARADA_PI09_R02.json').write_text(json.dumps(proof,indent=2)+'\n','utf8');print(json.dumps(proof))
if __name__=='__main__':main()
