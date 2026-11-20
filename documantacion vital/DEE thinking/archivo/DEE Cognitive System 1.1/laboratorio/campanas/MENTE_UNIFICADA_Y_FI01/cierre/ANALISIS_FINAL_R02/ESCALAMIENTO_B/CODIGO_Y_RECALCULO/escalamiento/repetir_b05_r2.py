"""Same-life raw-tree reuse after its actual first query and old-six panel.
No restore between episodes, no input overwrite, no re-teaching or repair.
"""
import argparse,gc,json,os
from pathlib import Path
from ensayar_arbol_b05_r1 import HERE,ROOT,SYSTEM,LAB,sha,dump,execute,native_imports,internal_A_close,memory_guard
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--level',type=int,choices=(8,128),required=True);args=ap.parse_args()
    OUT=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento'/('B05_REPEAT_R2_N'+str(args.level))
    SOURCE='FI01_B05_TREE_R1_N'+str(args.level)+'_single_first';TARGET='FI01_B05_N'+str(args.level)+'_REPEAT_R2'
    authorization=internal_A_close(LAB/'CIERRE_INTERNO_A.json');os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1');ni=native_imports()
    from capacidades import selector_acrecion_nativo as sel
    Store=ni[3];now=ni[5];s=Store();r=s.record(SOURCE);parent_snapshot=s.snapshot(r)
    dump(OUT/'PROTOCOLO.json',{'authorization':authorization,'before_first_native_tick':now(),'script_sha256':sha(__file__),
      'dependency_sha256':sha(HERE/'ensayar_arbol_b05_r1.py'),'source_life':SOURCE,'source_tick':r['physical']['tick'],'source_snapshot':str(parent_snapshot),'source_snapshot_sha256':sha(parent_snapshot),
      'new_fork':TARGET,'sequence':['zero','single_first','zero','single_first'],'all_raw_same_tick_each_frame':True,
      'between_frames':'Fixed2N passive plus explicit old-six panel, NO restore/erase. Same loaded world throughout4episodes, saved/loaded between them.',
      'scope':'Transport reuse and inherited reference use, not new threshold teaching, policy adaptation or independent replicas.'})
    s.fork(SOURCE,TARGET,kind='B05_CONTINUOUS_RAW_TREE_REUSE');gc.collect();memory_guard();rows=[]
    for i,label in enumerate(['zero','single_first','zero','single_first']):
        x=s.mutate(TARGET,'B05_CONTINUOUS_FRAME_R2',lambda a:execute(a,args.level,label,ni,sel,True),{'episode':i,'frozen_case':label,'script_sha256':sha(__file__)})
        dump(OUT/('episode_'+str(i)+'.json.gz'),x)
        row={'episode':i,'case':label,'choice':x['result']['reader']['choice'],'applied':sum(q['receipt']['status']=='applied'for q in x['result']['requests']),
          'requested':len(x['result']['requests']),'end_tick':x['physical']['tick'],'old_six':[q['reader']['formed_native_command']for q in x['result']['old_six_panel_after_2N']['rows']],
          'snapshot_sha256':x['INSTRUMENTO']['snapshot_sha256'],'output_sha256':sha(OUT/('episode_'+str(i)+'.json.gz'))}
        rows.append(row);print(json.dumps(row),flush=True);del x;gc.collect();memory_guard()
    dump(OUT/'RESUMEN.json',{'rows':rows,'source_snapshot_unchanged':sha(parent_snapshot)==r['snapshot_sha256'],'finished_utc':now(),'peak_process_bytes':memory_guard()})
if __name__=='__main__':main()
