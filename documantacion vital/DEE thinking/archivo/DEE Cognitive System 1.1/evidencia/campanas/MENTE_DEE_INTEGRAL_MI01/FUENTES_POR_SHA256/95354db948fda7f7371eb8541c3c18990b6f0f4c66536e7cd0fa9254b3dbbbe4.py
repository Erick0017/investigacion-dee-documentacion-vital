"""Portable primary-data auditor. Standard library; ZERO native ticks.

It does not import the DEE engine, select actions or repair a participant.
Raw primary files are exact byte exports, optionally losslessly gzip-packed.
Counts are observations/opportunities, never independent subject counts.
"""
import argparse,collections,gzip,hashlib,json,math,sys
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()
def root_default():
    here=Path(__file__).resolve().parent
    if(here.parent/'EVIDENCIA_CAUSAL').exists():return here.parent
    return here.parents[2]/'evidencia/campanas/MENTE_DEE_INTEGRAL_MI01'
def primary_dir(root):return root/'EVIDENCIA_CAUSAL/PRIMARIOS'if(root/'EVIDENCIA_CAUSAL/PRIMARIOS').exists()else root
def load(root,name,optional=False):
    for suffix in('.json','.json.gz'):
        p=primary_dir(root)/(name+suffix)
        if p.exists():
            b=p.read_bytes();return json.loads(gzip.decompress(b)if suffix.endswith('gz')else b)
    if optional:return None
    raise FileNotFoundError(name)
def body(d):
    if'data'in d:return d['data'].get('result',d['data'])
    z=d.get('result',d)
    return z.get('result',z)if isinstance(z,dict)else z
def native(v,direction=None,positive=True):
    return bool(isinstance(v,dict)and v.get('state')==1 and v.get('semantic')==1 and(not positive or int(v.get('s_reg',0))>0)and(direction is None or v.get('direction')==list(direction)))
def material(v,positive=True):
    return native(v,positive=positive)and v['direction'][0]==1 and abs(v['direction'][1])==1 and v['direction'][2]==0
def unpack(raw):
    x=int(raw);signed=lambda q:q-16 if q>=8 else q
    if not 0<=x<2**64:raise ValueError('RAW outside uint64')
    return {'state':x&0xffffffff,'s_reg':(x>>32)&65535,'semantic':(x>>60)&15,'direction':[signed((x>>k)&15)for k in(48,52,56)]}
def walk(x,path='$'):
    if isinstance(x,dict):
        yield path,x
        for k,v in x.items():yield from walk(v,path+'.'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from walk(v,path+'['+str(i)+']')
def validate_observations(root):
    checked=0;errors=[];sources=[]
    for p in sorted(primary_dir(root).glob('*.json*')):
        if p.name.endswith('.PRE_REGISTRO.json')or p.name.endswith('.PRE_REGISTRO.json.gz'):continue
        b=p.read_bytes();b=gzip.decompress(b)if p.suffix=='.gz'else b
        try:d=json.loads(b)
        except Exception:continue
        if not isinstance(d,dict):continue
        z=body(d)
        for path,v in walk(z):
            if all(k in v for k in('raw','state','s_reg','semantic','direction')):
                try:
                    expected=unpack(v['raw']);good=all(v[k]==value for k,value in expected.items())
                    if'clock'in v:good=good and 0<=int(v['clock'])<2**64
                except Exception:good=False
                checked+=1
                if not good:errors.append({'source':p.name,'path':path,'raw':v.get('raw')})
        sources.append({'source':p.name.removesuffix('.gz'),'uncompressed_sha256':sha(b),'bytes':len(b)})
    return{'native_observations_checked':checked,'mismatches':errors,'primary_files_read':len(sources),'source_hashes':sources,'not_claimed':'Repeated observations/metadata are not independent trials. This checks exact RAW decoding, not the truth of all cognitive interpretations.'}

def calculate(root):
    out={'schema':'MI01.portable.primary.recalculation.v1','native_ticks':0,'statistical_unit':'Named lived branches and opportunities. Shared-prefix forks and repeated queries are dependent.','raw_validation':validate_observations(root)}
    out['native_questions']={}
    for k in range(110,116):
        z=body(load(root,'MI01_CONSULTA_'+str(k)));out['native_questions'][str(k)]={'command':z['command'],'B_answer':z['B_answer'],'positive_receiver_codes':[r['sign']for r in z['reads']if native(r['native'],[r['sign'],0,0])],'not_recomputed_from_human_label':True}
    out['material_direction_controls']={}
    for k in range(40,45):
        z=body(load(root,'MI01_DIRECCION_'+str(k)));rows=z['rows'];useful=0;contacts=0
        for row in rows:
            a=row['action'];emitted=material(a,positive=False);r=a['direction'][1]if emitted else 0
            c=row['native_contact'].get(str(r),{});direction=[1 if r==row['availability']else-1,r,0]
            reached=bool(emitted and native(c,direction,positive=False));contacts+=reached;useful+=reached and r==row['availability']
        out['material_direction_controls'][str(k)]={'opportunities':len(rows),'positive_load_commands':sum(material(r['action'])for r in rows),'zero_or_positive_load_material_commands':sum(material(r['action'],False)for r in rows),'executed_native_contacts':contacts,'useful_contacts_predefined040':useful,'scope':'Zero-load criterion040 is distinct from the positive-load external motor codec. Postformed cut can leave zero-load route products.'}
    out['contact_order_composition']={}
    for k in range(220,224):
        z=body(load(root,'MI01_COMPUESTA_'+str(k)));q=z['composition']['ENTE'];out['contact_order_composition'][str(k)]={'joint':q['joint'],'consequence':q['consequence'],'directional_joint_and_use':native(q['joint'],[-1,1,1])and native(q['consequence'],[0,1,1])}
    out['reply_to_selector']={}
    for k in range(210,216):
        z=body(load(root,'MI01_RETORNO_PROTEGIDO_'+str(k)));q=z['use']['output'];out['reply_to_selector'][str(k)]={'output':q,'positive_load_material_decision':material(q),'choice':q['direction'][1]if material(q)else None}
    out['own_content_reuse']={}
    for k in range(280,284):
        z=body(load(root,'MI01_REUSO_'+str(k)));q=z['use']['output']if'use'in z else z.get('reuse',{}).get('output')
        if q is None:
            hits=[v for p,v in walk(z)if'output'in v and isinstance(v['output'],dict)and'raw'in v['output']];q=hits[-1]['output']if hits else None
        out['own_content_reuse'][str(k)]={'output':q,'positive_Y145':native(q,[0,1,0])and q['s_reg']==145 if q else False}
    out['own_content_reuse']['MAIN321']=body(load(root,'MI01_321_MAIN_REUSO'))['output']
    out['native_failure_request']={}
    for k in range(270,275):
        z=body(load(root,'MI01_COMPARTIDO_'+str(k)));rows=z['trajectory']['failure_frames'];out['native_failure_request'][str(k)]={'native_request_count':sum(native(r['native'],[1,-1,0])for r in rows if r['kind']=='failure_request'),'request_observations':[r for r in rows if r['kind']=='failure_request'],'B_response_observations':[r for r in rows if r['kind']=='private_source']}
    out['prepared_B_context']={}
    for k in range(340,348):
        z=body(load(root,'MI01_CONTEXTO_B_'+str(k)));tr=z['trajectory'];out['prepared_B_context'][str(k)]={'B_responses':[r for r in tr['frames']if r['kind']=='source_tick'],'fallback_B_responses':[r for r in tr['failure_frames']if r['kind']=='private_source'],'selector_at_return':[r for r in tr['failure_frames']if r['kind']=='failure_return'],'final_occupied':z['final']['occupied'],'scope':'Frame43 prepared, not a learned B reference. The requested helpers and their actual admission must be read separately348.'}
    out['frozen_windows']=[];frames=[];ext_rows=[]
    for k in(411,412,413):
        d=load(root,'MI01_'+str(k)+'_MAIN_RESERVA_'+str(k-410),True)
        if not d:continue
        z=body(d);rows=z['rows'];ext_rows.extend(rows);frames.extend(z['native_habitat_frames']);requests={int(v['id']):v for row in rows for v in row['requests']}
        statuses=collections.Counter(v.get('receipt',{}).get('status','not_observed')for v in requests.values())
        out['frozen_windows'].append({'id':k,'steps':len(rows),'first_tick':rows[0]['tick'],'last_tick':rows[-1]['tick'],'positive_load_motor_outputs':sum(material(r['native'])and r['native']['direction'][1]>0 for r in rows),'nonneutral_executed_actions':sum(r['executed_torque']!=0 for r in rows),'neutral_actions':sum(r['executed_torque']==0 for r in rows),'reward_sum':math.fsum(r['response']['reward']for r in rows),'environment_elapsed_initial':z['initial_environment']['elapsed'],'environment_elapsed_final':z['final_environment']['environment']['elapsed'],'sensor_and_cost_requests':len(requests),'receipt_statuses_at_window_end':dict(statuses),'final_native':z['final_native']})
    spec=load(root,'SELLO_EVALUACION_FIJADA');av=spec['options']['availability'];contacts={r['index']:r['native']for r in frames if r['kind']=='contact'};commands=[]
    for row in frames:
        if row['kind']!='command':continue
        a=row['native'];i=row['index'];act=native(a,[1,1,0]);ask=native(a,[1,-1,0]);c=contacts.get(i,{})
        useful=act and av[i]==1 and native(c,[1,1,0]);negative=act and av[i]==-1 and native(c,[-1,1,0])
        commands.append({'index':i,'tick':row['tick'],'availability':av[i],'native_command':a,'native_contact':c,'positive_load_act':act,'positive_load_question':ask,'useful_contact':bool(useful),'harmful_contact':bool(negative),'predefined_utility':int(useful)-int(negative)})
    out['frozen_native_opportunities']=commands
    out['frozen_summary']={'opportunities':len(commands),'positive_load_acts':sum(r['positive_load_act']for r in commands),'native_questions_at_regular_windows':sum(r['positive_load_question']for r in commands),'useful_contacts':sum(r['useful_contact']for r in commands),'harmful_contacts':sum(r['harmful_contact']for r in commands),'utility':sum(r['predefined_utility']for r in commands),'external_steps':len(ext_rows),'nonneutral_external_actions':sum(r['executed_torque']!=0 for r in ext_rows),'not_inferred':'A neutral external default is not a native learned decision. Invalid codes and silence stay in the opportunity denominator.'}
    final_state=load(root,'MI01_423_MAIN_ESTADO',True)
    if final_state:
        b=body(final_state)['protocol']['native_habitats']['MI01_EVALUACION_FIJADA'];f=b['direct_failure']['frames']
        questions=[r for r in f if r['kind']=='failure_request'and native(r['native'],[1,-1,0])]
        observed_replies=[r for r in b['frames']if r['kind']=='source_tick']+[r for r in f if r['kind']=='private_source']
        replies={}
        for r in observed_replies:
            v=r['native']
            if native(v)and v['direction']in([1,-1,0],[-1,-1,0]):replies[(r['tick'],tuple(v['site']),v['raw'])]=v
        out['frozen_failure_questions']=questions
        out['frozen_unique_B_replies']=list(replies.values())
        out['frozen_reply_to_selector']=[r for r in f if r['kind']=='failure_return']
        out['frozen_summary']['native_failure_initiated_questions']=len(questions)
        out['frozen_summary']['unique_valid_B_reply_events']=len(replies)
        out['frozen_summary']['valid_failure_reply_selector_uses']=sum(material(r['native'])for r in f if r['kind']=='failure_return')
    for name in('MI01_433_LIBRE_FIN_0TICKS','RECIBOS_B_CONTEXTO_348_0TICKS','CONTEXTO_B_307_0TICKS','RECONSTRUCCION_LOCAL_187_0TICKS','OBSERVADOR_INOCUIDAD_470','COMPARACION_EXTERNA_REFERENCIAS_480'):
        z=load(root,name,True)
        if z is not None:out[name]=z
    out['stress']={}
    for k in(460,461):
        d=load(root,'MI01_'+str(k)+'_ESTRES_CONTROL',True)
        if d:
            z=body(d);out['stress'][str(k)]={'stages':[{'tag':s['tag'],'physical':s['physical'],'selector':s['selector']}for s in z['stages']],'shock_requests':z['shock_requests'],'original_bank_phase3':z['original_bank_phase3'],'final':z['final']}
    out['null_actuator_windows']=[]
    for k in(450,451,452):
        d=load(root,'MI01_'+str(k)+'_ACTUADOR_ANULADO',True)
        if d:
            z=body(d);rows=z['rows'];out['null_actuator_windows'].append({'id':k,'steps':len(rows),'native_positive_outputs':sum(material(r['native'])for r in rows),'actual_nonneutral_actions':sum(r['executed_torque']!=0 for r in rows),'reward_sum':math.fsum(r['response']['reward']for r in rows),'last_environment':z['final_environment']['environment'],'final_native':z['final_native']})
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--raiz',type=Path,default=root_default());p.add_argument('--guardar',type=Path);a=p.parse_args();out=calculate(a.raiz);text=json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)
    if a.guardar:a.guardar.write_text(text,encoding='utf8')
    print(json.dumps({'native_ticks':0,'raw_observations_checked':out['raw_validation']['native_observations_checked'],'mismatches':out['raw_validation']['mismatches'],'frozen_summary':out['frozen_summary'],'windows':out['frozen_windows']},ensure_ascii=False,indent=2))
