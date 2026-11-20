"""R7 follow-up: postformed query control and low-content recurrence."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import mente_integral_mi01 as mi
from capacidades.mente_integral_mi01 import contexto_B_preparado as builder,fallo_y_consulta as candidate
from capacidades.integracion_situada_01 import ic_native_core as n
cases=[(343,'MI01_BASE_HISTORICA_T23453','fixed43','cut'),(344,'MI01_BASE_HISTORICA_T23453','fixed43','sham'),(345,'E1_MI01_MAIN','fixed43','none'),(346,'E1_MI01_MAIN','zero','none'),(347,'MI01_BASE_HISTORICA_T23453','sham43','none')]
atomic_json(E/'CONTEXTO_B_CONTROLES_R7B_PROTOCOLO.json',{'cases':cases,'availability':[1,-1],'private_raw':[14,14],'criterion':'Second low private content should require a retained scalar frame rather than surviving merely because only a large object gradient remains. Cut/sham is applied to the formed first query, not by omitting all apparatus.','late_test':'345/346 are exact forks of current MAIN T24752, with explicit new route experiences (not preserved old selection). These cannot transplant learned states into MAIN.','no_changed_outcome_rule':True})
for number,parent,context,cut in cases:
    life='MI01_CONTEXTO_B_'+str(number);fork(parent,life)
    def fn(a,life=life,context=context,cut=cut):
        experience=mi.train(a,episode=life+'.own_experience',contexts=[-1,1],feedback='paired',center=[40,35,55]);p=builder.prepare(a,builder='direct_failure',name=life,availability=[1,-1],private_values=[14,14],mode='intact',actor_return=False,b_context=context);extra=[]
        if cut!='none':
            site=n.move(p['S'],(1,-1,0),1)
            if cut=='sham':site=n.move(site,(0,0,1),19)
            extra.append(n.submit(a,'MI01.context_control.'+life,site,(0,0,0),p['plans'][0]['query_tick'],0,4))
        a.save(E/(life+'.PREPARADO.deetsnap.gz'));v=candidate.advance(a,name=life);a.save(E/(life+'.FINAL.deetsnap.gz'))
        return{'experience':experience,'plan':p,'trajectory':v,'extra_requests':n.receipts(a,extra),'frame_requests':n.receipts(a,p['prepared_B_context']['requests']),'final':physical(a.world,occupation=True)}
    v=run(life,life,fn)['result'];print(json.dumps({'case':number,'initial_selector':v['experience']['captures'][-1]['selector'],'commands':[[z['index'],z['native']['direction'],z['native']['s_reg']]for z in v['trajectory']['frames']if z['kind']=='command'],'responses':[[z['index'],z['native']['direction'],z['native']['s_reg']]for z in v['trajectory']['frames']if z['kind']=='source_tick'],'after_failure':[[z['index'],z['kind'],z['native']['direction'],z['native']['s_reg']]for z in v['trajectory']['failure_frames']if z['kind']in('private_source','failure_return')],'frame_admission':v['frame_requests'][0]['receipt'],'occupied':v['final']['occupied']},ensure_ascii=False),flush=True)
