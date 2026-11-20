"""Index only already-produced B06/B07/phase records; no native imports."""
import gzip,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parents[2]
EVIDENCE=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=EVIDENCE/'INDICE_B06_B07_CERRADO.json'
    if out.exists():raise FileExistsError(out)
    primaries=[];snapshots={};fields=[]
    folders=['B06_CADENCE_NOISE_R1','B07_FRESH_N67_N101_R1','B07_CADENCE_N67_N101_R2','B04_PHASE_PLUS6_R2']
    for folder in folders:
        for p in sorted((EVIDENCE/folder).glob('*.json.gz')):
            x=json.loads(gzip.decompress(p.read_bytes()));r=x.get('result',x);life=r.get('life',x.get('INSTRUMENTO',{}).get('life_id'))
            refs=list(r.get('snapshots',[]))
            if r.get('all_pending_snapshot'):refs.append(r['all_pending_snapshot'])
            i=x.get('INSTRUMENTO')
            if i:
                wanted=i['snapshot_sha256'];found=[q for q in(ROOT/'sistema/estado/checkpoints').glob(life+'.T'+str(i['tick'])+'.*.deetsnap.gz')if sha(q)==wanted]
                if len(found)!=1:raise ValueError('Complete life snapshot missing: '+str(p))
                refs.append({'path':str(found[0]),'sha256':wanted,'tick':i['tick']})
            for record in refs:
                q=Path(record['path']);h=sha(q)
                if h!=record['sha256']:raise ValueError('Complete source changed: '+str(q))
                snapshots[h]={'path':q.relative_to(ROOT).as_posix(),'sha256':h,'bytes':q.stat().st_size,
                  'life':life,'tick':record['tick'],'scope':'Complete local world, not included by default in analysis ZIP.'}
            primaries.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,
              'life':life,'complete_snapshot_sha256':[q['sha256']for q in refs]})
    for p in sorted((EVIDENCE/'B06_CADENCE_NOISE_R1/CAMPOS_COMPLETOS_0_TICKS').glob('*')):
        if p.is_file():fields.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,
          'scope':'Exact exported fields/decoder guidance; NOT full operative world.'})
    sources=[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(HERE.glob('*'))if p.is_file()and p.suffix in('.py','.md')]
    obj={'schema':'FI01.B06_B07.closed_evidence_index.v1','native_ticks':0,'primary_count':len(primaries),
      'primaries':primaries,'complete_local_snapshots':list(snapshots.values()),'exported_fields':fields,'exact_sources':sources,
      'omissions':'No engine/WHL/historicalZIP included. Complete snapshots remain local unless explicitly selected. B06passive17038is a measured count without full snapshot; fullfinal17427is afterold6panel.'}
    out.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'primaries':len(primaries),'snapshots':len(snapshots),'fields':len(fields),'out':str(out),'sha256':sha(out)}))
if __name__=='__main__':main()
