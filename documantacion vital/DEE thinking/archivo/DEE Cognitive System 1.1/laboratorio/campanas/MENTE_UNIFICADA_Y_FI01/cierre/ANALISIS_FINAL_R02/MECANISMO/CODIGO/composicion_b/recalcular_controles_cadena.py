"""Portable causal-chain control recalculation from archived primary fields."""
import argparse,base64,gzip,hashlib,json,zlib
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def sign(panel,pure=False):
    cs=[]
    for o in panel:
        v=o['direction']
        if o['state']<=0 or o['semantic']!=1:continue
        if pure and v in([0,0,-1],[0,0,1]):cs.append(v[2])
        if not pure and v[0]in(-1,0,1)and v[1]==1 and v[2]in(0,-1):cs.append(v[0])
    return cs[0]if len(cs)==1 else None
def pending_check(p):
    if p is None:return None
    artifact=base64.b64decode(p['prepared_output_base64']);payload=base64.b64decode(p['payload_base64'])
    return {'prepared_by':p['prepared_by'],'artifact_bytes':len(artifact),'artifact_hash_exact':sha(artifact)==p['prepared_output_sha256'],
      'payload_hash_exact':sha(payload)==p['payload_sha256'],'artifact_content_exact':(zlib.decompress(artifact)==payload)if p['prepared_by']==1 else artifact==hashlib.sha256(payload).digest()}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidencia',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
    files=[];scalars=[];memories=[];workers=[];receipts=[];raw_count=0;errors=[];pendings=[]
    def walk(o,file,path=''):
        nonlocal raw_count
        if isinstance(o,list):
            for i,v in enumerate(o):walk(v,file,path+'/'+str(i))
        elif isinstance(o,dict):
            if all(k in o for k in('raw','clock','site','state','semantic','direction')):
                raw_count+=1
                if not(0<=int(o['raw'])<2**64 and 0<=int(o['clock'])<2**64):errors.append(file+': non uint64')
            if 'receipt'in o and isinstance(o['receipt'],dict)and 'status'in o['receipt']:receipts.append({'file':file,'path':path,'id':o.get('id'),'status':o['receipt']['status']})
            if 'reader'in o and isinstance(o['reader'],dict):
                r=o['reader']
                if 'observations'in r:
                    actual=sign(r['observations'])
                    if actual!=r['choice']:errors.append(file+': current reader mismatch')
                    scalars.append({'file':file,'path':path,'query_tick':o['query_tick'],'raw_value':o.get('raw_sensor_value',o.get('value')),
                      'choice_from_primary':actual,'datum_after_raw':o.get('datum_after',{}).get('raw')})
                elif 'panel'in r:
                    actual=sign(r['panel'],True)
                    if actual!=r['formed_native_command']:errors.append(file+': memory reader mismatch')
                    memories.append({'file':file,'path':path,'context':o.get('context_signal'),'choice_from_primary':actual})
            if o.get('schema')=='EO02.local_worker.receipt.v2':
                workers.append({'file':file,'path':path,'worker':o['worker'],'operation':o['operation'],'accepted':o['accepted'],
                  'transaction_completed':o['transaction_completed'],'actual_output_bytes':o['output_bytes'],'prepared_artifact_check':o.get('prepared_artifact_check'),
                  'pending_after':pending_check(o.get('pending_transaction')),'read_back_verified':o['read_back_verified']})
            if 'prepared_output_base64'in o:
                check=pending_check(o);pendings.append({'file':file,'path':path,**check})
                if not all(check[k]for k in('artifact_hash_exact','payload_hash_exact','artifact_content_exact')):errors.append(file+': pending artifact mismatch')
            for k,v in o.items():walk(v,file,path+'/'+k)
    for p in sorted(a.evidencia.glob('*.json.gz')):
        o=json.loads(gzip.decompress(p.read_bytes()));files.append({'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes()),
          'snapshot_sha256':o['INSTRUMENTO']['snapshot_sha256'],'tick':o['INSTRUMENTO']['tick']});walk(o,p.name)
    result={'schema':'MUFI01.composition_controls.recalc.v1','physical_ticks_executed':0,'files':files,'scalar_uses':scalars,'memory_uses':memories,
      'actual_worker_operations':workers,'native_receipts':receipts,'pending_artifact_checks':pendings,'uint64_observations_checked':raw_count,'errors':errors,
      'scope':'Archived native reader and actual worker receipt recalculation, including failures/pending state. Does not execute DEE or external workers, and does not claim autonomous stage planning.'}
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'primaries':len(files),'scalar_uses':len(scalars),'memory_uses':len(memories),'workers':len(workers),'receipts':len(receipts),'errors':errors,'sha256':sha(a.salida.read_bytes())}))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
