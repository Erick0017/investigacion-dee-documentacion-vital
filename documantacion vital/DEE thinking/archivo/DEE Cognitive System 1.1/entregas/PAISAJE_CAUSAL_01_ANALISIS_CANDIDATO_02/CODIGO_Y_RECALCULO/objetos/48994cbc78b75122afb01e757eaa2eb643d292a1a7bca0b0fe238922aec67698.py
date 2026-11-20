"""Long matched application of the orbit-specific guard, with new reserves.

Source-local guard09cut a useful old word. The orbit guard preserves that
word in the short diagnostic. This cut tests the orbit guard over the full
actual event curriculum and a new post-design acquisition/use panel.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical,observe
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f,igualdad_fisica_03 as eq
from instrumentos_pc01 import guard,witness,receipts,frame,sha
from dee_thinking.persistence import encode_metadata
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='ES01_LONG7_D_no_material_queries'if a.case=='control'else'ES01_MAIN_05';life='PC01_APLICACION14_'+a.case;s.fork(parent,life,kind='CANDIDATE');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'historical_prefix':[],'long_history':[],'reserved':[],'criteria_before':'Freeze the new whole-course test before results: same historical lessons,24eventblocks402ticks, no intermediate word queries; prepared native orbit guard39,57,15 versus equal-material sham39,65,15. No counterfactual imported. Then one new near5lessonphase8 and first material recall atphase21; all acquired phases used for every reserved scene, strict6/10decoder unchanged. Report prior functions and cost, not a universal winner.','reserve':[[5,5],[-5,3],[3,5],[-3,3],[5,3],[-5,5],[3,3],[-3,5],[1,3],[-1,3]]}
def cap(x,label,row):data['historical_prefix'].append({'label':label,'tick':x.tick,'result':row})
def trial(x):
    if a.case!='control':
        data['protection']=guard(x.world,'PC01.APPLY14.ORBIT',[39,57 if a.case=='guard'else 65,15],10326)
        x.world.runtime.set_snapshot_metadata('DEE.Cognitive.System.1.1.PC01.orbit_guard',encode_metadata({'revision':'PC01.orbit_guard14.v1','case':a.case,'site':data['protection']['site'],'input_id':data['protection']['id'],'requested_tick':10326,'prepared_not_learned':True,'domain':'Matchedlexical05N67historyfromMAIN05T10325; conditional gains only if reserved panel succeeds'}))
        f.prepare(x,frame='lexical05',mode='relative_path',origin=(38,50,8),guarded=True,renew_sources=True);cap(x,'teach_near3',f.teach(x,frame='lexical05',parameter=3,word='cerca',phase_shift=0));cap(x,'first_near_recall',f.query(x,frame='lexical05'));cap(x,'teach_far3',f.teach(x,frame='lexical05',parameter=-3,word='lejos',phase_shift=4));cap(x,'both_recall',f.query(x,frame='lexical05'))
        for j,(k,load)in enumerate(((-3,5),(3,3),(-3,3),(3,5),(5,3),(-5,3))):cap(x,'current_'+str(j),f.context(x,frame='lexical05',parameter=k,load=load,decoder='strict'))
        cap(x,'retention',f.query(x,frame='lexical05'));cap(x,'old_words',e.query_words(x));cap(x,'old_contact',e.contact_query(x,frame='contactoA'));cap(x,'old_free',e.contact_query(x,frame='freeRepair5'));data['before_long']=physical(x.world,occupation=True);x.save(a.out/'T12066_ANTES_LARGO.deetsnap.gz')
        boundary=e.tick_at_or_after(x.tick,phase=13,lead=4);x.run_until(boundary);cap(x,'teach_near5',f.teach(x,frame='lexical05',parameter=5,word='cerca',phase_shift=0));cap(x,'teach_far5',f.teach(x,frame='lexical05',parameter=-5,word='lejos',phase_shift=4));cap(x,'four_before_long',f.query(x,frame='lexical05'));first=e.tick_at_or_after(x.tick,phase=13,lead=4)
        sequence=[(3,5),(-5,3),(-3,5),(5,3),(3,3),(-3,3),(-5,5),(5,5),(-3,3),(3,5),(5,3),(-5,3),(5,5),(-3,5),(3,3),(-5,5),(-3,3),(5,3),(-5,3),(3,5),(5,5),(3,3),(-3,5),(-5,3)]
        for j,(k,load)in enumerate(sequence):
            boundary=first+402*j;x.run_until(boundary);row=f.context(x,frame='lexical05',parameter=k,load=load,decoder='strict',emit_word_queries=False);x.run_until(boundary+401);data['long_history'].append({'episode':j+1,'parameter':k,'load':load,'result':row,'physical':physical(x.world,occupation=True)})
            if j in(3,11,23):x.save(a.out/('LARGO_T'+str(x.tick)+'.deetsnap.gz'))
            print(json.dumps({'progress':'long_history','case':a.case,'episode':j+1,'tick':x.tick}),flush=True)
        cap(x,'final_lexical',f.query(x,frame='lexical05'));cap(x,'prior_comparison_forms',e.query_words(x));cap(x,'prior_contact',e.contact_query(x,frame='contactoA'));cap(x,'prior_free',e.contact_query(x,frame='freeRepair5'));cap(x,'prior_temporal',e.temporal_query(x,frame='secuenciaA'));cap(x,'prior_equal',eq.query(x))
    data['before_new_acquisition']=physical(x.world,occupation=True);x.save(a.out/'ANTES_NUEVA_ADQUISICION_COMPLETO.deetsnap.gz')
    data['new_lesson']=f.teach(x,frame='lexical05',parameter=5,word='cerca',phase_shift=8);data['at_acquisition']=physical(x.world,occupation=True);x.save(a.out/'NUEVA_ASOCIACION_COMPLETO.deetsnap.gz');hub=next(b['hub']for b in e.prepare(x)['relational_words_v2']['lexical05']['banks']if b['id']=='d5');data['loop_observations']=[]
    for dt in(54,55,56,57,58,59,66,67):
        target=data['at_acquisition']['tick']+dt;x.run_until(target);site=e.move(hub,(1,1,1),dt);data['loop_observations'].append({'tick':x.tick,'site':site,'record':observe(x.world,site),'witness':witness(x.world,site,3)if dt in(57,58)else None})
    data['first_recall']=f.query(x,frame='lexical05',phase=21)
    for j,(k,load)in enumerate(data['reserve']):
        row=f.context(x,frame='lexical05',parameter=k,load=load,decoder='strict',emit_word_queries=False);data['reserved'].append({'trial':j+1,'parameter':k,'load':load,'result':row,'physical':physical(x.world,occupation=True)})
    data['old_after']={'words':e.query_words(x),'contact':e.contact_query(x,frame='contactoA'),'free':e.contact_query(x,frame='freeRepair5'),'time':e.temporal_query(x,frame='secuenciaA'),'equal_form':eq.query(x)};data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'new_phase_first_recall':data['first_recall']['SPANISH_DECODED'],'reserved':[r['result']['SPANISH_DECODED']for r in data['reserved']],'old_contact':data['old_after']['contact']['SPANISH_DECODED'],'old_free':data['old_after']['free']['SPANISH_DECODED'],'old_equal':data['old_after']['equal_form']['SPANISH_DECODED']}
data['commit']=s.mutate(life,'PC01_LONG_NATIVE_ORBIT_PROTECTION_LEARNING_APPLICATION14',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
