"""Long matched A/B/C query-dose trajectories; more acquisition in each life."""
from pathlib import Path
import argparse,sys,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import Store
from app.native_tools import physical,moore27
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f,igualdad_fisica_03 as eq
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False)
if a.case not in('D_no_material_queries',):raise ValueError('Unknown fixed comparison arm')
s=Store(a.system);parent='ES01_LEXICAL5_source_guards_strict';life='ES01_LONG7_'+a.case;s.fork(parent,life,kind='CANDIDATE')
data={'case':a.case,'life':life,'parent':s.record(parent),'episodes':[],'teaching':[],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'dependency_sha256':{m.__name__:hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()for m in(e,f,eq)},
 'contract_before':{'decoder':'strict unchanged6/10','block_ticks':402,'episodes':24,'same_initial_state':True,'same_current_event_ticks':True,'B_extra_R0_guards':6,'A_B_extra_all_phase_word_query_each_episode':True,'C_no_extra_intermediate_word_query':True,'no_independent_replicate_claim':True}}
sequence=[(3,5),(-5,3),(-3,5),(5,3),(3,3),(-3,3),(-5,5),(5,5),(-3,3),(3,5),(5,3),(-5,3),
 (5,5),(-3,5),(3,3),(-5,5),(-3,3),(5,3),(-5,3),(3,5),(5,5),(3,3),(-3,5),(-5,3)]
data['predeclared_current_events']=sequence
data['contract_before']['D_no_intermediate_word_probe']=True
decode=f.decode
def passive_context(a,*,frame,parameter=3,load=3,phase=None,decoder='strict',event_a=True,event_b=True,offroute=False):
    g=e.prepare(a);entry=g.get('relational_words_v2',{}).get(frame)
    if entry is None or'lexical_v3'not in entry or entry['lexical_v3']['after_comprehension']:raise ValueError('Lived pre-use lexical frame required')
    phases=entry['lexical_v3']['learned_phases'];selected=phases if phase is None else[phase]
    if parameter not in(-5,-3,-1,1,3,5)or load not in(3,5)or any(p not in phases for p in selected)or decoder not in('strict','bounded_native_provision'):raise ValueError('Current physical position/time and protocol phase domain')
    rows=[]
    for p in selected:
        baseline=e.tick_at_or_after(a.tick,phase=p)
        if baseline>a.tick:a.run_until(baseline)
        before={b['id']:e.obs(a,b['hub'])for b in entry['banks']};target=baseline+67;start=target-13;req=[]
        def send(name,payload,t,probe=False):
            r=(a.world.probe if probe else a.world.submit)(name,payload,t);req.append({'port':name,'payload':payload,'tick':t,'id':int(r.id)})
        if entry['mode']=='relative_path':at=bt=start;ap=entry['ports']['A_positions'][str(parameter)]
        else:at=start+max(0,-parameter);bt=start+max(0,parameter);ap=entry['ports']['A']
        if event_a:send(ap,load,at)
        if event_b:
            for b in entry['ports']['B']:send(b['off'if offroute else'on'],load,bt)
        # No word-probe material in this production arm; actual events are unchanged.
        a.run_until(target);after={b['id']:e.obs(a,b['hub'])for b in entry['banks']};qualified=[];increments={}
        for b in entry['banks']:
            key=b['id'];delta=after[key]['s_reg']-before[key]['s_reg'];increments[key]=delta
            accepted=(6,10)if decoder=='strict'else(6,7,8,10,11,12)
            if delta in accepted and decode({key:before[key]},entry)and decode({key:after[key]},entry):qualified.extend(decode({key:after[key]},entry))
        rows.append({'phase':p,'baseline_tick':baseline,'tick':a.tick,'before':before,'after':after,'native_increments_after_query_dose':increments,'SPANISH_DECODED':qualified,'requests':[e.receipt_at(a.world,r)for r in req]})
    return {'ENTORNO':{'actual_parameter':parameter,'load_each':load,'teacher_token_supplied':False,'repeated_actual_experiences':len(selected),'event_a':event_a,'event_b':event_b,'offroute':offroute},'ENTE':rows,'SPANISH_DECODED':[r for row in rows for r in row['SPANISH_DECODED']],
        'INSTRUMENTO':{'decoder_revision':decoder,'decoder':'Acquired X marker plus strict6/10 or a predeclared native-provision band6/7/8/10/11/12 without intermediate word-probe dose (zero). No sign/position/time comparison used by decoder.'},
        'INTERPRETACION':'Current context production in a finite trained frame. When all acquired phases are used the physical scene is presented once per phase; that cost is not hidden or endogenous.'}



def trial(x):
 if a.case=='B_query_regulated':data['query_regulator']=f.regulate_queries(x,frame='lexical05')
 # Align after the optional guard installation, before identical real lessons.
 boundary=e.tick_at_or_after(x.tick,phase=13,lead=4);x.run_until(boundary)
 data['teaching'].append(f.teach(x,frame='lexical05',parameter=5,word='cerca',phase_shift=0))
 data['teaching'].append(f.teach(x,frame='lexical05',parameter=-5,word='lejos',phase_shift=4))
 data['four_acquisitions_before_stream']=f.query(x,frame='lexical05')
 first=e.tick_at_or_after(x.tick,phase=13,lead=4);data['first_block_tick']=first
 for j,(k,load)in enumerate(sequence):
  boundary=first+402*j
  if x.tick>boundary:raise RuntimeError('Fixed trial calendar exceeded; do not shift it to hide a delay')
  x.run_until(boundary);row={'episode':j+1,'block_start':boundary,'environment_parameter':k,'load_each':load,'expected_auditor_only':'cerca'if k>0 else'lejos'}
  row['current']=passive_context(x,frame='lexical05',parameter=k,load=load,decoder='strict')
  if False:row['extra_probe']=f.query(x,frame='lexical05')
  x.run_until(boundary+401);row['block_end']=x.tick;row['physical']=physical(x.world,occupation=True);data['episodes'].append(row)
  if j in(3,11,23):x.save(a.out/('T'+str(x.tick)+'.deetsnap.gz'))
 data['final_lexical_query']=f.query(x,frame='lexical05');data['prior_comparison_forms']=e.query_words(x)
 data['prior_contact']=e.contact_query(x,frame='contactoA');data['prior_free']=e.contact_query(x,frame='freeRepair5');data['prior_temporal']=e.temporal_query(x,frame='secuenciaA');data['prior_equal']=eq.query(x)
 data['post']=physical(x.world,occupation=True)
 return {'tick':x.tick,'current_responses':[r['current']['SPANISH_DECODED']for r in data['episodes']],
  'final_words':data['final_lexical_query']['SPANISH_DECODED'],'prior_comparisons':data['prior_comparison_forms']['FORMAS_ACCESIBLES'],'prior_contact':data['prior_contact']['SPANISH_DECODED'],'prior_free':data['prior_free']['SPANISH_DECODED'],'prior_equal':data['prior_equal']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'EF01_LEXICAL_LONG_SAME_EVENTS_NO_INTERMEDIATE_WORD_PROBES_R7',trial)
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
