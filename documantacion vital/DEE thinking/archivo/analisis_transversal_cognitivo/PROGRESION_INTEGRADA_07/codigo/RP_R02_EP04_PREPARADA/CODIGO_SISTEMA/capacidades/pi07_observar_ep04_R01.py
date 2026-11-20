"""RP-only external EP04 recording around the literal R02 operation.

No R02 source/protocol/decoder/sensor/action/return change. The new mode is
accepted only in an explicit RP diagnostic at the known ordinal/cut. This is a
different recording pattern, not absence of all global observation.
"""
from pathlib import Path
import hashlib,importlib.util,json,uuid
from capacidades import pi07_regulacion_R02 as core
VERSION='DEE.PI07.RP.external_EP04_observer.R01'
OBSERVE='eci01-pi07-observar-episodio-04';MODES={*core.MODES,OBSERVE}
PROTOCOL=Path(__file__).with_name('PROTOCOLO_RP_OBSERVACION_EP04_PI07_R01.json')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def protocol():
 p=json.loads(PROTOCOL.read_text('utf8'))
 if p.get('status')!='SEALED_BEFORE_RP_NATIVE'or p.get('ordinal')!=4 or p.get('before_tick')!=827749 or p.get('after_tick')!=828531 or p.get('query_tick')!=828119:raise ValueError('One pre-fixed EP04 observation only')
 if sha(Path(core.__file__))!=p['R02_source_sha256']or sha(core.PROTOCOL)!=p['R02_protocol_sha256']:raise ValueError('Exact literal R02 core/protocol required')
 return p
def validate_literal(row):
 if isinstance(row,dict)and row.get('modo')==OBSERVE:
  if set(row)!={'modo'}:raise ValueError('No adjustable window/site/target/answer')
  return
 core.validate_literal(row)
def validate(a,row):
 if not isinstance(row,dict)or row.get('modo')!=OBSERVE:return core.validate(a,row)
 validate_literal(row);p=protocol();core.validate(a,{'modo':core.EPISODE});identity=core._identity(a);m=core._get(a)
 if '_RP_'not in identity['life_id']or m['ordinal']!=4 or int(a.tick)!=p['before_tick']or m['instrumentation']['global_enabled']is not False:raise ValueError('Only RP ordinal4 at the fixed coherent cut with inner recorder disabled')
def dispatch(a,row,*,actuator='closed',directory=None):
 if not isinstance(row,dict)or row.get('modo')!=OBSERVE:return core.dispatch(a,row,actuator=actuator,directory=directory)
 validate(a,row);p=protocol();identity=core._identity(a);core._home(directory,identity['life_id'])
 path=Path(__file__).with_name('observador_global_PI05_R01.py')
 if sha(path)!=p['codec_sha256']:raise ValueError('Exact d60 global recorder required')
 spec=importlib.util.spec_from_file_location('PI07_RP_EP04_global_d60',path);capture=importlib.util.module_from_spec(spec);spec.loader.exec_module(capture)
 refs=[core._observe(a,core.at(v))for v in((-1,-1,0),(1,-1,0))]
 cal=core._helper().schedule_trial(int(a.tick)+16,int(refs[0]['clock'])+16,6);q=cal['query_tick']
 if q!=p['query_tick']:raise ValueError('Actual fixed calendar differs; no favourable retiming')
 ticks=sorted({q+c+d for c in(-1,4,8,72,144,408,410)for d in(-2,-1,0,1,2)})
 target=Path(__file__).resolve().parents[1]/'estado/observacion_pasiva'/identity['life_id']/('PI07_RP_EP04_'+uuid.uuid4().hex)
 recorder=capture.GlobalRecorder(target,N=67,ticks=ticks,anchor_ticks={q-3,q+4,q+8,q+72,q+144,q+408,q+412},
  provenance={'life_id':identity['life_id'],'ordinal':4,'version':VERSION,'R02_actor_unchanged':True,'actor_receives_recording':False,'different_recording_pattern_not_no_global':True},max_frames=31,max_compressed_bytes=67108864)
 wrapped=capture.CapturingAdapter(a,ticks=ticks,recorder=recorder)
 try:
  original=core.dispatch(wrapped,{'modo':core.EPISODE},actuator=actuator,directory=directory)
  if original['after_tick']!=p['after_tick']:raise RuntimeError('Preserve an unexpected reached cut; never repair/rewind')
  record=recorder.close();before_save=core._physical(a)
  from dee_thinking.persistence import save_world_snapshot
  diagnostic=target/'NATIVE_EP04_DIAGNOSTICO.deetsnap.gz'
  save_world_snapshot(a.world,diagnostic,include_trace=True,compress=True,overwrite=False)
  if core._physical(a)!=before_save:raise RuntimeError('Diagnostic serialization changed physical state')
  return{'version':VERSION,'observed_ordinal':4,'original_result':original,'external_observation':record,
   'native_after_EP04':{'path':str(diagnostic),'bytes':diagnostic.stat().st_size,'sha256':sha(diagnostic),'not_a_complete_operational_backup':True},
   'new_native_ticks':original['new_native_ticks'],'R02_literal_source_preserved':True,'scope':'RP-only additional recording of EP04, same core inputs/reader/actions/return. Compare matched Native states; no automatic observation-passivity or learning claim.'}
 except BaseException:
  if not recorder.closed:recorder.close()
  raise
def operational_dependencies(a,directory):return core.operational_dependencies(a,directory)
def uncertain(a):return core.uncertain(a)
def code_files():return list(dict.fromkeys([Path(__file__),PROTOCOL,*core.code_files()]))
