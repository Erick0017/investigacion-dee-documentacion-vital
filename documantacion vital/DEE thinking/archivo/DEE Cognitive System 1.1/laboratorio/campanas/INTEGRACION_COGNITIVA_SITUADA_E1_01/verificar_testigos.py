"""Verify selected complete saved worlds with no engine or new native ticks."""
from pathlib import Path
import json,argparse,importlib.util,hashlib
def main():
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();root=a.package
    spec=importlib.util.spec_from_file_location('snapshot_reader',root/'CODIGO_Y_RECALCULO/snapshot_reader.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    index=json.loads((root/'TESTIGOS_ESTADO/INDICE_TESTIGOS.json').read_text(encoding='utf8'));summaries=[];collision=[];common=[]
    for row in index['witnesses']:
        path=root/row['member'];q=m.Snapshot(path);s=q.summary();assert s['encoded_sha256']==row['sha256']and s['tick']==row['tick']and s['N']==67 and s['checksum_valid'];s['member']=row['member'];s.pop('path',None);summaries.append(s)
        if 'AUTOPSY_MAIN_FIRST_LOSS' in path.name:collision.append({'tick':q.tick,'payload140_sites':[m.coord(i,q.N)for i,v in enumerate(q.raw)if (v>>32)&65535==140],'decisive_sites':[q.observation(p)for p in([19,19,50],[21,21,50],[20,20,50])]})
        if 'COMMON_ACTION' in path.name:common.append({'member':row['member'],'tick':q.tick,'native_quantity':q.observation([50,35,35]),'post_reference_hub':q.observation([49,36,35])})
    out={'native_ticks':0,'Runtime_instances':0,'checksum_and_field_verification':summaries,'main140_window':sorted(collision,key=lambda r:r['tick']),'common_future_native_fields':common,'scope':'Saved-state parser only. Exact entire raw/clock hashes and queues are available, not inferred from one port. Metadata is never executed. A signature count is not a unique-particle genealogy or global knowledge-erasure verdict.'};a.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'native_ticks':0,'saved_worlds_verified':len(summaries),'valid_full_checksums':sum(s['checksum_valid']for s in summaries)}))
if __name__=='__main__':main()
