"""CPC7 U0: acquired repertoire + physical request + returned-message memory.

Construction is frozen before experience. Only the generator transports current
observations. Decoders inspect present physical records, never expected labels.
"""
import argparse,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE/'endogenous'))
from common import ROOT,identity,put,sha,record,receipt,digest,operational,interface,until,local_context
from integrated import Session
import order_memory,repertoire_reference
import comparison_need as need

def create(k=16,center=(33,25,42),backend='LAZY',source_load=7,regulation=None):
    import dee_thinking as d
    if source_load==7:body=order_memory.prepare_geometry(center=center)
    else:
        import body_source
        body=body_source.prepare_geometry(center=center,source_load=source_load)
    adapter=need.prepare_geometry(origin=body['geometry']['emission_site'])
    spec,ports=repertoire_reference.geometry({'N':67,'K':k,'plane_gap':2,'translation':[0,0,0]})
    words={};ports=list(ports)
    for name,b in adapter['geometry']['branches'].items():
        if not b['dx']:continue
        sign=b['dx'];q=tuple(b['source_contact']);cue='message_form.teach.'+b['lane'];query='message_form.query.'+b['lane']
        ports.append(interface(cue,need.moved(q,(-sign,0,0),-3),(-sign,0,0)))
        ports.append(interface(query,need.moved(q,(-1,0,0),-3),(-1,0,0)))
        words[b['lane']]={'site':list(q),'teach_port':cue,'query_port':query,'teach_tick':21,'encounter_tick':24,
            'scope':'Opaque sign paired with arriving requested information, not a Spanish primitive or a response lookup'}
    ps=body['placements']+adapter['placements'];ports=body['interfaces']+adapter['interfaces']+ports
    if regulation:
        import need_regulation_v3
        guard=need_regulation_v3.prepare_geometry(adapter['geometry'],mode=regulation)
        ps+=guard['placements'];adapter['geometry']['regulation']=guard['geometry']
    sites=[(p.site.x,p.site.y,p.site.z) for p in ps]
    if len(set(sites))!=len(sites) or len({p.name for p in ports})!=len(ports):raise ValueError('Preparation overlap')
    recipe=d.OrganizationRecipe.research(67,ps,0);recipe.interfaces=ports
    recipe.execution=d.TickOptions(getattr(d.Backend,backend),2 if backend=='DENSE_PARALLEL' else 1)
    return Session(d.OrganizationalWorld.create(recipe),{'body':body['geometry'],'need':adapter['geometry'],'repertoire':spec,
        'message_form':words,'schema':'CPC7.U0.geometry.v1'},identity='U0_NEW_CPC7')

def observe_form(s,name):
    f=next(f for f in s.geometry['repertoire']['forms'] if f['name']==name)
    return record(s.world,f['hub'])

def decode(p,payload):
    valid=p['active'] and p['semantic']==1 and p['s_reg']>payload and p['direction'] in ([-1,-1,0],[-1,1,0])
    return {'valid':valid,'value':p['direction'][1] if valid else None,'physical':p,'provenance':'ENTE' if valid else 'INSTRUMENTO'}

def run(case,stream_path,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.monotonic();engine=identity()
    stream_path=Path(stream_path);stream=json.loads(stream_path.read_text(encoding='utf-8'))
    if stream['task']!='DIRECT':raise ValueError('Frozen central interface only direct forms; order body is a separate acquired relation')
    s=create(len(stream['interface']['forms']),tuple(case.get('center',[33,25,42])),case.get('backend','LAZY'),case.get('source_load',7),case.get('regulation'))
    w=s.world;g=s.geometry['need'];rows=[];readouts=[];word_reads=[];contexts=[];snaps=[];timings=[];forecasts=[]
    put(out/'CONFIG.json',{'case':case,'stream_sha256':sha(stream_path),'code_sha256':sha(__file__),'geometry':s.geometry,
        'preparation_freeze':'Before any target relation is acquired; no trained snapshot loaded',
        'dependency_sha256':{p.name:sha(p) for p in [HERE/'order_memory.py',HERE/'repertoire_reference.py',HERE/'endogenous/comparison_need.py',HERE/'endogenous/body_source.py',HERE/'endogenous/need_regulation_v3.py']},
        'criterion':'Question19 -> requested information24 paired with opaque form -> signal-only access91 and subsequent rounds; own repertoire queried by explicit named interface.',
        'claims_separated':['Comparison-conditioned native request','Fixed-interface access to own repertoire','New returned-information association','No generic uncertainty detector or learned source-choice claimed'],
        'decoder':'Active semantic1/s_reg>query/exact(-1,±1,0); invalid directions and absent fields preserved.'})
    if case.get('history','AB')!='NONE':s.stimulate(order_memory.experience(case.get('history','AB')))
    if not case.get('reader_omitted'):s.stimulate([{'port':'order.read','payload':7,'tick':2,'kind':'probe','origin':'COMMON_HISTORY_READER'}])
    s.stimulate(need.source_protocol(g,case.get('source_value',1),case.get('source_mode','paired')))
    def snap(label):
        p=out/(label+'.deetsnap');v=s.save(p);v['path']=p.name;snaps.append(v)
    snap('INITIAL_T0')
    observations={5,14,15,18,19,20,21,23,24,25,26,28,29,30,66,67,69,70,87,88,89,90,91,92,133,134,137,155,156,157,158,159,201,204,222,225,268,271,289,292,335,338}
    pending={};word_pending={};word_queries=case.get('word_query_ticks',[88,155,222,289])
    checkpoints=set(case.get('checkpoints',[24,70,91,137,204,271,338]))
    for tick in range(case.get('horizon',338)+1):
        before=time.perf_counter();s.advance_to(tick)
        if tick==5:
            forecasts.append({'emission_tick':5,'target_tick':15,'physical_emission':record(w,s.geometry['body']['emission_site']),
                'available_information':'Experienced A/B events and common reader; actual event not yet submitted','provenance':'ENTE'})
            put(out/'PREDICCIONES.json',forecasts)
        if tick==11 and not case.get('actual_omitted'):s.stimulate(need.actual_protocol(g,case.get('actual',-1)))
        if tick==21 and case.get('name_mode','paired')!='omitted':
            offset=int(case.get('name_mode')=='unpaired')
            s.stimulate([{'port':p['teach_port'],'payload':5,'tick':21+offset,'kind':'submit','origin':'OPAQUE_NAME_PAIRED_WITH_REQUESTED_CURRENT_INFORMATION'} for p in s.geometry['message_form'].values()])
        if tick in word_queries:
            qs=[{'port':p['query_port'],'payload':case.get('word_query_payload',5),'tick':tick,'kind':'probe','origin':'COMMON_OPAQUE_SIGN_QUERY_BOTH_BANKS'} for p in s.geometry['message_form'].values()]
            prior=len(s.requests);s.stimulate(qs);word_pending[tick+3]=s.requests[prior:]
        for e in (e for e in stream['stream'] if e['tick']==tick):
            f=e['stimulus']['form_id']
            if e['stimulus']['context_id']!=0:raise ValueError('Unsupported central context')
            req=[]
            if e['operation']=='experience':
                if e['teacher_present']:
                    sign=e['observed_consequence'];assert sign in(-1,1)
                    req.append({'port':f+'.event.'+('plus' if sign==1 else 'minus'),'payload':e['teacher_payload'],'tick':e['teacher_tick'],'kind':'submit','origin':'CURRENT_OBSERVED_CONSEQUENCE'})
                req.append({'port':f+'.signal','payload':e['signal_payload'],'tick':tick,'kind':'submit','origin':'OPAQUE_SYMBOL_EXPERIENCE'})
            elif e['operation']=='query':req=[{'port':f+'.signal','payload':e['query_payload'],'tick':tick,'kind':'probe','origin':'EXPLICIT_NAMED_REPERTOIRE_ACCESS'}]
            else:raise ValueError('Unsupported stream operation')
            prior=len(s.requests);s.stimulate(req)
            if e['operation']=='query':pending.setdefault(tick+3,[]).append((e,s.requests[prior]['id']))
        for e,identifier in pending.get(tick,[]):
            d=decode(observe_form(s,e['stimulus']['form_id']),e['query_payload']);r=receipt(w,identifier)
            readouts.append({'event_id':e['event_id'],'block':e['block'],'stimulus':e['stimulus'],'input_tick':e['tick'],'tick':tick,'receipt':r,
                'response':d['value'] if r['status']=='applied' else None,'coverage':d['valid'] and r['status']=='applied','physical':d['physical'],'provenance':'ENTE'})
        for q in word_pending.get(tick,[]):
            lane=q['port'].rsplit('.',1)[1];p=record(w,s.geometry['message_form'][lane]['site']);rr=receipt(w,q['id']);d=decode(p,q['payload'])
            word_reads.append({'input_tick':q['tick'],'tick':tick,'bank':lane,'receipt':rr,**d,'admitted_valid':d['valid'] and rr['status']=='applied'})
        if tick in observations:
            rows.append({'tick':tick,'body':order_memory.observations(w,s.geometry['body']),'need':need.capture(w,g),
                'message_form':{k:record(w,p['site']) for k,p in s.geometry['message_form'].items()}})
        if tick in (14,15,18,19,20,23,24,25,88,89,90,91,157,158):
            contexts.append({'tick':tick,'question_sites':{k:local_context(w,p['request_site']) for k,p in g['branches'].items()},
                'word_banks':{k:local_context(w,p['site']) for k,p in s.geometry['message_form'].items()}})
        if tick in checkpoints:
            snap('T'+str(tick));put(out/'PROGRESS.json',{'last_complete_tick':tick,'rows':rows,'word_reads':word_reads,'repertoire_reads':readouts,'checkpoints':snaps})
        timings.append(time.perf_counter()-before)
    at={r['tick']:r for r in rows}
    questions=[{'branch':k,'physical':p} for k,p in at[19]['need']['questions'].items() if p['active'] and p['direction'][0] in(-1,1) and p['direction'][1:]==[0,0]]
    result={'schema':'CPC7.U0.life.v1','case':case,'engine':engine,'input_sha256':sha(stream_path),'code_sha256':sha(__file__),
        'geometry':s.geometry,'individual':s.identity,'preparations':1,'diagnostic_forks':0,'continuations':0,'same_RUNTIME':True,
        'rows':rows,'requests':s.receipts(),'native_questions':questions,'predictions':forecasts,'responses':readouts,'word_reads':word_reads,
        'local_windows':contexts,'checkpoints':snaps,'final_physical':digest(w),'final_operational':operational(w),
        'resources':{'basic_buffers_bytes':32*67**3,'prepared_sites':len(order_memory.prepare_geometry()['placements'])+4,
                     'interfaces':len(w.runtime.channel_names),**repertoire_reference.memory()},
        'elapsed_seconds':time.monotonic()-started,'native_step_wall_seconds':sum(timings),'host_RAW_clock_edits_after_T0':[],
        'scope':'Shared-runtime integration. Selective named access is fixed interface, question is comparison-conditioned. Return-message sign and independent repertoire may interfere; invalid outputs retained.'}
    put(out/'MEASUREMENTS.json',result)
    print(json.dumps({'id':case['id'],'questions':len(questions),'word_reads':[(r['tick'],r['bank'],r['value']) for r in word_reads if r['admitted_valid']],
                      'repertoire_valid':sum(r['coverage'] for r in readouts),'seconds':result['elapsed_seconds']}),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--stream',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(json.loads(a.case.read_text(encoding='utf-8')),a.stream,a.out)
