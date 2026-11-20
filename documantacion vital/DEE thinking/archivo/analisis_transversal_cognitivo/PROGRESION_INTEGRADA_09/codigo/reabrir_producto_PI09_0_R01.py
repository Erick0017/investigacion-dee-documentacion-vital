"""Root-only public gestionar STATE/save/close0, never a material query."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,types
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def main(a):
 output=P/'control'/('REAPERTURA_SELECCIONADA_PRODUCTO_PI09.json'if a.seleccionado else'REAPERTURA_PRODUCTO_PI09.json')
 if output.exists():raise FileExistsError('Reapertura anterior preservada')
 if not a.ejecutar:print(json.dumps({'mode':'PLAN_ONLY','life_id':LIFE,'selected_phase':a.seleccionado,'Native_imported':False,'new_ticks':0,'material_public_use_pending':True}));return
 if (read(S/'estado/ACTIVO.json')['life_id']==LIFE)!=a.seleccionado:raise ValueError('La fase seleccionada/no seleccionada difiere de ACTIVO')
 cardfile=S/'estado/vidas'/LIFE/'VIDA.json';card=read(cardfile);beforefile=S/card['snapshot'];parser=load('PI09_product0_passive',RP/'observador_pasivo.py');before=parser.snapshot_view(beforefile);tick=card['physical']['tick']
 if tick!=903603:raise ValueError('La primera consolidación debe conservar el corte903603 sin uso decorativo')
 permission=load('PI09_actual_permission_probe',S/'capacidades/pi09_permiso_operativo_R01.py');runtime=types.SimpleNamespace(dimension=67,snapshot_metadata_entries=tuple(before['metadata'].items()));adapter=types.SimpleNamespace(world=types.SimpleNamespace(runtime=runtime));profile=permission.profile(adapter)
 if profile is None:raise ValueError('No hay perfil preparado/COMMITTED exacto')
 probes=[{'left':l,'right':r,'selected_route':permission.routes_public(adapter,{'modo':'eci01-balance','izquierda':l,'derecha':r})}for l,r in((17,6),(3,14),(10,10))]
 if any(p['selected_route']!=a.seleccionado for p in probes):raise ValueError('La ruta pública debe permanecer dormida antes de seleccionar y habilitarse sólo tras COMMITTED')
 ownerlib=load('PI09_actual_public_gestor_owner',RP/'propietario_diagnostico.py');ownerlib.configure(P,S,PY);tag='PI09_PRODUCT0_SELECTED_R01'if a.seleccionado else'PI09_PRODUCT0_UNSELECTED_R01';rows=[]
 with ownerlib.Owner(LIFE,tag,system=S)as owner:
  for label,mode,ordinal in(('PI09','eci01-pi09-estado',12),('C2C','eci01-pi04-c2c-estado',31),('FI','eci01-pi07-fi-acceso-estado',4)):
   identifier=tag+'_'+label;value=owner.material(identifier,{'modo':mode},feedback='omit',actuator='closed');primary=P/'ensayos'/(identifier+'.json')
   if value['before_tick']!=tick or value['after_tick']!=tick or value['result']['rows'][0]['progress']['ordinal']!=ordinal:raise ValueError('STATE cambió el tiempo o no conserva los recursos actuales')
   rows.append({'label':label,'mode':mode,'primary':str(primary),'sha256':sha(primary),'ordinal':ordinal,'new_native_ticks':0})
  owner.control('guardar')
 if owner.proc.poll()!=0 or(owner.q.get_meta('owner')or{}).get('running')or owner.q.outstanding():raise ValueError('El propietario público no cerró y concilió')
 current=read(cardfile);afterfile=S/current['snapshot'];after=parser.snapshot_view(afterfile);fields={k:before[k]==after[k]for k in('physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase')}
 changed={k for k in set(before['metadata'])|set(after['metadata'])if before['metadata'].get(k)!=after['metadata'].get(k)};allowed=lambda key:key=='DEE.Cognitive.System.1.1.life.v1'or key=='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'or key.startswith('DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1.queue.')
 physical=all(fields.values());statevalid=all(allowed(k)for k in changed)
 result={'schema':'DEE.PI09.product_public_gestor0.reopening.R01','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'life_id':LIFE,'new_ticks':0,'new_Native_inputs':0,'initial_tick':tick,'final_tick':current['physical']['tick'],'physical_unchanged':physical,'pending_reconciled':True,'operational_state_valid':statevalid,'owner_closed':True,'closed':True,'snapshot_sha256':current['snapshot_sha256'],'before_snapshot':{'path':str(beforefile),'sha256':sha(beforefile)},'after_snapshot':{'path':str(afterfile),'sha256':sha(afterfile)},'Native_field_equalities':fields,'metadata_changed_keys':sorted(changed),'public_route_static_probes':probes,'actual_communication':'Existing RP Owner sends public pedir/resultado/guardar/detener through product sistema/gestionar.py; no private direct scientific call','rows':rows,'selected':a.seleccionado,'material_public_use_executed':False,'new_function_at_cut':'Actual canonical EP11 plus whole Native equivalence through product0; no new material trial claimed'}
 with output.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(output),'sha256':sha(output),'new_ticks':0,'physical_unchanged':physical,'operational_state_valid':statevalid,'owner_closed':True,'snapshot_sha256':current['snapshot_sha256']}));return 0 if physical and statevalid else 2
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--seleccionado',action='store_true');p.add_argument('--ejecutar',action='store_true');raise SystemExit(main(p.parse_args()))
