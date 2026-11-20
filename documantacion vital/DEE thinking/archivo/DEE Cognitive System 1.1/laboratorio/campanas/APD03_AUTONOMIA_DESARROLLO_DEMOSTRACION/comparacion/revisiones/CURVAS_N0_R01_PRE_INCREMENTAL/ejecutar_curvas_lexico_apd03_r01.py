"""Finite Native AUX curve, executable only after Root's explicit GO token.

One physical owner at a time; exact complete snapshot loads. These diagnostic
branches are not paired service continuations and their memories never merge
into MAIN. Prefix: old14 common uses -> complete-source preflight -> one P0
preparation -> exact saved prefix -> six declared branches.
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
    with path.open('xb')as stream:
        stream.write(gzip.compress(data,mtime=0)if path.suffix=='.gz'else data)


def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj)
    return obj


def main():
    began=time.monotonic();deadline=began+1800
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--system',required=True,type=Path)
    parser.add_argument('--parent-snapshot',required=True,type=Path)
    parser.add_argument('--expected-parent-sha256',required=True)
    parser.add_argument('--expected-parent-tick',required=True,type=int)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--root-go',required=True,choices=['APD03_LEXICAL_CURVE_AUX_R01_ONLY'])
    args=parser.parse_args()
    if os.environ.get('OMP_NUM_THREADS')!='1':
        raise ValueError('OMP_NUM_THREADS=1 is required before any Native import')
    if args.out.exists():raise FileExistsError('New evidence directory required; no overwritten attempt')
    if sha(args.parent_snapshot)!=args.expected_parent_sha256:
        raise ValueError('Exact full physical parent differs; no alternate snapshot fallback')
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
    curve=module(here/'protocolo_curvas_lexico_apd03_r01.py','apd03_curve_runner')
    lexical=curve.lexical_module()
    recalculation=module(here/'recalcular_curvas_lexico_apd03_r01.py','apd03_curve_recalculation')
    plan=curve.plan();plan['budget_seconds']=1800;plan['maximum_simultaneous_Native_owners']=1
    plan['memory_limit_bytes']=512*1024*1024;plan['OMP_NUM_THREADS_required']='1'
    sources=[]
    paths=[Path(__file__),Path(curve.__file__),Path(lexical.__file__),Path(recalculation.__file__),
           Path(prior.__file__),Path(ma.__file__),Path(mu.__file__),
           args.system/'app/lives.py',args.system/'app/native_tools.py',args.system/'app/process_control.py']
    # Preserve bytes of modules already imported by the actual owner's load
    # path, rather than only hashes of source files that might later change.
    for loaded in list(sys.modules.values()):
        candidate=getattr(loaded,'__file__',None)
        if candidate:
            candidate=Path(candidate)
            if candidate.suffix=='.py'and candidate.is_file()and candidate.resolve().is_relative_to(args.system.resolve()):
                paths.append(candidate)
    for index,path in enumerate(dict.fromkeys(paths)):
        target=args.out/'CODIGO_EJECUTADO'/(str(index).zfill(3)+'_'+path.name)
        target.parent.mkdir(exist_ok=True);shutil.copyfile(path,target)
        sources.append({'source':str(path),'file':target.relative_to(args.out).as_posix(),
            'bytes':target.stat().st_size,'sha256':sha(target)})
    emit(args.out/'ANTES_DEL_PRIMER_TICK.json',{'schema':'APD03.lexical_curve.prospective.R01',
        'plan':plan,'sources':sources,'root_go':args.root_go,
        'source_snapshot_sha256':sha(args.parent_snapshot),'source_snapshot':str(args.parent_snapshot),
        'scope':'Full physical AUX only, no service SQLite import or queue consumption; no MAIN writes',
        'resources':current_resources()})
    class DeadlineAdapter:
        def __init__(self,adapter):self._adapter=adapter;self.world=adapter.world
        @property
        def tick(self):return self._adapter.tick
        def save(self,path):return self._adapter.save(path)
        def run_until(self,tick):
            while self.tick<tick:
                if time.monotonic()>=deadline:
                    raise TimeoutError('Frozen1800second AUX budget reached; preserve partial future')
                self._adapter.run_until(min(tick,self.tick+67))
    prefix_path=args.out/'PREFIJO_COMPLETO.deetsnap.gz'
    old14=None;preparation=None;screen=None;branches=[];prefix_error=None;stopped=None
    base=None;adapter=None
    try:
        base=load_adapter('fisica_directa',args.parent_snapshot);adapter=DeadlineAdapter(base)
        if adapter.tick!=args.expected_parent_tick:raise ValueError('Exact parent tick differs')
        initial=physical(adapter.world);adapter.save(args.out/'PADRE_CARGADO_COMPLETO.deetsnap.gz')
        old14={'scope':'One common old14 material panel before new preparation, not repeated per branch',
               'rows':[{'form':form,'result':prior.query(adapter,form,detailed=True)}for form in prior.FORM_CODEC]}
        emit(args.out/'OLD14_PREFIJO_COMUN.json.gz',old14)
        screen=lexical.preflight(adapter);emit(args.out/'PREFLIGHT_COMPLETO.json',screen)
        if not screen['admissible']:
            stopped='Complete preflight rejected; no lexical installation or branches'
            adapter.save(args.out/'FUTURO_PREFLIGHT_RECHAZADO_COMPLETO.deetsnap.gz')
        else:
            preparation=lexical.prepare(adapter);emit(args.out/'PREPARACION_UNICA.json.gz',preparation)
            adapter.save(prefix_path)
            prefix_witness={'tick':int(adapter.tick),'physical':physical(adapter.world),
                'snapshot_sha256':sha(prefix_path),
                'all_snapshot_metadata_sha256':hashlib.sha256(json.dumps(dict(adapter.world.runtime.snapshot_metadata_entries),sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()}
            emit(args.out/'PREFIJO_TESTIGO.json',prefix_witness)
    except Exception as error:
        prefix_error={'type':type(error).__name__,'detail':str(error),
            'physical':None if adapter is None else physical(adapter.world)}
        if adapter is not None:adapter.save(args.out/'FUTURO_PREFIJO_AL_FALLO_COMPLETO.deetsnap.gz')
        emit(args.out/'FALLO_PREFIJO.json',prefix_error)
    finally:
        del adapter,base;gc.collect()
    if prefix_path.exists()and prefix_error is None:
        for index,arm in enumerate(plan['arms']):
            if deadline-time.monotonic()<30:
                stopped='Wall guard before next complete branch; remaining arms not executed';break
            folder=args.out/('ARM_'+str(index)+'_'+arm['history']+'_'+str(arm['B_sign_auditor']))
            folder.mkdir();base=None;adapter=None
            try:
                base=load_adapter('fisica_directa',prefix_path);adapter=DeadlineAdapter(base)
                witness={'tick':int(adapter.tick),'physical':physical(adapter.world),
                    'snapshot_sha256':sha(prefix_path),
                    'all_snapshot_metadata_sha256':hashlib.sha256(json.dumps(dict(adapter.world.runtime.snapshot_metadata_entries),sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()}
                if witness!=prefix_witness:raise ValueError('Branch did not load the exact common complete prefix')
                emit(folder/'IGUALDAD_INICIAL.json',witness)
                row=curve.run_arm(adapter,history=arm['history'],b_sign=arm['B_sign_auditor'],
                    life_identity={'kind':'diagnostic_physical_branch','label':folder.name,
                        'parent_complete_snapshot_sha256':sha(prefix_path),'parent_tick':prefix_witness['tick']},detailed=True)
                emit(folder/'PRIMARIO.json.gz',row)
                computed=recalculation.recalculate(row);emit(folder/'RECALCULO.json',computed)
                adapter.save(folder/'FINAL_COMPLETO.deetsnap.gz')
                branches.append({'index':index,'arm':arm,'final_snapshot_sha256':sha(folder/'FINAL_COMPLETO.deetsnap.gz'),
                    'result':computed,'primary':(folder/'PRIMARIO.json.gz').relative_to(args.out).as_posix()})
                print(json.dumps({'index':index,'history':arm['history'],'B':arm['B_sign_auditor'],
                    'criterion':computed['first_criterion'],'old_same_valid4':computed['old_same_valid_sign'],
                    'tick':adapter.tick}),flush=True)
            except Exception as error:
                failure={'type':type(error).__name__,'detail':str(error),
                    'physical':None if adapter is None else physical(adapter.world)}
                if adapter is not None:adapter.save(folder/'FUTURO_AL_FALLO_COMPLETO.deetsnap.gz')
                emit(folder/'FALLO.json',failure);branches.append({'index':index,'arm':arm,'failure':failure})
                if isinstance(error,TimeoutError):stopped='Frozen wall budget reached within branch; future preserved'
            finally:
                del adapter,base;gc.collect()
            if stopped:break
    emit(args.out/'RESULTADOS.json',{'schema':'APD03.lexical_curve.executed.R01','plan':plan,
        'sources':sources,'old14_common_panel':None if old14 is None else'OLD14_PREFIJO_COMUN.json.gz',
        'preflight_admissible':None if screen is None else screen['admissible'],
        'prefix_error':prefix_error,'branches':branches,'stopped':stopped,
        'elapsed_seconds':time.monotonic()-began,'resources':current_resources(),
        'scope':'Six finite related diagnostic branches at most, not independent learners; only4representative old forms tested per branch, no complete14retention claim. No result transferred to MAIN.'})
    return 0


if __name__=='__main__':raise SystemExit(main())
