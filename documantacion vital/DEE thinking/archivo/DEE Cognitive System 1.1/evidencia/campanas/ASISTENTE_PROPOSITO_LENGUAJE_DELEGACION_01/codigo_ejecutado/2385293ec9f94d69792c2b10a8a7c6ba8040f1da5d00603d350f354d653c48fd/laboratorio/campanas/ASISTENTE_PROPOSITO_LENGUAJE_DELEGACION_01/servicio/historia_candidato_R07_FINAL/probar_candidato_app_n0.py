"""Zero-native-tick tests of the proposed APD transport/ownership extension.

The APD and memory objects below are explicit instrumentation fixtures, not DEE
participants. No runtime, physical responses, learning or arithmetic are faked.
"""
import argparse,difflib,hashlib,importlib.util,json,sys,types
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();here=Path(__file__).resolve().parent;candidate=here/'candidato_app'
    q=module('apd_transport_fixture',candidate/'cola_local.py');svc=module('apd_service_fixture',candidate/'servicio_persistente.py');checks={}
    base={'operacion':'sesion','situaciones':[{'modo':'apd','texto':'sumar','operandos':[3,8]}]}
    checks['literal_APD_accepted']=q.validate_request(base)=='sesion';checks['literal_not_mutated']=base['situaciones'][0]=={'modo':'apd','texto':'sumar','operandos':[3,8]}
    checks['upper_boundary32_accepted']=q.validate_request({'operacion':'sesion','situaciones':[{'modo':'apd','texto':'sumar','operandos':[32,0]}]})=='sesion'
    malformed=[('empty_form',{'modo':'apd','texto':'','operandos':[1,2]}),('target',{'modo':'apd','texto':'sumar','operandos':[1,2],'target':3}),('route',{'modo':'apd','texto':'sumar','operandos':[1,2],'ruta':'externa'}),('teacher_in_use',{'modo':'apd','texto':'sumar','operandos':[1,2],'senal':1}),('bool_operand',{'modo':'apd','texto':'sumar','operandos':[True,2]}),('negative_operand',{'modo':'apd','texto':'sumar','operandos':[-1,2]}),('overbound_operand',{'modo':'apd','texto':'sumar','operandos':[33,2]}),('wrong_count',{'modo':'apd','texto':'sumar','operandos':[1,2,3]}),('oversize_form',{'modo':'apd','texto':'x'*129,'operandos':[1,2]})]
    for name,row in malformed:
        try:q.validate_request({'operacion':'sesion','situaciones':[row]});checks['reject_'+name]=False
        except ValueError:checks['reject_'+name]=True
    checks['legacy_memory_still_admitted']=q.validate_request({'operacion':'sesion','situaciones':[{'modo':'memoria','contexto':'gamma'}]})=='sesion'
    checks['legacy_scalar_still_admitted']=q.validate_request({'operacion':'sesion','situaciones':[{'modo':'dato','valor':13}]})=='sesion'
    teacher={'modo':'apd-docencia','texto':'sumar','senal':1,'revision':True}
    environment_row={'modo':'apd-ambiente','configuracion':{'precios':[2,7],'demora':[0,3],'disponibilidad':[True,False],'presupuesto':2}}
    checks['explicit_teacher_admitted']=q.validate_request({'operacion':'sesion','situaciones':[teacher]})=='sesion'
    checks['explicit_environment_admitted']=q.validate_request({'operacion':'sesion','situaciones':[environment_row]})=='sesion'
    checks['environment_delay4096_admitted']=q.validate_request({'operacion':'sesion','situaciones':[{'modo':'apd-ambiente','configuracion':{**environment_row['configuracion'],'demora':[4096,0]}}]})=='sesion'
    for name,cfg in [('price29',{**environment_row['configuracion'],'precios':[29,2]}),('budget3',{**environment_row['configuracion'],'presupuesto':3})]:
        try:q.validate_request({'operacion':'sesion','situaciones':[{'modo':'apd-ambiente','configuracion':cfg}]});checks['reject_environment_'+name]=False
        except ValueError:checks['reject_environment_'+name]=True
    count_row={'modo':'apd-conteo','presencias':[1,0,1]}
    checks['literal_three_presences_admitted']=q.validate_request({'operacion':'sesion','situaciones':[count_row]})=='sesion'
    composition={'modo':'apd-componer','formas':['sumar','restar'],'datos':[3,8,2]}
    checks['literal_composition_admitted']=q.validate_request({'operacion':'sesion','situaciones':[composition]})=='sesion'
    checks['composition_not_transformed']=composition=={'modo':'apd-componer','formas':['sumar','restar'],'datos':[3,8,2]}
    for name,row in [('plan',{**composition,'plan':'ADD'}),('route',{**composition,'ruta':'externa'}),('one_form',{**composition,'formas':['sumar']}),('four_forms',{**composition,'formas':['a','b','c','d'],'datos':[0]*5}),('wrong_data',{**composition,'datos':[3,8]}),('bool_data',{**composition,'datos':[True,8,2]}),('outbound_data',{**composition,'datos':[17,8,2]})]:
        try:q.validate_request({'operacion':'sesion','situaciones':[row]});checks['reject_composition_'+name]=False
        except ValueError:checks['reject_composition_'+name]=True
    for name,values in [('boolean',[True,0]),('nonbinary',[1,2]),('one',[1]),('four',[0,1,1,0])]:
        try:q.validate_request({'operacion':'sesion','situaciones':[{'modo':'apd-conteo','presencias':values}]});checks['reject_count_'+name]=False
        except ValueError:checks['reject_count_'+name]=True
    for name,row in [('teacher_target',{**teacher,'target':1}),('teacher_revision_type',{**teacher,'revision':1}),('teacher_sign_type',{**teacher,'senal':True}),('environment_extra',{**environment_row,'ruta':'nativa'}),('environment_negative',{'modo':'apd-ambiente','configuracion':{**environment_row['configuracion'],'precios':[-1,2]}}),('environment_bool_budget',{'modo':'apd-ambiente','configuracion':{**environment_row['configuracion'],'presupuesto':True}})]:
        try:q.validate_request({'operacion':'sesion','situaciones':[row]});checks['reject_'+name]=False
        except ValueError:checks['reject_'+name]=True
    calls=[];package=types.ModuleType('capacidades');apd=types.ModuleType('asistente_proposito_01')
    apd.state=lambda adapter:calls.append(adapter)or{'operational':{'prepared':True}}
    literal_calls=[]
    def literal_fixture(adapter,row):
        if row.get('texto')=='OUTSIDE_FIXTURE'or 'OUTSIDE_FIXTURE'in row.get('formas',[]):raise ValueError('Fixture form has no admitted channel; no native information or semantic answer examined')
        literal_calls.append(row)
    apd.validate_literal=literal_fixture
    package.asistente_proposito_01=apd;package.percepcion_cruda_fi01=types.SimpleNamespace(get=lambda adapter:{'level':128});sys.modules['capacidades']=package
    class Memory:
        BASE_TOKENS=['gamma']
        def get(self,adapter):return{'enabled_contexts':['gamma']}
    own={'external_pending':None,'cascade_pending':None,'external_uncertain':None}
    capability=types.SimpleNamespace(ma=Memory(),get=lambda adapter:own)
    w=svc.NativeWorld(a.sistema,'INSTRUMENT_ONLY',backend='mente_unificada');w.a=object();w.capability=capability
    w.validate(base);checks['APD_only_passive_preparation_check']=calls==[w.a]
    checks['literal_checked_without_transformation']=literal_calls==[base['situaciones'][0]]
    try:w.validate({'operacion':'sesion','situaciones':[{'modo':'apd','texto':'OUTSIDE_FIXTURE','operandos':[1,2]}]});checks['out_of_domain_preflight']=False
    except ValueError:checks['out_of_domain_preflight']=True
    for mode_row in(teacher,environment_row):w.validate({'operacion':'sesion','situaciones':[mode_row]})
    w.validate({'operacion':'sesion','situaciones':[composition]});checks['all_composition_forms_checked_as_literals']=literal_calls[-1]is composition
    try:w.validate({'operacion':'sesion','situaciones':[{**composition,'formas':['sumar','OUTSIDE_FIXTURE']}]});checks['composition_domain_preflight']=False
    except ValueError:checks['composition_domain_preflight']=True
    w.validate({'operacion':'sesion','situaciones':[count_row]});checks['count_requires_existing128']=True
    package.percepcion_cruda_fi01.get=lambda adapter:{'level':64}
    try:w.validate({'operacion':'sesion','situaciones':[count_row]});checks['reject_other_count_frontend']=False
    except ValueError:checks['reject_other_count_frontend']=True
    package.percepcion_cruda_fi01.get=lambda adapter:{'level':128}
    try:w.validate({'operacion':'sesion','situaciones':[teacher,base['situaciones'][0]]});checks['teaching_cannot_be_hidden_in_evaluation']=False
    except ValueError:checks['teaching_cannot_be_hidden_in_evaluation']=True
    first=w.operational_dependencies();checks['old_witness_unchanged_when_no_hook']=first['exact_serialized_external_protocol_sha256']==hashlib.sha256(q.canonical(own).encode('utf8')).hexdigest()
    environment={'prices':[2,7],'delay':3,'available':True,'pending':None,'uncertain':None}
    capability.additional_operational_state=lambda adapter:dict(environment)
    second=w.operational_dependencies();third=w.operational_dependencies();checks['external_environment_exactly_repeatable']=second==third
    environment['prices']=[3,7];fourth=w.operational_dependencies();checks['price_change_is_in_operational_witness']=second['exact_serialized_external_protocol_sha256']!=fourth['exact_serialized_external_protocol_sha256']
    capability.external_uncertainty=lambda adapter:False;checks['explicit_false_uncertainty']=w.external_uncertainty()is False
    capability.external_uncertainty=lambda adapter:True;checks['explicit_true_uncertainty']=w.external_uncertainty()is True
    capability.external_uncertainty=lambda adapter:'unknown'
    try:w.external_uncertainty();checks['reject_nonboolean_uncertainty']=False
    except ValueError:checks['reject_nonboolean_uncertainty']=True
    class FaultWorld:
        tick=0;life='INSTRUMENT_ONLY';backend='mente_unificada';rec={'physical':{'tick':0}}
        def validate(self,payload):
            if payload.get('situaciones',[{}])[0].get('texto')=='OUTSIDE_FIXTURE':raise ValueError('Instrumental admission rejection before mutation')
        def execute(self,payload):self.calls+=1;raise RuntimeError('Instrumented unknown tool outcome, no real effect')
        def checkpoint(self,protocol,pending,operation):return{'native_ticks':0,'instrument_only':True}
        def fingerprint(self):return{'tick':0,'instrument_only':True}
    class FaultQueue:
        def __init__(self):self.finished=[]
        def outstanding(self):return[]
        def counters(self):return{'instrument_only':1}
        def meta(self,*args):pass
        def finish(self,*args,**kwargs):self.finished.append((args,kwargs))
    fw=FaultWorld();fw.calls=0;fq=FaultQueue();service=svc.PersistentService(fw,fq)
    service.perform({'id':'instrument_uncertain','payload':json.dumps(base),'payload_sha':'fixture','arrived_utc':'instrument_only'})
    checks['APD_effect_uncertainty_halts_without_retry']=service.uncertain and service.paused and fw.calls==1 and fq.finished[0][0][1]=='uncertain'
    fw2=FaultWorld();fw2.calls=0;fq2=FaultQueue();service2=svc.PersistentService(fw2,fq2)
    outside={'operacion':'sesion','situaciones':[{'modo':'apd','texto':'OUTSIDE_FIXTURE','operandos':[1,2]}]}
    service2.perform({'id':'instrument_outside','payload':json.dumps(outside),'payload_sha':'fixture','arrived_utc':'instrument_only'})
    checks['out_of_domain_not_external_uncertainty']=not service2.uncertain and fw2.calls==0 and fq2.finished[0][0][1]=='rejected_invalid'
    checks['no_DEE_module_imported']=not any(k=='dee_thinking'or k.startswith('dee_thinking.')for k in sys.modules)
    expected={'cola_local.py':'9b7a273b7396069f55cd8e12ea9ddc750576d41a4b51361650a248801df5acba','servicio_persistente.py':'20230a241996afe697e44dfa6d043f43212c6f886dc1c02c6315a35b54828162'}
    patches=[];sources=[]
    for name,baseline in expected.items():
        source=a.sistema/'app'/name;new=candidate/name;checks['source_baseline_'+name]=sha(source)==baseline
        patches.extend(difflib.unified_diff(source.read_text(encoding='utf8').splitlines(True),new.read_text(encoding='utf8').splitlines(True),fromfile='a/sistema/app/'+name,tofile='b/sistema/app/'+name))
        sources.append({'file':'app/'+name,'baseline_sha256':sha(source),'candidate_sha256':sha(new)})
    patch=here/'APLICAR_S_APD01_R07.patch'
    with patch.open('x',encoding='utf8')as f:f.writelines(patches)
    result={'schema':'DEE.APD01.service_patch.instrument_tests.v1','new_native_ticks':0,'new_DEE_participants':0,'checks':checks,'all_true':all(checks.values()),'sources':sources,'patch_sha256':sha(patch),'scope':'Instrumentation fixtures only; no claim of Spanish learning, mathematical competence, native route choice or tool delegation.'}
    a.salida.parent.mkdir(parents=True,exist_ok=True)
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(result,ensure_ascii=False));return 0 if result['all_true']else 1

if __name__=='__main__':raise SystemExit(main())
