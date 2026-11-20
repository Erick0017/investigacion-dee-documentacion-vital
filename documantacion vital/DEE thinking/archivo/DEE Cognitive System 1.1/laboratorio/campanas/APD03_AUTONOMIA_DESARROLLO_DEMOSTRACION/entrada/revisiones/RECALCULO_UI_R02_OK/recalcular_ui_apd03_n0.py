"""Auditoría portable de primarios de la entrada APD03; cero motor/ticks.

Reconstruye lectores fijos desde RAW, verifica el transporte literal y lee el
JSON realmente producido. No ejecuta una política, proveedor, enseñanza ni DEE.
"""
import argparse
from collections import Counter
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path

N=67
I=(33,33,33);J=(47,47,47);H=(47,17,47)
CONTEXTS={'alfa':(1,0,0),'beta':(0,1,0),'gamma':(1,1,0),'delta':(-1,1,0),'epsilon':(1,-1,0),'zeta':(-1,-1,0)}
FORMS={**{f:(I,v)for f,v in CONTEXTS.items()},'suma':(I,(-1,0,0)),'diferencia':(I,(0,-1,0)),'agrega':(J,(-1,0,0)),'resta':(J,(0,-1,0)),'total':(J,(1,0,0)),'quita':(J,(0,1,0)),'compara':(H,(1,0,0)),'recuerda':(H,(0,1,0))}
PARENT='64359d48edd49f8a1f5616ceacd04c4479a27383877c23381e217a39f0cc05a9'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def read(path):
    path=Path(path);b=path.read_bytes()
    return json.loads(gzip.decompress(b)if path.suffix=='.gz'else b)
def walk(x,path='$'):
    yield path,x
    if isinstance(x,dict):
        for k,v in x.items():yield from walk(v,path+'.'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from walk(v,path+'['+str(i)+']')
def decoded(o):
    n=int(o['raw'])
    if not 0<=n<2**64:raise ValueError('RAW no uint64')
    return{'state':n&0xffffffff,'semantic':(n>>60)&15,'s_reg':(n>>32)&65535,'direction':[((n>>k)&15)-(16 if((n>>k)&15)>=8 else 0)for k in(48,52,56)],'active':bool(n&0xffffffff)}
def pos(o,v,k,z=0):return tuple((o[j]+k*v[j]+(z if j==2 else 0))%N for j in range(3))
def pure_z(reader,codec):
    expected={pos(o,v,4,sg):sg for o,v in codec.values()for sg in(-1,1)}
    sites=[tuple(o['site'])for o in reader['panel']]
    if len(sites)!=len(expected)or set(sites)!=set(expected):raise ValueError('Conjunto de puertas fijo incompleto')
    candidates=[]
    for o in reader['panel']:
        d=decoded(o);sg=expected[tuple(o['site'])]
        if d['state']and d['semantic']==1 and d['direction']==[0,0,sg]:candidates.append({'site':o['site'],'sign':sg,'s_reg':d['s_reg']})
    return candidates[0]['sign']if len(candidates)==1 else None,candidates
def route_r04(reader):
    expected={(25+2*x,15,53):x for x in(-1,0,1)}
    obs=reader['observations'];sites=[tuple(o['site'])for o in obs]
    if len(sites)!=3 or set(sites)!=set(expected):raise ValueError('Tres puertas R04 distintas')
    cs=[]
    for o in obs:
        d=decoded(o);x=expected[tuple(o['site'])]
        if d['state']and d['semantic']==1 and d['direction']==[x,1,0]:cs.append(x)
    return cs[0]if len(cs)==1 else None,cs

def calculate(folder):
    folder=Path(folder);index=read(folder/'INDICE_PRIMARIOS.json');issues=[];checks=0
    def check(label,condition):
        nonlocal checks
        checks+=1
        if not condition:issues.append(label)
    for item in index['members']:
        p=folder/item['file'];check('bytes:'+item['file'],p.stat().st_size==item['bytes']);check('sha:'+item['file'],sha(p)==item['sha256'])
        if item.get('compression')=='gzip_exact_original_bytes':
            original=gzip.decompress(p.read_bytes());check('decoded_bytes:'+item['file'],len(original)==item['original_bytes']);check('decoded_sha:'+item['file'],hashlib.sha256(original).hexdigest()==item['original_sha256'])
    events=[json.loads(line)for line in gzip.decompress((folder/'SESIONES_ORIGINALES.jsonl.gz').read_bytes()).decode('utf8').splitlines()if line]
    before=read(folder/'ANTES_DEL_PRIMER_TICK.json');operational=read(folder/'RESULTADOS_OPERATIVOS.json');cuts=[read(folder/('CORTE_'+str(i)+'.json'))for i in(0,1)];runs=[read(folder/('EJECUCION_'+str(i)+'.json'))for i in(0,1)]
    life=before['life'];check('explicit_life',life=='DIAG_APD03_UI_R01');check('all_events_same_life',all(e['life_id']==life for e in events))
    imports=[e for e in events if e['event']=='explicit_complete_paired_import'];reopens=[e for e in events if e['event']=='same_personal_life_reopened'];starts=[e for e in events if e['event']=='owned_start_paused'];stops=[e for e in events if e['event']=='owned_stop']
    check('one_import_two_starts_one_reopen_two_stops',(len(imports),len(starts),len(reopens),len(stops))==(1,2,1,2))
    check('no_T0',imports[0]['no_T0']is True and imports[0]['source_snapshot_sha256']==PARENT)
    check('no_active_replacement',imports[0]['no_ACTIVO_replacement']is True)
    check('same_world_identity',all(c['record']['life_id']==c['record']['world_id']==life for c in cuts)and reopens[0]['world_id']==life)
    check('same_parent',all(c['record']['parent']['encoded_sha256']==PARENT and c['record']['parent']['source_tick']==548407 for c in cuts))
    check('two_processes',runs[0]['pid']!=runs[1]['pid']and starts[0]['observation']['pid']!=starts[1]['observation']['pid'])
    check('new_then_existing_argv','--nueva'in runs[0]['command']and'--vida'not in runs[0]['command']and'--vida'in runs[1]['command']and'--nueva'not in runs[1]['command'])
    check('all_processes_closed',all(r['returncode']==0 and r['resources']['job_active_processes']==0 for r in runs)and all(s['result']['exit_code']==0 and s['result']['resources']['job_active_processes']==0 for s in stops))
    check('owned_sequential_no_overlap',stops[0]['wall_utc']<reopens[0]['wall_utc']<starts[1]['wall_utc'])
    check('explicit_initial_pause',all(s['started_paused']and s['observation']['paused']and s['observation']['runtime_loads_in_this_process']==1 for s in starts))
    for i,c in enumerate(cuts):
        check('no_pending_or_uncertain:'+str(i),c['protocol']['pending_material']is None and c['protocol']['uncertain_preserved']is False)
        check('cut_equals_recorded_summary:'+str(i),operational['cuts'][i]==c)
    pkeys=('N','tick','RAW_sha256','clocks_sha256')
    check('same_loaded_full_physical_fingerprint',all(starts[1]['observation']['physical'][k]==cuts[0]['record']['physical'][k]for k in pkeys))
    check('same_saved_tick',starts[1]['observation']['last_saved_tick']==cuts[0]['record']['physical']['tick']==reopens[0]['tick'])
    check('same_protocol_epoch',starts[0]['observation']['epoch']==starts[1]['observation']['epoch']==6)
    check('not_reimported_after_reload',all(sum(op['kind']=='IMPORT_COMPLETE_STATE'for op in c['record']['operations'])==1 for c in cuts))
    check('actual_ticks',[c['record']['physical']['tick']for c in cuts]==[550353,550490])
    check('root_end_attestation',operational['same_sources_before_after']and operational['protected_originals_unchanged'])
    for source in before['sources']:
        p=folder/'CODIGO_EJECUTADO'/Path(source['file']).name
        check('frozen_source:'+source['file'],p.stat().st_size==source['bytes']and sha(p)==source['sha256'])
    # Sólo se recorren una vez los resultados por ID, no stdout ni espejos.
    admissions=[e for e in events if e['event']in('literal_control','literal_material_submission')]
    responses=[e for e in events if e['event']in('control_result','literal_material_result')]
    check('one_submission_per_id',len({e['id']for e in admissions})==len(admissions))
    check('one_result_per_id',len({e['id']for e in responses})==len(responses))
    check('same_submitted_result_IDs',{e['id']for e in admissions}=={e['id']for e in responses})
    by_id={e['id']:e for e in responses};raw_count=0;raw_unique={};receipts={};readers=[];parsed_by_id={};receipt_versions={}
    for event in admissions:
        key=event['id'];response=by_id[key];row=response['result']['request'];parsed=json.loads(row['result']);payload=json.loads(row['payload']);parsed_by_id[key]=parsed
        expected=event['payload']if event['event']=='literal_material_submission'else{'operacion':event['operation']}
        check(key+':literal_payload',payload==expected);check(key+':payload_sha',hashlib.sha256(canonical(payload).encode()).hexdigest()==row['payload_sha']);check(key+':same_id',key==row['id']==parsed['id'])
        check(key+':completed',row['status']=='completed'and response['result']['admission']=='queued');check(key+':epoch',parsed['owner_epoch']==6)
        check(key+':result_committed_world',parsed['committed_snapshot']['life_id']==life)
        for path,node in walk(parsed):
            if not isinstance(node,dict):continue
            if 'raw'in node and'site'in node and'tick'in node:
                raw_count+=1;d=decoded(node)
                for field,value in d.items():
                    if field in node:check(key+path+':RAW_'+field,node[field]==value)
                if'clock'in node:check(key+path+':clock_uint64',0<=int(node['clock'])<2**64)
                stamp=(tuple(node['site']),int(node['tick']));value=(str(node['raw']),str(node.get('clock')))
                if stamp in raw_unique:check(key+path+':same_site_tick',raw_unique[stamp]==value)
                else:raw_unique[stamp]=value
            if isinstance(node.get('receipt'),dict)and'id'in node['receipt']:
                r=node['receipt'];rid=r['id'];entry={k:r.get(k)for k in('id','kind','requested_tick','effective_tick','status','reason','channels')}
                receipt_versions.setdefault(rid,[]).append(entry)
                if rid in receipts:
                    prior=receipts[rid];fixed=('id','kind','requested_tick','channels')
                    check(key+path+':same_requested_input',all(prior[k]==entry[k]for k in fixed))
                    # El registro de ruta se tomó antes de las entradas futuras;
                    # la consecuencia posterior conserva sus recibos terminales.
                    # Scheduled no es un segundo input ni un rechazo definitivo.
                    if prior['status']=='scheduled'and entry['status']!='scheduled':receipts[rid]=entry
                    elif prior['status']!='scheduled'and entry['status']=='scheduled':pass
                    else:check(key+path+':same_receipt_stage',prior==entry)
                else:receipts[rid]=entry
                if'id'in node:check(key+path+':receipt_id',node['id']==rid)
                if'tick'in node:check(key+path+':receipt_tick',node['tick']==r['requested_tick'])
                if r['status']=='applied':check(key+path+':effective_tick',r['effective_tick']==r['requested_tick'])
            if'formed_native_command'in node and'panel'in node:
                sign,cs=pure_z(node,{f:(I,v)for f,v in CONTEXTS.items()}if len(node['panel'])==12 else FORMS)
                check(key+path+':fixed_reader_sign',sign==node['formed_native_command']);check(key+path+':fixed_reader_candidates',cs==node['candidates']);readers.append({'id':key,'path':path,'sign':sign,'gates':len(node['panel'])})
    material=[e for e in admissions if e['event']=='literal_material_submission'];rows=[parsed_by_id[e['id']]['result']['rows'][0]for e in material]
    check('four_material',[e['payload']['situaciones'][0]['modo']for e in material]==['apd02','apd02-docencia','apd02-lenguaje','apd02-lenguaje'])
    request=material[0]['payload']['situaciones'][0];case=rows[0];word,_=pure_z(case['word']['reader'],FORMS);route,route_candidates=route_r04(case['route']['reader'])
    check('sum_exact_original_request',request=={'modo':'apd02','texto':'suma','operandos':[18,7]});check('sum_operator_from_RAW',word==1==case['native_operator_command']and case['selected_operation']=='add')
    check('selected_external_from_RAW',route==0==case['native_route_command']and case['route']['reader']['choice']==route and case['selected_procedure']=='external')
    receipt=case['committed_effect'];artifact=read(folder/'ARTEFACTOS/task_90.json');artifact_file=folder/'ARTEFACTOS/task_90.json'
    check('one_provider_only',receipt['provider_calls']=={'external':1,'native':0}and receipt['no_dual_execution_or_fallback']is True)
    check('no_native_math_attribution',case['native_numeric']is None and case['external_tool']['not_a_DEE_operation']is True)
    check('real_committed_file',receipt['state']=='committed'and receipt['effect_phase']=='readback'and receipt['fixture_does_not_advance_DEE']is False)
    check('artifact_exact_bytes',sha(artifact_file)==receipt['artifact']['sha256']and artifact_file.stat().st_size==receipt['artifact']['bytes'])
    check('artifact_matches_request',artifact=={'schema':'DEE.APD02.calculation_artifact.v1','task_id':'task_90','operands':[18,7],'operation':'add','procedure':'external','value':25})
    check('sum_number_readback',artifact['value']==receipt['raw_provider_response']['value']==receipt['used_value']==receipt['reported_value']==18+7)
    check('feedback_omitted_not_teacher',case['feedback_mode']=='omit'and case['native_consequence']['mode']=='omit'and not case['native_consequence']['requests'])
    teacher=rows[1];teacher_receipts=teacher['requests'];check('explicit_teacher_minus',teacher['lesson_is_external']and teacher['teacher_sign']==-1 and teacher['kind']=='explicit_APD02_revision')
    check('three_teacher_applied',len(teacher_receipts)==3 and all(r['receipt']['status']=='applied'for r in teacher_receipts))
    check('teacher_hub_not_output_label',decoded(teacher['hub'])['state']>0 and decoded(teacher['hub'])['semantic']==1 and decoded(teacher['hub'])['direction']==[0,0,-1])
    language=[]
    for event,case in zip(material[2:],rows[2:]):
        word,_=pure_z(case['word']['reader'],FORMS);interaction=case['interaction'];answer,_=pure_z(interaction['reader'],{f:(I,v)for f,v in CONTEXTS.items()})
        check(event['id']+':acquired_minus',word==case['native_function_choice']==-1)
        check(event['id']+':history_query_not_current_comparison',interaction['kind']=='query'and interaction['context_signal']=='gamma'and case['operator_supplied_context']=='gamma')
        check(event['id']+':gamma_plus_RAW',answer==1);check(event['id']+':datum_literal',case['public_datum']==23)
        language.append({'id':event['id'],'function_choice_from_RAW':word,'interaction_kind':interaction['kind'],'context_supplied_by_operator':'gamma','historical_answer_from_RAW':answer,'before_tick':parsed_by_id[event['id']]['before_tick'],'after_tick':parsed_by_id[event['id']]['after_tick']})
    parent=read(folder/'HISTORIA_APD02/REGISTROS_VENTANA.json.gz');last=parent['records']['apd02qr_new_functions'];last_parsed=json.loads(last['result']);last_case=last_parsed['result']['rows'][0];last_sign,_=pure_z(last_case['word']['reader'],FORMS)
    check('parent_last_compara_RAW_plus',last_case['literal_form']=='compara'and last_sign==last_case['native_function_choice']==1)
    check('parent_exact_cut',parent['final']['snapshot_sha256']==PARENT and all(parent['final']['physical'][k]==starts[0]['observation']['physical'][k]for k in pkeys))
    later=[]
    for key,row in parent['records'].items():
        if key.endswith('_parsed')or not isinstance(row,dict)or'payload'not in row:continue
        parsed=json.loads(row['result'])
        if parsed['before_tick']>=last_parsed['after_tick']:
            later.extend(json.loads(row['payload']).get('situaciones',[]))
    check('no_later_parent_explicit_compara_teacher',not any(r.get('modo')=='apd02-docencia'and r.get('texto')=='compara'for r in later))
    # Native inputs and FIFO requests have distinct units/denominators.
    native_status=Counter(r['status']for r in receipts.values());ordered=[by_id[e['id']]['result']['request']for e in admissions]
    check('FIFO_ordered_sequences',[r['seq']for r in ordered]==sorted(r['seq']for r in ordered))
    check('FIFO_nonoverlap',all(a['finished_utc']<=b['started_utc']for a,b in zip(ordered,ordered[1:])))
    check('no_native_rejections',all(r['status']=='applied'for r in receipts.values()))
    return{'schema':'APD03.single_entry.archived_recalculation.R02','issues':issues,'checks':checks,'new_native_ticks':0,'kind':'ARCHIVED_RECALCULATION_NOT_REPRODUCTION_OR_NEW_LEARNING',
        'transport':{'requested':len(admissions),'admitted':len(responses),'completed':sum(e['result']['request']['status']=='completed'for e in responses),'material':len(material),'control':len(admissions)-len(material),'ids':[e['id']for e in admissions]},
        'native_inputs':{'unique_requested':len(receipts),'status_counts':dict(native_status),'scheduled_mirrors_resolved':sum(any(r['status']=='scheduled'for r in versions)and receipts[rid]['status']!='scheduled'for rid,versions in receipt_versions.items()),'unresolved_scheduled':sum(r['status']=='scheduled'for r in receipts.values())},'RAW':{'serialized_observations':raw_count,'unique_site_tick_witnesses':len(raw_unique),'fixed_readers':readers},
        'known_task':{'original_request':request,'operation_from_RAW':'add','route_from_RAW':route,'selected_procedure':'external','provider_calls':receipt['provider_calls'],'artifact_value':artifact['value'],'artifact_sha256':sha(artifact_file),'arithmetic_is_external_here':True},
        'explicit_revision':{'form':'compara','prior_last_functional_RAW_sign':last_sign,'prior_use_end_tick':last_parsed['after_tick'],'teacher_sign':-1,'requested':len(teacher_receipts),'applied':sum(r['receipt']['status']=='applied'for r in teacher_receipts),'later_uses':language,'no_claim_of_new_prelesson_UI_probe':True},
        'continuity':{'life_id':life,'world_id':life,'source_snapshot_sha256':PARENT,'initial_tick':starts[0]['observation']['tick'],'stopped_ticks':[c['record']['physical']['tick']for c in cuts],'actual_worker_PIDs':[s['observation']['pid']for s in starts],'supervisor_PIDs':[r['pid']for r in runs],'same_full_physical_fingerprint_before_new_input':True,'same_epoch':6,'imports':len(imports),'reopens':len(reopens),'safe_stops':len(stops),'no_pending_material_or_uncertain_at_cuts':True},
        'resources':{'runs':[{k:r[k]for k in('elapsed_seconds','resources')}for r in runs],'energy':'NO_MEDIDA','not_a_60_minute_reservation':True},
        'scope':['One diagnostic life, two ordinary CLI processes and explicit operator script; no outside human user was tested.','Native decisions selected the sole arithmetic provider and the learned function. The external calculator computed25; this is not Native arithmetic.','Contextgamma, opportunities and teaching sign/order were supplied by the operator; no autonomous context/exploration claim.','The prior plus sign is the last archived parent use, not an unexecuted initial UI question.','This recalculation checks raw gates, payloads and committed bytes. Omitted full snapshots/SQLite remain required for actual continuation.','End-of-test source/protected-original preservation is the archived operator attestation, not a fresh scan of live source.','The28N0fixtures remain mocks and are not converted into28Native tests.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--evidencia',type=Path,required=True);parser.add_argument('--salida',type=Path,required=True);a=parser.parse_args();result=calculate(a.evidencia)
    with a.salida.open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'issues':result['issues'],'checks':result['checks'],'transport':result['transport']['requested'],'native_inputs':result['native_inputs'],'new_ticks':0}));raise SystemExit(bool(result['issues']))
