"""New source/route/timing interventions around the proven wrapped return."""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,igualdad_fisica_03 as f
from instrumentos_pc01 import guard,witness,receipts,native_digest,sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='ES01_MAIN_04';life='PC01_REF05_'+a.case;s.fork(parent,life,kind='DIAGNOSTIC_COPY');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'phases':[],'witnesses':[],'interventions':[],'criteria_before':'Existing equality acquisition/read protocol is preserved except one explicitly named input or a native route intervention. Later magnitude61/119/70/120 and old contact/free/time/equality form are assessed in every branch. The one-off scalar target comparison is audit-only; fixed Spanish decoders unchanged. Replays are alternate futures, not corrections of MAIN.'}
def cap(x,label,row):data['phases'].append({'label':label,'tick':x.tick,'result':row})
def present_variant(x,value,*,teacher=False,probe_lead=1):
    if value!=56 or teacher:return original_present(x,value=value,teacher=teacher,probe_lead=probe_lead)
    entry=f.prepare(x);target=e.tick_at_or_after(x.tick,phase=3,lead=8);first=len(x.quantity.state['requests']);x.quantity.present_object(value,round_index=(target-70)//67)
    if a.case!='omit_reader':x.quantity.input('quantity.reader',7,target-1,True)
    req=[]
    if a.case!='omit_probe':
        name=entry['ports']['material_probe'+str(probe_lead)];tick=target+1-probe_lead
        if a.case=='probe_offroute':
            # Same zero-load normal carrier and timing; shifted9Z. Native admission
            # and its consequences remain recorded, no fabricated receipt.
            port=next(p for p in x.world.interfaces if p.name==name);q=port.channel.injection_site;v=port.channel.direction
            r=guard(x.world,'PC01.REF05.OFFROUTE',[q.x,q.y,(q.z+9)%67],tick,direction=(v.dx,v.dy,v.dz),semantic=1,payload=0);data['interventions'].append(r)
        else:
            if a.case=='probe_delay':tick+=1
            r=x.world.probe(name,0,tick);req.append({'port':name,'payload':0,'tick':tick,'id':int(r.id)})
    x.run_until(target);comparison=e.obs(x,entry['center']);x.run_until(target+1);route=e.obs(x,entry['route_slot']);x.run_until(target+4);word=e.obs(x,entry['hub'])
    return{'ENTORNO':{'current_magnitude':value,'format_cue':5},'ENTE':{'native_comparison':comparison,'native_route_product':route,'word_record':word},'INSTRUMENTO':{'comparison_tick':target,'word_tick':target+4,'teacher_label_supplied':False,'explicit_variant':a.case,'requests':[e.receipt_at(x.world,r)for r in req],'quantity_requests':x.quantity.receipts()[first:]},'INTERPRETACION':'Single declared protocol-input ablation or phase/path variant, not a learned policy.'}
original_present=f.present
def trial(x):
    if a.case in('guard','guard_sham'):
        data['interventions'].append(guard(x.world,'PC01.REF05.ROUTE',[47,38,33 if a.case=='guard'else 42],9983))
    if a.case=='early_guard':data['interventions'].append(guard(x.world,'PC01.REF05.EARLY',[52,33,38],9921))
    if a.case in('divert','divert_sham'):
        data['interventions'].append(guard(x.world,'PC01.REF05.DIVERT',[52,32,39 if a.case=='divert'else 48],9921,direction=(0,1,-1),semantic=1,payload=0))
    oldrun=x.run_until
    def watched(target):
        for t in(9917,9918,9919,9920,9921,9922,9923,9984,9985,9986,9987):
            if x.tick<t<=target:
                oldrun(t);data['witnesses'].append({'tick':t,'source_route':witness(x.world,[50,35,36],3),'reference_meeting':witness(x.world,[49,36,35],3),'foreign_expected':observe(x.world,[(50+(t-9920))%67,(35-(t-9920))%67,(36+(t-9920))%67]),'physical':physical(x.world,occupation=True)})
        oldrun(target)
    x.run_until=watched
    f.present=present_variant
    try:
        f.prepare(x);cap(x,'equality_teaching',f.present(x,value=86,teacher=True,probe_lead=1))
        for j in range(3):cap(x,'equality_recall_'+str(j),f.query(x))
        for value in(86,56,110,86):cap(x,'current_equality_'+str(value),f.context(x,value=value,probe_lead=1))
    finally:f.present=original_present
    for name in('contactoA','freeRepair5'):cap(x,'previous_'+name,e.contact_query(x,frame=name))
    cap(x,'previous_time',e.temporal_query(x,frame='secuenciaA'));cap(x,'previous_comparison_forms',e.query_words(x));cap(x,'equal_after',f.query(x));data['before_new_use']=physical(x.world,occupation=True)
    for value in(61,119,70,120):cap(x,'new_magnitude_'+str(value),e.context(x,value=value,method='B'))
    cap(x,'equal_form_later',f.query(x));data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'new_magnitudes':[r['result']['TRADUCCION']['SPANISH_DECODED']for r in data['phases']if r['label'].startswith('new_magnitude')],'old_functions':{r['label']:r['result'].get('SPANISH_DECODED')for r in data['phases']if r['label'].startswith('previous_')or r['label']=='equal_form_later'}}
data['commit']=s.mutate(life,'PC01_WRAPPED_REFERENCE_RETURN_SOURCE_AND_ROUTE05',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
