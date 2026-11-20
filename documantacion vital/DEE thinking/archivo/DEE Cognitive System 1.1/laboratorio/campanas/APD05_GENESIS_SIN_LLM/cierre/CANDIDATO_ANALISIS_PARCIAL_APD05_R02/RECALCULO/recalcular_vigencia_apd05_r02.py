"""Archived exact-RAW recalculation. Stdlib only; no engine, actor or targets fed back."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json

def read_json(raw):
    return json.loads(raw) if isinstance(raw,str) else raw

def walk(value,path='$'):
    yield path,value
    if isinstance(value,dict):
        for k,v in value.items():
            if k in ('result','result_json') and isinstance(v,str) and v.lstrip().startswith(('{','[')):
                v=json.loads(v)
            yield from walk(v,path+'.'+str(k))
    elif isinstance(value,list):
        for i,v in enumerate(value):yield from walk(v,path+'['+str(i)+']')

def fields(obs):
    raw=int(obs['raw'])
    if not 0<=raw<2**64:raise ValueError('Not uint64 RAW')
    d={'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,'semantic':(raw>>60)&15,
       'direction':[((raw>>k)&15)-(16 if((raw>>k)&15)>=8 else 0) for k in(48,52,56)]}
    for k,v in d.items():
        if k in obs and obs[k]!=v:raise ValueError('RAW/decoded disagreement: '+k)
    if 'clock'in obs and not 0<=int(obs['clock'])<2**64:raise ValueError('Not uint64 clock')
    return d

def native_six(reader):
    candidates=[]
    for obs in reader['observations']:
        f=fields(obs)
        for x in(-1,0,1):
            for z in(0,-1):
                if obs['site']==[15+2*x,17,15+2*z] and f['state']>0 and f['semantic']==1 and f['direction']==[x,1,z]:
                    candidates.append(x)
    return candidates[0] if len(candidates)==1 else None,len(candidates)

def lexical36(reader):
    candidates=[]
    geometries=[((33,33,33),v)for v in((1,0,0),(0,1,0),(1,1,0),(-1,1,0),(1,-1,0),(-1,-1,0),(-1,0,0),(0,-1,0))]
    geometries += [((47,47,47),v)for v in((-1,0,0),(0,-1,0),(1,0,0),(0,1,0))]
    geometries += [((47,17,47),v)for v in((1,0,0),(0,1,0))]
    geometries += [((47,7,47),v)for v in((-1,0,0),(0,-1,0),(1,0,0),(1,1,0))]
    gates={tuple((o[i]+4*v[i]+(sign if i==2 else 0))%67 for i in range(3)):sign
           for o,v in geometries for sign in(-1,1)}
    if len(gates)!=36 or len(reader['panel'])!=36:raise ValueError('Frozen lexical36 geometry differs')
    if {tuple(obs['site'])for obs in reader['panel']}!=set(gates):raise ValueError('Lexical panel coverage differs')
    for obs in reader['panel']:
        f=fields(obs)
        sign=gates[tuple(obs['site'])]
        if f['state']>0 and f['semantic']==1 and f['direction']==[0,0,sign]:candidates.append(sign)
    return candidates[0] if len(candidates)==1 else None,len(candidates)

def summarize(records):
    access=[];words=[];numbers=[];native={};checks=0;seen=set();ticks=[]
    for index,event in enumerate(records):
        for loc,node in walk(event,'$['+str(index)+']'):
            if not isinstance(node,dict):continue
            if 'raw'in node and 'site'in node:
                fields(node);checks+=1
            if 'receipt'in node and isinstance(node['receipt'],dict) and 'id'in node['receipt']:
                r=node['receipt'];key=str(r['id']);old=native.get(key)
                if old and old.get('status')not in('pending','scheduled','admitted') and old!=r:
                    raise ValueError('Contradictory terminal Native receipt '+key)
                native[key]=r
            if 'selection_native_trial'in node and 'codec'in node:
                trial=node['selection_native_trial'];stamp=('access',trial['read_tick'])
                if stamp in seen:continue
                seen.add(stamp);sign,count=native_six(trial['reader'])
                codec=node['codec'];curr=codec['current_version'];cache=codec['cached_version'];cachecode=0 if cache is None else cache+1
                components=[0]*128;components[0]=2*(curr+1);components[1]=19-2*cachecode
                if trial['raw_components']!=components:raise ValueError('Independent fixed codec mismatch')
                if sign!=node['physical_choice'] or sign!=trial['reader']['choice']:raise ValueError('Reported physical choice disagrees with RAW')
                action={-1:'USE',0:'WAIT',1:'INSPECT'}.get(sign)
                if action!=node['physical_action']:raise ValueError('Frozen actuator mapping differs')
                # Evaluation only: never imported by the Native actor.
                expected='INSPECT' if cache is None or curr!=cache else 'USE'
                access.append({'episode':node['episode'],'tick':trial['read_tick'],'current':curr,'cached':cache,
                    'RAW_sign':sign,'candidate_count':count,'action':action,'prospective_expected':expected,
                    'matches_reference20_access_criterion':action==expected,'effect':node['committed_effect'],
                    'locator':loc})
            if isinstance(node.get('reader'),dict) and 'panel'in node['reader'] and 'form'in node:
                stamp=('word',node['form'],node.get('read_tick'))
                if stamp in seen:continue
                seen.add(stamp);sign,count=lexical36(node['reader'])
                if sign!=node['reader']['formed_native_command']:raise ValueError('Lexical reported answer differs from RAW')
                words.append({'form':node['form'],'tick':node.get('read_tick'),'RAW_sign':sign,'candidate_count':count,'locator':loc})
            if node.get('kind')in('APD04_candidate_scalar_classification','APD04_candidate_native_balance'):
                trial=node['native_trial'];stamp=(node['kind'],trial['read_tick'])
                if stamp in seen:continue
                seen.add(stamp);sign,count=native_six(trial['reader'])
                if sign!=node['physical_choice']:raise ValueError('Numerical reported answer differs from RAW')
                numbers.append({'kind':node['kind'],'tick':trial['read_tick'],'RAW_sign':sign,'candidate_count':count,'locator':loc})
        transport=event.get('transport',{})
        if transport.get('result'):
            r=read_json(transport['result']);ticks.append([r.get('before_tick'),r.get('after_tick')])
    return {'access':access,'lexical_queries':words,'numeric_uses':numbers,
        'transport_statuses':dict(Counter(r.get('transport',{}).get('status','not_transport') for r in records)),
        'native_ids_unique':len(native),'native_receipt_statuses':dict(Counter(r.get('status') for r in native.values())),
        'RAW_observation_checks':checks,'operation_tick_intervals':ticks,
        'access_formed':sum(r['candidate_count']==1 for r in access),
        'access_correct_in_reference20_domain':sum(r['matches_reference20_access_criterion'] for r in access),
        'access_useful_environmental_effects':sum(bool(r['effect'].get('useful')) for r in access),
        'scope':'Archived recalculation only. Prepared version interface and environmental cache are not learned attention; IDs are new receipts in supplied records, not independent lives. No Native execution.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('events');p.add_argument('--output',required=True);a=p.parse_args()
    source=Path(a.events);raw=source.read_bytes();records=[json.loads(x) for x in raw.splitlines() if x.strip()]
    result={'schema':'APD05.exact_RAW_archived_version_recalculation.R02','source_sha256':hashlib.sha256(raw).hexdigest(),**summarize(records)}
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({k:result[k]for k in('native_ids_unique','native_receipt_statuses','access_formed','access_correct_in_reference20_domain','access_useful_environmental_effects')},ensure_ascii=False))

if __name__=='__main__':main()
