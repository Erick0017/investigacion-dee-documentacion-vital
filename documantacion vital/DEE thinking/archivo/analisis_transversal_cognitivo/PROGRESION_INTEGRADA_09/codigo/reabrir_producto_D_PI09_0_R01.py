"""Root-only exact Discovery public STATE/save/close0 after same-ID move."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,types
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01';PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'
KEYS={'D':('DEE.Cognitive.PI09.persistent_environment.D.R02',12),'R02':('DEE.Cognitive.PI09.selective_registered_consultation.R02',18),'FI8':('DEE.Cognitive.PI09.explicit_FI_eight_offer_lot.R01',8),'C2C':('DEE.Cognitive.PI04.C2C.coordination.R01',32)}
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def load(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def stocks(view):
 out={}
 for label,(key,total)in KEYS.items():
  m=json.loads(view['metadata'][key]);out[label]={'ordinal':m['ordinal'],'total':total,'remaining':total-m['ordinal']}
 return out
def main(a):
 output=P/'control'/('REAPERTURA_SELECCIONADA_D_PRODUCTO_PI09.json'if a.seleccionado else'REAPERTURA_D_PRODUCTO_PI09.json');need(not output.exists(),'Prior zero reopening preserved')
 if not a.ejecutar:print(json.dumps({'mode':'PLAN_ONLY_NO_STATE_OR_NATIVE','life_id':LIFE,'new_ticks':0,'public_STATES':['D','historical_R02','FI8','C2C'],'finite_stock_dynamic_no_reset':True}));return
 need((read(S/'estado/ACTIVO.json')['life_id']==LIFE)==a.seleccionado,'Selected/unselected phase differs');cardfile=S/'estado/vidas'/LIFE/'VIDA.json';beforecard=read(cardfile);parser=load('PI09_D_product0_passive',RP/'observador_pasivo.py');beforefile=S/beforecard['snapshot'];before=parser.snapshot_view(beforefile);tick=before['physical']['tick'];stock=stocks(before)
 nativecard=S/'estado/vidas'/PARENT/'VIDA.json';parent=read(nativecard);protected={str(p):sha(p)for p in(nativecard,S/parent['snapshot'])};need(parent['physical']['tick']==903603,'Parent Native must stay quiet')
 profile=load('PI09_D_public_profile_probe',S/'capacidades/pi09_permiso_operativo_D_R01.py');adapter=types.SimpleNamespace(world=types.SimpleNamespace(runtime=types.SimpleNamespace(dimension=67,snapshot_metadata_entries=tuple(before['metadata'].items()))));need(profile.profile(adapter)is not None,'Exact D profile missing');probes=[profile.routes_public(adapter,{'modo':'eci01-balance','izquierda':l,'derecha':r})for l,r in((17,6),(3,14),(10,10))];need(probes==[a.seleccionado]*3,'Public FI8 route must be dormant until selected COMMITTED')
 # Reuse the already used public client implementation, not its Native target
 # or main(); only the exact current LIFE global changes in this namespace.
 client=load('PI09_D_existing_public_gestor_client',H/'reabrir_producto_PI09_0_R02.py');need(sha(H/'reabrir_producto_PI09_0_R02.py')=='fd3aab3aaaf1e4940d4fc0e55670301dbbaa0289a534509ff183d2e021adf88f','Literal public client changed');client.LIFE=LIFE
 driver=load('PI09_D_product0_existing_owner',RP/'propietario_diagnostico.py');driver.configure(P,S,PY);tag='PI09_D_PRODUCT0_SELECTED_R01'if a.seleccionado else'PI09_D_PRODUCT0_UNSELECTED_R01';rows=[]
 with driver.Owner(LIFE,tag,system=S)as owner:
  for label,mode in(('D','eci01-pi09-d-estado'),('R02','eci01-pi09-estado'),('FI8','eci01-pi09-fi-lote-estado'),('C2C','eci01-pi04-c2c-estado')):
   value,commands=client.public_state(owner,tag,label,{'modo':mode});need(value['before_tick']==value['after_tick']==tick and value['result']['rows'][0]['progress']['ordinal']==stock[label]['ordinal'],'STATE advanced time or resource counter')
   file=P/'ensayos'/(tag+'_'+label+'.json');rows.append({'label':label,'primary':str(file),'sha256':sha(file),'public_commands':commands,'new_native_ticks':0})
  saved=client.public_control(tag,'guardar','guardar');stopped=client.public_control(tag,'detener','detener');owner.proc.wait(timeout=60)
 need(owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running')and not owner.q.outstanding(),'Actual owner closed and queue reconciled required')
 card=read(cardfile);afterfile=S/card['snapshot'];after=parser.snapshot_view(afterfile);fields={k:before[k]==after[k]for k in('physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase')};changed=[k for k in set(before['metadata'])|set(after['metadata'])if before['metadata'].get(k)!=after['metadata'].get(k)];allowed=lambda k:k in('DEE.Cognitive.System.1.1.life.v1','DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1')or k.startswith('DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1.queue.');valid=all(allowed(k)for k in changed);unchanged=protected=={p:sha(Path(p))for p in protected};stockequal=stock==stocks(after)
 result={'schema':'DEE.PI09.D.product_public0.reopening.R01','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'life_id':LIFE,'selected':a.seleccionado,'new_ticks':0,'new_Native_inputs':0,'initial_tick':tick,'final_tick':card['physical']['tick'],'physical_unchanged':all(fields.values()),'pending_reconciled':True,'operational_state_valid':valid and stockequal and unchanged,'owner_closed':True,'closed':True,'snapshot_sha256':card['snapshot_sha256'],'before_snapshot':{'path':str(beforefile),'sha256':sha(beforefile)},'after_snapshot':{'path':str(afterfile),'sha256':sha(afterfile)},'Native_field_equalities':fields,'metadata_changed_keys':changed,'stock_before':stock,'stock_after':stocks(after),'stock_unchanged':stockequal,'Native_parent_unchanged':unchanged,'rows':rows,'public_save':saved,'public_stop':stopped,'public_route_static_probes':probes,'material_public_use_executed':False}
 with output.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(output),'sha256':sha(output),'new_ticks':0,'physical_unchanged':result['physical_unchanged'],'stock_unchanged':stockequal,'owner_closed':True}));return 0 if result['physical_unchanged']and result['operational_state_valid']else 2
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--ejecutar',action='store_true');ap.add_argument('--seleccionado',action='store_true');raise SystemExit(main(ap.parse_args()))
