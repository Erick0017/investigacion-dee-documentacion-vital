"""Index existing B05 primaries/code and full local checkpoints; zero DEE imports.
No scientific experiment, native tick, source modification or life continuation.
"""
import gzip,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parents[2]
EVIDENCE=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=EVIDENCE/'INDICE_B05_CERRADO.json'
    if out.exists():raise FileExistsError(out)
    primaries=[];snapshots={};source=[]
    for p in sorted(EVIDENCE.glob('B*/*.json.gz')):
        x=json.loads(gzip.decompress(p.read_bytes()))
        if 'INSTRUMENTO'not in x:continue
        i=x['INSTRUMENTO'];life=i['life_id'];tick=i['tick'];wanted=i['snapshot_sha256']
        found=[]
        for q in(ROOT/'sistema/estado/checkpoints').glob(life+'.T'+str(tick)+'.*.deetsnap.gz'):
            if sha(q)==wanted:found.append(q)
        if len(found)!=1:raise ValueError('Complete recorded checkpoint not uniquely found: '+str(p))
        q=found[0];snapshots[wanted]={'path':q.relative_to(ROOT).as_posix(),'bytes':q.stat().st_size,'sha256':wanted,'life':life,'tick':tick,
          'kind':'COMPLETE_LOCAL_OPERATIONAL_WORLD','included_in_analysis':'No: local continuation state, not replaced by primary extraction'}
        primaries.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'life':life,'tick':tick,'complete_snapshot_sha256':wanted})
        for ed in x.get('result',{}).get('diagnostic_edits',[]):
            if not ed.get('performed'):continue
            z=ed['pre_snapshot'];q=Path(z['path'])
            if sha(q)!=z['sha256']:raise ValueError('Diagnostic pre-cut checkpoint changed')
            snapshots[z['sha256']]={'path':q.relative_to(ROOT).as_posix(),'bytes':q.stat().st_size,'sha256':z['sha256'],'life':life,'tick':ed['tick'],
              'kind':'COMPLETE_DIAGNOSTIC_PRE_CUT_WORLD_NOT_CURRENT_LIFE_POINTER','included_in_analysis':'No: full local checkpoint; decisive RAW/context/clock and effect included in primary'}
    for p in sorted(HERE.glob('*')):
        if p.is_file()and p.suffix in('.py','.md','.json')or p.is_file()and p.name.endswith('.json.gz'):
            source.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),
              'role':'EXACT_SOURCE_OR_PROTOCOL; includes archived failed/replaced revisions, not all executed native.'})
    for p in[HERE.parent/'transferencia_b/frontend_b01_r2.py']:
        source.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'role':'FIXED_S_FRONTEND_SOURCE_USED_BY_B05'})
    obj={'schema':'FI01.B05.existing_evidence_index.v1','native_ticks':0,'primary_count':len(primaries),'primaries':primaries,
      'complete_local_snapshots':list(snapshots.values()),'sources_and_protocols':source,
      'scope':'B02/B03/B04 negatives, B05 raw-tree screen/reuse/individual relevance/history/cuts/shams. Analysis exports are not operational backups.',
      'omissions':'Original engine/WHL, historical campaign corpus and full local world snapshots are not copied into the analysis ZIP. All listed complete worlds remain local; index records exact hashes and locators. No unique failed primary is excluded by this index.'}
    out.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'out':str(out),'primaries':len(primaries),'complete_snapshots':len(snapshots),'bytes':out.stat().st_size,'sha256':sha(out)}))
if __name__=='__main__':main()
