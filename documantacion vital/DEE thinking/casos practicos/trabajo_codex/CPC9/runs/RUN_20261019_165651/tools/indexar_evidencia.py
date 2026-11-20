"""File-level data ledger: exact integers and explicit execution modalities.

Counts are containers, not independent scientific replicas. Source hashes
and original per-front ledgers remain the authority for life/fork identity.
"""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'revision/INDICE_EVIDENCIA.json');a=p.parse_args()
    rows=[];bad=[];exact=0;field_mismatches=[]
    def scan(v,path):
        nonlocal exact
        if isinstance(v,dict):
            for k,x in v.items():
                if k.lower()in('raw','clock'):
                    if type(x)is int and 0<=x<2**64 or isinstance(x,str)and x.isdigit()and 0<=int(x)<2**64:exact+=1
                    else:bad.append({'locator':path+'/'+k,'type':type(x).__name__,'value':repr(x)[:100]})
                else:scan(x,path+'/'+k)
            if all(k in v for k in('raw','state','s_reg','direction','semantic')):
                x=int(v['raw']);nibbles=[(x>>s)&15 for s in(48,52,56)];direction=[y-16 if y>=8 else y for y in nibbles]
                if x&0xffffffff!=v['state']or(x>>32)&65535!=v['s_reg']or(x>>60)&15!=v['semantic']or direction!=v['direction']:
                    field_mismatches.append({'locator':path,'raw':v['raw']})
        elif isinstance(v,list):
            for i,x in enumerate(v):scan(x,path+'/'+str(i))
    for branch in('resultados','front_relations/resultados','front_semantics/resultados'):
        for path in sorted((ROOT/branch).rglob('*.json')):
            if path.name not in('MEDICIONES.json','MEASUREMENTS.json'):continue
            d=json.loads(path.read_text(encoding='utf8'));name=path.relative_to(ROOT).as_posix();scan(d,name)
            rows.append({'member':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,
              'schema':d.get('schema'),'case_id':d.get('case_id',path.parent.name),'status':d.get('status'),
              'declared_preparations':d.get('preparations'),'declared_continuations':d.get('continuations',d.get('restored_continuations')),
              'declared_forks':d.get('diagnostic_forks'),'last_tick':d.get('last_complete_tick'),
              'continuity_type':d.get('continuity_type'),'parent':d.get('parent',d.get('parent_snapshot_sha256')),
              'warning':'Container counts do not equal individuals/replicas; see modality, parent hashes and front reconciliation.'})
    report={'schema':'CPC9.primary.index.v1','engine_imported':False,'files':rows,'terminal_statuses':dict(Counter(r['status']for r in rows)),
       'exact_uint64_fields':exact,'invalid_exact_fields':bad,'unpacked_field_mismatches':field_mismatches,
       'field_formulas':{'state':'RAW & 0xffffffff','s_reg':'(RAW >>32)&65535','semantic':'(RAW >>60)&15','direction':'signed4-bit nibbles at48/52/56'},
       'scope':'Only primary measurement JSON containers. Technical command failures without Runtime are in jobs. Historical Core has an independent ledger; not added to MAIN.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'primary_containers':len(rows),'statuses':report['terminal_statuses'],'exact_uint64_fields':exact,'invalid':len(bad),'field_mismatches':len(field_mismatches)}))
    if bad or field_mismatches:raise SystemExit(2)
if __name__=='__main__':main()
