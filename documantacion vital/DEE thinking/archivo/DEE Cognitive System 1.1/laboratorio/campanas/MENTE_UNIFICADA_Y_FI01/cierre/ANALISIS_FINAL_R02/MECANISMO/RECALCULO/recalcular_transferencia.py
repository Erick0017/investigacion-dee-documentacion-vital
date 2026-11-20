"""Portable stdlib-only recalculation; no DEE imports or physical ticks."""
import argparse,base64,gzip,hashlib,json,struct,zlib
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def derived(obs,kind):
    candidates=[]
    for o in obs:
        v=o['direction']
        if not(o['state']>0 and o['semantic']==1):continue
        if kind=='six'and v[0]in(-1,0,1)and v[1]==1 and v[2]in(0,-1):candidates.append(v[0])
        if kind=='pureZ'and v in([0,0,-1],[0,0,1]):candidates.append(v[2])
    return candidates[0]if len(candidates)==1 else None

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidencia',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
    files=[];trials=[];associations=[];lessons=[];fixtures=[];instrument_failures=[];native_receipts=[];complete_arrays=[];errors=[];raw_count=0
    def visit(o):
        nonlocal raw_count
        if isinstance(o,dict):
            if 'receipt'in o and isinstance(o['receipt'],dict)and 'status'in o['receipt']:
                native_receipts.append({'file':relative,'request_id':o.get('id'),'status':o['receipt']['status']})
            if all(k in o for k in('raw','clock','site','direction','s_reg','semantic','state')):
                raw_count+=1
                if not(0<=int(o['raw'])<2**64 and 0<=int(o['clock'])<2**64):errors.append('Non uint64 observation')
            for v in o.values():visit(v)
        elif isinstance(o,list):
            for v in o:visit(v)
    def scalar(row,file):
        actual=derived(row['reader']['observations'],'six');reported=row['reader']['choice']
        if actual!=reported:errors.append(file+': scalar reader mismatch')
        q=row['query_tick'];fr={f['tick']:f['sites']for f in row['frames']}
        primary={tuple(x['site']):x for x in fr[q+6]}
        for ob in row['reader']['observations']:
            if primary.get(tuple(ob['site']))!=ob:errors.append(file+': reader not identical to primary frame')
        s=(14,15,16);bytick={t:next((x for x in obs if tuple(x['site'])==s),None)for t,obs in fr.items()}
        requests=row['requests'];statuses={}
        for r in requests:
            status=r['receipt']['status'];statuses[status]=statuses.get(status,0)+1
        refs=row.get('references',[])
        record={'file':file,'label':row['label'],'query_tick':q,'read_tick':q+6,'raw_value':row['value'],'choice_from_primary':actual,
          'requested':len(requests),'receipt_status_counts':statuses,'S_raw_at_qplus3':bytick[q+3]['raw']if bytick[q+3]else None,
          'S_raw_at_qplus5':bytick[q+5]['raw']if bytick[q+5]else None,'S_raw_final':bytick[q+8]['raw']if bytick[q+8]else None,
          'reference_s_reg':[x['s_reg']for x in refs]}
        if 'environment_after_action'in row:
            env=row['environment_after_action'];n=env['actual_bytes'];normal=-1 if n<20 else 1
            record.update(actual_file_bytes=n,useful_aligned=actual==normal,useful_counterlaw=actual==-normal,feedback_sent=env['feedback_sent'])
            if actual is None:record['response_class']='abstention_or_ambiguous'
            elif actual==0:record['response_class']='neutral'
            else:record['response_class']='signed'
            if record['useful_aligned']!=env['useful_aligned']or record['useful_counterlaw']!=env['useful_counterlaw']:errors.append(file+': external law mismatch')
        trials.append(record)
    for p in sorted(a.evidencia.rglob('*')):
        if not p.is_file()or not(p.name.endswith('.json')or p.name.endswith('.json.gz')):continue
        if p.name.startswith('RECALCULO')or p.name.startswith('INDICE'):continue
        o=read(p);relative=p.relative_to(a.evidencia).as_posix();files.append({'file':relative,'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size});visit(o)
        if isinstance(o,dict)and o.get('schema')=='MUFI01.BT.TUH.full_arrays.lossless.v1':
            worlds=o['worlds'];base=worlds['U'];arrays={}
            def ahash(values):
                h=hashlib.sha256()
                for v in values:
                    n=int(v)
                    if not 0<=n<2**64:raise ValueError('Non uint64 full-world field')
                    h.update(struct.pack('<Q',n))
                return h.hexdigest()
            for arm in('U','T','H'):
                w=worlds[arm]
                if arm=='U':raw,clock=list(w['raw']),list(w['clock'])
                else:
                    raw,clock=list(base['raw']),list(base['clock'])
                    for key,field,basefield,target in[('raw_delta','raw','base_raw',raw),('clock_delta','clock','base_clock',clock)]:
                        indices=set()
                        for delta in w[key]:
                            j=delta['index']
                            if j in indices or target[j]!=delta[basefield]:errors.append(relative+': lossless delta base mismatch')
                            indices.add(j);target[j]=delta[field]
                okay=(ahash(raw)==w['raw_sha256']and ahash(clock)==w['clock_sha256']and len(raw)==len(clock)==67**3 and w['tick_before']==w['tick_after']==30891)
                if not okay:errors.append(relative+': reconstructed full-world hash/tick mismatch')
                arrays[arm]=(raw,clock)
                complete_arrays.append({'file':relative,'arm':arm,'tick':w['tick_before'],'uint64_values_verified':len(raw)+len(clock),'full_hashes_exact':okay,'snapshot_sha256':w['snapshot_sha256'],
                  'raw_difference_sites':[]if arm=='U'else[x['site']for x in w['raw_delta']],'clock_differences':0 if arm=='U'else len(w['clock_delta']),'unfinished_receipts':len(w['unfinished_receipts'])})
            for arm in('T','H'):
                actual=[j for j,(x,y)in enumerate(zip(arrays[arm][0],arrays['U'][0]))if x!=y]
                expected=[x['index']for x in worlds[arm]['raw_delta']]
                if actual!=expected:errors.append(relative+': reconstructed difference set mismatch')
            del arrays
        if p.name.endswith('_FIXTURES.json'):
            for f in o:
                b=base64.b64decode(f['payload_base64']);q=f['worker_request'];public=q['raw_observations'];payload=bytes(public)*max(1,32+sum(public[::2]))
                regenerated=zlib.compress(payload,9)if q['executed_worker']==1 else hashlib.sha256(payload).digest()
                okay=(b==regenerated and len(b)==f['actual_readback_bytes']and sha(b)==f['sha256']==f['worker_receipt']['output_sha256'])
                fixtures.append({'file':relative,'worker':q['executed_worker'],'public':public,'bytes':len(b),'sha256':sha(b),'regenerated_exact':okay})
                if not okay:errors.append(relative+': fixture mismatch')
            continue
        if isinstance(o,dict)and o.get('schema')=='DCS1.1.life.v1':
            for op in o.get('operations',[]):
                if not op.get('kind','').startswith('FAILED_'):continue
                before,after=op['before'],op['after'];same=before==after
                instrument_failures.append({'file':relative,'life':o['life_id'],'error':op['error'],
                  'before_tick':before['tick'],'after_tick':after['tick'],'full_physical_hashes_unchanged':same})
                if not same:errors.append(relative+': instrument failure unexpectedly changed physics')
        r=o.get('result',{})if isinstance(o,dict)else{}
        for row in r.get('trials',[]):scalar(row,relative)
        for k in('source_scalar_trials','destination_trials'):
            for row in r.get(k,[]):scalar(row,relative)
        for row in r.get('lessons',[]):
            final=row['frames'][-1]['refs'];lessons.append({'file':relative,'lesson':row['lesson'],'arrival_tick':row['scheduled_arrival'],
              'reference_s_reg':[x['s_reg']for x in final],'difference':final[0]['s_reg']-final[1]['s_reg'],'receipt_status':row['request']['receipt']['status']})
        for row in r.get('rows',[]):
            native=row.get('native',row)
            if 'reader'not in native:continue
            rr=native['reader'];panel=rr.get('panel')
            if panel is None:continue
            actual=derived(panel,'pureZ')
            if actual!=rr['formed_native_command']:errors.append(relative+': pureZ mismatch')
            rec={'file':relative,'stage':row.get('stage','retention'),'context':native['context_signal'],'read_tick':native['read_tick'],'choice_from_primary':actual,
              'requested':len(native['requests']),'admitted':sum(x['receipt']['status']=='applied'for x in native['requests'])}
            if 'external_emission'in row:
                emission=row['external_emission'];expected=b'DEE-CONTEXT-RIGHT\n'if actual==-1 else b'DEE-CONTEXT-LEFT\n'if actual==1 else None
                if(expected.hex()if expected else None)!=emission['bytes_hex']:errors.append(relative+': header differs from physical sign')
                if(sha(expected)if expected else None)!=emission['sha256']:errors.append(relative+': header SHA differs from emitted primary bytes')
                rec.update(emitted_header_hex=emission['bytes_hex'],useful_aligned=actual==-1,useful_counterlaw=actual==1,feedback_sent=emission['feedback_sent'])
            associations.append(rec)
    result={'schema':'MUFI01.transfer_recalculation.stdlib.v1','physical_ticks_executed':0,'files':files,'exact_uint64_observations_checked':raw_count,
      'scalar_trials':trials,'source_lessons':lessons,'arbitrary_association_uses':associations,'actual_file_fixtures':fixtures,'instrument_failures':instrument_failures,'native_receipts':native_receipts,'complete_world_arrays':complete_arrays,'errors':errors,
      'limits':'Recalculation validates exported primary observations, receipt denominators and actual file codecs. It does not re-execute DEE, establish unrecorded trajectories, or turn aligned P0 codecs into acquired abstraction.'}
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(files),'scalar_trials':len(trials),'association_uses':len(associations),'lessons':len(lessons),'errors':errors,'output_sha256':sha(a.salida.read_bytes())}))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
