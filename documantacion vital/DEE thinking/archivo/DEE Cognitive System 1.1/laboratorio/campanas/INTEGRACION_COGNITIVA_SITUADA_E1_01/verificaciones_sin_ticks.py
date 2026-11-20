"""Read saved bytes, normalize only documented channel labels, no Runtime."""
from pathlib import Path
import sys,json,importlib.util,subprocess
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';SYSTEM=ROOT/'sistema'
sp=importlib.util.spec_from_file_location('saved_only',SYSTEM/'capacidades/observador_causal_retrospectivo_01.py');saved=importlib.util.module_from_spec(sp);sp.loader.exec_module(saved)
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def cp_for(file):
    d=read(EV/file);i=d['INSTRUMENTO'];life=i['life_id'];tick=i['tick'];expected=i['snapshot_sha256']
    return next(p for p in(SYSTEM/'estado/checkpoints').glob(life+'.T'+str(tick)+'.*')if saved.sha(p.read_bytes())==expected)
def normalized(events,channels):
    return[{**e,'channels':[channels[n]for n in e['channels']]}for e in events]
checks=[]
for a,b in [('SOCIAL_DELAY_LOW_125.json','SOCIAL_DELAY_PASSIVE_131.json'),('STRESS_REPLAY_ALL_148.json','STRESS_REPLAY_PASSIVITY_153.json')]:
    x,y=saved.Snapshot(cp_for(a)),saved.Snapshot(cp_for(b));checks.append({'a':a,'b':b,'a_snapshot_sha256':x.encoded_sha256,'b_snapshot_sha256':y.encoded_sha256,'RAW_equal':x.raw==y.raw,'clocks_equal':x.clocks==y.clocks,'pending_material_events_equal_after_declared_channel_label_normalization':normalized(x.pending,x.channels)==normalized(y.pending,y.channels),'receipt_outcomes_equal_after_channel_label_normalization':normalized(x.receipts,x.channels)==normalized(y.receipts,y.channels),'channel_physical_multiset_equal':sorted(json.dumps(v,sort_keys=True)for v in x.channels.values())==sorted(json.dumps(v,sort_keys=True)for v in y.channels.values()),'identity_metadata_not_claimed_identical':True,'full_checksum_valid':[x.checksum_valid,y.checksum_valid]})
r=subprocess.run([sys.executable,'-B',str(LAB/'verify_fence_probe.py')],capture_output=True,text=True,encoding='utf8',timeout=30)
if r.returncode:raise RuntimeError(r.stderr)
out={'native_ticks':0,'worlds_instantiated':0,'snapshot_byte_comparisons':checks,'read_fence_probe':json.loads(r.stdout),'source_sha256':saved.sha(Path(__file__).read_bytes()),'scope':'Zero-tick structural/agenda verification and denied-I/O audit-only calls. Metadata identity differences are not silently declared physical differences or omitted as full-file equality.'}
(EV/'VERIFICACIONES_ESTRUCTURALES_Y_BARRERA_169.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'snapshot_comparisons':checks,'read_fence_results':out['read_fence_probe']['results']},ensure_ascii=False))
