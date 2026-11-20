"""Portable retrospective checks of exported APD02 mechanism primaries; no DEE import."""
import argparse,gzip,hashlib,json
from pathlib import Path

def sha(data):return hashlib.sha256(data).hexdigest()
def signed4(n):return n-16 if n>=8 else n
def decode(raw):
    if isinstance(raw,bool)or isinstance(raw,float):raise ValueError('Lossy/noninteger RAW')
    n=int(raw)
    if not 0<=n<2**64:raise ValueError('RAW outside uint64')
    return{'state':n&0xffffffff,'s_reg':(n>>32)&65535,'direction':[signed4((n>>k)&15)for k in(48,52,56)],'semantic':(n>>60)&15}
def read_json(path):
    b=path.read_bytes();return json.loads(gzip.decompress(b)if path.suffix=='.gz'else b)

def verify(root):
    issues=[];files=[];rows=[];nraw=0;nclock=0;nroutes=0;nnumeric=0;nfiles=0;nrelations=0;nacc=0
    def issue(file,where,kind,detail):issues.append({'file':file,'pointer':where,'kind':kind,'detail':detail})
    def walk(obj,file,pointer=''):
        nonlocal nraw,nclock,nroutes,nnumeric,nrelations,nacc
        if isinstance(obj,list):
            for i,value in enumerate(obj):walk(value,file,pointer+'/'+str(i))
            return
        if not isinstance(obj,dict):return
        if 'raw'in obj and isinstance(obj['raw'],(str,int)):
            try:
                d=decode(obj['raw']);nraw+=1
                for k,v in d.items():
                    if k in obj and obj[k]!=v:issue(file,pointer,'encoded_field_mismatch',{'field':k,'encoded':v,'reported':obj[k]})
                if 'clock'in obj:
                    if isinstance(obj['clock'],(bool,float))or not 0<=int(obj['clock'])<2**64:raise ValueError('Lossy/nonuint64clock')
                    nclock+=1
            except(ValueError,TypeError)as e:issue(file,pointer,'invalid_exact_record',str(e))
        if 'choice'in obj and isinstance(obj.get('observations'),list)and len(obj['observations'])==3:
            candidates=[]
            for o in obj['observations']:
                d=decode(o['raw']);v=d['direction']
                if d['state']and d['semantic']==1 and v[1:]==[1,0]and v[0]in(-1,0,1):candidates.append(v[0])
            found=candidates[0]if len(candidates)==1 else None;nroutes+=1
            if found!=obj['choice']:issue(file,pointer,'route_reader_mismatch',{'decoded':found,'reported':obj['choice'],'candidates':candidates})
        if 'numeric_result'in obj and 'representation_bias'in obj and isinstance(obj.get('observation'),dict):
            o=obj['observation'];d=decode(o['raw']);valid=d['state']>0 and d['semantic']==1 and d['direction']==[1,-1,-1]
            got=d['s_reg']-obj['representation_bias']if valid else None;nnumeric+=1
            if got!=obj['numeric_result']:issue(file,pointer,'numeric_reader_mismatch',{'decoded':got,'reported':obj['numeric_result']})
        if 'formed_native_command'in obj and isinstance(obj.get('panel'),list):
            signs=[]
            for o in obj['panel']:
                d=decode(o['raw'])
                if d['state']and d['semantic']==1 and d['direction']in([0,0,-1],[0,0,1]):signs.append(d['direction'][2])
            found=signs[0]if len(signs)==1 else None;nrelations+=1
            if found!=obj['formed_native_command']:issue(file,pointer,'common_relation_reader_mismatch',{'decoded':found,'reported':obj['formed_native_command'],'candidates':signs})
        if 'value'in obj and 'valid'in obj and isinstance(obj.get('sites'),list)and len(obj['sites'])==2:
            vals=[]
            for o in obj['sites']:
                if not isinstance(o,dict)or 'raw'not in o:break
                d=decode(o['raw'])
                if d['state']and d['semantic']==1 and d['direction']==[0,1,0]:vals.append(d['s_reg']-4096)
            else:
                found=vals[0]if len(vals)==1 else None;nacc+=1
                if found!=obj['value']or obj['valid']!=(len(vals)==1):issue(file,pointer,'recirculating_accumulator_reader_mismatch',{'decoded':found,'reported':obj['value'],'fixed_representation_bias':4096})
        for key,value in obj.items():walk(value,file,pointer+'/'+key.replace('~','~0').replace('/','~1'))
    for path in sorted(root.rglob('*')):
        if not path.is_file()or not(path.name.endswith('.json.gz')or path.suffix=='.json'):continue
        rel=path.relative_to(root).as_posix()
        if any(part in('CODIGO_EJECUTADO','RECALCULO','RECALCULADO')for part in path.relative_to(root).parts)or path.name.startswith('RECALCULO_'):continue
        raw=path.read_bytes()
        try:obj=read_json(path)
        except(ValueError,UnicodeError,OSError)as e:
            issue(rel,'','unparseable_primary',str(e));continue
        files.append({'file':rel,'bytes':len(raw),'sha256':sha(raw)})
        walk(obj,rel)
        value=obj.get('result',obj)if isinstance(obj,dict)else None
        if not isinstance(value,dict):continue
        use=value.get('use')
        if not isinstance(use,dict):continue
        row={'file':rel,'query_tick':use.get('query_tick'),'query_present':use.get('query_present',True),'choice':use.get('reader',{}).get('choice'),'boundary':use.get('boundary')}
        outcome=value.get('consequence',value.get('outcome'))
        if isinstance(outcome,dict):
            row.update({'category':outcome.get('category'),'mode':outcome.get('mode'),'references_before':[int(o['s_reg'])for o in outcome.get('before',[])],'references_after':[int(o['s_reg'])for o in outcome.get('after',[])]})
            if len(row['references_after'])==2:row['D_after']=row['references_after'][0]-row['references_after'][1]
            allr=outcome.get('all_generic_resources',[])
            row['generic_statuses']=[r.get('receipt',{}).get('status')for r in allr]
        committed=value.get('committed_effect')
        if isinstance(committed,dict):
            row.update({'actual_effect_state':committed.get('state'),'selected_procedure':committed.get('selected_procedure'),'price':committed.get('price'),'provider_calls':committed.get('provider_calls')})
            selected='native'if row['choice']==-1 else'external'if row['choice']in(0,1)else None
            if selected!=committed.get('selected_procedure'):issue(rel,'/result/committed_effect','selected_provider_differs_from_native_choice',{'native_choice':row['choice'],'provider':committed.get('selected_procedure')})
            calls=committed.get('provider_calls',{})
            if selected and(calls.get(selected)!=1 or sum(calls.values())!=1):issue(rel,'/result/committed_effect','dual_or_missing_selected_execution',calls)
            ar=committed.get('artifact')
            if isinstance(ar,dict):
                target=path.parent/ar['relative_path']
                if not target.resolve().is_relative_to(root.resolve()):issue(rel,'/result/committed_effect','unsafe_artifact_locator',ar)
                elif not target.is_file():issue(rel,'/result/committed_effect','missing_committed_bytes',ar)
                else:
                    b=target.read_bytes();nfiles+=1
                    if len(b)!=ar['bytes']or sha(b)!=ar['sha256']:issue(rel,'/result/committed_effect','artifact_bytes_mismatch',ar)
                    try:
                        body=json.loads(b);public=value['public_request'];operands=public['operands'];expected=operands[0]+operands[1]if body['operation']=='add'else operands[0]-operands[1]
                        correct=body['value']==expected and body['operands']==operands and body['task_id']==public['task_id']and body['procedure']==selected
                        row.update({'artifact_sha256':sha(b),'artifact_bytes':len(b),'numeric_from_actual_bytes':body['value'],'numeric_correct_given_committed_operator':correct})
                        quality=value.get('quality',{});claimed=quality.get('axes',{}).get('numeric_correct_for_original_request')
                        if claimed is not None and claimed!=(body['value']==expected):issue(rel,'/result/quality','private_numeric_audit_mismatch',{'computed':expected,'actual':body['value'],'claimed':claimed})
                        if body['operation']!='add':issue(rel,'/result/committed_effect','unreserved_operation_for_SUM_family',body['operation'])
                        wanted='SUCCESS'if correct and committed.get('state')=='committed'and committed['price']<=2 and committed['delay_ticks']<=8 else'FAILURE'
                        if value.get('actor_feedback',{}).get('category')!=wanted:issue(rel,'/result/actor_feedback','generic_quality_projection_mismatch',{'calculated':wanted,'reported':value.get('actor_feedback')})
                    except(KeyError,ValueError,TypeError)as e:issue(rel,'/result/committed_effect','artifact_decode_error',str(e))
        elif isinstance(value.get('artifact'),dict):
            ar=value['artifact'];target=path.parent/ar['file']
            if not target.is_file():issue(rel,'/result/artifact','missing_R03_actual_file',ar)
            else:
                b=target.read_bytes();nfiles+=1
                if len(b)!=ar['bytes']or sha(b)!=ar['sha256']:issue(rel,'/result/artifact','R03_actual_bytes_mismatch',ar)
                body=json.loads(b);vals=body['operands'];expected=vals[0]+vals[1]
                row.update({'artifact_sha256':sha(b),'artifact_bytes':len(b),'numeric_from_actual_bytes':body['value'],'numeric_correct_given_committed_operator':body['value']==expected,'price':value.get('modelled_price_of_actual_action'),'category':value.get('only_category_returned')})
        if 'native_choice'in value and value['native_choice']!=row['choice']:issue(rel,'/result/native_choice','copied_choice_mismatch',value['native_choice'])
        rows.append(row)
    return{'schema':'APD02.mechanism.archived_recalculation.v1','primary_files':files,'decoded_RAW_occurrences':nraw,'decoded_clock_occurrences':nclock,'route_readers_recomputed':nroutes,'native_numeric_readers_recomputed':nnumeric,'relation_readers_recomputed':nrelations,'accumulator_readers_recomputed':nacc,'actual_artifact_bytes_verified':nfiles,'cases':rows,'issues':issues,'scope':'Stdlib archived numerical/RAW/clock, fixed reader, selected-provider, actual JSON byte/hash and generic quality checks. Repeated observations are occurrences, not independent samples. No Runtime, new ticks, dense-snapshot replay, unique lineage or claim of full causal equality. Synthetic sensitivity categories remain distinct from actual quality tasks. Missing/unexecuted arms and negative outputs remain in source primaries.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    if a.salida.resolve().is_relative_to(a.evidencia.resolve()):raise ValueError('Output must be outside immutable evidence tree')
    if a.salida.exists():raise FileExistsError('No overwrite of prior recalculation')
    result=verify(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8');print(json.dumps({k:result[k]for k in('decoded_RAW_occurrences','route_readers_recomputed','native_numeric_readers_recomputed','actual_artifact_bytes_verified')},sort_keys=True));print('issues='+str(len(result['issues'])));return 1 if result['issues']else 0
if __name__=='__main__':raise SystemExit(main())
