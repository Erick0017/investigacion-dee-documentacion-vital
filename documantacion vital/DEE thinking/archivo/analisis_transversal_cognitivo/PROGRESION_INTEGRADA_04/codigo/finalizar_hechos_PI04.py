"""Close PI04 document facts only from actual committed/closed evidence.

Default is read-only validation. --apply creates ONE new final facts JSON.
No DEE import, Native, authoring, rendering, publication or selection writes.
ACTIVO identifies the selected life/adoption reference; VIDA is its current cut.
"""
from pathlib import Path
import argparse,copy,datetime,hashlib,json,re
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=R/'DEE Cognitive 2.0';S=C/'sistema'
MARK='[[CIERRE_REAL_PENDIENTE]]'
def need(ok,message):
 if not ok:raise ValueError(message)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def info(p):
 p=Path(p).resolve(strict=True);b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def physical_equal(a,b):return all(a[k]==b[k]for k in('N','tick','RAW_sha256','clocks_sha256'))
def primary(path):
 value=read(path)
 if value.get('status')=='completed'and'result'in value:
  value=json.loads(value['result'])if isinstance(value['result'],str)else value['result']
 need(isinstance(value,dict)and isinstance(value.get('result'),dict)and len(value['result']['rows'])==1,'Actual single material result required')
 return value,value['result']['rows'][0]
def build(a):
 inputs=[a.borrador,a.adopcion,a.postsync,a.panel,a.replay,P/'REGISTRO_CAMPANA.json',S/'estado/ACTIVO.json',C/'PROYECTO.json',C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json']
 before={str(Path(p).resolve()):info(p)for p in inputs}
 m=read(a.borrador);need(m.get('closed_for_authoring')is False,'Only the preserved authoring draft may be finalized')
 adoption=read(a.adopcion);need(adoption.get('phase')=='COMMITTED','Actual COMMITTED adoption proof required')
 active=read(S/'estado/ACTIVO.json');life=active['life_id'];card_path=S/'estado/vidas'/life/'VIDA.json';card=read(card_path)
 need(adoption['life_id']==adoption['record']['life_id']==life,'Adopted/current life differs; do not choose highest branch tick')
 need(card['physical']['N']==67 and card['physical']['tick']>=active['tick']>=adoption['record']['physical']['tick'],'Current cut/selection/adoption reference incoherent')
 parent=adoption['physical_parent_protected'];need(parent['life_id']=='ECI02_PI03_MAIN'and parent['tick']==775355 and parent['snapshot_sha256']=='5581d3785bf7d7194b5bdb545827aab55f0659d8b3f2c00301425d89616cf07b','Actual protected physical predecessor differs')
 parent_card=read(S/'estado/vidas'/parent['life_id']/'VIDA.json');need(parent_card['physical']['tick']==775355 and parent_card['snapshot_sha256']==parent['snapshot_sha256'],'Protected parent changed')
 snapshot=S/card['snapshot'];need(info(snapshot)['sha256']==card['snapshot_sha256'],'Current snapshot bytes do not match VIDA')
 sync=read(a.postsync);need(sync.get('phase')=='COMMITTED_METADATA_ONLY'and sync.get('Native_and_ACTIVO_unchanged')is True,'Actual completed post-use metadata synchronization required')
 e=sync['evidence'];cut=e['current_cut'];use=e['actual_post_commit_use']
 need(cut['life_id']==life and physical_equal(cut['physical'],card['physical'])and cut['snapshot_sha256']==card['snapshot_sha256'],'Post-use witness differs from actual current VIDA')
 need(e['Native_snapshot_pending']==0 and e['Native_C2C_closed']is True,'Native/current C2C is not closed')
 need(use['after_tick']==card['physical']['tick']and use['before_tick']>=adoption['record']['physical']['tick'],'Post-commit use does not reach actual current cut')
 cruce=Path(a.cruce)if a.cruce else Path(use['evidence']['path'])
 need(info(cruce)['sha256']==use['evidence']['sha256'],'Cross proof differs from actual synchronized post-use')
 cross_value,cross=primary(cruce)
 need(cross['ordinal']==22 and cross['spec']['context']==2 and(cross['spec']['left'],cross['spec']['right'])==(29,4),'Actual preregistered crossed opportunity22 required')
 need(cross['selected_operation']=='diferencia'and cross['actual_numeric_result']==25 and cross['applied_route']==1 and cross['useful_product']is True,'Actual crossed function/result/route/product criterion not met')
 need(not cross['first_NULL_preserved']and not cross.get('first_rejected_preserved')and cross['after_tick']==card['physical']['tick'],'Cross had unresolved output/admission or is not current cut')
 need(cross_value['committed_snapshot']['life_id']==life,'Cross is not the actual principal trajectory')
 panel=read(a.panel);need(panel.get('schema')=='DEE.PI04.existing_panel12.actual.R01'and panel['life']==life and panel['owner_closed']is True,'Actual closed panel on this genealogy required')
 need(panel['correct']==panel['tested']==12 and panel['inputs']['unique_requested']==panel['inputs']['applied']==929 and panel['inputs']['other']==0,'Panel criterion/denominator differs')
 need(panel['after_tick']<=cross['before_tick']and panel['after_tick']<card['physical']['tick'],'Panel must be located before final later use; never imply a new panel at final cut')
 replay=read(a.replay)
 need(replay.get('schema')=='DEE.PI04.C2C.cold_Native_replay.verified.v1'and replay.get('status')=='NATIVE_REPLAY_VERIFIED'and replay.get('Native_executed')is True and replay.get('closed')is True,'Actual cold Native replay verification required; a prepared recipe/script is insufficient')
 need(replay['life_id']!=life and replay['N']==67 and replay['initial_tick']==800379 and replay['final_tick']==816019,'Replay diagnostic identity/prefix differs')
 need(replay['opportunities']==20 and replay['products']==19 and replay['reserved_opportunities']==replay['reserved_products']==8 and replay['arithmetic_correct']==20,'Replay behavior differs')
 need(replay['Native_inputs_unique']==replay['Native_inputs_applied']==3720 and replay['Native_inputs_rejected_or_other']==0 and replay['actual_replay_Native_ticks']==15640,'Replay dose/horizon differs')
 project=read(C/'PROYECTO.json');cont=read(C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json')
 need(project['selected_life']==cont['life_id']==life and project['latest_saved_tick']==cont['physical_cut']['tick']==card['physical']['tick'],'Current project/continuity not synchronized')
 need(project['manual_internal_edition']=='1.30','Original Manual must remain1.30 until literal publication')
 manual=C/project['manual_current'];need(info(manual)['sha256']==m['manual_original']['sha256'],'Original Manual changed before authoring')
 need(a.comando and all(c.strip()and MARK not in c for c in a.comando),'Root must provide actual verified usage/reproduction commands; do not invent them')
 budget=read(P/'REGISTRO_CAMPANA.json');need(budget['budget']['Native_ticks_all_branches']==120000,'Declared Native ceiling changed')
 floor=budget.get('new_Native_ticks_closed_floor');need(type(floor)is int and 0<=floor<=120000,'Invalid/direct closed Native ledger floor')
 final_tick=card['physical']['tick'];adopt_tick=adoption['record']['physical']['tick'];panel_tick=panel['after_tick']
 principal={'life_id':life,'N':67,'tick':final_tick,'profile':card['profile'],'snapshot_sha256':card['snapshot_sha256'],
  'snapshot_relative_to_product':'sistema/'+card['snapshot'],'physical_parent':parent,'transport_parent_preserved':card.get('parent'),
  'adoption_performed':True,'adoption_tick':adopt_tick,'ACTIVO_reference_tick':active['tick'],
  'full_pair':e['latest_complete_pair'],'adoption_proof':info(a.adopcion),'post_use_sync_proof':info(a.postsync)}
 panel_text=f'El panel anterior acreditó 12/12 funciones y 929/929 entradas en esta misma línea hasta T{panel_tick}. Después ocurrió el uso cruzado del resultado 25 con ruta positiva, hasta T{final_tick}; no se ejecutó otro panel completo en ese último corte.'
 closure=f'Principal COMMITTED {life}, N67, T{final_tick}; padre físico ECI02_PI03_MAIN T775355 preservado. ACTIVO conserva la referencia de selección T{active["tick"]}; VIDA, PROYECTO y continuidad acreditan el estado actual T{final_tick}. '+panel_text
 use_text=f'El uso real posterior a adopción del ordinal22 seleccionó DIFERENCIA para29/4, produjo25, lo presentó a MU y obtuvo un archivo usando ruta positiva. El valor real permitió una segunda actuación diferente de la primera selección. Culminó enT{final_tick}; la secuencia y los puentes siguen preparados.'
 replay_text='La receta fría se ejecutó realmente por el gestor en un diagnóstico nuevo desdeT800379hastaT816019: reprodujo19/20productos,8/8reservas,20aritméticas y3720/3720entradas. Es reproducción material de la adquisición y su control publicado, no sólo cargar un estado aprendido ni recalcularJSON. No añadió esa experiencia al principal.'
 # Every marker is replaced with evidence-bound closing prose; specific sections
 # below use the narrower witness rather than a generic success paragraph.
 def replace(value):
  if isinstance(value,str):return value.replace(MARK,closure).replace('Este borrador no certifica una promoción.','La adopción indicada se acredita mediante los comprobantes de producto y continuidad; la documentación no la sustituye.')
  if isinstance(value,list):return[replace(x)for x in value]
  if isinstance(value,dict):return{k:replace(v)for k,v in value.items()}
  return value
 result=replace(copy.deepcopy(m));result['principal']=principal;result['closed_for_authoring']=True
 result['schema']='DEE.PI04.closed_scientific_authoring_facts.v1';result['closed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 result['manual_before_publication_current_edition']='1.30';result['intended_publication_edition']='1.31';result['documents_published_by_finalizer']=False
 result['resume4']=closure;result['release_cut']='Corte final PI04: '+closure
 result['state_of_edition']='Edición documental1.31; original1.30 preservado literalmente. '+closure
 result['cover_summary']='PI04: coordinación contextual Native asistida, observación histórica externa y controles de señales. Real/constante/yoked:19/12/20productos, reserva8/6/8; sin ventaja de contingencia verdadera. '+closure
 for section in result['sections']:
  if section['title'].startswith('47.8'):
   section['paragraphs']=[p.split('El panel completo de funciones anteriores')[0].strip() if 'El panel completo de funciones anteriores'in p else p for p in section['paragraphs']if'Control del enlace número'not in p]
   section['paragraphs']+=[panel_text,use_text]
  if section['title'].startswith('47.9'):
   section['paragraphs']=[p for p in section['paragraphs']if'46 expectativas'not in p]
   section['paragraphs']+=[replay_text,'Comandos aportados porRootdesde operaciones verificadas, con destinos/IDs nuevos cuando se reproduzca:']
   section['commands']=a.comando
  if section['title'].startswith('47.10'):section['paragraphs'][-1]=closure+' '+use_text
 if a.enlace:
  link=read(a.enlace);need(link.get('schema')=='DEE.PI04.C2C.actual_batch.R01'and link['owner_closed']is True and link['arm']=='link_cut'and link['completed']==1,'Actual closed one-op link control required')
  need(link['products']==0 and link['arithmetic_correct']==1,'Link control expected real arithmetic without downstream product')
  link_text='El control de enlace omitió las cuatro entradas deMUdespués de una aritmética real:182entradas frente186, misma edad782ticks y ningún producto. Demuestra dependencia del eslabón dentro del protocolo; no es un sham semántico isodosis.'
  for section in result['sections']:
   if section['title'].startswith('47.8'):section['paragraphs'].append(link_text)
  result['sources'].append(str(Path(a.enlace).resolve()));inputs.append(a.enlace)
 else:
  for section in result['sections']:
   if section['title'].startswith('47.8'):section['paragraphs'].append('No se incorpora aquí una puntuación de control de enlace: su comprobante Native no fue suministrado al finalizador. Los intentos técnicos sin encolado no cuentan como ensayos funcionales.')
 result['compendium_paragraphs'][-1]=closure+' '+use_text
 result['compendium_paragraphs'].append(replay_text)
 result['Native_budget_direct_record']={'source':info(P/'REGISTRO_CAMPANA.json'),'budget':budget['budget'],'new_Native_ticks_closed_floor':floor,'scope':'Direct preserved campaign ledger, not a new census or Native measurement.'}
 result['final_evidence']={'adoption':info(a.adopcion),'postsync':info(a.postsync),'panel':info(a.panel),'cross':info(cruce),'cold_replay':info(a.replay),'ACTIVO_reference':active,'current_VIDA':info(card_path),'current_snapshot':info(snapshot)}
 result['unresolved_fields_must_be_filled_before_closed_true']=[];result['no_adoption_or_publication_authorized_by_this_file']=True
 result['sources']+=['control/ADOPCION_PRODUCTO_PI04.json',str(Path(a.postsync).resolve()),str(Path(a.panel).resolve()),str(cruce.resolve()),str(Path(a.replay).resolve())]
 need(all(len(s['paragraphs'])<=12 for s in result['sections']),'Section paragraph cap exceeded')
 need(MARK not in json.dumps(result,ensure_ascii=False),'Unresolved closing marker remains')
 for path,old in before.items():need(info(path)==old,'An input changed during finalization: '+path)
 need(read(card_path)==card and read(S/'estado/ACTIVO.json')==active,'Native current/selection changed during finalization')
 return result
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--apply',action='store_true')
 ap.add_argument('--borrador',type=Path,default=P/'control/CIERRE_CIENTIFICO_PI04_BORRADOR.json')
 ap.add_argument('--adopcion',type=Path,default=P/'control/ADOPCION_PRODUCTO_PI04.json')
 ap.add_argument('--postsync',type=Path,required=True);ap.add_argument('--panel',type=Path,required=True)
 ap.add_argument('--cruce',type=Path);ap.add_argument('--enlace',type=Path)
 ap.add_argument('--replay',type=Path,default=P/'control/C2C_COLD20_NATIVE_VERIFICADA_R01.json')
 ap.add_argument('--comando',action='append',required=True);ap.add_argument('--salida',type=Path,default=P/'control/CIERRE_CIENTIFICO_PI04.json');a=ap.parse_args()
 result=build(a)
 if a.apply:
  need(not a.salida.exists(),'Final facts already exist; preserve and inspect instead of overwriting')
  with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
 print(json.dumps({'mode':'FINAL_FACTS_CREATED'if a.apply else'DRY_RUN_NO_WRITES','principal':result['principal'],'panel_scope':result['final_evidence']['panel'],'documents_published':False,'Native_ticks':0,'output':str(a.salida)if a.apply else None},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
