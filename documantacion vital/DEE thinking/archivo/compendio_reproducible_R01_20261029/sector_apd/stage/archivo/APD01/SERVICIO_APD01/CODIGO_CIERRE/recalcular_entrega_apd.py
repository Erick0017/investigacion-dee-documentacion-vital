"""Portable recalculation of the final exact-FullZIP operational proof.

Reads archived physical observations and actual exported artifact bytes only.
Does not import DEE, open an operational journal, invoke a tool or repeat work.
"""
import argparse,hashlib,importlib.util,json,zlib
from pathlib import Path

spec=importlib.util.spec_from_file_location('portable_exact_APD',Path(__file__).with_name('auditar_apd_resultados_r04.py'));apd=importlib.util.module_from_spec(spec);spec.loader.exec_module(apd)

def load(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')
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

def calculate(root):
    proof=load(root/'PRUEBA_FULL.json');index=load(root/'ARCHIVOS_REALES.json');protocol=load(root/'PROTOCOLO_FULL_FIJO.json');prospective=load(root/'PROTOCOLO_MATERIAL_PROSPECTIVO_ORIGINAL.json');service=proof.get('service_sequence',{});checks={};issues=[];observations={};readers={};worker_rows={};apd_rows={};actual={}
    def check(name,value):
        checks[name]=bool(value)
        if not value:issues.append(name)
    check('recorded_exact_archive_operational_completion',proof['status']=='COMPLETED_WITH_RECORDED_SCOPE')
    check('recorded_source_and_archive_protection',proof['originals_unchanged']and proof['zip_unchanged'])
    check('bound_literal_settings_are_the_executed_settings',protocol['service_protocol']==service['protocol'])
    material=dict(protocol['service_protocol']);material['auditor_form_signs_from_closed_results']={};check('prospectively_frozen_material_requests_not_changed',material==prospective['service_protocol']and sha(root/'PROTOCOLO_MATERIAL_PROSPECTIVO_ORIGINAL.json')==protocol['approved_material_protocol_sha256'])
    nodes=list(objects(proof));prepared={(x['output_name'],x['output_sha256']):x for x in nodes if x.get('schema')=='EO02.local_worker.receipt.v2'and x.get('operation')=='prepare'}
    for i,row in enumerate(index['files']):
        data=(root/row['file']).read_bytes();check('actual_artifact_'+str(i),len(data)==row['bytes']and hashlib.sha256(data).hexdigest()==row['sha256']);actual[(row['name'],row['sha256'])]=data
    for node in nodes:
        key=hashlib.sha256(canonical(node)).hexdigest()
        if all(k in node for k in('raw','state','s_reg','direction','semantic'))and key not in observations:
            f=apd.unpack(node['raw']);observations[key]=f;check('raw_'+key,node['state']==(int(node['raw'])&0xffffffff)and node['s_reg']==f['payload']and node['direction']==f['direction']and node['semantic']==f['semantic'])
        if node.get('kind')in('APD01_integrated_request','APD01_prepared_count','APD01_assisted_composition')and key not in apd_rows:
            audit=apd.audit(node,root/'ARTEFACTOS');check('APD_'+key,not audit['issues']);apd_rows[key]=audit
        if 'observations'in node and'choice'in node and isinstance(node['observations'],list)and len(node['observations'])in(3,6)and key not in readers:
            obs=node['observations'];site_set={tuple(o['site'])for o in obs};origins=[o for o in((15,15,15),(15,45,15))if site_set=={(o[0]+2*x,o[1]+2,o[2]+2*z)for x in(-1,0,1)for z in((0,-1)if len(obs)==6 else(0,))}]
            check('fixed_selector_geometry_'+key,len(origins)==1)
            if len(origins)==1:
                origin=origins[0];cs=[]
                for o in obs:
                    f=apd.unpack(o['raw']);d=[(o['site'][0]-origin[0])//2,1,(o['site'][2]-origin[2])//2]
                    if f['active']and f['semantic']==1 and f['direction']==d:cs.append(d[0])
                decoded=cs[0]if len(cs)==1 else None;check('selector_'+key,node['choice']==decoded);readers[key]={'kind':'fixed_selector','origin':origin,'command':decoded,'candidates':cs}
        if 'panel'in node and'formed_native_command'in node and isinstance(node['panel'],list)and len(node['panel'])==12 and key not in readers:
            obs=node['panel'];mixed='observation'in obs[0];allowed={(33+4*x,33+4*y,33+z):(x,y,z)if mixed else(0,0,z)for x,y in((1,0),(0,1),(1,1),(-1,1),(1,-1),(-1,-1))for z in(-1,1)};raws=[v['observation']if mixed else v for v in obs];cs=[]
            check('fixed_old_memory_geometry_'+key,{tuple(o['site'])for o in raws}==set(allowed))
            for o in raws:
                f=apd.unpack(o['raw']);d=allowed.get(tuple(o['site']))
                if d and f['active']and f['semantic']==1 and f['direction']==list(d):cs.append(d[2])
            command=cs[0]if len(cs)==1 else None;check('memory_'+key,node['formed_native_command']==command);readers[key]={'kind':'memory','command':command,'candidates':cs}
        if node.get('schema')=='EO02.local_worker.receipt.v2'and key not in worker_rows:
            values=node['raw_observations'];content=bytes(values)*max(1,32+sum(values[::2]));output=zlib.compress(content,9)if node['worker']==1 else hashlib.sha256(content).digest();check('worker_output_'+key,actual.get((node['output_name'],node['output_sha256']))==output and len(output)==node['output_bytes']and hashlib.sha256(content).hexdigest()==node['input_sha256'])
            if node['operation']in('prepare','execute_service'):
                preferred=1 if sum(values[::2])+node['modelled_capacity_credit_not_actor_input']>=sum(values[1::2])else-1;check('worker_law_'+key,node['accepted']==(node['worker']==preferred))
            elif node['operation']=='verify_commit':
                pc=node['prepared_artifact_check'];pre=prepared.get((pc['name'],pc['sha256']));data=actual.get((pc['name'],pc['sha256']));valid=False;same=pre is not None and pre['input_sha256']==node['input_sha256']and pre['raw_observations']==values
                if pre and data is not None:
                    try:valid=zlib.decompress(data)==content if pre['worker']==1 else data==hashlib.sha256(content).digest()
                    except zlib.error:valid=False
                accepted=bool(same and valid and node['worker']!=pre['worker']);check('worker_prepared_bytes_'+key,data is not None and len(data)==pc['bytes']and pc['valid']==valid and pc['actual_file_read']);check('worker_commit_'+key,node['accepted']==accepted and node['transaction_completed']==accepted)
            worker_rows[key]={'operation':node['operation'],'accepted':node['accepted'],'commit':node['transaction_completed'],'worker':node['worker'],'native_tick':node['native_tick']}
    first=service.get('saved_pending',{}).get('committed_snapshot');second=service.get('reloaded_pending',{}).get('committed_snapshot');check('pending_reload_has_actual_witnesses',bool(first and second))
    if first and second:check('same_physical_and_serialized_pending_after_process_reload',first['physical']==second['physical']and first['operational_dependencies']==second['operational_dependencies']and first['operational_dependencies']['external_pending_present']and first['operational_dependencies']['cascade_pending_present'])
    continuation=service.get('pending_reload_verified',{});check('same_existing_FINISH_not_requeued',all(continuation.get(k)is True for k in('physical_fields_identical','external_protocol_exact_SHA_identical','no_new_world_or_T0','same_literal_finish_not_requeued')))
    jobs=service.get('owned_job_closed_resources',[]);check('two_owned_trees_closed_without_hidden_retry',len(jobs)==2 and all(x['resource'].get('job_active_processes')==0 for x in jobs)and not service.get('forced_exclusive_owned_job_cleanup'))
    clients=service.get('apd_before',[])+service.get('apd_after_reload',[]);check('actual_new_assistant_client_used',bool(clients)and all(x.get('new_assistant_launcher_actually_used')is True and x.get('actual_literal_client_argv',[None])[0]=='asistente'for x in clients))
    client_shas={x['launcher_sha256_from_exact_extraction']for x in clients};check('literal_client_source_bytes_exported',client_shas=={sha(root/'CODIGO/arrancar.py')})
    def memory_map(value):
        native=json.loads(value['request']['result'])['result'];rows=[x['result']['rows'][0]for x in native['rows']];contexts=[x['context_signal']for x in rows];expected=[x['contexto']for x in service['protocol']['old_panel']]
        if len(contexts)!=len(expected)or len(set(contexts))!=len(contexts)or set(contexts)!=set(expected):raise ValueError('Exact unique old-memory contexts are not preserved')
        return{x['context_signal']:x['reader']['formed_native_command']for x in rows}
    memory={key:memory_map(service[name])for key,name in(('before','old_panel_before'),('after_explicit_teaching','old_panel_after_teaching'),('after_reload','old_panel_after_reload'))};check('memory_maps_reconstructed_from_actual_reader_rows',all(service['memory_delivery_assertions'][key]==value for key,value in memory.items()))
    witness=protocol['offline_history_witness']['source_last_memory_observations'];source_history={key:value['expected_from_declared_history']for key,value in witness.items()};target=service['protocol']['declared_teaching']['contexto'];sign=service['protocol']['declared_teaching']['senal'];expect_after={key:sign if key==target else value for key,value in memory['before'].items()}
    memory_scope={'actual_reader_maps':memory,'expected_taught_history_from_source_witness':source_history,'initial_contexts_matching_source_history':{key:memory['before'].get(key)==value for key,value in source_history.items()},'after_teacher_and_reload_match_expected_change':{key:memory['after_explicit_teaching'].get(key)==value and memory['after_reload'].get(key)==value for key,value in expect_after.items()},'teacher_target_initially_differs':memory['before'].get(target)!=sign,'scope':'Functional observations, not integrity conditions: an already equal target does not demonstrate a new revision; no failing sign is repaired or fed to the actor.'}
    fences=[x['INSTRUMENTO_FENCE']for x in nodes if'INSTRUMENTO_FENCE'in x];check('truthful_python_hook_receipts_not_OS_sandbox',bool(fences)and all(not f['denied']and f.get('no_lab_evidence_or_history_reads_allowed')is False and f.get('operational_history_reads_universally_blocked')is False and f.get('no_undeclared_external_lab_or_evidence_reads_allowed')is True for f in fences))
    return {'schema':'DEE.APD01.exact_FullZIP_archived_recalculation.v1','checks':checks,'issues':issues,'RAW_observation_objects_checked':len(observations),'fixed_reader_objects_checked':len(readers),'readers':readers,'APD_uses_and_compositions_checked':len(apd_rows),'APD_results':list(apd_rows.values()),'worker_receipt_objects_checked':len(worker_rows),'workers':list(worker_rows.values()),'memory_functional_observations':memory_scope,'recorded_functional_issues':service.get('functional_issues',[]),'recorded_archive':{'sha256':proof['zip_sha256'],'bytes':proof.get('zip_bytes')},'sources':[{'file':n,'sha256':sha(root/n)}for n in('PRUEBA_FULL.json','ARCHIVOS_REALES.json','PROTOCOLO_FULL_FIJO.json','PROTOCOLO_MATERIAL_PROSPECTIVO_ORIGINAL.json','CODIGO/arrancar.py')],'scope':'Recalculation of exported uint64/readers and actual bytes only. Repeated dictionaries are deduplicated by canonical content, not counted as lives. Native snapshots, journals, engine and FullZIP are omitted and not re-opened; their hashes and protection are archived operational receipts, not freshly reverified here. Word history, arithmetic conditional on operator, artifact completion and modeled cost remain separate. No Runtime, external tool, action or repaired response is executed.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();r=calculate(a.evidencia)
    with a.salida.open('x',encoding='utf8')as f:json.dump(r,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'issues':r['issues'],'RAW':r['RAW_observation_objects_checked'],'APD':r['APD_uses_and_compositions_checked']}));raise SystemExit(bool(r['issues']))
