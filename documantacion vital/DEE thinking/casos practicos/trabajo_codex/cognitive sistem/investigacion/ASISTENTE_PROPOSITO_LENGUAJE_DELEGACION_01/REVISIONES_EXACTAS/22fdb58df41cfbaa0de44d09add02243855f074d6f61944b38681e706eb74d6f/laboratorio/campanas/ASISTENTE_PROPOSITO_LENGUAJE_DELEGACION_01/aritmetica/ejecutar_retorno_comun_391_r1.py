"""APD01 finite native common-consequence contrasts, no policy or answer host."""
import argparse
import gc
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import time


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def emit(path,value):
    if path.exists():raise FileExistsError('Preserve primary '+str(path))
    b=json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2).encode('utf-8')+b'\n'
    path.write_bytes(gzip.compress(b,mtime=0)if path.suffix=='.gz'else b)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--system',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--parent',default='APD01_BASE_LEXICA');a=ap.parse_args()
    if a.out.exists():raise FileExistsError('New run only')
    a.out.mkdir(parents=True);sys.path.insert(0,str(a.system.resolve()))
    from app.lives import Store
    from app.native_tools import physical
    from app.process_control import protect_current
    from capacidades import mente_unificada_01 as mu
    from capacidades import mente_acumulativa_r02 as ma
    protect_current(output=a.out/'RECURSOS.json')
    here=Path(__file__).parent;source=here/'retorno_comun_391_candidato_r1.py'
    sp=importlib.util.spec_from_file_location('APD01_COMMON391_R1',source);module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module)
    protocol_path=here/'PROTOCOLO_RETORNO_COMUN_391_R1.json';protocol=json.loads(protocol_path.read_text(encoding='utf-8'))
    store=Store(a.system);parent=store.record(a.parent);archive=a.out/'CODIGO_EJECUTADO';archive.mkdir()
    sources=[]
    for n,p in enumerate([Path(__file__),source,protocol_path,a.system/'capacidades/mente_unificada_01.py',a.system/'capacidades/selector_acrecion_nativo.py']):
        target=archive/(str(n).zfill(2)+'_'+p.name);shutil.copyfile(p,target)
        sources.append({'source':str(p.resolve()),'archived':target.relative_to(a.out).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size})
    emit(a.out/'ANTES_DEL_PRIMER_TICK.json',{'protocol':protocol,'parent':parent,'sources':sources,'native_not_yet_started':True})
    start=time.monotonic();outcomes=[]
    for parity in('even','odd'):
        for arm in protocol['arms_per_parity']:
            if time.monotonic()-start>=protocol['budget_seconds']:
                outcomes.append({'parity':parity,'arm':arm,'not_executed':'Fixed300s budget'});continue
            name=parity+'_'+arm['label'];life='APD01_COST391_R1_'+name;folder=a.out/name;folder.mkdir()
            fork=store.fork(a.parent,life,kind='APD01_IDENTICAL_PREFIX_COMMON_COST391_CONTROL');emit(folder/'00_FORK.json.gz',fork)
            def run(owner):
                value={'before':physical(owner.world),'feedback':module.deliver(owner,arm['cost'],parity=parity,mode=arm['mode'])}
                owner.save(folder/'01_DESPUES_RETORNO_COMPLETO.deetsnap.gz')
                value['after_feedback']=physical(owner.world);owner.run_until(owner.tick+134)
                value['common_use']=mu.current(owner,21,detail=False)
                value['old_six']=[{'context':ctx,'result':ma.query(owner,ctx,detail=False)}for ctx in('alfa','beta','gamma','delta','epsilon','zeta')]
                value['final']=physical(owner.world,occupation=True)
                return value
            try:
                result=store.mutate(life,'APD01_COMMON_COST391_R1',run,{'arm':arm,'parity':parity,'protocol_sha256':sha(protocol_path)})
                emit(folder/'02_RESULTADO_COMPLETO.json.gz',result);v=result['result'];before=v['feedback']['references_before'];after=v['feedback']['references_after']
                row={'id':name,'life':life,'timing':v['feedback']['timing'],'reference_pre':[x['s_reg']for x in before],'reference_post':[x['s_reg']for x in after],
                     'feedback_choice':v['feedback']['reader']['choice'],'common21_choice':v['common_use']['reader']['choice'],
                     'old_six':[x['result']['reader']['formed_native_command']for x in v['old_six']], 'final_record':store.record(life)}
            except Exception as e:
                row={'id':name,'life':life,'error':{'type':type(e).__name__,'detail':str(e)},'reached':store.record(life),'no_rollback':True}
                emit(folder/'02_ERROR_CONSERVADO.json.gz',row)
            outcomes.append(row);gc.collect();print(json.dumps({k:v for k,v in row.items()if k not in('final_record','reached')},ensure_ascii=False),flush=True)
    emit(a.out/'RESULTADOS.json',{'schema':'APD01.common_cost391.actual_histories.v1','elapsed':time.monotonic()-start,'parent':parent,'outcomes':outcomes,
                                 'scope':'Prepared fixed common cost channel, not A/B credit assignment or general learned policy. Every actual future retained.'})
    return 0


if __name__=='__main__':raise SystemExit(main())
