"""Recalculate exact-Full proof from exported bytes; no Native/provider calls."""
import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HELPER_SHA='cb044a96301bdb179e595954ef51182b0b503bdca60630b5aa4fbaa0bdfe7aeb'
def read(path):
    path=Path(path);data=path.read_bytes();return json.loads(gzip.decompress(data)if path.suffix=='.gz'else data)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def unwrap(value):return value.get('request')or value
def recalculate(root):
    root=Path(root).resolve(strict=True);helper=root/'CODIGO_EJECUTADO/probar_full_apd03_entrada.py'
    if sha(helper)!=HELPER_SHA:raise ValueError('Not the exact previously approved executed helper; no silent decoder change')
    spec=importlib.util.spec_from_file_location('full_fixed_raw_readers_N0',helper);U=importlib.util.module_from_spec(spec);spec.loader.exec_module(U)
    if any(n.startswith('dee_thinking')for n in sys.modules):raise RuntimeError('Archived recalculation unexpectedly imported Native')
    result=read(root/'EVIDENCIA/RESULTADOS_FULL_APD03.json.gz');outer=read(root/'VERIFICACION_FULL_APD03_R01.json');protocol=read(root/'EVIDENCIA/PROTOCOLO_CONGELADO.json');original_protocol=read(root/'EVIDENCIA/PROTOCOLO_ORIGINAL_BYTES.json')
    raw=gzip.decompress((root/'EVIDENCIA/SESIONES_ORIGINALES.jsonl.gz').read_bytes());events=[json.loads(line)for line in raw.splitlines()if line]
    checks=0;issues=[]
    def check(value,message):
        nonlocal checks
        checks+=1
        if not value:issues.append(message)
    bat_help=root/'EVIDENCIA/VERIFICACION_BAT_HELP_APD03_R01.json'
    if bat_help.is_file():
        help_report=read(bat_help)
        check(help_report['new_native_ticks']==0 and help_report['new_lives']==0,'The .bat help check created a life or ticks')
        check(help_report['returncode']==0 and not help_report['issues'],'Actual .bat help did not reach the expected launcher')
        check(help_report['before']==help_report['after'],'Actual .bat help changed personal life bytes')
    check(protocol['status']=='CLOSED_FOR_EXACT_FULL_PROOF','Prospective protocol was not closed')
    check(original_protocol==protocol and sha(root/'EVIDENCIA/PROTOCOLO_ORIGINAL_BYTES.json')==outer['protocol_sha256'],'Original passed protocol bytes differ from the externally verified hash')
    check(protocol['personal_life']=='APD03_FULL_R01'and protocol['source_life']=='APD03_MAIN'and protocol['source_tick']==604825,'Unexpected life/cut')
    check(protocol['new_luma_teacher']==-1 and protocol['baseline_luma_required']==1 and protocol['baseline_nara_required']==-1,'Opposite prospective lesson changed')
    check(protocol['goal']=={'text':'suma','operands':[24,5],'second_visible':False,'context':1,'maximum_opportunities':4},'Prospective new goal changed')
    check(protocol==result['protocol'],'Execution changed the closed protocol')
    if 'native_proof'in outer:check(outer['native_proof']==result,'Outer/inner proof results differ')
    check(outer.get('zip_still_exact')is True,'Original approved archive not confirmed unchanged')
    check(outer.get('managed_manifest_after')==outer.get('managed_manifest'),'Managed package changed during proof')
    check(outer.get('execution',{}).get('resources',{}).get('job_active_processes')==0,'Outer owned job not empty')
    check(all(r['exit_code']==0 and r['resources']['job_active_processes']==0 for r in result['runs']),'A UI owner did not close successfully')
    imports=[e for e in events if e['event']=='explicit_complete_paired_import'];starts=[e for e in events if e['event']=='owned_start_paused'];stops=[e for e in events if e['event']=='owned_stop'];opens=[e for e in events if e['event']=='same_personal_life_reopened']
    check((len(imports),len(starts),len(stops),len(opens))==(1,3,3,2),'Not one import/three sequential owners/two reopens')
    check(all(e['life_id']=='APD03_FULL_R01'for e in events),'Journal mixes personal lives')
    submissions=[e for e in events if e['event']=='literal_material_submission'];check(len({e['id']for e in submissions})==len(submissions),'Material request was submitted more than once')
    controls=[e for e in events if e['event']=='literal_control'];check(len({e['id']for e in controls})==len(controls),'Control request ID duplicated')
    by_mode={};receipts={};raws=0;terminal=Counter();lessons=[];uses=[];artifacts=[];goal_actions=[]
    for event in events:
        if event['event']not in('literal_material_result','control_result','same_id_read_only_result'):continue
        row=unwrap(event['result']);payload=json.loads(row['payload']);body=json.loads(row['result'])if row.get('result')else None
        check(row['id']==event['id'],'UI/queue ID mismatch');check(hashlib.sha256(canonical(payload).encode()).hexdigest()==row['payload_sha'],'Literal payload SHA mismatch')
        if body is None:continue
        check(body['id']==row['id'],'Result/queue ID mismatch')
        check(body['before_tick']<=body['after_tick'],'Result reversed ticks')
        if event['event']=='literal_material_result':
            sub=next((s for s in submissions if s['id']==row['id']),None)
            check(sub is not None and sub['payload']==payload,'Material request was not the literal submitted content')
            terminal[row['status']]+=1
            mode=payload['situaciones'][0]['modo'];by_mode.setdefault(mode,[]).append(event)
        for _,node in U.walk(body):
            if not isinstance(node,dict):continue
            if'raw'in node and'site'in node:
                fields=U.decoded(node);raws+=1
                for k,v in fields.items():
                    if k in node:check(node[k]==v,'RAW field differs:'+k)
            if isinstance(node.get('receipt'),dict)and'id'in node['receipt']:
                r=node['receipt'];old=receipts.get(r['id'])
                if old:check(all(old.get(k)==r.get(k)for k in('kind','requested_tick','channels')),'Native ID refers to different input')
                if not old or old['status']=='scheduled':receipts[r['id']]=r
    panels=[U.panel_map(U.body(e))for e in by_mode.get('apd03-panel',[])]
    if panels:
        check(panels[0].get('luma')==1 and panels[0].get('nara')==-1,'Selected baseline was not luma+/nara-')
        for panel in panels[1:]:
            for form,prior in panels[0].items():check(panel.get(form)==(-1 if form=='luma'else prior),'Retention/revision differs:'+form)
    check(len(panels)==3,'Expected three real material panels')
    for event in by_mode.get('apd03-docencia',[]):
        r=U.body(event)['rows'][0];requests=r['requests'];lessons.append({'form':'luma','sign':r['teacher_sign'],'requested':len(requests),'applied':sum(v['receipt']['status']=='applied'for v in requests)})
        check(r['teacher_sign']==-1 and len(requests)==3 and all(v['receipt']['status']=='applied'for v in requests),'Opposite explicit teacher was not applied3/3')
    check(len(lessons)==1,'One explicit revision was required')
    for event in by_mode.get('apd03-lenguaje',[]):
        r=U.body(event)['rows'][0];choice=U.sign(r['word']['reader']);interaction=r['interaction'];content=U.sign(interaction['reader'])if interaction and interaction.get('kind')=='query'else None
        uses.append({'form':r['literal_form'],'public_datum':r['public_datum'],'operator_context':r['operator_supplied_context'],'function_RAW':choice,'interaction_kind':interaction.get('kind')if interaction else None,'memory_answer_RAW':content})
    check(len(uses)==3,'Expected baseline use, revised use and reopened use')
    if len(uses)==3:
        check(uses[0]['function_RAW']==1,'Baseline luma+ was not actually used before teaching')
        check(all(r['function_RAW']==-1 and r['interaction_kind']=='query'for r in uses[1:]),'Revised function did not persist across reopening')
        check([r['public_datum']for r in uses]==[24,23,17]and[r['operator_context']for r in uses]==['gamma','gamma','delta'],'Prospective new values/context sequence changed')
    for event in by_mode.get('apd03-paso',[]):
        step=U.body(event)['rows'][0]
        for r in step['opportunities']:
            action=U.action_sign(r['native_selection']['reader']);effect=r['environment_effect'];nums=[]
            check(action==r['native_selection']['reader']['choice'],'Recorded action is not the fixed RAW gate')
            check(effect['selected_action']==('ACT'if action==-1 else'QUERY'if action in(0,1)else None),'Command did not follow fixed action transduction')
            for numeric in r['native_numeric']:
                trial=numeric['native_trial'];frame=next(f for f in trial['frames']if f['tick']==trial['datum_tick']-2);o=frame['fields']['C'];fields=U.decoded(o)
                check(o['site']==[12,17,18]and fields['active']and fields['semantic']==1 and fields['direction']==[1,-1,-1],'Invalid native numeric C gate')
                value=fields['s_reg']-(0 if numeric['operation']=='suma'else 32);check(value==numeric['numeric_reader']['numeric_result'],'Numeric result is not RAW-derived');nums.append(value)
            committed=effect['committed_effect']
            if committed is not None:check(committed['provider_calls']=={'native':1,'external':0}and len(nums)==1 and committed['raw_provider_response']['value']==nums[0],'Actual goal used other provider or a non-RAW number')
            goal_actions.append({'action_RAW':action,'selected_action':effect['selected_action'],'new_public_fact':effect.get('new_public_fact_revealed'),'numbers_RAW':nums,'file_completed':effect.get('final_goal_file_completed')})
        check(step['progress']['verified_file_goal_completed'],'New goal not completed in the fixed four opportunities')
    for path in sorted((root/'EVIDENCIA/ARTEFACTOS').rglob('*')):
        if not path.is_file():continue
        value=read(path);check(value.get('operands')==[24,5]and value.get('operation')=='add'and value.get('procedure')=='native'and value.get('value')==29,'Actual archived goal file is not native SUM24,5=29')
        artifacts.append({'file':path.relative_to(root).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path),'content':value})
    check(len(artifacts)==1,'Expected one real new goal artifact')
    for i in(1,2):
        if len(starts)>i and len(result['cuts'])>=i:
            before=starts[i]['observation']['physical'];prior=result['cuts'][i-1]['record']['physical']
            check(all(before[k]==prior[k]for k in('N','tick','RAW_sha256','clocks_sha256')),'Reopened another physical state before new input')
    for cut in result['cuts']:
        check(cut['record']['life_id']=='APD03_FULL_R01'and cut['record']['world_id']=='APD03_FULL_R01','Cut changed personal identity')
        check(cut['record']['parent']['encoded_sha256']==protocol['source_snapshot_sha256'],'Cut changed imported parent')
        check(cut['protocol']['pending_material']is None and not cut['protocol']['uncertain_preserved'],'STOP left pending/uncertain UI state')
    check(not result['issues'],'Execution itself recorded functional issues:'+repr(result['issues']))
    return {'schema':'APD03.Full.archived_recalculation.R01','new_native_ticks':0,'new_provider_calls':0,'checks':checks,'issues':issues,'material_submissions':len(submissions),'material_result_statuses':dict(terminal),'control_submissions':len(controls),'native_unique_receipts':len(receipts),'native_receipt_statuses':dict(Counter(r['status']for r in receipts.values())),'RAW_observations_checked':raws,'baseline_and_later_panels_RAW':panels,'explicit_lessons':lessons,'actual_uses':uses,'goal_actions_RAW':goal_actions,'actual_goal_artifacts':artifacts,'one_import':len(imports),'sequential_owners':len(starts),'confirmed_STOP':len(stops),'reopens':len(opens),'final_tick':result['cuts'][-1]['record']['physical']['tick']if result['cuts']else None,'zip_sha256':outer['zip_sha256'],'scope':'Archived recalculation only, separate from the actual Native Full proof. Same computer, not a different human or machine; fixed task/operator/context and prepared codec. No general autonomy or energy claim.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',required=True,type=Path);p.add_argument('--salida',required=True,type=Path);a=p.parse_args();r=recalculate(a.evidencia)
    with a.salida.open('x',encoding='utf8',newline='\n')as f:json.dump(r,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'checks':r['checks'],'issues':r['issues'],'new_native_ticks':0},ensure_ascii=False));return bool(r['issues'])
if __name__=='__main__':raise SystemExit(main())
