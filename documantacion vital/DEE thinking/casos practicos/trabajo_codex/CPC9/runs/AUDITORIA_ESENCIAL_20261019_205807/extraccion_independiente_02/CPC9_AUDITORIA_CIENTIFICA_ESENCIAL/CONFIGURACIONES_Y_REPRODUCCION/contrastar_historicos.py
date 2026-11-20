"""Case-bound comparison of recorded physical fingerprints, not old PASS flags."""
from pathlib import Path
from collections import defaultdict
import argparse,json,sys,re
sys.path.insert(0,str(Path(__file__).resolve().parent))
from codec import Reader
sys.stdout.reconfigure(encoding='utf8')
def physical(x):
    result=set()
    def visit(v):
        if isinstance(v,dict):
            raw=v.get('RAW_sha256',v.get('raw_sha256'));clock=v.get('clocks_sha256',v.get('clock_sha256'))
            if 'tick'in v and isinstance(raw,str)and isinstance(clock,str)and len(raw)==len(clock)==64:result.add((v['tick'],raw,clock))
            for k,w in v.items():
                if any(s in k.lower()for s in('expected','prediction','predicted','target')):continue
                visit(w)
        elif isinstance(v,list):
            for w in v:visit(w)
    visit(x);return result
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=Reader(a.root/'EVIDENCIA_PRIMARIA_ESENCIAL');bysha=defaultdict(list);fresh=defaultdict(list);proof=None
    for row in r.index['documents']:
        for o in row['origins']:
            bysha[o['sha256']].append(row['id'])
            if o.get('kind')=='ORIGINAL_EXTERNAL_FILE'and o.get('member')=='PRUEBA_RECUPERACION_DESDE_CERO.json':proof=r.get(row['id']);proof_id=row['id']
            name=o.get('member','')
            if o.get('kind')=='COMPLETED_CLEAN_RUN_FILE'and(Path(name).name in('MEASUREMENTS.json','RESULTADOS.json','OBSERVED.json','PRIMARY_TRANSITIONS.json')or Path(name).name.startswith('TRIAL_')):fresh[o['family']].append((row['id'],name))
    results=[]
    for family,pdata in proof['family_results'].items():
        refs=[]
        def walk(x):
            if isinstance(x,dict):
                h=[v for k,v in x.items()if isinstance(v,str)and len(v)==64 and v in bysha and any(t in k.lower()for t in('historical','original','primary'))]
                if h:
                    ident=x.get('id',x.get('case',x.get('field')))
                    if isinstance(ident,str):refs.extend((ident,v)for v in h)
                for v in x.values():walk(v)
            elif isinstance(x,list):
                for v in x:walk(v)
        walk(pdata);rows=[]
        for ident,h in sorted(set(refs)):
            original=bysha[h][0];old=physical(r.get(original));candidates=[(k,n)for k,n in fresh[family]if ident.casefold()in{v.casefold()for v in Path(n).parts}or Path(n).stem.casefold()==ident.casefold()]
            # No fallback to union of different cases or different individuals.
            for actual,name in candidates:
                new=physical(r.get(actual));common=old&new
                rows.append({'case_id_binding':ident,'binding':'EXACT_PATH_COMPONENT','historical_document':original,'historical_original_sha256':h,'completed_replay_document':actual,'replay_relative_path':name,
                  'historical_fingerprint_count':len(old),'replay_fingerprint_count':len(new),'exact_matches':len(common),'historical_not_present_in_this_file':len(old-new),'replay_additional':len(new-old),
                  'status':'MATCHED_RECORDED_FINGERPRINTS'if old and old<=new else'PARTIAL_COVERAGE_NOT_A_PHYSICS_VERDICT'if common else'NO_COMPARABLE_FINGERPRINTS',
                  'scope':'Only explicitly recorded full-array RAW/clocks/tick fingerprints; not empirical proof of every intermediate state or semantic acquisition.'})
        results.append({'family':family,'old_proof_status':pdata.get('status'),'old_proof_document':proof_id,'old_proof_pointer':'/family_results/'+family,
          'new_native_execution':False,'paired_records':rows,'not_automatically_promoted':'Missing pairs mean this generic audit did not certify that family anew; source data and original family-specific checks are included.'})
    obj={'schema':'CPC9.audit.case_bound_recorded_fingerprint_contrast.v1','engine_imported':False,'families':results,'pairs':sum(len(x['paired_records'])for x in results),
      'matched_pairs':sum(y['status']=='MATCHED_RECORDED_FINGERPRINTS'for x in results for y in x['paired_records']),
      'new_physical_reproductions':0,'limitation':'Fingerprint equality is rechecked from original and already completed replay primaries. This does not repeat the campaign or replace family-specific raw/clock readers.'}
    with a.out.open('x',encoding='utf8')as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'families':len(results),'pairs':obj['pairs'],'matched_pairs':obj['matched_pairs'],'new_physical_reproductions':0}))
if __name__=='__main__':main()
