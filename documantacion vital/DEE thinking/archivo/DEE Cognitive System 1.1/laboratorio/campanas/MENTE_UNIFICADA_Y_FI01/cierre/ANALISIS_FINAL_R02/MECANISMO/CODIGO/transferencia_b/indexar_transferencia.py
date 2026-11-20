"""Bounded local evidence/source/checkpoint index; no imports of DEE."""
import gzip,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import frontend_b01_r2 as f
def main():
    ev=f.OUT.parent;checkpoints=[];files=[];sources=[]
    for p in sorted(ev.rglob('*')):
        if not p.is_file()or p.name.startswith('INDICE'):continue
        files.append({'path':p.relative_to(ev).as_posix(),'bytes':p.stat().st_size,'sha256':f.digest(p),
          'analysis_inclusion':'omit_regenerable_intermediate'if p.name.startswith('RECALCULO')and p.name!='RECALCULO_TRANSFERENCIA_FINAL.json'else'include'})
        if not p.name.endswith('.json.gz'):continue
        o=json.loads(gzip.decompress(p.read_bytes()));ins=o.get('INSTRUMENTO')
        if ins is None:continue
        matches=list((f.SYSTEM/'estado/checkpoints').glob(ins['life_id']+'.T'+str(ins['tick'])+'.*.deetsnap.gz'))
        exact=[q for q in matches if f.digest(q)==ins['snapshot_sha256']]
        if len(exact)!=1:raise ValueError('Missing exact complete original operational checkpoint '+p.name)
        q=exact[0];checkpoints.append({'primary':p.relative_to(ev).as_posix(),'life':ins['life_id'],'tick':ins['tick'],'snapshot_path':str(q),
          'snapshot_sha256':f.digest(q),'snapshot_bytes':q.stat().st_size,'analysis_inclusion':False,'reason':'Complete operational state remains locally; analysis export is not a continuity backup.'})
    for p in sorted(HERE.glob('*')):
        if p.is_file():sources.append({'file':p.name,'path':str(p),'bytes':p.stat().st_size,'sha256':f.digest(p)})
    f.dump(ev/'INDICE_TRANSFERENCIA_FINAL.json',{'schema':'MUFI01.BT.final_evidence_index.v1','source_closed_A':{'path':str(f.SYSTEM/f.CUT),'sha256':f.EXPECTED,'unchanged':f.digest(f.SYSTEM/f.CUT)==f.EXPECTED},
      'evidence':files,'sources':sources,'complete_snapshots_local_only':checkpoints,
      'scope':'Includes all successful/negative/control primaries, two zero-tick recorded instrument errors, exact full-array lossless export and regenerated artifact disclosure. Does not duplicate motor or whole operational states. No new DEE tick.'})
    print(json.dumps({'evidence_files':len(files),'evidence_bytes':sum(x['bytes']for x in files),'source_files':len(sources),'local_complete_snapshots':len(checkpoints),
      'index_sha256':f.digest(ev/'INDICE_TRANSFERENCIA_FINAL.json'),'recalc_sha256':f.digest(HERE/'recalcular_transferencia.py'),'reference_sha256':f.digest(ev/'RECALCULO_TRANSFERENCIA_FINAL.json')}))
if __name__=='__main__':main()
