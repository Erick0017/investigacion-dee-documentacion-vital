"""Root-only actual product owner STATE/save/close0. No cognitive input or
time advance. Public-route probe evaluates only fixed permission metadata.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,types
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main(a):
 output=P/'control'/('REAPERTURA_PRODUCTO_PI08.json'if not a.seleccionado else'REAPERTURA_SELECCIONADA_PRODUCTO_PI08.json')
 if output.exists():raise FileExistsError('Existing reopening preserved; do not repeat')
 if not a.ejecutar:print(json.dumps({'mode':'PLAN_ONLY','life_id':LIFE,'product':str(S),'selected_phase':a.seleccionado,'NativeRuntime_opened':False,'new_Native_inputs':0,'new_ticks':0}));return
 active=read(S/'estado/ACTIVO.json')
 if(active['life_id']==LIFE)!=a.seleccionado:raise ValueError('Explicit selected/unselected phase differs from actual ACTIVO')
 cardfile=S/'estado/vidas'/LIFE/'VIDA.json';card=read(cardfile);beforefile=S/card['snapshot'];parser=load('PI08_product0_passive_parser',RP/'observador_pasivo.py');before=parser.snapshot_view(beforefile);tick=card['physical']['tick'];rows=[]
 permission=load('PI08_actual_product_permission_probe',S/'capacidades/pi08_permisos_operativos_R01.py');runtime=types.SimpleNamespace(dimension=67,snapshot_metadata_entries=tuple(before['metadata'].items()));adapter=types.SimpleNamespace(world=types.SimpleNamespace(runtime=runtime));permission._ORIGINAL_FI_ROUTE=lambda unused,row:False
 probes=[{'left':left,'right':right,'route_to_declared_alternative':permission._outer_FI_route(adapter,{'modo':'eci01-balance','izquierda':left,'derecha':right})}for left,right in((17,6),(3,14),(10,10))]
 if not all(p['route_to_declared_alternative']for p in probes):raise ValueError('Actual prepared/COMMITTED public profile does not bind all outer FI')
 ownerlib=load('PI08_existing_product0_owner',RP/'propietario_diagnostico.py');ownerlib.configure(P,S,PY)
 tag='PI08_PRODUCT0_SELECTED_R01'if a.seleccionado else'PI08_PRODUCT0_UNSELECTED_R01'
 with ownerlib.Owner(LIFE,tag,system=S)as owner:
  for label,literal in(('R03',{'modo':'eci01-pi07-r03-estado'}),('C2C',{'modo':'eci01-pi04-c2c-estado'}),('FI',{'modo':'eci01-pi07-fi-acceso-estado'})):
   identifier=tag+'_'+label;value=owner.material(identifier,literal,feedback='omit',actuator='closed');primary=P/'ensayos'/(identifier+'.json')
   if value['before_tick']!=tick or value['after_tick']!=tick:raise ValueError('STATE advanced the actual world')
   rows.append({'label':label,'primary':str(primary),'sha256':sha(primary),'before_tick':tick,'after_tick':tick})
  owner.control('guardar')
 if owner.proc.poll()!=0 or(owner.q.get_meta('owner')or{}).get('running')or owner.q.outstanding():raise ValueError('Product owner did not close/reconcile')
 current=read(cardfile);afterfile=S/current['snapshot'];after=parser.snapshot_view(afterfile);fields={k:before[k]==after[k]for k in('physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase')};changed={k for k in set(before['metadata'])|set(after['metadata'])if before['metadata'].get(k)!=after['metadata'].get(k)};allowed=lambda key:key=='DEE.Cognitive.System.1.1.life.v1'or key=='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'or key.startswith('DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1.queue.')
 physical=all(fields.values());statevalid=all(allowed(key)for key in changed)
 result={'schema':'DEE.PI08.product_owner0.reopening.v1','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'life_id':LIFE,'new_ticks':0,'new_Native_inputs':0,'initial_tick':tick,'final_tick':current['physical']['tick'],'physical_unchanged':physical,'pending_reconciled':True,'operational_state_valid':statevalid,'owner_closed':True,'closed':True,'snapshot_sha256':current['snapshot_sha256'],'before_snapshot':{'path':str(beforefile),'sha256':sha(beforefile)},'after_snapshot':{'path':str(afterfile),'sha256':sha(afterfile)},'Native_field_equalities':fields,'metadata_changed_keys':sorted(changed),'public_route_permission_probes_without_Native_question':probes,'rows':rows,'selected':a.seleccionado,'no_adoption_or_material_test_by_this_helper':True,'scope':'Actual product owner loaded the complete moved currentlife, validatedall operational dependencies, used STATEonly andsaved/closed0. Permission probe is static against actual frozen metadata/currentcontract, not a Native FI answer.'}
 put(output,result);print(json.dumps({'proof':str(output),'sha256':sha(output),'new_ticks':0,'physical_unchanged':physical,'operational_state_valid':statevalid,'owner_closed':True,'snapshot_sha256':current['snapshot_sha256']}));return 0 if physical and statevalid else 2
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--seleccionado',action='store_true');ap.add_argument('--ejecutar',action='store_true');raise SystemExit(main(ap.parse_args()))
