"""Replay ONLY the newly localized114tick loss interval on one diagnostic fork.
All future inputs already present in the exact snapshot; no new target/cue.
Two rolling complete states are an auditor buffer, never participant memory.
"""
import sys,shutil,importlib.util
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import ic_native_core as core
sp=importlib.util.spec_from_file_location('snapshot_only',SYSTEM/'capacidades/observador_causal_retrospectivo_01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
s=Store();start_hash=json.loads((EV/'C02_MAIN_171_RECORD_plus.json').read_text(encoding='utf8'))['result']['INSTRUMENTO']['snapshot_sha256']
end_hash=json.loads((EV/'C02_MAIN_171_CONTINUAR.json').read_text(encoding='utf8'))['result']['INSTRUMENTO']['snapshot_sha256']
start=next(p for p in(s.root/'estado/checkpoints').glob('E1_CICLO02_MAIN.T20927.*')if digest_file(p)==start_hash)
end=next(p for p in(s.root/'estado/checkpoints').glob('E1_CICLO02_MAIN.T21041.*')if digest_file(p)==end_hash)
name='C02_DIAG_220_ACCESO_TARDIO';fork('E1_CICLO02_MAIN',name,checkpoint=str(start.relative_to(s.root)))
atomic_json(EV/'DIAGNOSTICO_TARDIO_PROTOCOLO_220.json',{'start':str(start.relative_to(s.root)),'start_sha256':start_hash,'end_reference':str(end.relative_to(s.root)),'end_sha256':end_hash,
 'window':[20927,21041],'new_inputs':0,'protected_MAIN_advanced':False,'counterpart':'Already executed exact original continuation, not a new independent replicate',
 'following':'Ballistic tube from observed+X7 at[11,59,23] T20572; first departure terminates that simple lineage assertion',
 'logging':'Passive RAW/clocks/context and two full-state rolling buffers; no response-dependent inputs or timing changes. Full pre/post retained at first departure.'})
def test(a):
    frames=[];first=None;folder=EV/'BUFFER_DIAGNOSTICO_220';folder.mkdir(exist_ok=True)
    initial=physical(a.world,occupation=True)
    for t in range(20928,21042):
        buffer=folder/('A.deetsnap.gz'if t%2 else'B.deetsnap.gz');a.save(buffer)
        ic.advance(a,until=t,record=False);site=[(11+t-20572)%67,59,23];read=observe(a.world,site)
        expected=read['state']==1 and read['semantic']==1 and read['s_reg']==7 and read['direction']==[1,0,0]
        row={'tick':t,'expected_site':site,'read':read,'tube_continuation_observed':expected,
             'nonzero_context':[o for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)if(o:=observe(a.world,core.move(site,(x,y,z))))['raw']!='0']}
        if first is None and not expected:
            pre=EV/(name+'.PRE_FIRST_DEPARTURE.deetsnap.gz');post=EV/(name+'.POST_FIRST_DEPARTURE.deetsnap.gz');shutil.copy2(buffer,pre);a.save(post)
            first={'tick':t,'pre':{'path':str(pre.relative_to(ROOT)),'sha256':digest_file(pre)},'post':{'path':str(post.relative_to(ROOT)),'sha256':digest_file(post)},'row':row}
        frames.append(row)
    return{'initial':initial,'first_departure':first,'frames':frames,'final':physical(a.world,occupation=True),'new_inputs':0,
           'scope':'Observed local departure, not proof of global historical information erasure or a unique single-parent identity after collision.'}
run(name,name,test,{'spec':'DIAGNOSTICO_TARDIO_PROTOCOLO_220.json'})
actual=m.Snapshot(s.snapshot(s.record(name)));reference=m.Snapshot(end)
comparison={'RAW_equal':actual.raw==reference.raw,'clocks_equal':actual.clocks==reference.clocks,'interfaces_equal':actual.channels==reference.channels,
 'pending_equal':actual.pending==reference.pending,'receipts_equal':actual.receipts==reference.receipts,'next_event_equal':actual.next_event_id==reference.next_event_id,
 'next_sequence_equal':actual.next_sequence==reference.next_sequence,'no_new_inputs':True,'native_ticks_diagnostic_copy_only':114,
 'reference_original_sha256':end_hash,'actual_diagnostic_sha256':s.record(name)['snapshot_sha256']}
atomic_json(EV/'OBSERVADOR_DIAGNOSTICO_220_COMPARACION.json',comparison)
assert all(comparison[k]for k in('RAW_equal','clocks_equal','interfaces_equal','pending_equal','receipts_equal','next_event_equal','next_sequence_equal'))
print(json.dumps(comparison,ensure_ascii=False))
