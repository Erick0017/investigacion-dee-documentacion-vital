"""Extraction-only D2 verification. Documentary stdlib; no Native/DEE imports.

The literal PI08 second-stage validator is adapted in memory at exactly three
return-only expressions. Actual failure, actions, RAW decoder and inputs retain
their original checks; None/Yoke's separate returned valence is never rewritten
in primary evidence. Missing future closures are WAIT, not predicted outcomes.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,ast,hashlib,importlib.util,json
VERSION='DEE.PI09.persistent_environment.D.R02'
def require(ok,why):
    if not ok:raise ValueError(why)
def sha(data):return hashlib.sha256(data).hexdigest()
def sibling(name):
    s=importlib.util.spec_from_file_location('_D_documentary_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def parsers():
    shared=sibling('RECALCULAR_CONSULTA_PI09_R01');old,m=shared.load_literal()
    file=Path(__file__).with_name('RECALCULAR_C_PI08_LITERAL.py');text=file.read_text('utf-8-sig');tree=ast.parse(text)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='stage2');original=ast.dump(fn,include_attributes=False)
    fn.args.args.append(ast.arg(arg='expected_return'))
    class ReturnOnly(ast.NodeTransformer):
        def __init__(self):self.changed=[]
        def visit_Compare(self,node):
            node=self.generic_visit(node)
            source=ast.unparse(node.left)
            if source in ("row['returned_failed']","ret[0]['actual_environment_failed']") and len(node.comparators)==1 and isinstance(node.comparators[0],ast.Name)and node.comparators[0].id=='failed':
                self.changed.append(source);node.comparators[0]=ast.Name(id='expected_return',ctx=ast.Load())
            return node
        def visit_Dict(self,node):
            node=self.generic_visit(node)
            for i,key in enumerate(node.keys):
                if isinstance(key,ast.Constant)and key.value=='returned_failed'and isinstance(node.values[i],ast.Name)and node.values[i].id=='failed':
                    self.changed.append('returned_failed result');node.values[i]=ast.Name(id='expected_return',ctx=ast.Load())
            return node
    transform=ReturnOnly();fn=transform.visit(fn);require(transform.changed==["row['returned_failed']","ret[0]['actual_environment_failed']",'returned_failed result'],'Exact three return-only documentary adapter anchors')
    ast.fix_missing_locations(fn);exec(compile(ast.Module(body=[fn],type_ignores=[]),str(file)+':D_return_only_documentary_adapter','exec'),old.__dict__);old.VERSION=VERSION
    return shared,old,m,{'literal_sha256':sha(file.read_bytes()),'adapted_expressions':transform.changed,'source_stage2_AST_sha256':sha(original.encode()),'actual_function_actions_decoder_unchanged':True}
def calculate(root,index_name='INDICE_D_PI09_R02.json'):
    root=Path(root).resolve(strict=True);shared,old,m,adapter=parsers();index=json.loads(shared.local(root,index_name).read_bytes())
    require(index['schema']=='DEE.PI09.D.portable_primary_index.R02','Exact D portable index required')
    verified={}
    def members(v):
        if isinstance(v,dict):
            if {'file','bytes','sha256'}<=set(v):shared.checked(root,v);require(v['file']not in verified or verified[v['file']]==v['sha256'],'Conflicting aliases');verified[v['file']]=v['sha256']
            for child in v.values():members(child)
        elif isinstance(v,list):
            for child in v:members(child)
    members(index)
    p=json.loads(shared.checked(root,index['protocol']));require(p['schema']=='DEE.PI09.persistent_environment.D.protocol.R02'and len(p['schedule'])==12 and p['evaluation_horizon']==6 and [r['wait_ticks']for r in p['schedule']]==[0,0,0,400,0,0,0,0,400,0,0,0],'Fixed D2 supply and external wait protocol')
    products={v['sha256']:shared.checked(root,v)for v in index['products']};witnesses={};unmatched=[]
    for item in index['witnesses']:
        value=json.loads(shared.checked(root,item));key=(item['arm'],value['ordinal']);require(key not in witnesses,'Duplicate immediate witness ordinal');witnesses[key]=(item,value)
    return_plans={};closures=[]
    for item in index['closures']:
        closed=json.loads(shared.checked(root,item));require(closed.get('schema')in('DEE.PI09.D.actual.finite_owner_phase.R02','DEE.PI09.D.actual.finite_owner_phase.R03')and closed.get('closed')is True,'Only actual closed finite supervisors are documentary input; failed closed outcomes retained')
        closures.append({'arm':item['arm'],'life_id':closed['life_id'],'status':closed['status'],'error':closed['error'],'initial_tick':closed['initial_tick'],'final_tick':closed['final_tick'],'new_Native_ticks':closed['new_Native_ticks'],'sha256':item['sha256']})
        require(closed['new_Native_ticks']==closed['final_tick']-closed['initial_tick'],'Closure tick denominator')
    for item in index['plans']:
        plan=json.loads(shared.checked(root,item))
        for step in plan['steps']:
            literal=step['literal']
            if literal.get('modo')=='eci01-pi09-d-preparar'and literal['brazo']=='yoked':
                yp=json.loads(literal['plan']);require(yp['schema']=='DEE.PI09.D.yoked_return.fixed_permutation.v1'and yp['permutation']==[2,0,4,1,5,3]and len(yp['source_failed'])==6 and all(type(v)is bool for v in yp['source_failed'])and yp['values']==[yp['source_failed'][i]for i in yp['permutation']],'Prespecified actual-source return yoke')
                require(item['arm']not in return_plans or return_plans[item['arm']]==yp,'Conflicting actual return plan');return_plans[item['arm']]=yp
    complete=[];adverse=[];aux=[];preparations=[];bygroup=defaultdict(list);allids=defaultdict(dict);seen_intervals=defaultdict(list)
    for item in index['primaries']:
        primary=json.loads(shared.checked(root,item));rr=shared.rows(primary);arm=item['arm'];policy='real'if arm=='real_reproduction'else arm
        if primary['status']!='completed':adverse.append({'arm':arm,'file':item['file'],'status':primary['status'],'error':primary.get('error'),'scientific_result_not_fabricated':True})
        for row in rr:
            if row.get('version')!=VERSION:aux.append({'arm':arm,'file':item['file'],'version':row.get('version')});continue
            life=row.get('life_id');group=(life,arm);require(life,'D row requires actual life identity')
            if 'P0_guard'in row and 'ready'in row:
                before=row['P0_guard']['preflight'];after=row['P0_guard']['actual_after'];m.observation(before);post=m.observation(after)
                direct,counts,aliases=old.summary(row['requests'],row['Native_inputs'],m)
                require(before['site']==after['site']==[52,48,48]and int(before['raw'])==0 and len(direct)==1,'One fixed guard birth from wholeRAW0 only')
                for rid,r in direct.items():require(r['site']==[52,48,48]and r['direction']==[0,0,0]and r['payload']==0 and r['requested_tick']==row['before_tick']+2,'Fixed support position/calendar')
                ready=counts['applied']==1 and int(after['raw'])==4<<60
                require(row['ready']is ready and row['after_tick']-row['before_tick']==3 and row['old_R02_ordinal_preserved']==12 and row['old_metadata_literal_unchanged'],'Guard fact/admission/ancestor differs')
                preparations.append({'life_id':life,'arm':arm,'ready':ready,'preflight_RAW':before['raw'],'after_RAW':after['raw'],'Native_inputs':{'unique_requested':len(direct),'status_counts':dict(counts)},'new_Native_ticks':3,'P0_environment_not_learned_regulation':True})
                allids[group].update(direct);continue
            if 'first_stage'not in row:
                progress=row.get('progress');aux.append({'arm':arm,'file':item['file'],'present':row.get('present'),'ordinal':progress.get('ordinal')if progress else None,'pending':progress.get('pending')if progress else None});continue
            require(primary['status']=='completed','A noncompleted transport result cannot be counted as completed D')
            i=row['ordinal'];require(type(i)is int and 0<=i<12 and(policy=='real'or i<6),'Finite D bounds; controls only6')
            require(row['D_feedback_arm']==policy and row['D_environment_fixed_guard']==[52,48,48]and row['old_R02_ordinal_preserved']==12,'D feedback/guard/genealogy differs')
            key=(arm,i);require(key in witnesses,'Full immediate q1+8 witness required');wi,w=witnesses[key]
            ptr=row['external_immediate_first_stage_witness'];require(ptr['sha256']==wi['sha256']and ptr['bytes']==wi['bytes'],'Immediate preserved witness hash/bytes differ')
            first,fd=shared.first_stage(row['first_stage'],w,row,'native_real',m,old,{})
            if policy=='real':expected_return=row['actual_failed']
            elif policy=='none':expected_return=False
            else:require(arm in return_plans,'Closed actual yoke plan required');expected_return=return_plans[arm]['values'][i]
            require(type(expected_return)is bool,'Returned valence must be explicit Boolean')
            second,sd=old.stage2(row['second_stage'],first['bit'],p,i,m,products,expected_return)
            direct,counts,aliases=old.summary(row['requests'],row['Native_inputs'],m)
            require(set(direct)==set(fd)|set(sd)and row['actual_failed']is second['actual_failed']and row['returned_failed']is second['returned_failed'],'All direct two-stage requests dedup; actual and returned failures distinct')
            q1=row['first_stage']['query_tick'];q2=second['query_tick'];wait=row['prepared_wait_ticks'];before=row['before_prepared_wait'];ticks=row['after_tick']-before
            require(wait==p['schedule'][i]['wait_ticks']and row['whole_new_native_ticks']==ticks and row['before_tick']==before+wait and ticks<=2110+wait and q2>=q1+782,'Fixed declared wait plus unaltered C-core calendar/bound')
            require(row['old_metadata_literal_unchanged']and row['no_first_trace_credit_claim'],'Ancestral history/credit scope differs')
            for rid,r in direct.items():require(rid not in allids[group]or allids[group][rid]==r,'Receipt alias differs');allids[group][rid]=r
            before_banks=row['second_stage']['reference_before'];require([x['site']for x in before_banks]==[[7,39,50],[9,39,50]],'Fixed inherited A/B reference sites')
            decoded_banks=[m.observation(x)for x in before_banks];last_frame=row['second_stage']['return_frames'][-1];last_A=m.observation(last_frame['A']);last_B=m.observation(last_frame['B'])
            bank_delta={'before_A_minus_B':decoded_banks[0]['s_reg']-decoded_banks[1]['s_reg'],'after_A_minus_B':last_A['s_reg']-last_B['s_reg'],'before_reference_ticks':[x['tick']for x in before_banks],'before_reference_clocks':[x['clock']for x in before_banks],'after_reference_tick':last_frame['tick']}
            record={'life_id':life,'arm':arm,'ordinal':i,'evaluation_or_future':'evaluation'if i<6 else'explicit_future_use','nominal_cue_auditor_only':p['schedule'][i]['cue'],'before_tick':before,'after_tick':row['after_tick'],'Native_ticks':ticks,'prepared_wait_ticks':wait,'q1':q1,'q2':q2,'q2_minus_q1':q2-q1,'q1_phase67_391_782':[q1%67,q1%391,q1%782],'q2_phase67_391_782':[q2%67,q2%391,q2%782],'first':first,'second':second,'joint_useful':not second['actual_failed'],'banks_before_second':before_banks,'decoded_bank_difference':bank_delta,'return_frames':row['second_stage']['return_frames'],'Native_inputs':{'unique_requested':len(direct),'status_counts':dict(counts),'aliases_not_events':aliases},'primary_sha256':item['sha256']}
            # Banks are preserved as literal observations; the RAW parser already
            # validates each A/B/hub frame in the second-stage return path.
            complete.append(record);bygroup[group].append(record);seen_intervals[group].append((before,row['after_tick']))
    used={(r['arm'],r['ordinal'])for r in complete}
    for key,(item,w)in witnesses.items():
        if key not in used:
            m.observation(w['actual_preview_observation']);old.reader(w['reader'],m)
            unmatched.append({'arm':key[0],'ordinal':key[1],'sha256':item['sha256'],'q1':w['query_tick'],'observation_tick':w['observation_tick'],'completed_second_stage_not_invented':True})
    groups=[]
    for (life,arm),rr in sorted(bygroup.items()):
        rr.sort(key=lambda r:r['ordinal']);require([r['ordinal']for r in rr]==list(range(len(rr))),'No omitted/duplicate D ordinal')
        for a,b in zip(rr,rr[1:]):require(a['after_tick']==b['before_tick'],'Unreported Native interval between same-life D opportunities')
        ev=[r for r in rr if r['ordinal']<6];future=[r for r in rr if r['ordinal']>=6];statuses=Counter(r['status']for r in allids[life,arm].values())
        revisions=[]
        for fail in ev:
            if not fail['second']['actual_failed']:continue
            later=[r for r in ev if r['ordinal']>fail['ordinal']and r['first']['bit']==fail['first']['bit']and r['second']['actual_motor']is not None and r['second']['actual_motor']!=fail['second']['actual_motor']]
            for changed in later:
                useful_after=[r['ordinal']for r in ev if r['ordinal']>=changed['ordinal']and r['joint_useful']]
                revisions.append({'actual_failed_ordinal':fail['ordinal'],'failed_valence_actually_returned':fail['second']['returned_failed'],'same_submitted_bit':fail['first']['bit'],'failed_second_motor':fail['second']['actual_motor'],'later_changed_ordinal':changed['ordinal'],'changed_second_motor':changed['second']['actual_motor'],'changed_case_useful':changed['joint_useful'],'useful_ordinals_from_change':useful_after,'at_least_two_later_actual_useful':len(useful_after)>=2,'descriptive_not_query_specific_credit':True})
        groups.append({'life_id':life,'arm':arm,'completed':len(rr),'evaluation_completed':len(ev),'evaluation_useful':sum(r['joint_useful']for r in ev),'future_completed':len(future),'future_useful':sum(r['joint_useful']for r in future),'Native_ticks_opportunities':sum(r['Native_ticks']for r in rr),'questions_applied':sum(r['first']['question_applied']for r in ev),'messages_offered':sum(r['second']['message_offered']for r in ev),'messages_delivered':sum(r['second']['message_delivered']for r in ev),'actual_failed':[r['second']['actual_failed']for r in ev],'returned_failed':[r['second']['returned_failed']for r in ev],'actual_second_motors':[r['second']['actual_motor']for r in ev],'revision_after_failure_descriptors':revisions,'Native_inputs_unique_included_preparation':len(allids[life,arm]),'Native_status_counts':dict(statuses)})
    if 'yoked'in return_plans:
        source=next((g for g in groups if g['arm']=='real'and g['evaluation_completed']==6),None)
        require(source is not None and return_plans['yoked']['source_failed']==source['actual_failed'],'Return yoke must match all six included actual Real failures, not a constructed favourable vector')
    pairs=[]
    for other in('none','yoked'):
        for i in range(6):
            a=[r for r in complete if r['arm']=='real'and r['ordinal']==i];b=[r for r in complete if r['arm']==other and r['ordinal']==i]
            if len(a)!=1 or len(b)!=1:continue
            a,b=a[0],b[0];pairs.append({'left':'real','right':other,'ordinal':i,'same_age':(a['before_tick'],a['after_tick'])==(b['before_tick'],b['after_tick']),'same_q1_q2':(a['q1'],a['q2'])==(b['q1'],b['q2']),'same_submitted_bit':a['first']['bit']==b['first']['bit'],'same_request_count':a['Native_inputs']['unique_requested']==b['Native_inputs']['unique_requested'],'same_actual_return':a['second']['returned_failed']==b['second']['returned_failed'],'left_useful':a['joint_useful'],'right_useful':b['joint_useful'],'left_query':a['first']['question_applied'],'right_query':b['first']['question_applied'],'left_second_motor':a['second']['actual_motor'],'right_second_motor':b['second']['actual_motor']})
    return {'schema':'DEE.PI09.D.recalculated_persistent_environment.R02','integrity_passed':True,'Native_executed':False,'DEE_imported':False,'verified_members':len(verified),'documentary_return_adapter':adapter,'closures':closures,'preparations':preparations,'groups':groups,'rows':complete,'paired_observations':pairs,'failed_preserved_attempts':adverse,'unmatched_first_stage_witnesses':unmatched,'auxiliary_rows':aux,'all_three_evaluation_arms_closed6':all(any(g['arm']==arm and g['evaluation_completed']==6 for g in groups)for arm in('real','none','yoked')),'approval':False,'scope':'Fixed environmental P0 support plus unchanged shared-bank Native two-stage selection. Actual and returned valence remain separate. Descriptive revision is not isolated query credit, general agency or learned guard construction. Future6 are never included in first6 comparison.'}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--raiz',required=True);ap.add_argument('--indice',default='INDICE_D_PI09_R02.json');ap.add_argument('--salida',required=True);a=ap.parse_args();out=Path(a.salida).absolute();require(not out.exists(),'New separate result only');result=calculate(a.raiz,a.indice)
    with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'integrity_passed':True,'groups':result['groups'],'sha256':sha(out.read_bytes()),'Native_executed':False},ensure_ascii=False))
