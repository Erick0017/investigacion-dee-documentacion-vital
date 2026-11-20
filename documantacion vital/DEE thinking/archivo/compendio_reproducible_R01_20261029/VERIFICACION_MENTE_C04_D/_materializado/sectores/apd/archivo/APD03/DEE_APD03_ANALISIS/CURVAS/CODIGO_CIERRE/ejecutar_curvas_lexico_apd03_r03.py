"""R03 documentary-guard correction: use the existing prepared R02 prefix.

No old14/p0 repetition. Exact canonical complete bytes and physical fields
are checked before branch teaching. In-memory metadata before/after official
save is inventoried to distinguish persistence bookkeeping from Native ticks.
"""
import argparse
import gc
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import time


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
    with path.open('xb')as stream:stream.write(gzip.compress(data,mtime=0)if path.suffix=='.gz'else data)


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj


def metadata(adapter):return dict(adapter.world.runtime.snapshot_metadata_entries)


def inventory(values):
    canonical=json.dumps(values,sort_keys=True,separators=(',',':')).encode('utf8')
    return {'all_metadata_sha256':hashlib.sha256(canonical).hexdigest(),
        'entries':[{'key':k,'UTF8_bytes':len(v.encode('utf8')),'sha256':hashlib.sha256(v.encode('utf8')).hexdigest()}
            for k,v in sorted(values.items())]}


def main():
    began=time.monotonic();deadline=began+1800
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--system',required=True,type=Path)
    parser.add_argument('--prefix',required=True,type=Path)
    parser.add_argument('--expected-prefix-sha256',required=True)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--root-go',required=True,choices=['APD03_LEXICAL_CURVE_AUX_R03_PREFIX_ONLY'])
    args=parser.parse_args()
    if os.environ.get('OMP_NUM_THREADS')!='1':raise ValueError('OMP_NUM_THREADS=1 required before Native imports')
    if args.out.exists():raise FileExistsError('Preserve previous attempts; new output directory required')
    if sha(args.prefix)!=args.expected_prefix_sha256:raise ValueError('Exact existing R02 prepared prefix required')
    args.out.mkdir(parents=True)
    sys.path.insert(0,str(args.system.resolve()))
    from app.lives import load_adapter
    from app.native_tools import physical
    from app.process_control import protect_current,current_resources
    from capacidades import lexico_apd02_01 as prior
    from capacidades import mente_acumulativa_r02 as ma
    from capacidades import mente_unificada_01 as mu
    protect_current(output=args.out/'RECURSOS.json',memory_limit=512*1024*1024)
    here=Path(__file__).resolve().parent
    curve=load(here/'protocolo_curvas_lexico_apd03_r02.py','curve_r03')
    lexical=curve.lexical_module()
    recalc=load(here/'recalcular_curvas_lexico_apd03_r01.py','recalc_r03')
    plan=curve.plan();plan.update(existing_prefix_sha256=sha(args.prefix),
        old14_and_preparation_repeated=False,budget_seconds=1800,
        equality_contract='Exact encoded and decoded complete snapshot bytes + physical fields + common loaded metadata inventories; no branch-specific experience before the guard')
    paths=[Path(__file__),Path(curve.__file__),Path(lexical.__file__),Path(recalc.__file__),
        Path(prior.__file__),Path(ma.__file__),Path(mu.__file__),
        args.system/'app/lives.py',args.system/'app/native_tools.py',args.system/'app/process_control.py']
    for obj in list(sys.modules.values()):
        path=getattr(obj,'__file__',None)
        if path:
            path=Path(path)
            if path.suffix=='.py'and path.is_file()and path.resolve().is_relative_to(args.system.resolve()):paths.append(path)
    sources=[]
    for index,path in enumerate(dict.fromkeys(paths)):
        target=args.out/'CODIGO_EJECUTADO'/(str(index).zfill(3)+'_'+path.name)
        target.parent.mkdir(exist_ok=True);shutil.copyfile(path,target)
        sources.append({'source':str(path),'file':target.relative_to(args.out).as_posix(),
            'bytes':target.stat().st_size,'sha256':sha(target)})
    encoded=args.prefix.read_bytes();decoded=gzip.decompress(encoded)
    old_witness=json.loads(args.prefix.with_name('PREFIJO_TESTIGO.json').read_bytes())
    emit(args.out/'ANTES_DEL_PRIMER_TICK.json',{'plan':plan,'sources':sources,
        'prefix':str(args.prefix),'prefix_encoded_sha256':sha(args.prefix),
        'prefix_decoded_sha256':hashlib.sha256(decoded).hexdigest(),'old_prefix_witness':old_witness,
        'root_go':args.root_go,'scope':'Physical diagnostic branches only; no paired service, original or MAIN mutation'})
    class DeadlineAdapter:
        def __init__(self,adapter):self._adapter=adapter;self.world=adapter.world
        @property
        def tick(self):return self._adapter.tick
        def save(self,path):return self._adapter.save(path)
        def run_until(self,tick):
            while self.tick<tick:
                if time.monotonic()>=deadline:raise TimeoutError('Frozen1800second limit reached; preserve actual future')
                self._adapter.run_until(min(tick,self.tick+67))
    branches=[];common=None;stopped=None
    for index,arm in enumerate(plan['arms']):
        if deadline-time.monotonic()<30:
            stopped='Wall guard before next branch';break
        folder=args.out/('ARM_'+str(index)+'_'+arm['history']+'_'+str(arm['B_sign_auditor']))
        folder.mkdir();base=None;adapter=None
        try:
            base=load_adapter('fisica_directa',args.prefix);adapter=DeadlineAdapter(base)
            before_values=metadata(adapter);before_inventory=inventory(before_values);physical_before=physical(adapter.world)
            adapter.save(folder/'ANTES_COMPLETO.deetsnap.gz')
            after_values=metadata(adapter);after_inventory=inventory(after_values);physical_after=physical(adapter.world)
            branch_encoded=(folder/'ANTES_COMPLETO.deetsnap.gz').read_bytes();branch_decoded=gzip.decompress(branch_encoded)
            changed=[{'key':key,'before_present':key in before_values,'after_present':key in after_values,
                'before_sha256':None if key not in before_values else hashlib.sha256(before_values[key].encode('utf8')).hexdigest(),
                'after_sha256':None if key not in after_values else hashlib.sha256(after_values[key].encode('utf8')).hexdigest()}
                for key in sorted(set(before_values)|set(after_values))if before_values.get(key)!=after_values.get(key)]
            witness={'tick':int(adapter.tick),'physical':physical_before,
                'before_official_save_metadata':before_inventory,'after_official_save_metadata':after_inventory,
                'official_save_changed_metadata_keys':changed,
                'full_encoded_byte_identical':branch_encoded==encoded,
                'full_decoded_byte_identical':branch_decoded==decoded,
                'save_preserved_physical':physical_before==physical_after}
            emit(folder/'IGUALDAD_INICIAL.json',witness)
            if index==0:
                emit(folder/'METADATOS_RUNTIME_ANTES_SAVE.json.gz',before_values)
                emit(folder/'METADATOS_RUNTIME_DESPUES_SAVE.json.gz',after_values)
            if not(witness['full_encoded_byte_identical']and witness['full_decoded_byte_identical']and witness['save_preserved_physical']and physical_before==old_witness['physical']):
                raise ValueError('Complete serialized state/physical inequality; do not proceed')
            if common is None:common=witness
            elif witness!=common:raise ValueError('The six loaded runtimes do not have identical metadata/complete initial state')
            event_count=[0]
            def record_event(kind,data):
                emit(folder/'PASOS'/(str(event_count[0]).zfill(3)+'_'+kind+'.json.gz'),
                    {'kind':kind,'index':event_count[0],'tick_after_completed_step':int(adapter.tick),'primary':data})
                event_count[0]+=1
            row=curve.run_arm(adapter,history=arm['history'],b_sign=arm['B_sign_auditor'],
                life_identity={'kind':'diagnostic_physical_branch','label':folder.name,
                    'parent_complete_snapshot_sha256':sha(args.prefix),'parent_tick':int(adapter.tick)},
                detailed=True,on_event=record_event)
            emit(folder/'PRIMARIO.json.gz',row)
            calculated=recalc.recalculate(row);emit(folder/'RECALCULO.json',calculated)
            adapter.save(folder/'FINAL_COMPLETO.deetsnap.gz')
            branches.append({'index':index,'arm':arm,'result':calculated,
                'primary':(folder/'PRIMARIO.json.gz').relative_to(args.out).as_posix(),
                'final_snapshot_sha256':sha(folder/'FINAL_COMPLETO.deetsnap.gz')})
            print(json.dumps({'index':index,'history':arm['history'],'B':arm['B_sign_auditor'],
                'criterion':calculated['first_criterion'],'old_same_valid4':calculated['old_same_valid_sign'],'tick':adapter.tick}),flush=True)
        except Exception as error:
            failure={'type':type(error).__name__,'detail':str(error),'physical':None if adapter is None else physical(adapter.world)}
            if adapter is not None:adapter.save(folder/'FUTURO_AL_FALLO_COMPLETO.deetsnap.gz')
            emit(folder/'FALLO.json',failure);branches.append({'index':index,'arm':arm,'failure':failure})
            if isinstance(error,TimeoutError):stopped='Frozen wall limit inside branch; partial future preserved'
        finally:
            del adapter,base;gc.collect()
        if stopped:break
    emit(args.out/'RESULTADOS.json',{'schema':'APD03.lexical_curve.executed.R03.documentary_guard',
        'plan':plan,'sources':sources,'branches':branches,'stopped':stopped,
        'common_loaded_full_state_witness':common,'elapsed_seconds':time.monotonic()-began,
        'resources':current_resources(),'scope':'At most six diagnostic branches sharing one once-prepared prefix; no result or memory merged into MAIN.'})
    return 0


if __name__=='__main__':raise SystemExit(main())
