"""Native return of retained B content to the consumed E1 form channel.

Same prepared opportunities for both possible contents. First turns contribute
only -X/-Y, never a content Zbit. No reference, word teacher or old state is
reintroduced. Transport is prepared, not a strategy discovered by E1.
"""
from pathlib import Path
import argparse,sys,json,gzip
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path[:0]=[str(a.system),str(Path(__file__).parent),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01')]
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,paisaje_causal_01 as pc
from instrumentos_pc01 import guard,receipts,sha,frame,witness
from conductos_nativos import routes_for_common_arrival
from avance_acotado import install as install_budget
from dee_thinking.persistence import decode_metadata,encode_metadata
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='AA01_RECEPTOR14_down'if'down'in a.case else'AA01_RECEPTOR14_up';life='AA01_RETORNO15_'+a.case;s.fork(parent,life,kind='CANDIDATE');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'criteria_before':'Retained received Zcontent, not the original source name, determines its fixed inverse codebook route. Allfour Bslots have equal opportunities. Generic -X and-Y initial turns cannot supply either Zsign. No content/ref/teacher after parent. Distinguish returnofform from restoredcurrentcomparison and from Bretention; moving a carrier is not copying it.','requests':[]}
def trial(x):
    window=install_budget(x,a.out,seconds=220);data['worker_window']={k:v for k,v in window.items()if k!='original'};data['pre']=physical(x.world,occupation=True);entries=dict(x.world.runtime.snapshot_metadata_entries);meta=decode_metadata(entries['DEE.Cognitive.System.1.1.AA01.B_recovery14']);B=meta['B'];words=e.prepare(x)['words'];first=e.tick_at_or_after(x.tick,phase=meta['phase'],lead=10);data['first_transform_tick']=first;data['B_geometry']=B;data['source_geometry']=words;seen={}
    def send(name,site,d,t,payload=0,sem=1):
        key=(tuple(site),tuple(d),t,payload,sem)
        if key in seen:return seen[key]
        r=guard(x.world,'AA01.RETURN15.'+name,site,t,direction=d,semantic=sem,payload=payload);data['requests'].append(r);seen[key]=r;return r
    def arrive(name,site,d,t,payload=0):return send(name,e.move(site,d,-3),d,t-3,payload)
    starts={};endpoints={};mapping={}
    for key,item in B.items():
        z=item['z'];R=item['effect'];destination='menos'if z<0 else'más';mapping[key]=destination;starts[key]={'site':e.move(R,(0,0,z),5),'direction':[0,0,z]};endpoints[key]={'site':words[destination]['hub'],'direction':words[destination]['signature']}
        normalize=e.move(R,(0,1,0),12)if'normalizer_sham'in a.case else R
        arrive('NORMALIZE.'+key+'.X',normalize,(-1,0,0),first,0);arrive('NORMALIZE.'+key+'.Y',normalize,(0,-1,0),first,0)
        if'content_cut'in a.case or'content_sham'in a.case:
            site=e.move(R,(1,1,z),-4)
            if'content_sham'in a.case:site=e.move(site,(1,0,0),12)
            send('CONTENT_CUT.'+key,site,(0,0,0),first-5,0,4)
    plans=routes_for_common_arrival(starts,endpoints,first+5,phase=6);goal=next(iter(plans.values()))['arrival_tick'];data['plans']=plans;data['goal_tick']=goal;data['fixed_Z_to_form_mapping']=mapping
    for key,plan in plans.items():
        for j,turn in enumerate(plan['turns']):
            for k,pulse in enumerate(turn['pulses']):arrive('RELAY.'+key+'.'+str(j)+'.'+str(k),turn['site'],pulse['direction'],turn['tick'],pulse['payload'])
    data['all_recovery_inputs_queued_before_observing_the_B_code']=True;data['no_reference_or_word_reteaching']=True;moments={first-1,first,first+5,goal-1,goal};before_phase=e.tick_at_or_after(x.tick,phase=6)
    if before_phase<first:moments.add(before_phase)
    for plan in plans.values():
        for turn in plan['turns']:moments.update((turn['tick']-1,turn['tick']))
    data['samples']=[]
    with gzip.open(a.out/'CAMPOS_RETORNO.jsonl.gz','xt',encoding='utf8',compresslevel=6)as f:
        for tick in sorted(moments):
            x.run_until(tick);f.write(json.dumps(frame(x.world),separators=(',',':'))+'\n');data['samples'].append({'tick':tick,'physical':physical(x.world)})
            if tick==before_phase:data['old_form_passive_before_return']={word:observe(x.world,item['hub'])for word,item in words.items()}
            if tick==first-1:data['pre_B_normalization']={key:witness(x.world,item['effect'])for key,item in B.items()}
            if tick==first:data['normalized_B']={key:observe(x.world,item['effect'])for key,item in B.items()}
            if tick==first+5:data['transport_started']={key:observe(x.world,row['site'])for key,row in starts.items()}
            if tick==goal:data['returned_forms']={word:observe(x.world,item['hub'])for word,item in words.items()};data['returned_state_complete']=x.save(a.out/'RETORNO_CODIGO_ESTADO_COMPLETO.deetsnap.gz')
    data['current_after']={}
    for value in(61,119,70,120):data['current_after'][str(value)]=e.context(x,value=value,method='B')
    data['other_after']={'near':pc.current_dose(x,parameter=3,load=4),'far':pc.current_dose(x,parameter=-3,load=6),'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5')}
    Btick=e.tick_at_or_after(x.tick,phase=meta['phase'],lead=3)
    for key,item in B.items():arrive('FINAL_B_RECALL.'+key,item['effect'],(1,1,0),Btick,7)
    x.run_until(Btick);data['B_after']={key:observe(x.world,item['effect'])for key,item in B.items()};data['receipts']=receipts(x.world.runtime);data['post']=physical(x.world,occupation=True)
    x.world.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.AA01.return15',encode_metadata({'parent_B_recovery':meta,'plans':plans,'first_tick':first,'goal_tick':goal,'returned_not_copied':True,'no_content_teacher_or_reference_supplied':True}));return{'life':life,'tick':x.tick,'first':first,'goal':goal,'returned':{k:r['direction']for k,r in data['returned_forms'].items()},'current_words':{k:v['TRADUCCION']['SPANISH_DECODED']for k,v in data['current_after'].items()},'other_words':{k:v.get('SPANISH_DECODED')for k,v in data['other_after'].items()},'B_still_qualified':[key for key,row in data['B_after'].items()if e.valid(row,(1,1,-1))or e.valid(row,(1,1,1))]}
try:data['commit']=s.mutate(life,'AA01_NATIVE_RETURN_WITHOUT_RETEACHING_15',trial)
except Exception as error:
    data['instrument_failure']={'type':type(error).__name__,'detail':str(error)};data['failed_complete_state']=s.record(life);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if'Cooperative time window ended'in str(error):print(json.dumps({'status':'PARTIAL_TIME_WINDOW','life':life,'tick':data['failed_complete_state']['physical']['tick']}));raise SystemExit(0)
    raise
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
