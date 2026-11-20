"""Read-only extraction of complete RAW/clocks after the worker contrast.

No Runtime, native import, tick or restoration. Sparse encoding preserves every
uint64 using a declared clock default plus all exceptions, not an occupied ROI.
"""
import argparse,gzip,hashlib,importlib.util,json,shutil
from collections import Counter
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fixture',type=Path,required=True);p.add_argument('--evidencia',type=Path,required=True);a=p.parse_args()
    root=a.fixture/'sistema';out=a.evidencia;spec=importlib.util.spec_from_file_location('external_observer',root/'capacidades/observador_causal_retrospectivo_01.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    frames={};arms=[]
    for label in('CUT','SHAM'):
        rec=json.loads((root/'estado/vidas'/('MU_WORKER_'+label)/'VIDA.json').read_bytes());s=m.Snapshot(root/rec['snapshot']);summary=s.summary()
        if summary['encoded_sha256']!=rec['snapshot_sha256']:raise ValueError('Snapshot pointer changed')
        key=summary['RAW_sha256']+'_'+summary['clocks_sha256']
        if key not in frames:
            default=Counter(s.clocks).most_common(1)[0][0]
            frames[key]={'N':s.N,'tick':s.tick,'RAW_sha256':summary['RAW_sha256'],'clocks_sha256':summary['clocks_sha256'],
                'raw_nonzero':[[i,str(v)]for i,v in enumerate(s.raw)if v],
                'clock_default':str(default),'clock_exceptions':[[i,str(v)]for i,v in enumerate(s.clocks)if v!=default]}
        arms.append({'label':label,'frame_key':key,'source_snapshot':str(root/rec['snapshot']),'snapshot_sha256':s.encoded_sha256,
            'checksum_valid':s.checksum_valid,'physical':rec['physical'],'scope':'Complete physical RAW/clocks only; different receipts, metadata, external outcome and identities are NOT claimed identical.'})
    result={'schema':'DEE.unified.worker_interrupt_complete_arrays.v1','frames':frames,'arms':arms,'native_ticks':0,
        'scope':'Read-only complete-field extraction from actual final diagnostic snapshots. Coincident physical arrays do not establish equality of complete causal/transport state.'}
    target=out/'ESTADOS_FINALES.json.gz'
    with gzip.GzipFile(filename=str(target),mode='wb',mtime=0)as f:f.write((json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    code=out/'codigo';code.mkdir(exist_ok=True)
    for rel in('gestionar.py','app/lives.py','app/native_tools.py','app/servicio_persistente.py','app/cola_local.py','app/importacion_emparejada.py','app/access_guard.py','capacidades/mente_unificada_01.py','capacidades/mente_acumulativa_r02.py','capacidades/selector_acrecion_nativo.py','capacidades/eo02_trabajador_local.py','capacidades/observador_causal_retrospectivo_01.py'):
        dest=code/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,dest)
    shutil.copyfile(a.fixture/'PREPARACION.json',out/'PREPARACION.json')
    print(json.dumps({'file':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'frames':len(frames),'complete_uint64':sum(2*f['N']**3 for f in frames.values()),'native_ticks':0}))


if __name__=='__main__':main()
