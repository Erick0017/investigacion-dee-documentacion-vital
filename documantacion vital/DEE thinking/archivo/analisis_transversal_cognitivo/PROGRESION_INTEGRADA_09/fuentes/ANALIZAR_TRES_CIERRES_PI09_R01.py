"""Passive closed Native/Always/Never analysis. Never opens active Yoke.
Uses the frozen documentary RAW/receipt verifiers; writes only PI09/fuentes.
"""
from pathlib import Path
from collections import Counter
import hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent;P=H.parent
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
r=load_module('PI09_closed_documentary',P/'codigo/RECALCULAR_CONSULTA_PI09_R01.py');e=load_module('PI09_closed_eval_helpers',H/'EVALUAR_CRITERIOS_CONSULTA_PI09_R01.py')
old,m=r.load_literal();protocol=json.loads((P/'codigo/PROTOCOLO_PI09_CONSULTA_R01.json').read_bytes())
ROLE_TAGS={'native_real':('NATIVE','PI09_NATIVE_R03'),'always_real':('ALWAYS','PI09_ALWAYS_R03'),'never':('NEVER','PI09_NEVER_R03')}
def sha_file(file):
    h=hashlib.sha256()
    with file.open('rb')as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def require(ok,why):
    if not ok:raise ValueError(why)
def run():
    sources={};groups=[];records={};initials={}
    for role,(slug,tag)in ROLE_TAGS.items():
        file=P/'control'/(tag+'.json');proof=json.loads(file.read_bytes());require(proof['status']=='CLOSED_FINITE_PHASE'and proof['closed']is True and proof['error']is None,'Only closed role is readable: '+role)
        require(proof['protected_before']==proof['protected_after'],'Protected principal changed')
        source={'path':str(file),'sha256':sha_file(file),'life_id':proof['life_id'],'initial_tick':proof['initial_tick'],'final_tick':proof['final_tick'],'Native_ticks':proof['new_Native_ticks']};sources[role]=source
        rr=e.actual_rows(proof);require(len(rr)==12 and [row['ordinal']for _,row in rr]==list(range(12)),'All12 exact ordinals required')
        initial=next(row for rec in proof['records']if rec['label']=='STATE_BEFORE'for row in rec['rows']);initials[role]=initial['physical']
        checked=[];ids={};questions=[];banktrace=[];products={}
        for rec,row in rr:
            primary=P/'ensayos'/(rec['id']+'.json');require(sha_file(primary)==rec['sha256'],'Closed summary/primary literal differs')
            home=P/'estados'/slug/'sistema/estado/servicios_locales'/proof['life_id']/'PI09_CONSULTA_SELECTIVA_R02'
            ptr=row['external_immediate_first_stage_witness'];wfile=home/ptr['file'];require(wfile.stat().st_size==ptr['bytes']and sha_file(wfile)==ptr['sha256'],'Full immediate witness differs');w=json.loads(wfile.read_bytes())
            artifact=row['second_stage']['message']['artifact']
            if artifact:
                product=home/artifact['file'];data=product.read_bytes();require(len(data)==64 and r.sha(data)==artifact['sha256'],'Actual64Bproduct differs');products[artifact['sha256']]=data
            first,fd=r.first_stage(row['first_stage'],w,row,role,m,old,{})
            old.VERSION=row['version'];second,sd=old.stage2(row['second_stage'],first['bit'],protocol,row['ordinal'],m,products)
            direct,counts,aliases=old.summary(row['requests'],row['Native_inputs'],m);require(set(direct)==set(fd)|set(sd),'Two direct stages must account for all unique inputs')
            for rid,value in direct.items():require(rid not in ids or ids[rid]==value,'Cross-episode receipt alias disagrees');ids[rid]=value
            before=e.bank_fields(row['second_stage']['reference_before']);last=row['second_stage']['return_frames'][-1];after=e.bank_fields([last['A'],last['B']])
            checked.append({'ordinal':row['ordinal'],'stage':protocol['schedule'][row['ordinal']]['stage'],'nominal_cue_auditor_only':protocol['schedule'][row['ordinal']]['cue'],'before_tick':row.get('before_prepared_wait',row['before_tick']),'after_tick':row['after_tick'],'Native_ticks':row['after_tick']-row.get('before_prepared_wait',row['before_tick']),'wait_declared':row['prepared_wait_ticks'],'q1':row['first_stage']['query_tick'],'q2':row['second_stage']['calendar']['query_tick'],'q1_phase67_391_782':[row['first_stage']['query_tick']%n for n in(67,391,782)],'q2_phase67_391_782':[row['second_stage']['calendar']['query_tick']%n for n in(67,391,782)],'first':first,'second':second,'joint_useful':not second['actual_failed'],'Native_status_counts':dict(counts),'banks_before_second':before,'banks_after_return':after,'bank_delta_change':after['A_minus_B']-before['A_minus_B'],'primary_sha256':rec['sha256']})
        require(sum(x['Native_ticks']for x in checked)==proof['new_Native_ticks'],'Primary/phase time denominator differs')
        status=Counter(v['status']for v in ids.values());reserve=checked[6:12]
        group={'arm':role,'life_id':proof['life_id'],'closed':True,'opportunities':12,'useful':sum(x['joint_useful']for x in checked),'reserved_useful':sum(x['joint_useful']for x in reserve),'reserved_opportunities':6,'questions_scheduled':sum(x['first']['question_scheduled']for x in checked),'questions_applied':sum(x['first']['question_applied']for x in checked),'Native_first_choices':[x['first']['Native_choice']for x in checked],'actual_first_motors':[x['first']['actual_query_motor']for x in checked],'Native_second_choices':[x['second']['Native_choice']for x in checked],'actual_second_motors':[x['second']['actual_motor']for x in checked],'FI_q4':[x['second']['FI_q4']for x in checked],'FI_q6':[x['second']['FI_q6']for x in checked],'messages_offered':sum(x['second']['message_offered']for x in checked),'messages_delivered':sum(x['second']['message_delivered']for x in checked),'actual_failures':[x['second']['actual_failed']for x in checked],'returned_failures':[x['second']['returned_failed']for x in checked],'Native_ticks':proof['new_Native_ticks'],'Native_inputs_unique':len(ids),'Native_status_counts':dict(status),'bank_delta_before_second':[x['banks_before_second']['A_minus_B']for x in checked],'bank_delta_after_return':[x['banks_after_return']['A_minus_B']for x in checked],'rows':checked}
        groups.append(group);records[role]=checked
        # Release the much larger completed Root envelope; retain compact actual
        # derived rows only. No active-state read is needed.
        del proof,rr
    pairs=[]
    for other in('always_real','never'):
        for a,b in zip(records['native_real'],records[other]):
            pairs.append({'reference':other,'ordinal':a['ordinal'],'same_q1_q2':(a['q1'],a['q2'])==(b['q1'],b['q2']),'same_age':(a['before_tick'],a['after_tick'])==(b['before_tick'],b['after_tick']),'Native_useful':a['joint_useful'],'reference_useful':b['joint_useful'],'Native_query':a['first']['question_applied'],'reference_query':b['first']['question_applied']})
    require(not any(k=='dee_thinking'or k.startswith('dee_thinking.')for k in sys.modules),'Documentary evaluator must not import DEE')
    value={'schema':'DEE.PI09.three_closed_arms.passive_actual_analysis.R01','Native_executed':False,'DEE_imported':False,'active_Yoke_opened':False,'actual_sources':sources,'same_initial_physical':all(v==initials['native_real']for v in initials.values()),'groups':groups,'matched_exposure_pairs':pairs,'interpretation_limits':['Preliminary actual3arms; causal content contrast waits for closedYoke.','Native query selectivity is physically exercised, not newly learned query-specific credit.','AllNative andAlways outcomes may be nonfailure; shared-bank changes and inherited bias must be reported.','Inputs,ticks,queries andutility remain separate; no arbitraryenergy score orcounterfactualutility.','Reference effects are material, including conflicts and indirect shared-state changes; a forcedreference motor is not called Nativechosen.'],'approval':False,'all_adoption_gates_met':False}
    out=H/'TRES_BRAZOS_CERRADOS_PI09_R01.json'
    with out.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'output':str(out),'sha256':sha_file(out),'groups':[{k:g[k]for k in('arm','useful','reserved_useful','questions_applied','Native_inputs_unique','Native_status_counts','Native_ticks','messages_delivered','bank_delta_before_second','bank_delta_after_return')}for g in groups],'Yoke_opened':False},ensure_ascii=False))
if __name__=='__main__':run()
