"""Optional PC01 native preparations/readers, NOT a new motor or manager.

The orbit guard is preparedR0. The dose reader is an instrument transducer,
not a learned semantic decoder. Only actual native acquiredXselectsa token.
No laboratory/evidence/targets are imported in normal operation.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from dee_thinking.consolidated import exact_receipt
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f,puente_lexico_10 as b

VERSION='PC01.experimental.v1'
GUARD_KEY='DEE.Cognitive.System.1.1.PC01.context_guard.v1'

def _configuration(a):
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if int(a.world.runtime.dimension)!=67 or e.KEY not in entries:raise ValueError('PC01 requires an existing complete N67 Spanish-life state; never prepares a substitute')
    return decode_metadata(entries[e.KEY])

def _frame(a,frame='lexical05'):
    entry=_configuration(a).get('relational_words_v2',{}).get(frame)
    if entry is None or entry['origin']!=[38,50,8]or entry['mode']!='relative_path' or 'lexical_v3'not in entry:raise ValueError('PC01requires the explicitly tested N67lexical05physical frame')
    if entry['lexical_v3'].get('after_comprehension'):raise ValueError('Originalsharedwordreaderispost-useunvalidated; no reconstruction')
    return entry

def protection_state(a):
    configuration=_configuration(a);entries=dict(a.world.runtime.snapshot_metadata_entries);m=decode_metadata(entries[GUARD_KEY])if GUARD_KEY in entries else None
    historical=entries.get('DEE.Cognitive.System.1.1.PC01.orbit_guard')
    if m is None and historical:
        h=decode_metadata(historical)
        if h.get('case')=='guard':m={'origin':'RecordedPC01application14','site':h['site'],'input_id':h['input_id'],'requested_tick':h['requested_tick'],'prepared_not_learned':True}
    site=[39,57,15]
    free=entries.get('DEE.Cognitive.System.1.1.PC01.free24')
    return{'INSTRUMENTO':{'profile':'PC01.orbit_guard','metadata':m,'lexical_frame_prepared':'lexical05'in configuration.get('relational_words_v2',{}),'free_route_preparation':decode_metadata(free)if free else None,'passive':True,'not_a_policy_learned_from_consequences':True},'ENTE':e.obs(a,site),'INTERPRETACION':'Samefixedpositionmayhelponehistoryandharmanother. PresenceofSEM4doesnotcertifyallfunctionsorindefinitestability.'}

def schedule_mapped_free_diversion(a,*,tick=26162):
    """Explicit P0 pulse for the mapped24history; not a general healing policy."""
    _frame(a)
    if type(tick)is not int or tick!=26162 or a.tick>tick:raise ValueError('This revision only supports the mapped future boundary26162 on its declared historical preparation. Never rewinds or retries.')
    name='PC01.FREE24.DIVERT'
    if name in a.world.runtime.channel_names:raise ValueError('Diversion channel already exists; do not duplicate an intervention')
    ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(57,0,19);ch.direction=d.Direction(0,1,1);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=name;p.channel=ch;a.world.declare_interface(p);r=a.world.submit(name,0,tick)
    info={'id':int(r.id),'channel':name,'site':[57,0,19],'tick':tick,'payload':0,'direction':[0,1,1],'semantic':1,'submitted':exact_receipt(r)}
    a.world.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.PC01.free24',encode_metadata({'schema':'PC01.free24.v1','mode':'divert','input':info,'prepared_not_acquired_strategy':True,'history':'Exactforkoftheprotected14lifeT25467; allcurrentinputsidenticalto17'}))
    return{'INSTRUMENTO':info,'status':'SCHEDULED_NOT_YET_PROVEN_APPLIED','INTERPRETACION':'Zero-load native material interaction preserves and redirects the mapped blocker. Timing/source chosen by researcher; not P2, not automatic cleanup, not valid for arbitrary late histories.'}

def schedule_new_context_protection(a,*,mode='divert'):
    """Fixed40preparation for the mapped future, never an autonomous selector."""
    _frame(a)
    if mode not in('guard','divert')or a.tick>39824:raise ValueError('PC01revision40only:explicitmodeandpre-interventioncheckpointrequired; no past input or repair')
    name='PC01.NEW40.'+('GUARD'if mode=='guard'else'DIVERT')
    if name in a.world.runtime.channel_names:raise ValueError('New-context intervention already declared')
    site=[60,7,32]if mode=='guard'else[59,8,31];direction=(0,0,0)if mode=='guard'else(1,-1,1);tick=39824 if mode=='guard'else 39832
    ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*site);ch.direction=d.Direction(*direction);ch.state=1;ch.semantic=4 if mode=='guard'else 1;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=name;p.channel=ch;a.world.declare_interface(p);r=a.world.submit(name,0,tick)
    result={'id':int(r.id),'channel':name,'site':site,'tick':tick,'payload':0,'direction':list(direction),'semantic':ch.semantic,'submitted':exact_receipt(r)}
    a.world.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.PC01.new_context40',encode_metadata({'mode':mode,'input':result,'prepared_not_learned_strategy':True,'scope':'MappedR33parent39752andnew+1phase12lesson; protectsnewmarkerwithknowncollateralold-functionlosses. Notageneralattentionmechanism.'}))
    return{'INSTRUMENTO':result,'status':'SCHEDULED_NOT_YET_PROVEN_APPLIED'}

def query_transformed_form(a,*,payload=7,use=False,word=None):
    """Use an already prepared41reader; never creates/trains a replacement."""
    _frame(a);entries=dict(a.world.runtime.snapshot_metadata_entries);key='DEE.Cognitive.System.1.1.PC01.transformed_reader41'
    if key not in entries:raise ValueError('No lived transformed-reader state; a catalog entry is not an acquired life')
    view=decode_metadata(entries[key])
    if view.get('reader_site')!=[57,18,43]or view.get('phase')!=39844%67 or view.get('action_consumptive'):raise ValueError('Wrong or post-use unvalidated native reader; do not reconstruct it')
    if type(payload)is not int or payload!=7 or type(use)is not bool or word not in(None,'cerca','lejos')or(use and word is None):raise ValueError('Finite41query:payload7; explicit recognized token required for consumptive use')
    name='PC01.POST41.LATER_QUERY'
    if name not in a.world.runtime.channel_names:raise ValueError('Full state lacks the lived query interface')
    target=e.tick_at_or_after(a.tick,phase=view['phase'],lead=3);req=[];r=a.world.probe(name,payload,target-3);req.append({'id':int(r.id),'port':name,'payload':payload,'tick':target-3});effect=None
    if use:
        sign=1 if word=='cerca'else-1;effect=e.move(view['reader_site'],(sign,1,1),4);direction=(-sign,-1,0);site=e.move(effect,direction,-3);port='PC01.POST41.USE.'+word
        if port in a.world.runtime.channel_names:raise ValueError('One-shot token action already declared')
        ch=d.ChannelSpec();ch.name=port;ch.injection_site=d.Coordinate(*site);ch.direction=d.Direction(*direction);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=port;p.channel=ch;a.world.declare_interface(p);r=a.world.submit(port,7,target+1);req.append({'id':int(r.id),'port':port,'payload':7,'tick':target+1})
    a.run_until(target);read=e.obs(a,view['reader_site']);words=['cerca'if read['direction'][0]>0 else'lejos']if e.valid(read,(1,1,1))or e.valid(read,(-1,1,1))else[];action=None
    if use:
        a.run_until(target+4);action=e.obs(a,effect);view['action_consumptive']=True;view['last_action_tick']=a.tick;a.world.runtime.set_snapshot_metadata(key,encode_metadata(view))
    return{'ENTE':{'read':read,'action':action},'SPANISH_DECODED':words,'NATIVE_ACTION_OBSERVED':None if action is None else e.valid(action,(0,0,1)),'INSTRUMENTO':{'material_probe':True,'recognized_token':word,'prepared_reader_not_self_selected':True,'consumptive':use,'requests':[e.receipt_at(a.world,r)for r in req]},'INTERPRETACION':'Native code recall/use from a lived transformed influence. Does not retest current spatial truth, re-teach a word, certify general Spanish or fill an absent reading.'}

def schedule_context_protection(a,*,tick=None):
    _configuration(a);state=protection_state(a)
    if state['INSTRUMENTO']['metadata']is not None:return{**state,'status':'ALREADY_RECORDED_NO_NEW_INPUT'}
    tick=a.tick+1 if tick is None else tick
    if type(tick)is not int or tick<a.tick:raise ValueError('Futureexactintegerboundaryrequired')
    name='PC01.CONTEXT_GUARD.V1'
    if name in a.world.runtime.channel_names:raise ValueError('Unrecordedexistingguardchannel; donot silently reinterpret it')
    ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(39,57,15);ch.direction=d.Direction(0,0,0);ch.state=1;ch.semantic=4;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=name;p.channel=ch;a.world.declare_interface(p);r=a.world.submit(name,0,tick)
    m={'schema':'PC01.context_guard.v1','site':[39,57,15],'input_id':int(r.id),'requested_tick':tick,'prepared_not_learned':True,'resources':'Onezero-loadSEM4materialinput; noRAW/clockedit','validated_history':'Application14fromMAIN05T10325anditsdeclaredcurriculum; prospective late16didnotestablishageneraladvantage'};a.world.runtime.set_snapshot_metadata(GUARD_KEY,encode_metadata(m))
    return{'INSTRUMENTO':m,'receipt':exact_receipt(r),'status':'SCHEDULED_NOT_YET_PROVEN_APPLIED','INTERPRETACION':'Doesnotadvanceorwaitforanoccupiedporttobecomeempty. Subsequentnormalnativeevolutiondecidesadmission; noretryorcleanup.'}

def current_dose(a,*,parameter,load,mode='full',frame='lexical05',phases=None):
    if type(parameter)is not int or parameter not in(-5,-3,-1,1,3,5)or type(load)is not int or load not in(2,3,4,5,6):raise ValueError('PC01dose domain: parameter+/-1/3/5 and exactactualdose2..6')
    if mode not in('full','no_A','no_B','offroute_B','no_events'):raise ValueError('Unknownexplicitnativecontrol')
    entry=_frame(a,frame);selected=list(entry['lexical_v3']['learned_phases'])if phases is None else list(phases)
    if not selected or any(type(p)is not int or p not in entry['lexical_v3']['learned_phases']for p in selected):raise ValueError('Onlyrecordedprotocolopportunityphasesmaybeselected; metadataisnotanevidenceverdict')
    rows=[]
    for phase in selected:
        baseline=e.tick_at_or_after(a.tick,phase=phase);a.run_until(baseline);before={b['id']:e.obs(a,b['hub'])for b in entry['banks']};target=baseline+67;start=target-13;req=[]
        def send(port):
            r=a.world.submit(port,load,start);req.append({'port':port,'payload':load,'tick':start,'id':int(r.id)})
        if mode not in('no_A','no_events'):send(entry['ports']['A_positions'][str(parameter)])
        if mode not in('no_B','no_events'):
            for port in entry['ports']['B']:send(port['off'if mode=='offroute_B'else'on'])
        a.run_until(target);after={b['id']:e.obs(a,b['hub'])for b in entry['banks']};qualified=[];strict=[];deltas={}
        for bank in entry['banks']:
            key=bank['id'];delta=after[key]['s_reg']-before[key]['s_reg'];deltas[key]=delta;old=f.decode({key:before[key]},entry);new=f.decode({key:after[key]},entry)
            if old and new and delta==2*load:qualified.extend(new)
            if old and new and delta in(6,10):strict.extend(new)
        rows.append({'phase':phase,'baseline_tick':baseline,'tick':a.tick,'before':before,'after':after,'increments':deltas,'dose_relative_decoded':qualified,'historical_strict_decoded':strict,'requests':[e.receipt_at(a.world,r)for r in req]})
    return{'actual_parameter':parameter,'actual_dose_each':load,'teacher_token_supplied':False,'physical_presentations':len(selected),'rows':rows,'SPANISH_DECODED':sorted(set(v['text']for r in rows for v in r['dose_relative_decoded'])),'historical_strict_SAME_TRAJECTORY':sorted(set(v['text']for r in rows for v in r['historical_strict_decoded'])),'instrument_limit':'2Lchecksphysicaldose,notsemanticsign; tokencomesfromacquirednativeX. Fixedexternalcoordination,notendogenouslearnedrouting. Historical3/5APIunchanged.'}

def existing_word_view(a,*,frame='lexical05',bank='d5',phase=21,view='PC01_existing_d5_view'):
    entry=_frame(a,frame)
    if type(phase)is not int or phase not in entry['lexical_v3']['learned_phases']:raise ValueError('Requestedphasehasno recordedexperience/opportunity')
    source=next((p for p in entry['banks']if p['id']==bank),None)
    if source is None:raise ValueError('Explicitunknownsourcebank')
    g=e.prepare(a);views=g.setdefault('lexical_bridges_v10',{});descriptor={'schema':'PC01.existing_word_view.v1','hub':source['hub'],'word_phase':phase,'ports':{'query':source['query']},'codebook':entry['lexical_v3']['codebook'],'taught':True,'after_comprehension':False,'view_of':{'frame':frame,'bank':bank,'phase':phase,'no_new_matter_or_learned_fields':True},'scope':'Viewonly. Nativeabsenceorfailureisnotfilledbythismetadata.'}
    if view in views:
        actual=views[view]
        if actual.get('view_of')!=descriptor['view_of']or actual.get('after_comprehension'):raise ValueError('Existingviewidentity/post-use state differs')
        return actual
    views[view]=descriptor;a.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g));return descriptor

def communicate_existing_word(a,*,communication,request_word=None,cut=False,sham=False):
    view='PC01_existing_d5_view';existing_word_view(a,view=view);result=b.communicate(a,bridge=view,communication=communication,request_word=request_word,cut=cut,sham=sham)
    if request_word is not None:
        g=e.prepare(a);g['relational_words_v2']['lexical05']['lexical_v3']['after_comprehension']=True;a.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g))
    return result
