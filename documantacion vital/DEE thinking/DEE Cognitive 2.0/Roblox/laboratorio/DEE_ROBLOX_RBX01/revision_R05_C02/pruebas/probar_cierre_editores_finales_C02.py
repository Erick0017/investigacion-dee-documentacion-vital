"""Pure final18/identity guard fixtures. No process, Native, GUI or DB calls."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'control/verificar_editores_finales_C02.py';ps=ROOT/'control/cerrar_editores_finales_C02.ps1'
s=importlib.util.spec_from_file_location('_final_editors_guards',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
w=dict(schema='DEE.RBX01.C02.world_checkpoint.v1',world_id='RBX01_R05_C02_R02',scenario_sha256=m.FP,
 native_life_id=m.LIFE,native_tick=970000,S=dict(nativeTick=970000,completedCycles=18,cycle=18),
 boundary=dict(completed_opportunities=18,next_opportunity=19,phase='BOUNDARY',native_phase='IDLE',uncertain=False,pending_action=None,pending_operation=None),
 events=[dict(kind='SESSION_CLOSED')],pose_trace=[dict(t=1)],body_pose=list(range(12)),physical=dict(parts=[dict(name='test')]))
m.final_world(w,m.LIFE,970000);tests=[dict(name='all18_final_World_identity',passed=True)]
for field in('completed_opportunities','next_opportunity','uncertain'):
 bad=copy.deepcopy(w);bad['boundary'][field]={'completed_opportunities':17,'next_opportunity':18,'uncertain':True}[field]
 try:m.final_world(bad,m.LIFE,970000)
 except RuntimeError:tests.append(dict(name='reject_'+field,passed=True))
 else:raise AssertionError(field)
bad=copy.deepcopy(w);bad['S']['nativeTick']=None
try:m.final_world(bad,m.LIFE,970000)
except RuntimeError:tests.append(dict(name='reject_missing_actual_tick',passed=True))
else:raise AssertionError('null tick')
epoch=datetime.datetime(1601,1,1,tzinfo=datetime.timezone.utc)
base=datetime.datetime(2026,11,15,8,22,54,tzinfo=datetime.timezone.utc)-epoch
assert (base.days*86400+base.seconds)*10000000+4396167==m.TARGETS[13064]['creation_filetime']
opened=json.loads((ROOT/'evidencia/APERTURA_PROGRAMMED_C02_R01_RESULTADO.json').read_text('utf-8-sig'))
assert opened['opened_process']['creation_filetime']==m.TARGETS[7820]['creation_filetime']
tests.append(dict(name='both_exact_creation_filetimes_from_root_and_launch_record',passed=True))
t=ps.read_text('utf8');ast.parse(p.read_text('utf8'))
assert 'Pid=13064;'in t and 'Pid=7820;'in t and 'ProtectedC01Pid=7252'in t
assert 'elseif($Force)'in t and '$row.CloseMainWindowReturned=$p.CloseMainWindow()'in t
assert 'Stop-Process -Id $entry.Target.Pid'in t and 'Start-Process'not in t
assert '-DateKind String'in t and 'GlobalMemoryStatusEx'in t and 'Get-CimInstance'not in t
tests.append(dict(name='literal_two_targets_graceful_first_force_only_false_no_CIM_date_strings',passed=True))
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
r=dict(schema='DEE.RBX01.C02.final_editor_close.offline_fixtures.R01',tests=tests,all_passed=True,
 sha256={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest()for x in(p,ps)},
 Native_calls=0,MCP_calls=0,HTTP_calls=0,GUI_calls=0,process_close_calls=0,actual_experiment_DB_opened=False)
out=ROOT/'pruebas'/('CIERRE_EDITORES_FINALES_'+stamp+'.json');out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf8');print(json.dumps(r,indent=2))
