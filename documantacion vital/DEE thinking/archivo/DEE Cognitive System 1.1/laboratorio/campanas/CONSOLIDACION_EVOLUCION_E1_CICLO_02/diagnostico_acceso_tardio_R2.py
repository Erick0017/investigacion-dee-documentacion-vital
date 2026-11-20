"""Continue the reached diagnostic state after save refused buffer overwrite.
No rewind. Immutable bounded112tick detailed snapshots replace the failed
two-file buffer. This is ONE decisive interval, not default dense telemetry.
"""
import sys,shutil,importlib.util
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import ic_native_core as core
sp=importlib.util.spec_from_file_location('snapshot_only',SYSTEM/'capacidades/observador_causal_retrospectivo_01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
s=Store();name='C02_DIAG_220_ACCESO_TARDIO';assert s.record(name)['physical']['tick']==20929
end_hash=json.loads((EV/'C02_MAIN_171_CONTINUAR.json').read_text(encoding='utf8'))['result']['INSTRUMENTO']['snapshot_sha256']
end=next(p for p in(s.root/'estado/checkpoints').glob('E1_CICLO02_MAIN.T21041.*')if digest_file(p)==end_hash)
atomic_json(EV/'DIAGNOSTICO_TARDIO_CONTINUACION_221.json',{'life':name,'resume_tick':20929,'original_end':end_hash,
 'previous_failure':'Immutable a.save correctly refused overwrite of diagnostic buffer at20929. Original failed attempt and both buffers remain.',
 'revised_recording':'One bounded112tick deep interval with unique immutable complete pre-states; not default per-tick campaign recording.',
 'new_inputs':0,'MAIN_advanced':False,'no_rewind':True})
def test(a):
    frames=[];first=None;folder=EV/'VENTANA_DIAGNOSTICA_221';folder.mkdir(exist_ok=True);initial=physical(a.world,occupation=True)
    pre_read=observe(a.world,[(11+a.tick-20572)%67,59,23])
    for t in range(20930,21042):
        pre=folder/('PRE_T'+str(t)+'.deetsnap.gz');a.save(pre)
        ic.advance(a,until=t,record=False);site=[(11+t-20572)%67,59,23];read=observe(a.world,site)
        expected=read['state']==1 and read['semantic']==1 and read['s_reg']==7 and read['direction']==[1,0,0]
        row={'tick':t,'expected_site':site,'read':read,'tube_continuation_observed':expected,
             'nonzero_context':[o for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)if(o:=observe(a.world,core.move(site,(x,y,z))))['raw']!='0']}
        if first is None and not expected:
            post=EV/(name+'.POST_FIRST_DEPARTURE.deetsnap.gz');a.save(post)
            first={'tick':t,'pre':{'path':str(pre.relative_to(ROOT)),'sha256':digest_file(pre)},'post':{'path':str(post.relative_to(ROOT)),'sha256':digest_file(post)},'row':row}
        frames.append(row)
    return{'initial':initial,'initial_tube':pre_read,'first_departure':first,'frames':frames,'final':physical(a.world,occupation=True),'new_inputs':0,
           'scope':'First departure ends the unbranched ballistic lineage; matching payload later is not a unique identity. Not whole-state information erasure.'}
run(name,'C02_DIAG_221_CONTINUACION',test,{'spec':'DIAGNOSTICO_TARDIO_CONTINUACION_221.json'})
actual=m.Snapshot(s.snapshot(s.record(name)));reference=m.Snapshot(end)
comparison={'RAW_equal':actual.raw==reference.raw,'clocks_equal':actual.clocks==reference.clocks,'interfaces_equal':actual.channels==reference.channels,
 'pending_equal':actual.pending==reference.pending,'receipts_equal':actual.receipts==reference.receipts,'next_event_equal':actual.next_event_id==reference.next_event_id,
 'next_sequence_equal':actual.next_sequence==reference.next_sequence,'no_new_inputs':True,'native_ticks_diagnostic_copy_only_total':114,
 'reference_original_sha256':end_hash,'actual_diagnostic_sha256':s.record(name)['snapshot_sha256']}
atomic_json(EV/'OBSERVADOR_DIAGNOSTICO_221_COMPARACION.json',comparison)
assert all(comparison[k]for k in('RAW_equal','clocks_equal','interfaces_equal','pending_equal','receipts_equal','next_event_equal','next_sequence_equal'))
print(json.dumps(comparison,ensure_ascii=False))
