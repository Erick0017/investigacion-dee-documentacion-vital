"""Prepared D tests with pure Fakes, never Native/DEE or current world reads."""
from pathlib import Path
from types import SimpleNamespace
import ast,copy,hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent;P=H.parent
s=importlib.util.spec_from_file_location('pi09_D_fake_subject',H/'pi09_entorno_persistente_D_R01.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
checks=[]
def check(name,ok):
    if not ok:raise AssertionError(name)
    checks.append(name)
def reject(name,fn):
    try:fn()
    except (ValueError,KeyError):checks.append(name);return
    raise AssertionError(name)
p,ph=d.protocol(False)
check('12_declared_6evaluated_6future',len(p['schedule'])==12 and p['evaluation_horizon']==6 and p['future_stock']==6)
check('six_evaluated_contexts_fixed',[(r['cue'],r['message_payload'])for r in p['schedule'][:6]]==[('threat',5),('none',8),('falsecue',11),('threat',8),('none',5),('threat',11)])
check('guard48_raw0_legal_birth_sem4_one',p['guard']=={'site':[52,48,48],'direction':[0,0,0],'state':0,'semantic':4,'payload':0,'birth_offset':2,'preparation_ticks':3})
check('R02_literal_source_unchanged',d._sha(d.PARENT_SOURCE.read_bytes())==d.PARENT_SHA)
check('distinct_D_namespace',d.KEY.endswith('.D.R01')and d.FOLDER=='PI09_ENTORNO_PERSISTENTE_D_R01')
for mode in(d.EPISODE,d.STATE):d.validate_literal({'modo':mode});checks.append('literal_'+mode)
for field in('expected','forzar','bank','site','ticks'):reject('no_actor_'+field,lambda field=field:d.validate_literal({'modo':d.EPISODE,field:1}))
for role in('real','none'):
    d.validate_literal({'modo':d.PREPARE,'brazo':role});checks.append('prepare_literal_'+role)
source=[True,False,True,False,False,True];plan={'schema':'DEE.PI09.D.yoked_return.fixed_permutation.v1','permutation':[2,0,4,1,5,3],'source_failed':source,'values':[source[i]for i in[2,0,4,1,5,3]],'source_evidence_sha256':'a'*64};encoded=json.dumps(plan);loaded=d.validate_yoke(encoded)
check('negative_return_dose_equal',sum(source)==sum(loaded['values']))
check('prefixed_yoke_derangement',all(i!=j for i,j in enumerate(plan['permutation'])))
for role in('real','none','yoked'):
    for i in range(6):
        for failed in(False,True):
            meta={'ordinal':i,'control':{'arm':role,'return_plan':loaded}};actual=d._returned(meta,failed);expected=failed if role=='real'else False if role=='none'else loaded['values'][i]
            check('return_'+role+'_'+str(i)+'_'+str(failed),actual is expected)
bad=copy.deepcopy(plan);bad['permutation']=[0,1,2,3,4,5];reject('yoke_not_retuned',lambda:d.validate_yoke(json.dumps(bad)))
bad=copy.deepcopy(plan);bad['values'][0]=not bad['values'][0];reject('yoke_cannot_replace_actual_values',lambda:d.validate_yoke(json.dumps(bad)))
check('exact_selected_real_only_constant',d.LIVES['real'].endswith('DISCOVERY_01')and d.REPRO_IDS==['ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DREPRO_01'])
class Runtime:
    snapshot_metadata_entries=[]
class Adapter:
    world=SimpleNamespace(runtime=Runtime())
check('no_KEY_dependencies_no_material',d.operational_dependencies(Adapter(),None)['present']is False)
check('no_KEY_uncertainty_false',d.uncertain(Adapter())is False)
# The adapted episode is inherited byte-for-byte from R02, including all
# Native input/reader/decoder/actuator/calendar calls and compact metadata.
bridge=d._bridge();bridge.SOURCE=P.parent/'PROGRESION_INTEGRADA_08/codigo/pi08_consulta_condicional_C_R03.py'
c=bridge._C();text,n=bridge._transformed_episode(bridge.SOURCE.read_text('utf-8-sig'));check('inherited_scientific_9_anchor_body',n==9 and'no_generic_return_scheduled_for_first_trace'in text)
original_prepare=d.prepare;root=P/'control/PRUEBA_FAKE_D_PI09_R01';root.mkdir(exist_ok=False)
saved={name:getattr(d,name)for name in('validate','protocol','_identity','_old_literals','_core')}
parent={'body_P0':{'prepared_before_PI09':True},'life_id':'NATIVE_ANCESTOR','ordinal':12,'rows':[{}]*12};old={d.PARENT_KEY:json.dumps(parent)}
def fake_prepare(occupied=False,terminal='applied'):
    home=root/('occupied'if occupied else terminal);home_parent=home.parent;events=[];declared=[];requests=[];holder={};a=SimpleNamespace(tick=100,world=SimpleNamespace(runtime=SimpleNamespace(channel_names=[])))
    def observe(adapter,site):
        raw=1 if occupied else(4<<60)if adapter.tick==103 and terminal=='applied'else 0
        return {'raw':str(raw),'state':raw&0xffffffff,'semantic':raw>>60,'s_reg':0,'direction':[0,0,0],'site':list(site),'tick':a.tick,'clock':str(a.tick),'active':bool(raw&0xffffffff)}
    def record(adapter,meta,directory,event):holder['m']=meta;events.append(copy.deepcopy(event))
    def submit(adapter,channel,payload,tick,values,**kwargs):
        q={'id':1,'port':channel,'payload':payload,'requested_tick':tick,**kwargs,'receipt':{'id':1,'status':terminal}};values.append(q);requests.append(q);return q
    core=SimpleNamespace(_home=lambda *args:home,_observe=observe,_native=lambda:(None,None,None,json.loads,None),_record=record,_submit=submit,_receipts=lambda *args:args[1],_summary=lambda values,start,end:{'unique_requested':1,'applied':int(terminal=='applied'),'all_terminal':True},body=SimpleNamespace(_declare=lambda *args:declared.append(args[1:]),SafeAdapter=lambda adapter:SimpleNamespace(run_until=lambda tick:setattr(adapter,'tick',tick))))
    d.validate=lambda *args:None;d.protocol=lambda *args,**kw:(p,ph);d._identity=lambda *args:{'life_id':d.LIVES['real']};d._old_literals=lambda *args:old;d._core=lambda:core
    if occupied:
        reject('occupied_preflight_refuses_no_side_effect',lambda:original_prepare(a,{'modo':d.PREPARE,'brazo':'real'},root));check('occupied_no_birth_step_metadata',a.tick==100 and not declared and not requests and not events);return
    result=original_prepare(a,{'modo':d.PREPARE,'brazo':'real'},root)
    check('one_legal_birth_'+terminal,len(requests)==len(declared)==1 and requests[0]['requested_tick']==102 and requests[0]['site']==(52,48,48)and requests[0]['direction']==(0,0,0)and requests[0]['payload']==0 and declared[0][-2:]==(0,4))
    check('P0_exact3_ticks_'+terminal,result['new_native_ticks']==3 and a.tick==103)
    check('old_R02_12_and_stock_preserved_'+terminal,result['old_R02_ordinal_preserved']==12 and holder['m']['environmental_supply']['old_R02_stock6_preserved'])
    check('new12_supply_no_physical_bank_reset_'+terminal,result['new_D_opportunities']==12 and holder['m']['environmental_supply']['physical_bank_reset']is False)
    check('readiness_respects_terminal_admission_'+terminal,result['ready']is(terminal=='applied'))
    check('known_rejection_not_unknown_'+terminal,holder['m']['uncertain']is False)
fake_prepare();fake_prepare(occupied=True);fake_prepare(terminal='rejected_occupied')
for name,value in saved.items():setattr(d,name,value)
check('no_DEE_import_after_all_tests',not any(k=='dee_thinking'or k.startswith('dee_thinking.')for k in sys.modules))
value={'schema':'DEE.PI09.D.prepared_environment.pure_tests.R01','passed':True,'Native_executed':False,'DEE_imported':False,'fixture_MOCK_ONLY_NOT_NATIVE':True,'material_P0_or_passivity_not_tested':True,'source_was_not_read_from_active_world':True,'checks':checks,'count':len(checks),'module_sha256':d._sha((H/'pi09_entorno_persistente_D_R01.py').read_bytes()),'protocol_sha256':ph,'parent_R02_sha256':d.PARENT_SHA}
out=P/'control/PRUEBAS_PURAS_ENTORNO_D_PI09_R01.json'
with out.open('x',encoding='utf8')as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'checks':len(checks),'sha256':d._sha(out.read_bytes())}))
