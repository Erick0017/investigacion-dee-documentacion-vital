"""Explicit4.0->4.5 checkpoint adapter check; no historical runner imports."""
from array import array
import argparse
import hashlib
import json
from pathlib import Path
import sys
import traceback


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def physical(world):
    r=world.runtime
    return {'tick':int(r.current_tick),
            'raw_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
            'clock_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}


def operative(world):
    r=world.runtime
    receipts=[{'id':int(x.id),'kind':str(x.kind),'status':str(x.status),
               'requested_tick':int(x.requested_tick),'effective_tick':None if x.effective_tick is None else int(x.effective_tick),
               'channels':list(x.channels),'reason':str(x.reason)} for x in r.receipts]
    return {'tick':int(r.current_tick),'dimension':int(r.dimension),'paused':bool(r.paused),
            'protocol_phase':str(r.protocol_phase),'channels':list(r.channel_names),'receipts':receipts,
            'protocols':[{'id':str(x.id),'completed':bool(x.completed),'next_index':int(x.next_index)} for x in world.protocols],
            'external_operations':list(world.external_operations)}


def main():
    p=argparse.ArgumentParser();p.add_argument('--reference',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    import dee_thinking as d
    from dee_thinking.consolidated import load_consolidated_session
    from dee_thinking.persistence import load_world_snapshot
    result={'schema':'DEE4.5.explicit-legacy-checkpoint-continuation.v1','source_sha256':sha(__file__),
            'python':sys.executable,'module':d.__file__,'version':d.__version__,'native_sha256':sha(d._native.__file__),
            'reference_directory':str(a.reference),'inputs':{},'checks':{},'panels':[]}
    try:
        assert d.__version__=='4.5.0'
        assert Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
        for name in ('sesion_demo.deetsnap.gz','sesion_continuada.deetsnap.gz','CONTINUATION.json'):
            result['inputs'][name]={'bytes':(a.reference/name).stat().st_size,'sha256':sha(a.reference/name)}
        original_before=dict(result['inputs'])
        base,_=load_world_snapshot(a.reference/'sesion_demo.deetsnap.gz')
        base_physical=physical(base);base_operative=operative(base)
        s=load_consolidated_session(a.reference/'sesion_demo.deetsnap.gz',allow_legacy=True)
        result['adapter']={'mode':'EXPLICIT_LEGACY_DESCRIPTOR_ATTACH_NO_REPREPARATION',
                           'initial_state_available':s.preparation.initial_state_available}
        result['checks']['load_physical_exact']=physical(s.world)==base_physical
        result['checks']['load_operative_exact_except_added_descriptor_metadata']=operative(s.world)==base_operative
        result['load_physical']=base_physical
        assert all(result['checks'].values())
        # Exactly the native inputs of the archived continuation event file:
        # three common queries335; double teacher revisionL03@402; three queries469.
        # No new exposure or answer is synthesized from the archived transcript.
        result['panels'].append(s.query(['L03','L04','L09'],335,payload=5))
        s.revise('L03',1,402,method='double_teacher')
        s.run_until(405)
        result['passive_after_revision']=s.observe('L03')
        result['panels'].append(s.query(['L03','L04','L09'],469,payload=5))
        expected,_=load_world_snapshot(a.reference/'sesion_continuada.deetsnap.gz')
        result['final_physical']=physical(s.world);result['expected_physical']=physical(expected)
        result['final_operative']=operative(s.world);result['expected_operative']=operative(expected)
        result['checks']['continued_RAW_clocks_tick_exact']=result['final_physical']==result['expected_physical']
        result['checks']['continued_operative_exact_except_added_metadata']=result['final_operative']==result['expected_operative']
        result['checks']['original_files_unchanged']=all(sha(a.reference/name)==v['sha256'] for name,v in original_before.items())
        result['pending_receipts_final']={'actual':sum(x['status']=='scheduled' for x in result['final_operative']['receipts']),
                                           'reference':sum(x['status']=='scheduled' for x in result['expected_operative']['receipts'])}
        result['queue_scope']='No pending future requests in either final checkpoint; direct queue internals are not a public binding.'
        result['metadata_scope']='Descriptor/session metadata is added explicitly; legacy metadata and scientific bytes are preserved. External facade request journal is not retroactively reconstructed.'
        result['historical_runner_imports']=[name for name in sys.modules if name in ('life','integrated','common','console','selective_native')]
        assert not result['historical_runner_imports']
        assert all(result['checks'].values())
        result['status']='PASS'
    except BaseException as error:
        result['status']='FAIL';result['error_type']=type(error).__name__;result['error']=str(error);result['traceback']=traceback.format_exc()
        raise
    finally:
        (a.out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':main()
