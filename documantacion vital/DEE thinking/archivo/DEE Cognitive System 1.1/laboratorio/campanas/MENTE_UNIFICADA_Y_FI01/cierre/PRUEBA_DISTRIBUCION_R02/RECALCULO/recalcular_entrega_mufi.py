"""Portable RAW/reader/actual-file recalculation of the archived exact-ZIP proof.

No DEE import, native replay, source computer access or policy computation.
The omitted full ZIP/world hashes are archived receipts, not rechecked here.
"""
import argparse,gzip,hashlib,json,zlib
from pathlib import Path

def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def canonical(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')
def fields(value):
    if type(value)is not int and not(isinstance(value,str)and value.isdecimal()):raise ValueError('Exact uint64 required')
    n=int(value)
    if not 0<=n<2**64:raise ValueError('uint64 outside domain')
    return {'state':n&0xffffffff,'s_reg':(n>>32)&65535,'semantic':(n>>60)&15,'direction':[v-16 if v>=8 else v for v in[(n>>s)&15 for s in(48,52,56)]]}
def objects(x):
    if isinstance(x,dict):
        yield x
        for k,v in x.items():
            if k in('stdout','result')and isinstance(v,str)and v.lstrip().startswith('{'):
                try:yield from objects(json.loads(v))
                except json.JSONDecodeError:pass
            else:yield from objects(v)
    elif isinstance(x,list):
        for v in x:yield from objects(v)

def calculate(root,proof_name='VERIFICACION_FULLZIP_EXACTO_R3.json',outcome='completed'):
    if Path(proof_name).name!=proof_name:raise ValueError('Explicit local archived proof filename required')
    proof=load(root/proof_name);index=load(root/'ARCHIVOS_REALES.json');issues=[];checks={};observations={};readers={};workers={}
    def check(k,v):
        checks[k]=bool(v)
        if not v:issues.append(k)
    statuses={'completed':'COMPLETED_WITH_RECORDED_SCOPE','continued':'COMPLETED','instrument_timeout':'FAILED_WITH_STATE_PRESERVED'}
    check('archived_run_has_declared_outcome',proof['status']==statuses[outcome])
    if outcome=='instrument_timeout':check('preserved_export_client_timeout',proof.get('error',{}).get('detail')=='Technical control not completed: delivery_pending_export')
    check('recorded_original_and_archive_protection',proof['originals_unchanged']and proof['zip_unchanged'])
    actual={};all_nodes=list(objects(proof))
    prepared={ (n['output_name'],n['output_sha256']):n for n in all_nodes if n.get('schema')=='EO02.local_worker.receipt.v2'and n.get('operation')=='prepare'}
    for i,row in enumerate(index['files']):
        data=(root/row['file']).read_bytes();check('actual_worker_file_'+str(i),len(data)==row['bytes']and hashlib.sha256(data).hexdigest()==row['sha256']);actual[(row['name'],row['sha256'])]=data
    for node in all_nodes:
        if all(k in node for k in('raw','state','s_reg','direction','semantic')):
            key=hashlib.sha256(canonical(node)).hexdigest()
            if key not in observations:
                f=fields(node['raw']);observations[key]=f;check('RAW_'+key,all(node[k]==v for k,v in f.items()))
        if 'observations'in node and'choice'in node and isinstance(node['observations'],list)and node['observations']and all(isinstance(o,dict)and'raw'in o for o in node['observations']):
            key=hashlib.sha256(canonical(node)).hexdigest()
            if key in readers:continue
            obs=node['observations'];expected={(15+2*x,17,15+2*z):(x,1,z)for x in(-1,0,1)for z in((0,-1)if len(obs)==6 else(0,))};c=[]
            check('fixed_scalar_geometry_'+key,len(obs)in(3,6)and{tuple(o['site'])for o in obs}==set(expected))
            for o in obs:
                f=fields(o['raw']);d=expected.get(tuple(o['site']))
                if d and f['state']and f['semantic']==1 and f['direction']==list(d):c.append(d[0])
            decoded=c[0]if len(c)==1 else None;check('scalar_reader_'+key,node['choice']==decoded);readers[key]={'kind':'native_three_or_six_fixed_gates','choice':decoded,'candidates':c}
        if 'panel'in node and'formed_native_command'in node and isinstance(node['panel'],list)and node['panel']:
            key=hashlib.sha256(canonical(node)).hexdigest()
            if key in readers:continue
            mixed='observation'in node['panel'][0];obs=[p['observation']if mixed else p for p in node['panel']];c=[]
            if mixed:
                allowed={(33+4*x,33+4*y,33+z):(x,y,z)for x,y in((1,0),(0,1),(1,1),(-1,1),(1,-1),(-1,-1))for z in(-1,1)}
            else:
                allowed={(33+4*x,33+4*y,33+z):(0,0,z)for x,y in((1,0),(0,1),(1,1),(-1,1),(1,-1),(-1,-1))for z in(-1,1)}
            check('fixed_twelve_memory_geometry_'+key,len(obs)==12 and{tuple(o['site'])for o in obs}==set(allowed))
            for o in obs:
                f=fields(o['raw']);d=allowed.get(tuple(o['site']))
                if d and f['state']and f['semantic']==1 and f['direction']==list(d):c.append(d[2])
            decoded=c[0]if len(c)==1 else None;check('memory_reader_'+key,node['formed_native_command']==decoded);readers[key]={'kind':'auxiliary_mixed_direction'if mixed else'explicit_context_pureZ','command':decoded,'candidates':c}
        if node.get('schema')=='EO02.local_worker.receipt.v2':
            key=hashlib.sha256(canonical(node)).hexdigest()
            if key in workers:continue
            values=node['raw_observations'];content=bytes(values)*max(1,32+sum(values[::2]));output=zlib.compress(content,9)if node['worker']==1 else hashlib.sha256(content).digest()
            check('worker_bytes_'+key,actual.get((node['output_name'],node['output_sha256']))==output and len(output)==node['output_bytes']and hashlib.sha256(content).hexdigest()==node['input_sha256'])
            if node['operation']in('prepare','execute_service'):
                expected=1 if sum(values[::2])+node['modelled_capacity_credit_not_actor_input']>=sum(values[1::2])else-1
                check('worker_environment_law_'+key,node['accepted']==(node['worker']==expected))
            elif node['operation']=='verify_commit':
                pc=node['prepared_artifact_check'];identity=(pc['name'],pc['sha256']);pre=prepared.get(identity);data=actual.get(identity)
                same_payload=pre is not None and pre['input_sha256']==node['input_sha256']and pre['raw_observations']==values
                valid=False
                if data is not None and pre is not None:
                    try:valid=(zlib.decompress(data)==content)if pre['worker']==1 else(data==hashlib.sha256(content).digest())
                    except zlib.error:valid=False
                accepted=bool(same_payload and valid and node['worker']!=pre['worker'])
                check('worker_actual_prepared_file_'+key,data is not None and len(data)==pc['bytes']and pc['actual_file_read']and pc['valid']==valid)
                check('worker_verify_commit_law_'+key,node['accepted']==accepted and node['transaction_completed']==accepted)
            workers[key]={'operation':node['operation'],'native_tick':node['native_tick'],'worker':node['worker'],'accepted':node['accepted'],'commit':node['transaction_completed'],'bytes':len(output)}
    service=proof.get('service_sequence',{});continuity=service.get('pending_reload_verified',{})
    if outcome!='instrument_timeout':check('archived_pending_continuation_verified',all(continuity.get(k)is True for k in('physical_fields_identical','external_protocol_exact_SHA_identical','no_new_world_or_T0','same_literal_finish_not_requeued')))
    return {'schema':'DEE.unified.exact_archive.portable_recalculation.v1','issues':issues,'checks':checks,'declared_archived_outcome':outcome,'RAW_observation_objects_checked':len(observations),'reader_objects_checked':len(readers),'readers':readers,'worker_receipt_objects_checked':len(workers),'workers':list(workers.values()),'recorded_functional_issues':service.get('functional_issues',[]),'recorded_zip':{'sha256':proof['zip_sha256'],'bytes':proof.get('zip_bytes')},'sources':[{'file':n,'sha256':hashlib.sha256((root/n).read_bytes()).hexdigest()}for n in(proof_name,'ARCHIVOS_REALES.json')],'scope':'Archived arithmetic only. Duplicate receipt/reader dictionaries copied in stdout are counted once by their exact canonical content, not as independent lives. The full ZIP, native snapshots, SQLite and source originals remain omitted and are not re-opened by this calculation. An archived instrumental timeout is explicitly negative and is not relabelled successful; continuation has a separate identity/receipt. Functional failures, if any, remain separate from integrity discrepancies; no semantic target is fed back to DEE.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);p.add_argument('--prueba',default='VERIFICACION_FULLZIP_EXACTO_R3.json');p.add_argument('--esperado',choices=('completed','continued','instrument_timeout'),default='completed');a=p.parse_args();r=calculate(a.evidencia,a.prueba,a.esperado);a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(r,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'issues':r['issues'],'RAW':r['RAW_observation_objects_checked'],'readers':r['reader_objects_checked'],'worker_receipts':r['worker_receipt_objects_checked'],'functional_issues':r['recorded_functional_issues']}));return bool(r['issues'])

if __name__=='__main__':raise SystemExit(main())
