"""Root-only: una oportunidad pública D7, sólo después de D COMMITTED.

No prepara ni reinicia nada: consume la oferta D ordinal7 ya existente.
Usa gestionar pedir/resultado y controles reales; guarda y reabre sin avance.
Por defecto sólo muestra el plan. El propietario existente aplica Job512MiB.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,sys
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01';KEY='DEE.Cognitive.PI09.persistent_environment.D.R02';BOUND=2110;OUTPUT=P/'control/USO_PUBLICO_D_EP7_PI09_R01.json';LOCK=P/'PI09_ROOT_NATIVE_WRITER.lock'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def load(name,p):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def write(v):
 temp=OUTPUT.with_name(OUTPUT.name+'.WRITING')
 with temp.open('w',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(temp,OUTPUT)
def ref(p):return {'path':str(p),'sha256':sha(p)}
def snapshot(parser):
 card=read(S/'estado/vidas'/LIFE/'VIDA.json');file=S/card['snapshot'];need(sha(file)==card['snapshot_sha256'],'Checkpoint actual inconsistente');return card,parser.snapshot_view(file)
def public_episode(client,owner,tag):
 identifier=tag+'_EP7';literal={'modo':'eci01-pi09-d-episodio'};need(owner.q.get(identifier)is None,'ID anterior conservado; no se reenvía')
 admission,p1=client.cli(tag,'EP7_pedir',['mente-unificada-pedir','--vida',LIFE,'--id',identifier,'--situaciones',json.dumps([literal],separators=(',',':')),'--retorno','real','--actuador','closed','--esperar','0'])
 need(not str(admission.get('admission','')).startswith('rejected'),'Petición rechazada; conservar ID y diagnóstico')
 p2=client.public_control(tag,'EP7_reanudar','reanudar');owner.wait(identifier,limit=600)
 answer,p3=client.cli(tag,'EP7_resultado',['mente-unificada-resultado','--vida',LIFE,'--id',identifier]);p4=client.public_control(tag,'EP7_pausar','pausar');row=answer.get('request',{})
 need(row.get('id')==identifier and row.get('status')=='completed','Futuro no completado; conservar la misma petición sin reintento')
 file=P/'ensayos'/(identifier+'.json')
 with file.open('x',encoding='utf8')as f:json.dump(row,f,ensure_ascii=False,indent=2);f.write('\n')
 return json.loads(row['result']),{'literal':literal,'primary':ref(file),'commands':[p1,p2,p3,p4]}
def run(a):
 need(Path(sys.executable).resolve()==PY.resolve(),'Root debe usar el Python oficial con Job512MiB')
 need(a.confirmar_adopcion_D,'Sólo tras decisión explícita y COMMITTED real de D')
 need(not OUTPUT.exists()and not LOCK.exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Otra ejecución o resultado previo debe conservarse')
 adopted=P/'control/ADOPCION_D_PRODUCTO_PI09.json';need(adopted.exists()and read(adopted).get('phase')=='COMMITTED'and read(adopted).get('life_id')==LIFE,'D debe estar realmente COMMITTED antes del uso público')
 need(read(S/'estado/ACTIVO.json')['life_id']==LIFE,'Se exige Discovery seleccionada, nunca una vida alternativa')
 parser=load('PI09_public_EP7_passive',RP/'observador_pasivo.py');card,before=snapshot(parser);progress=json.loads(before['metadata'][KEY]);initial=card['physical']['tick'];need(initial>917679 and progress['ordinal']==7 and len(progress['rows'])==7,'Se exige Discovery adoptada con la oferta7 disponible')
 ledger=load('PI09_final_public_ledger',H/'ledger_PI09_misma_identidad_R01.py');budget=read(P/'REGISTRO_CAMPANA.json')['budget'];known=ledger.ledger();need(known['ticks']+BOUND<=budget['Native_ticks_all_branches'],'La oferta finita no cabe en el presupuesto Native restante')
 deadline=datetime.datetime.fromisoformat(budget['new_experimental_uses_cutoff_local']);need(datetime.datetime.now(datetime.timezone.utc)<deadline.astimezone(datetime.timezone.utc),'El plazo prospectivo de nuevo uso material ya terminó')
 with LOCK.open('x',encoding='utf8')as f:json.dump({'pid':os.getpid(),'phase':'FINAL_PUBLIC_D_EP7','new_worlds':0,'max_ticks':BOUND,'memory_limit_bytes':512*1024*1024},f)
 base={'schema':'DEE.PI09.actual_selected_public_D_EP7.R01','life_id':LIFE,'Root_explicit_D_adoption':True,'D_adopted':True,'new_worlds':0,'initial_tick':initial,'finite_bound':BOUND,'memory_limit_bytes':512*1024*1024,'literal':{'modo':'eci01-pi09-d-episodio'},'no_expected_response_passed_to_actor':True,'automatic_retry':False,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};write({**base,'status':'RUNNING','closed':False})
 client=load('PI09_actual_public_client_for_EP7',H/'reabrir_producto_PI09_0_R02.py');need(sha(H/'reabrir_producto_PI09_0_R02.py')=='fd3aab3aaaf1e4940d4fc0e55670301dbbaa0289a534509ff183d2e021adf88f','Cambió el cliente público conservado');client.LIFE=LIFE;client.S=S
 ownerlib=load('PI09_public_final_owned',RP/'propietario_diagnostico.py');ownerlib.configure(P,S,PY);tag='PI09_PUBLIC_D_EP7_R01'
 try:
  with ownerlib.Owner(LIFE,tag,system=S)as owner:
   value,record=public_episode(client,owner,tag);saved=client.public_control(tag,'guardar','guardar');stopped=client.public_control(tag,'detener','detener');owner.proc.wait(timeout=60)
  need(owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running')and not owner.q.outstanding(),'El propietario material debe cerrar coherentemente')
  material_card,material_view=snapshot(parser);m=json.loads(material_view['metadata'][KEY]);need(m['ordinal']==8 and len(m['rows'])==8 and 0<material_card['physical']['tick']-initial<=BOUND,'La oportunidad debe avanzar una sola oferta y respetar la cota')
  with ownerlib.Owner(LIFE,tag+'_REOPEN0',system=S)as again:
   state,commands=client.public_state(again,tag+'_REOPEN0','STATE',{'modo':'eci01-pi09-d-estado'});need(state['before_tick']==state['after_tick']==material_card['physical']['tick']and state['result']['rows'][0]['progress']['ordinal']==8,'La reapertura no debe avanzar ni consumir oferta')
   save0=client.public_control(tag+'_REOPEN0','guardar','guardar');stop0=client.public_control(tag+'_REOPEN0','detener','detener');again.proc.wait(timeout=60)
  need(again.proc.poll()==0 and not(again.q.get_meta('owner')or{}).get('running')and not again.q.outstanding(),'La reapertura debe cerrar y conciliar')
  final,after=snapshot(parser);fields={k:material_view[k]==after[k]for k in('physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase')};need(all(fields.values())and json.loads(after['metadata'][KEY])==m,'Reapertura0 con igualdad completa y stock literal requerida')
  row=value['result']['rows'][0];result={**base,'status':'CLOSED_PUBLIC_MATERIAL_AND_REOPEN0','closed':True,'owner_closed':True,'pending_reconciled':True,'final_tick':final['physical']['tick'],'new_Native_ticks':final['physical']['tick']-initial,'ordinal_before':7,'ordinal_after':8,'remaining':4,'actual_failed':row.get('actual_failed'),'functional_success':row.get('actual_failed')is False,'actual_row':row,'public_material_record':record,'public_save':saved,'public_stop':stopped,'reopen0':{'new_ticks':0,'Native_field_equalities':fields,'stock_unchanged':True,'public_state_commands':commands,'save':save0,'stop':stop0},'current_record':final,'snapshot_sha256':final['snapshot_sha256'],'selected_life_unchanged':read(S/'estado/ACTIVO.json')['life_id']==LIFE,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};write(result)
  need(read(LOCK)['pid']==os.getpid(),'Sólo se libera el mutex propio');LOCK.unlink();print(json.dumps({'proof':str(OUTPUT),'sha256':sha(OUTPUT),'closed':True,'functional_success':result['functional_success'],'new_ticks':result['new_Native_ticks']}));return 0 if result['functional_success']else 2
 except BaseException as exc:
  write({**base,'status':'STOPPED_PRESERVED','closed':False,'error':repr(exc),'automatic_retry':False,'mutex_preserved_for_Root_inspection':True});raise
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--ejecutar',action='store_true');ap.add_argument('--confirmar-adopcion-D',dest='confirmar_adopcion_D',action='store_true');a=ap.parse_args()
 if not a.ejecutar:print(json.dumps({'mode':'PLAN_ONLY_NO_STATE_OR_NATIVE','only_after_Root_decision':'D_COMMITTED','life_id':LIFE,'public_literal':{'modo':'eci01-pi09-d-episodio'},'ordinal':{'before':7,'after':8,'total':12},'max_ticks':BOUND,'save_reopen0':True,'no_new_world':True}));return 0
 return run(a)
if __name__=='__main__':raise SystemExit(main())
