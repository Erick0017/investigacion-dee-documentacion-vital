"""Supervised 3.5 CPC3 -> native4 replay comparison. Never product runtime code.

Only the isolated reference child imports the preserved CPC3 implementation.
States compare as full uint64 byte arrays, not terminal labels or file hashes.
"""
import argparse
from array import array
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import time
import zlib

def write(path,value):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(value,indent=2,default=str),encoding='utf-8');os.replace(q,p)

def state(world,path):
    rt=world.runtime
    raw=array('Q',rt.raw_copy()).tobytes();clock=array('Q',rt.clock_copy()).tobytes()
    data=struct.pack('<QQQ',rt.current_tick,rt.dimension,len(raw))+raw+clock
    Path(path).write_bytes(zlib.compress(data,9))
    return {'tick':rt.current_tick,'dimension':rt.dimension,'state_file':str(Path(path).name),
            'raw_sha256':hashlib.sha256(raw).hexdigest(),'clock_sha256':hashlib.sha256(clock).hexdigest(),
            'full_array_comparison_available':True}

def receipt(r):
    if isinstance(r,dict):return {k:r.get(k) for k in ('id','status','requested_tick','effective_tick','reason')}
    return {'id':r.id,'status':str(r.status),'requested_tick':r.requested_tick,'effective_tick':r.effective_tick,'reason':r.reason}

def current(e):
    x=e.observe()
    return {k:x.get(k) for k in ('tick','delta','centers_available','reader_available','supports_intact','axis_projection','physical_output','a','b','write_gates')}

def worker(a):
    import dee_thinking as d
    import dee_thinking._native as native
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    scratch=tempfile.TemporaryDirectory(prefix='dt40-parity-')
    scratch_path=Path(scratch.name)
    reference=a.worker=='reference'
    if reference:
        sys.path.insert(0,str(Path(a.root)/'evidence'/'CPC3'/'src'))
        from core.entity import Entity
        from core.comparison_entity import CentralComparisonEntity
        from lenguaje.association import AssociationSession,composition_world,experience_composition,query_composition
        def entity(initial=False,change=80,profile='continuity'):
            return (Entity if profile=='continuity' else CentralComparisonEntity).create(initial_open=initial,change_tick=change)
        def save(e,p):
            q=scratch_path/p.name;e.save(str(q));p.write_bytes(q.read_bytes())
        def load(p,profile='continuity'):return (Entity if profile=='continuity' else CentralComparisonEntity).load(str(scratch_path/p.name))
    else:
        def entity(initial=False,change=80,profile='continuity'):
            p=d.CognitiveParameters();p.seed_path=d.reference_seed_path();p.initial_open=initial;p.change_tick=change;p.profile=profile
            return d.CognitiveSession.create(p)
        def save(e,p):
            q=scratch_path/p.name;e.save_snapshot(str(q));p.write_bytes(q.read_bytes())
        def load(p,profile='continuity'):return d.CognitiveSession.load_snapshot(str(scratch_path/p.name))
    captures={};operations={};started=time.monotonic()
    def capture(name,e):
        x=state(e.world,out/(name+'.state.zlib'));x['observation']=current(e);x['receipts']=[receipt(r) for r in e.world.runtime.receipts]
        captures[name]=x
    e=entity();capture('continuity_T32',e)
    operations['initial_sense']=e.sense();capture('continuity_T34',e)
    operations['prediction_T37']=e.predict();capture('continuity_T37',e)
    save(e,out/'continuity_pending.deetsnap');restored=load(out/'continuity_pending.deetsnap')
    capture('continuity_loaded_T37',restored)
    for t in (163,292,554,812,945):
        row=e.sense();capture('continuity_T'+str(e.tick),e);operations['sense_'+str(t)]=row
        restored.sense()
        if state(e.world,out/'direct_tmp.state.zlib')!=state(restored.world,out/'loaded_tmp.state.zlib'):
            # Compare physical arrays rather than the intentionally different filenames.
            direct=zlib.decompress((out/'direct_tmp.state.zlib').read_bytes());again=zlib.decompress((out/'loaded_tmp.state.zlib').read_bytes())
            if direct!=again:raise AssertionError('save-load changed native future')
    e.advance(1032-e.tick);capture('continuity_T1032',e)
    # Fixed finite reference controls differ in histories and current consequence.
    for initial in (False,True):
        for change in (None,80):
            label='comparison_'+str(int(initial))+'_'+('stable' if change is None else 'changed')
            c=entity(initial,change,'comparison');c.sense();p=c.predict();capture(label+'_T37',c)
            save(c,out/(label+'_pending.deetsnap'));c2=load(out/(label+'_pending.deetsnap'),'comparison')
            result=c.compare();result2=c2.compare();capture(label+'_T84',c);capture(label+'_loaded_T84',c2)
            decoder=result['comparison_decoder'];operations[label]={'prediction':p['prediction_set'],'marker':decoder,'status':result['status']}
            if zlib.decompress((out/(label+'_T84.state.zlib')).read_bytes())!=zlib.decompress((out/(label+'_loaded_T84.state.zlib')).read_bytes()):raise AssertionError('comparison pending save/load mismatch')
            if c.predict()['status']!='OUTSIDE_FORECAST_DOMAIN':raise AssertionError('comparison marker reused as a forecast')
    if reference:
        assoc=AssociationSession.create();assoc.train((7,11));association_result=assoc.query_simultaneous(13)
        w=composition_world(2);experience_composition(w,[(3,9),(3,11)]);composition_result=query_composition(w,13)
    else:
        assoc=d.NativeAssociationSession.create();assoc.train([7,11]);association_result=assoc.query_panel(13)
        w=d.create_learnable_cascade(2);d.experience_composition(w,[(3,9),(3,11)]);composition_result=d.query_composition(w,13)
    captures['association_T11']=state(assoc.world,out/'association_T11.state.zlib')
    captures['composition_T16']=state(w,out/'composition_T16.state.zlib')
    operations['association']=association_result;operations['composition']=composition_result
    write(out/'RESULTS.json',{'worker':a.worker,'python':sys.executable,'module':d.__file__,
          'native_module':native.__file__,'native_binary_sha256':hashlib.sha256(Path(native.__file__).read_bytes()).hexdigest(),
          'version':d.__version__,'captures':captures,'operations':operations,'elapsed_seconds':time.monotonic()-started})

def compare(a):
    root=Path(a.root).resolve();spec=importlib.util.spec_from_file_location('supervise40',root/'supervise40.py');sup=importlib.util.module_from_spec(spec);spec.loader.exec_module(sup)
    output=Path(a.output).resolve();output.mkdir(parents=True,exist_ok=True)
    for kind,python in [('reference',a.python_reference),('native',a.python_new)]:
        dest=output/kind
        if (dest/'RESULTS.json').exists():continue
        argv=[python,'-I','-B',str(Path(__file__).resolve()),'--root',str(root),'--worker',kind,'--output',str(dest)]
        job=sup.run(root,'cognitive_parity_'+kind+'_'+str(int(time.time())),argv,timeout=480,cwd=str(output))
        if job['exit_code']!=0:raise RuntimeError('parity worker failed: '+kind+' '+str(job))
    ref=json.loads((output/'reference'/'RESULTS.json').read_text(encoding='utf-8'))
    new=json.loads((output/'native'/'RESULTS.json').read_text(encoding='utf-8'))
    rows=[]
    for key,x in ref['captures'].items():
        y=new['captures'][key];bx=zlib.decompress((output/'reference'/x['state_file']).read_bytes());by=zlib.decompress((output/'native'/y['state_file']).read_bytes())
        row={'capture':key,'full_raw_clock_tick_equal':bx==by,'reference_sha256':hashlib.sha256(bx).hexdigest(),'native_sha256':hashlib.sha256(by).hexdigest()}
        if 'receipts' in x:row['receipts_equal']=x['receipts']==y['receipts']
        if 'observation' in x:
            fields={}
            for f in ('tick','delta','centers_available','reader_available','supports_intact','axis_projection','a','b','write_gates'):
                fields[f]=x['observation'][f]==y['observation'][f]
            # native4 supplies an additional RAW alias. Compare physical fields explicitly.
            fields['physical_output']=all(x['observation']['physical_output'][f]==y['observation']['physical_output'][f] for f in ('tick','site','raw','clock','state','s_reg','semantic','direction','active'))
            for f in ('a','b'):
                fields[f]=all(x['observation'][f][v]==y['observation'][f][v] for v in ('tick','site','raw','clock','state','s_reg','semantic','direction','active'))
            row['readout_fields_equal']=fields
        rows.append(row)
    passed=all(r['full_raw_clock_tick_equal'] and r.get('receipts_equal',True) and all(r.get('readout_fields_equal',{}).values()) for r in rows)
    result={'technical_equality':passed,'reference_version':ref['version'],'new_version':new['version'],'captures':rows,
            'scope':'one CPC3 MAIN T32->T1032, four physical comparison episodes, acquired mobile relations and online cascade; not independent scientific replications',
            'modalities':{'reference_import':'TEST_ONLY_CPC3_3.5','native_product':'COMPILED_4.0_PUBLIC_API'},'reference_elapsed':ref['elapsed_seconds'],'native_elapsed':new['elapsed_seconds']}
    write(output/'COMPARISON.json',result)
    if not passed:raise AssertionError('native cognitive parity mismatch; details retained')
    print(json.dumps(result))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--output',required=True)
    p.add_argument('--python-reference');p.add_argument('--python-new');p.add_argument('--worker',choices=['reference','native'])
    a=p.parse_args();worker(a) if a.worker else compare(a)
