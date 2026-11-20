"""Archived MAIN goal/FIFO/native-world continuity, stdlib only and zero ticks."""
import argparse,collections,gzip,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
SERVICE='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'
ASSISTANT='DEE.Cognitive.System.1.1.APD02.assistant.R01'
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,p):
    sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values():yield from walk(v)
    elif isinstance(x,list):
        for v in x:yield from walk(v)
def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('Never replace an earlier calculation')
    ev=a.evidence;ctx=read(ev/'CONTEXTO_ARCHIVADO.json');helper=load('goal_primitive_audit',HERE/'auditar_evento_objetivo_apd02_r02.py')
    observer=load('snapshot_array_reconstructor',HERE/'observador_causal_retrospectivo_01.py')
    quality=load('archived_goal_quality',ev.parent/'FUENTES/W1/capacidades/evaluador_calidad_apd02.py')
    issues=[];checks=0
    def check(label,condition):
        nonlocal checks
        checks+=1
        if not condition:issues.append(label)
    states={}
    for rel,item in ctx['state_witnesses'].items():
        path=ev/rel;check(rel+':witness_hash',sha(path)==item['witness_sha256']);s=read(path)
        arrays=observer.frame_arrays(s);del arrays
        check(rel+':source_anchor',s['source_sha256']==item['source_sha256']and s['checksum_valid']is True)
        check(rel+':no_pending_native',s['pending_native']==[])
        s['goal']=json.loads(s['metadata'][ASSISTANT]).get('goal_pending')
        s['service']=json.loads(s['metadata'][SERVICE])
        s['transport_slots']=[json.loads(v)for k,v in s['metadata'].items()if k.startswith(SERVICE+'.queue.')and not json.loads(v).get('empty')]
        states[rel]=s
    windows=[];allrows={};alllogs=[];goals=[];raw_count=0;receipts={};other=[]
    for context in ctx['windows']:
        tag=context['tag'];folder=ev/context['folder'];x=read(folder/'REGISTROS_VENTANA.json.gz');proto=read(folder/'PROTOCOLO.json')
        dump=read(folder/'COLA_EXPORTADA_OBSERVADA.json');exportrows={r['id']:r for r in dump['selected_rows']}
        logs=[json.loads(line)for line in(folder/'ADMISIONES.jsonl').read_text(encoding='utf8').splitlines()if line];alllogs.extend(logs)
        check(tag+':closed_owner',not x['owner_final']['running']and x['owner_returncode']==0 and x['job_final']['job_active_processes']==0 and not x.get('forced_own_job_close'))
        check(tag+':source_freeze',x['sources_unchanged']and x.get('error')is None)
        initial=states[context['initial_state']];export=states[context['export_state']];final=states[context['final_state']]
        check(tag+':exact_named_snapshot_links',initial['source_sha256']==proto['snapshot_sha256']==x['initial']['snapshot_sha256']and final['source_sha256']==x['final']['snapshot_sha256'])
        check(tag+':arrays_match_primary',all(final[k]==x['final']['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')))
        check(tag+':controls_do_not_change_physics',all(export[k]==final[k]for k in('N','tick','RAW_sha256','clocks_sha256','channels','pending_native')))
        check(tag+':goal_unchanged_export_STOP',export['goal']==final['goal'])
        check(tag+':open_epoch_preserved',not final['service']['closed_epoch']and final['service']['epoch']==x['owner_final']['epoch'])
        # An export DB legitimately captures its own row processing. Validate
        # the exact committed outbox receipt; do not execute or replay it.
        exportid=x['export']['id'];receipt=export['service']['last_completed_receipt'];outbox=folder/'OUTBOX_EXPORT_ORIGINAL.json'
        check(tag+':processing_export_committed_outbox',exportrows[exportid]['status']=='processing'and receipt['id']==exportid and receipt['result_sha256']==sha(outbox))
        check(tag+':processing_export_payload',receipt['payload_sha256']==exportrows[exportid]['payload_sha'])
        exported_body=read(outbox);actual_export=x['export']
        check(tag+':processing_export_outbox_exact',exported_body=={k:v for k,v in actual_export.items()if k not in('committed_snapshot','paired_export')})
        for identifier,row in x['records'].items():
            if identifier.endswith('_parsed'):continue
            parsed=json.loads(row['result']);check(tag+identifier+':terminal_transport',row['status']=='completed'and parsed['id']==identifier==row['id'])
            check(tag+identifier+':payload_hash',hashlib.sha256(row['payload'].encode()).hexdigest()==row['payload_sha'])
            if identifier+'_parsed'in x['records']:check(tag+identifier+':parsed_mirror',parsed==x['records'][identifier+'_parsed'])
            if identifier in allrows:check(identifier+':same_transport_not_requeued',allrows[identifier]==row)
            allrows[identifier]=row
            for node in walk(parsed):
                if 'raw'in node and'site'in node:
                    f=helper.decode(node['raw']);raw_count+=1
                    for k,v in f.items():
                        if k in node:check(tag+identifier+':decoded_'+k,node[k]==v)
                rec=node.get('receipt')
                if isinstance(rec,dict)and'id'in rec:
                    key=str(rec['id']);previous=receipts.get(key)
                    if previous is None or previous['status']=='scheduled':receipts[key]=rec
                    elif rec['status']!='scheduled':check(tag+identifier+':terminal_native_receipt_stable',previous==rec)
            result=parsed.get('result',{});rows=result.get('rows',[]);payload=json.loads(row['payload'])
            for slot,item in enumerate(rows):
                mode=payload['situaciones'][slot]['modo'];kind=item.get('kind')
                if kind=='APD02_native_goal_opportunities':
                    expected=item['operational_environment_state']['private_environment']['second'];events=[]
                    for op in item['result']['opportunities']:
                        key=tag+':'+identifier+':'+str(slot)+':'+str(op['opportunity']);artifact=ctx['artifacts'].get(key)
                        directory=ev/artifact['directory']if artifact else None
                        audited=helper.audit_goal_opportunity(op,artifact_directory=directory,quality_module=quality,expected_second=expected)
                        check(key+':goal_primitive',not audited['issues']);events.append(audited)
                        # The words and route query sources carry only generic
                        # resources. A coincident payload5 is not a b sensor.
                        check(key+':generic_word_sources',all(r['value']in(5,7)for r in op['word']['requests']))
                        check(key+':generic_route_sources',all(r['payload']in(0,5)for r in op['native_selection']['requests']))
                    goals.append({'tag':tag,'id':identifier,'slot':slot,'mode':mode,'events':events,'goal_state_after':item['operational_environment_state'],
                        'before':item['before'],'after':item['after'],'goal_completed':item['operational_environment_state']['progress']['verified_file_goal_completed']})
                elif kind=='explicit_external_goal_initialization':
                    check(identifier+':initialization_zero_ticks',item['native_ticks']==0)
                    other.append({'id':identifier,'kind':kind,'public':item['public_observation'],'progress':item['progress']})
                elif kind=='APD02_quality_request':
                    key=tag+':'+identifier+':'+str(slot)+':0';directory=ev/ctx['artifacts'][key]['directory'];effect=item['committed_effect']
                    request={'task_id':effect['task_id'],'text':item['literal_form'],'operands':item['raw_operands']}
                    report=quality.evaluate_literal_committed(request,effect,sandbox_root=directory,policy={'max_operand':32,'max_artifact_bytes':4096,'max_price':2,'max_delay_ticks':8,'resource_limits_required_for_success':True})
                    check(key+':new_input_actual_file',all(report[k]==item['quality'][k]for k in report if k!='evaluation_resources'))
                    sign=helper.physical_word(item['word']['reader']);route=helper.physical_action(item['route']['reader'])
                    check(key+':new_input_operation_and_route',item['selected_operation']==('add'if sign==1 else'sub')and item['selected_procedure']==('native'if route==-1 else'external'))
                    if item['native_numeric']is not None:check(key+':new_input_actual_native_number',helper.physical_number(item['native_numeric'])==effect['used_value'])
                    other.append({'id':identifier,'kind':kind,'operands':item['raw_operands'],'actual':effect['used_value'],'quality':report['feedback']['category'],'completed':report['task_success']})
                elif mode=='apd02-lenguaje':
                    sign=helper.physical_word(item['word']['reader']);interaction=item['interaction']
                    check(identifier+':new_functions_follow_sign',interaction['kind']==('native_current_selection'if sign==1 else'query'))
                    other.append({'id':identifier,'kind':kind,'form':item['literal_form'],'choice':sign,'interaction_kind':interaction['kind']})
                elif mode=='apd02-acumular':
                    frame=item['frames'][-1];values=[]
                    for ob in frame['reader']['sites']:
                        f=helper.decode(ob['raw'])
                        if f['state']and f['semantic']==1 and f['direction']==[0,1,0]:values.append(f['s_reg']-4096)
                    value=values[0]if len(values)==1 else None
                    check(identifier+':renewal_actual_RAW',value==item['numeric_result']and item['legacy_uses_after']==item['legacy_uses_before']+1)
                    other.append({'id':identifier,'kind':kind,'increment':item['increment'],'actual':value,'delay_periods':item['delay_periods'],'cursor_before':item['legacy_uses_before'],'cursor_after':item['legacy_uses_after']})
        windows.append({'tag':tag,'primary_sha256':sha(folder/'REGISTROS_VENTANA.json.gz'),'initial':x['initial'],'final':x['final'],
            'owner_initial':x['owner_initial'],'owner_final':x['owner_final'],'pending':x['pending'],'proto':proto,'logs':logs,'queue_export':dump,
            'export_processing_reconciliation_eligible_not_reexecuted_by_auditor':True,'states':context})
    w1,w2=windows;one=states[w1['states']['final_state']];two=states[w2['states']['initial_state']]
    check('cross_process_exact_native_file',w1['final']['snapshot_sha256']==w2['initial']['snapshot_sha256']==one['source_sha256']==two['source_sha256'])
    check('cross_process_distinct_PID',w1['owner_final']['pid']!=w2['owner_initial']['pid'])
    check('cross_process_exact_goal_world',one['goal']==two['goal'])
    pending=w1['pending'];expected=w2['proto']['expected_initial_pending']
    check('one_declared_pending',len(pending)==len(expected)==1 and pending[0]['id']==expected[0]['id']and json.loads(pending[0]['payload'])==expected[0]['payload'])
    identifier=pending[0]['id'];completed=allrows[identifier]
    fixed=('id','seq','payload','payload_sha','arrived_utc','arrived_ns','is_control')
    check('pending_FIFO_identity_preserved',all(pending[0][k]==completed[k]for k in fixed)and completed['status']=='completed')
    check('pending_admitted_once_across_windows',sum(r['id']==identifier for r in alllogs)==1 and not any(r['id']==identifier for r in w2['logs']))
    check('native_pending_slot_exact',any(s['id']==identifier and s['payload']==expected[0]['payload']and s['payload_sha256']==pending[0]['payload_sha']for s in one['transport_slots']))
    resumed=next(g for g in goals if g['id']==identifier);old=one['goal'];first=resumed['events'][0]
    check('goal_counter_and_public_data_not_restarted',first['opportunity']==old['progress']['opportunities_used']+1 and first['public_before']==old['public'])
    check('new_input_after_exact_pending_completion',next(r for k,r in allrows.items()if k.endswith('new_request_boundary'))['started_utc']>=completed['finished_utc'])
    check('no_final_pending_or_uncertain',w2['pending']==[]and not w2['owner_final']['uncertain_external_result'])
    material=sorted((r for r in allrows.values()if not r['is_control']),key=lambda r:r['seq'])
    check('material_FIFO_by_original_seq',[r['started_utc']for r in material]==sorted(r['started_utc']for r in material))
    status=collections.Counter(r['status']for r in receipts.values())
    result={'schema':'APD02.MAIN.goal_pending_fifo.archive.R01','new_native_ticks':0,'engine_imported':False,'issues':issues,'checks':checks,
        'RAW_observations_checked':raw_count,'unique_native_requests':len(receipts),'native_admission':dict(status),
        'transport':{'new_admissions':len(alllogs),'unique_new_ids':len({r['id']for r in alllogs}),'completed_rows':len(allrows),
            'material_completed':len(material),'control_completed':sum(bool(r['is_control'])for r in allrows.values()),'same_pending_id':identifier,'pending_was_requeued':False},
        'goal_results':goals,'other_functions':other,'cross_process':{'first_pid':w1['owner_final']['pid'],'second_pid':w2['owner_initial']['pid'],
            'first_final_snapshot':w1['final']['snapshot_sha256'],'second_initial_snapshot':w2['initial']['snapshot_sha256'],
            'same_world_id':w1['final']['world_id']==w2['initial']['world_id'],'same_goal_state':one['goal']==two['goal'],
            'pending_original_seq':pending[0]['seq'],'first_counter':old['progress']['opportunities_used'],'resumed_first_opportunity':first['opportunity']},
        'continuity_final':w2['final'],'scope':['Archived current MAIN execution, not AUX learning transferred to MAIN',
            'Snapshot field witnesses retain full RAW/clocks/interfaces/pending/metadata; historical native receipt ledgers are omitted, so they are not resumable backups',
            'Exact original full native snapshot SHA links both owners; metadata/history differs legitimately across export and STOP controls',
            'Export processing row has exact committed outbox eligibility; this auditor never imports/reexecutes it and the actual next owner used the postSTOP journal',
            'Private b is legitimate external-world operational state, not supplied to native word/route codecs before QUERY',
            'ACT/QUERY codec, goal criterion, opportunities, arithmetic and stopping remain prepared; no missing-data semantic detection/general planner claimed']}
    with a.output.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,sort_keys=True,indent=2)
    print(json.dumps({'issues':issues,'checks':checks,'RAW':raw_count,'native_requests':len(receipts),'admission':dict(status),'goal_parts':len(goals),'same_pending':identifier},ensure_ascii=False))
    if issues:raise SystemExit(1)
if __name__=='__main__':main()
