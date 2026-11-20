"""Archived R16 recalc: exact integers only, stdlib, no DEE import or ticks."""
from array import array
from pathlib import Path
import argparse,gzip,hashlib,json,sys

def read(p):
    p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def field(v,k):
    x=(v>>k)&15;return x-16 if x&8 else x
def decode(v):return {'state':v&0xffffffff,'semantic':v>>60,'s_reg':(v>>32)&65535,'direction':[field(v,k)for k in(48,52,56)]}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('folder',type=Path);ap.add_argument('--out',type=Path);args=ap.parse_args();p=args.folder
    checks=0;observations=0;rows=[];cache={}
    def ck(ok,label):
        nonlocal checks
        checks+=1
        if not ok:raise AssertionError(label)
    def exact(o):
        nonlocal observations
        d=decode(int(o['raw']));ck(all(o[k]==d[k]for k in d),'RAW decoding '+str(o.get('site')));observations+=1
    def read_choice(reader):
        cs=[]
        for o in reader['observations']:
            exact(o);x=(o['site'][0]-15)//2;z=(o['site'][2]-15)//2
            if o['state']>0 and o['semantic']==1 and o['direction']==[x,1,z]:cs.append(x)
        return cs[0]if len(cs)==1 else None
    def arr(h):
        if h not in cache:
            b=gzip.decompress((p/'fields'/(h+'.u64le.gz')).read_bytes());ck(hashlib.sha256(b).hexdigest()==h,'field SHA '+h);a=array('Q');a.frombytes(b)
            if sys.byteorder!='little':a.byteswap()
            ck(len(a)==67**3,'field count');cache[h]=a
        return cache[h]
    records={label:read(p/(label+'.json.gz'))for label in('unprotected_age_matched','protected_R3')}
    prot=records['protected_R3'];q=prot['scalar_or_reused_history'];t=q['timing']
    ck(t['requested_query_tick']==62556 and t['effective_query_tick']==62562 and t['wait_ticks']==6,'prospective6tick displacement')
    ck((62562-2)//391==(62562+8)//391,'protected phase interval')
    ck(len(q['requests'])==4 and all(r['receipt']['status']=='applied'for r in q['requests']),'protected scalar4/4')
    ck(prot['prepared_phase_flag']['native_ticks_advanced']==0 and prot['prepared_phase_flag']['learned_fields_edited']is False,'P0 flag does not advance or edit learned fields')
    for label,r in records.items():
        for o in r['refs_matched']:exact(o)
        ck(r['matched']['tick']==62570,'common age')
        ck([o['s_reg']for o in r['refs_matched']]==([104,125]if label=='unprotected_age_matched'else[105,125]),'matched references')
        raw=r['common_raw128'];v=[0]*128;v[0]=19;v[2]=2
        ck(raw['raw_components']==v,'same fixed128input vector')
        ck(raw['query_tick']==62760 and raw['read_tick']==62766,'common native read schedule')
        ck(len(raw['requests'])==176 and all(x['receipt']['status']=='applied'for x in raw['requests']),'raw176/176')
        choice=read_choice(raw['reader']);ck(choice==raw['reader']['choice']and choice==(None if label=='unprotected_age_matched'else 1),'frozen six-class output')
        for f in raw['frames']:
            for o in f['fields'].values():exact(o)
        if label=='protected_R3':
            ck(raw['timing']['wait_ticks']==0,'common raw frame did not receive extra shift')
            for f in q['frames']:
                for o in f['sites']:exact(o)
        old=r['old_six_panel'];commands=[];total=0
        for row in old['rows']:
            candidates=[]
            for o in row['reader']['panel']:
                exact(o);sg=o['site'][2]-33
                if sg in(-1,1)and o['state']>0 and o['semantic']==1 and o['direction']==[0,0,sg]:candidates.append(sg)
            formed=candidates[0]if len(candidates)==1 else None
            ck(formed==row['reader']['formed_native_command'],'fixed old common reader');commands.append(formed)
            total+=len(row['requests']);ck(all(x['receipt']['status']=='applied'for x in row['requests']),'old row admission')
        ck(commands==[-1,1,1,-1,-1,1]and total==42,'old six fixed learned responses and42/42')
        ck(r['final']['tick']==63255,'final age')
        rows.append({'label':label,'matched_references':[o['s_reg']for o in r['refs_matched']],'raw_choice':choice,'raw_admission':'176/176','old_six':commands,'old_admission':'42/42','final_tick':63255})
    agendas=read(p/'AGENDAS.json.gz');comparisons=[]
    for tag in('62570_MATCHED','62704_PASSIVE','AFTER_COMMON_RAW128','AFTER_OLD_SIX'):
        a=agendas['unprotected_age_matched_'+tag];b=agendas['protected_R3_'+tag]
        ar,br=[arr(q['summary']['RAW_sha256'])for q in(a,b)];ac,bc=[arr(q['summary']['clocks_sha256'])for q in(a,b)]
        rawdiff=[i for i,(x,y)in enumerate(zip(ar,br))if x!=y];clockdiff=[i for i,(x,y)in enumerate(zip(ac,bc))if x!=y]
        ck(rawdiff==[(14*67+14)*67+15]and clockdiff==[],'full difference exactly A, no clocks '+tag)
        ck(a['channels']==b['channels']and a['owner_interfaces']==b['owner_interfaces'],'same physical interfaces '+tag)
        ck(not a['pending']and not b['pending']and not a['owner_protocols']and not b['owner_protocols'],'empty final/owner queues '+tag)
        comparisons.append({'tag':tag,'RAW_differences':len(rawdiff),'clocks_differences':len(clockdiff),'receipts_equal':a['receipts']==b['receipts']})
    result={'classification':'Archived exact recalc, no native reproduction','new_ticks':0,'checks':checks,'failures':0,'decoded_observations':observations,'rows':rows,'full_comparisons':comparisons,
      'scope':'One paired P0 temporal-assistance reserve at a known failure phase. Not autonomous regulation, general avoidance of interference or unlimited stability.'}
    data=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2).encode()
    if args.out:args.out.write_bytes(data)
    else:print(data.decode())
if __name__=='__main__':main()
