"""Portable primary-record arithmetic for the shared-world B application.
No DEE import/ticks. Rebuilds fixed readers and actual synthetic artifact bytes.
"""
import argparse,base64,gzip,hashlib,itertools,json,zlib
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def fields(raw):
    n=int(raw)
    if not 0<=n<2**64:raise ValueError('Exact uint64 RAW required')
    ds=[(n>>i)&15 for i in(48,52,56)]
    return {'state':n&0xffffffff,'s_reg':(n>>32)&65535,'semantic':n>>60,'direction':[x-16 if x&8 else x for x in ds]}
def walk(v,path='$'):
    yield path,v
    if isinstance(v,dict):
        for k,x in v.items():
            if k not in('stdout','stderr'):yield from walk(x,path+'.'+k)
    elif isinstance(v,list):
        for j,x in enumerate(v):yield from walk(x,path+'['+str(j)+']')
def recalc(folder):
    result={'schema':'MUFI01.B.actual_application.archived.v1','native_ticks':0,'files':[],'cases':[],'errors':[],
      'raw_checks':0,'reader_checks':0,'artifact_checks':0,'worker_checks':0,'scope':'Archived recalc from exact RAW and serialized external artifact bytes, not native reproduction or new learning.'}
    pending={};items=[]
    for p in sorted(folder.glob('B_MAIN*.json.gz')):
        raw=p.read_bytes();data=json.loads(gzip.decompress(raw));items.append((p,data));result['files'].append({'name':p.name,'bytes':len(raw),'sha256':sha(raw)})
        for loc,x in walk(data.get('result',{})):
            if isinstance(x,dict)and all(k in x for k in('prepared_output_base64','payload_base64','prepared_by')):
                artifact=base64.b64decode(x['prepared_output_base64']);payload=base64.b64decode(x['payload_base64'])
                expected=zlib.compress(payload,9)if x['prepared_by']==1 else hashlib.sha256(payload).digest()
                result['artifact_checks']+=1
                if artifact!=expected or sha(artifact)!=x['prepared_output_sha256']or sha(payload)!=x['payload_sha256']:result['errors'].append({'file':p.name,'at':loc,'artifact':'Bytes or digest mismatch'})
                pending[x['prepared_output_sha256']]={'artifact':artifact,'payload':payload,'prepared_by':x['prepared_by']}
    for p,data in items:
        root=data.get('result',{});case={'case':data.get('case',p.name),'returncode':data.get('returncode'),'requested':0,'receipts':{},'responses':[],'workers':[]};requests={}
        if data.get('returncode')!=0:case['instrument_error']=data.get('stderr')
        for loc,x in walk(root):
            if not isinstance(x,dict):continue
            if all(k in x for k in('raw','state','s_reg','semantic','direction')):
                result['raw_checks']+=1
                for k,v in fields(x['raw']).items():
                    if x[k]!=v:result['errors'].append({'file':p.name,'at':loc,'field':k,'recorded':x[k],'recomputed':v})
            if isinstance(x.get('receipt'),dict)and'id'in x:
                requests[x['id']]=x['receipt']
            if 'formed_native_command'in x and'panel'in x:
                candidates=[f['direction'][2]for f in map(lambda o:fields(o['raw']),x['panel'])if f['state']>0 and f['semantic']==1 and f['direction']in([0,0,-1],[0,0,1])]
                expected=candidates[0]if len(candidates)==1 else None;result['reader_checks']+=1
                if expected!=x['formed_native_command']:result['errors'].append({'file':p.name,'at':loc,'pureZ_reader':expected,'recorded':x['formed_native_command']})
                case['responses'].append({'reader':'pureZ','choice':expected,'at':loc})
            if 'choice'in x and isinstance(x.get('observations'),list)and len(x['observations'])in(3,6):
                directions=[(s,1,0)for s in(-1,0,1)]if len(x['observations'])==3 else[(s,1,z)for s in(-1,0,1)for z in(0,-1)]
                candidates=[]
                for direction,o in zip(directions,x['observations']):
                    f=fields(o['raw'])
                    if f['state']>0 and f['semantic']==1 and f['direction']==list(direction):candidates.append(direction[0])
                expected=candidates[0]if len(candidates)==1 else None;result['reader_checks']+=1
                if expected!=x['choice']:result['errors'].append({'file':p.name,'at':loc,'native_reader':expected,'recorded':x['choice']})
                case['responses'].append({'reader':'six_fixed'if len(directions)==6 else'three_fixed','choice':expected,'at':loc})
            if x.get('schema')=='EO02.local_worker.receipt.v2':
                result['worker_checks']+=1
                if x['operation']=='verify_commit':
                    check=x['prepared_artifact_check'];old=pending.get(check['sha256'])
                    if old is None:result['errors'].append({'file':p.name,'at':loc,'verify':'Original actual pending bytes omitted'});continue
                    payload=old['payload'];accepted=x['worker']!=old['prepared_by'];artifact_ok=len(old['artifact'])==check['bytes']and sha(old['artifact'])==check['sha256']
                    if not artifact_ok:result['errors'].append({'file':p.name,'at':loc,'verify':'Artifact bytes mismatch'})
                else:
                    v=x['raw_observations'];payload=bytes(v)*max(1,32+sum(v[::2]));accepted=x['worker']==(1 if sum(v[::2])+x['modelled_capacity_credit_not_actor_input']>=sum(v[1::2])else-1)
                output=zlib.compress(payload,9)if x['worker']==1 else hashlib.sha256(payload).digest()
                checks={'input_bytes':len(payload),'input_sha256':sha(payload),'output_bytes':len(output),'output_sha256':sha(output),'accepted':accepted}
                for k,v in checks.items():
                    if x[k]!=v:result['errors'].append({'file':p.name,'at':loc,'worker_field':k,'recorded':x[k],'recomputed':v})
                case['workers'].append({'operation':x['operation'],'native_worker':x['worker'],'accepted':accepted,'transaction_completed':bool(accepted and x['operation']=='verify_commit'),'output_bytes':len(output)})
        case['requested']=len(requests)
        for x in requests.values():case['receipts'][x['status']]=case['receipts'].get(x['status'],0)+1
        result['cases'].append(case)
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path);a=p.parse_args();r=recalc(a.evidencia);text=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
    if a.salida:a.salida.write_text(text,encoding='utf8')
    else:print(text)
    if r['errors']:raise SystemExit(2)
if __name__=='__main__':main()
