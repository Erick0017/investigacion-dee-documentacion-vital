"""One additional prospectively frozen raw-scale reserve.

V2FRONTERA3 duplicatedFRONTERA1 through a generator period. Both remain as
age repetition; this extra distinct raw sequence is not substituted for them.
Only positive inputs shift by1; the unchanged external law still has to act.
"""
from pathlib import Path
import gzip,json,os,sys,time
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(HERE))
from app.lives import Store
from app.native_tools import digest_file,atomic_json
from validacion_final_r10 import TIGHT,run
from piloto_sensorial_r10 import LIFE
from serie_cuatro_r05 import ram
FRAMES=[[v+1 for v in row]for row in TIGHT['FRONTERA3']]
def main():
    dest=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/capacidad/R10_V2_RESERVA_ESCALA_NUEVA.json.gz'
    if dest.exists():raise FileExistsError(dest)
    seal=HERE/'PROTOCOLO_R10_ESCALA_EXTRA.json'
    if not seal.exists():atomic_json(seal,{'raw_frames':FRAMES,'reference':4,'unchanged_reader':True,'purpose':'Third distinct raw input set; retain duplicate V2FRONTERA3 as an age repeat. No target enters participant.'})
    files=[Path(__file__),HERE/'validacion_final_r10.py',HERE/'sensorial_r10.py',HERE/'piloto_sensorial_r10.py',ROOT/'sistema/capacidades/ente_evolucion_02_core.py']
    archive=HERE/'revisiones/R10_EXTRA';archive.mkdir(parents=True,exist_ok=True)
    for f in files:
        t=archive/f.name
        if t.exists()and digest_file(t)!=digest_file(f):raise ValueError('Source changed')
        if not t.exists():t.write_bytes(f.read_bytes())
    store=Store();beg=time.monotonic();r=store.mutate(LIFE,'R10_V2_DISTINCT_RAW_SCALE_RESERVE',lambda a:run(a,FRAMES,'real'),details={'prospective_extra':FRAMES,'not_a_replacement_for_duplicate':True})
    rec=store.record(LIFE);out={'life_id':LIFE,'case':'ESCALA_NUEVA','sources':{str(f):digest_file(f)for f in files},'elapsed_seconds':time.monotonic()-beg,'ram':ram(),
      'snapshot':rec['snapshot'],'snapshot_sha256':rec['snapshot_sha256'],'snapshot_bytes':rec['storage']['encoded_bytes'],'extra_protocol_sha256':digest_file(seal),'result':r}
    with gzip.open(dest,'wt',encoding='utf8',compresslevel=6)as f:json.dump(out,f,ensure_ascii=False,allow_nan=False)
    print(json.dumps({'path':str(dest),'tick':rec['physical']['tick'],'rows':[{'v':q['values'],'cmd':q['native']['formed_native_command'],'ok':q['native']['job_completed'],
      'own':[v['s_reg']for v in q['native']['after']['own']],'statuses':[v['receipt']['status']for v in q['input_receipts']]}for q in r['result']['rows']]},ensure_ascii=False))
if __name__=='__main__':main()
