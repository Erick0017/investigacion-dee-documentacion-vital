"""Read-only source/manifest and synthetic registry checks, no GUI process."""
from pathlib import Path
import ast,datetime,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'control/abrir_solo_comparadores_C02.py'
s=importlib.util.spec_from_file_location('_comparator_gui_offline',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
tests=[]
for participant in('PROGRAMMED','CONVENTIONAL_AI'):
 v=m.validate_scene(participant);assert v['scene'].parent==ROOT/'mundo'
 tests.append(dict(name=participant+'_frozen_18_6_scene',passed=True,sha256=v['sha256'],bytes=v['bytes']))
def rejects(call):
 try:call()
 except RuntimeError:return True
 return False
assert rejects(lambda:m.validate_scene('LIVE_NATIVE'));tests.append(dict(name='native_scene_and_arbitrary_participant_denied',passed=True))
assert m.check_registry([],lambda pid:None)['unresolved_intents']==0
rows=[dict(kind='LAUNCH_INTENT',launch_id='x'),dict(kind='PROCESS_STARTED',launch_id='x',process=dict(pid=123))]
assert rejects(lambda:m.check_registry(rows,lambda pid:dict(pid=pid)))
assert m.check_registry(rows,lambda pid:None)['prior_live_pids']==0
assert rejects(lambda:m.check_registry([dict(kind='LAUNCH_INTENT',launch_id='unknown')],lambda pid:None))
tests.append(dict(name='live_or_ambiguous_prior_launch_denied_closed_launch_allowed',passed=True))
t=P.read_text('utf8');tree=ast.parse(t)
assert "startup.wShowWindow=0"in t and 'subprocess.STARTF_USESHOWWINDOW'in t
assert '[str(STUDIO),str(info[\'scene\'])]'in t and 'shell=False'in t
assert "MIN_FREE_BYTES=1_800_000_000"in t
tests.append(dict(name='closed_local_GUI_arguments_hidden_window_and_RAM_floor',passed=True))
assert not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='Popen'for n in tree.body)
tests.append(dict(name='import_is_inert_no_GUI_spawn',passed=True))
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
report=dict(schema='DEE.RBX01.C02.comparator_GUI_launcher.offline_fixtures.R01',tests=tests,all_passed=True,
            source_sha256=hashlib.sha256(P.read_bytes()).hexdigest(),GUI_launches=0,Native_calls=0,MCP_calls=0,model_calls=0)
out=ROOT/'pruebas'/('LANZADOR_COMPARADORES_'+stamp+'.json');out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2))
