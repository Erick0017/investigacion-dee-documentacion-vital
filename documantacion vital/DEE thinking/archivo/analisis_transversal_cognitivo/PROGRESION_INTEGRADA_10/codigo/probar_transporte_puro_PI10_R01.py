"""Pure transport-fence checks on frozen bytes and an in-memory fake adapter.

No Native import/owner, live state read/write, input, tick or adoption. This is
instrumentation verification, not a scientific retention experiment.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,types
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def fake(entries):return types.SimpleNamespace(world=types.SimpleNamespace(runtime=types.SimpleNamespace(snapshot_metadata_entries=tuple(entries.items()),dimension=67)))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--sistema-codigo',type=Path,default=P/'estados/P0/sistema');ap.add_argument('--salida',default='PRUEBA_PURA_TRANSPORTE_PI10_R01.json');a=ap.parse_args();system=a.sistema_codigo.resolve(strict=True)
 if system.parent.parent!=(P/'estados').resolve():raise ValueError('Explicit isolated prepared code only')
 t=load('PI10_pure_transport_test_module',H/'pi10_transporte_ancestral_R01.py');t.__file__=str(system/'capacidades/pi10_transporte_ancestral_R01.py');t.SCOPE=system/'capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json'
 q=load('PI10_passive_frozen_bytes_parser',C/'reproducibilidad/observador_pasivo.py');pair=P/'pares/PRINCIPAL_D_T922371';entries=q.snapshot_view(pair/'VIDA.deetsnap.gz')['metadata'];scope=json.loads(t.SCOPE.read_text('utf-8-sig'))
 system_identity=json.loads(entries[t.SYSTEM]);system_identity['life_id']=scope['life_id'];entries[t.SYSTEM]=json.dumps(system_identity);tests=[]
 tests.append({'case':'exact_current_clone_identity_and_ancestral_hashes','ok':t.identity(fake(entries))['life_id']==scope['life_id']})
 corrupt=dict(entries);key=next(iter(scope['inherited_metadata_sha256']));corrupt[key]+=' ';denied=False
 try:t.identity(fake(corrupt))
 except ValueError:denied=True
 tests.append({'case':'reject_changed_acquired_ancestor_metadata','ok':denied})
 old=dict(entries);leaf=dict(system_identity);leaf['life_id']=t.OLD_D;old[t.SYSTEM]=json.dumps(leaf)
 tests.append({'case':'original_D_does_not_enter_new_transport_scope','ok':not t.applies(fake(old))})
 for mode in('eci01-pi08-b-estado','eci01-pi08-c-estado','eci01-pi07-estado','eci01-pi07-r02-estado'):
  t.validate_external(fake(entries),{'modo':mode},payload={'operacion':'sesion','situaciones':[{'modo':mode}],'retorno':'omit','actuador':'closed'})
 tests.append({'case':'four_inherited_STATE_routes_remain_readonly_admissible','ok':True})
 denied=False
 try:t.validate_external(fake(entries),{'modo':'eci01-pi09-d-episodio'},payload={'operacion':'sesion'})
 except ValueError:denied=True
 tests.append({'case':'old_D_material_calendar_cannot_reopen','ok':denied})
 if not all(r['ok']for r in tests):raise ValueError('Pure transport fence regression')
 result={'schema':'DEE.PI10.pure_transport_fence_checks.R01','tests':tests,'actual_Native_executed':False,'new_Native_ticks':0,'fake_adapter_in_memory_only':True,'source_closed_pair_manifest_sha256':sha(pair/'EXPORTACION_SERVICIO.json'),'tested_source_sha256':sha(H/'pi10_transporte_ancestral_R01.py'),'scope_sha256':sha(t.SCOPE)}
 if Path(a.salida).name!=a.salida or not a.salida.endswith('.json'):raise ValueError('Only a proof basename within campaign/control')
 out=P/'control'/a.salida
 if out.exists():
  if json.loads(out.read_text('utf-8-sig'))!=result:raise ValueError('Prior pure proof differs; preserve rather than overwrite')
 else:
  with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
