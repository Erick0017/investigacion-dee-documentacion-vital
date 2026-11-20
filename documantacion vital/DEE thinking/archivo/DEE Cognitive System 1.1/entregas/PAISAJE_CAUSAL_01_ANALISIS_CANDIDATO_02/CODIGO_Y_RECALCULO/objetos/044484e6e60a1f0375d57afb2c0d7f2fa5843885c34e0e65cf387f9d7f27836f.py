"""New preregistered dose-domain reader, not a retrospective old decoder fix.

The old API keeps its3/5domain and strict6/10criterion. This new experimental
protocol tests2/4/6and a fixed2Lmaterial-increment prediction. Native wordX
chooses the token. Lnever determines which token; it is instrument dose.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f,igualdad_fisica_03 as eq
from instrumentos_pc01 import receipts,sha
from dee_thinking.persistence import encode_metadata
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_APLICACION14_guard';life='PC01_DOSIS17_'+a.case;s.fork(parent,life,kind='CANDIDATE');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'trials':[],'criteria_before':'Distinct recipePC01.dose17: exact same physical geometry/learned markers, new current doses2/4/6. Decodeacquiredwordonlyifbefore/afterqualifiedandincrement=2L, fixed before any reserved response. Historicalstrict6/10is also computed on the SAME native data, outside its original load domain, not scored as product regression. No extra teacher cue; each actual scene is repeated at all acquired phases. NoA/noB/offrouteB/bothomitted controls on exact forks.','schedule':[[5,2],[-3,4],[3,6],[-5,6],[5,4],[-3,2],[3,4],[-5,2],[5,6],[-5,4],[3,2],[-3,6]]if a.case=='reserved'else[[5,4]]}
def native_current(x,k,load):
    entry=e.prepare(x)['relational_words_v2']['lexical05'];phases=entry['lexical_v3']['learned_phases'];rows=[]
    for phase in phases:
        baseline=e.tick_at_or_after(x.tick,phase=phase);x.run_until(baseline);before={b['id']:e.obs(x,b['hub'])for b in entry['banks']};target=baseline+67;start=target-13;req=[]
        def send(port):
            r=x.world.submit(port,load,start);req.append({'port':port,'payload':load,'tick':start,'id':int(r.id)})
        if a.case not in('no_A','no_events'):send(entry['ports']['A_positions'][str(k)])
        if a.case not in('no_B','no_events'):
            for b in entry['ports']['B']:send(b['off'if a.case=='offroute_B'else'on'])
        x.run_until(target);after={b['id']:e.obs(x,b['hub'])for b in entry['banks']};qualified=[];strict=[];deltas={}
        for b in entry['banks']:
            key=b['id'];delta=after[key]['s_reg']-before[key]['s_reg'];deltas[key]=delta;old=f.decode({key:before[key]},entry);new=f.decode({key:after[key]},entry)
            if old and new and delta==2*load:qualified.extend(new)
            if old and new and delta in(6,10):strict.extend(new)
        rows.append({'phase':phase,'baseline_tick':baseline,'tick':x.tick,'before':before,'after':after,'increments':deltas,'dose_relative_decoded':qualified,'historical_strict_decoded':strict,'requests':[e.receipt_at(x.world,r)for r in req]})
    return{'actual_parameter':k,'actual_dose_each':load,'teacher_token_supplied':False,'physical_presentations':len(phases),'rows':rows,'SPANISH_DECODED':sorted(set(v['text']for r in rows for v in r['dose_relative_decoded'])),'historical_strict_SAME_TRAJECTORY':sorted(set(v['text']for r in rows for v in r['historical_strict_decoded'])),'instrument_limit':'2Lchecks physical dose, not semantic sign; token comes from acquired nativeX. Current protocol is an explicitly prepared coordinator, not endogenous learned routing.'}
def trial(x):
    data['pre']=physical(x.world,occupation=True)
    for j,(k,load)in enumerate(data['schedule']):
        row=native_current(x,k,load);data['trials'].append(row);x.world.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.PC01.dose17',encode_metadata({'schema':'PC01.dose17.v1','case':a.case,'completed_episodes':j+1,'actual_curriculum':data['schedule'],'last_tick':x.tick,'decoder':'qualifiednativeXplus2Lmaterialincrement','no_expected_words_in_state':True}))
        if j in(3,7,11):x.save(a.out/('T'+str(x.tick)+'_CONTINUIDAD_COMPLETA.deetsnap.gz'))
    data['old_after']={'forms':f.query(x,frame='lexical05'),'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5'),'time':e.temporal_query(x,frame='secuenciaA'),'equal':eq.query(x),'comparison_forms':e.query_words(x)};data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'new_dose_responses':[r['SPANISH_DECODED']for r in data['trials']],'historical_strict_on_same_data':[r['historical_strict_SAME_TRAJECTORY']for r in data['trials']],'contact':data['old_after']['contact']['SPANISH_DECODED'],'free':data['old_after']['free']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'PC01_POST_DESIGN_DOSE_EXTENSION17',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
