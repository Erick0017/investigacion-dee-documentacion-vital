"""Exact frozen-prefix controls. No results are returned to MAIN."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades.mente_integral_mi01 import externo_selector as motor,fallo_y_consulta as body
from capacidades.integracion_situada_01 import ic_native_core as n,ic_external as old_bridge
from capacidades.observador_causal_retrospectivo_01 import Snapshot
EXPECTED='afc1d19c27da44ec1810704cfd08cd6c2c2ff0148dcc5af8411f7b91c9402713';name='MI01_EVALUACION_FIJADA'

def prefix():
    for p in(S/'estado/checkpoints').glob('E1_MI01_MAIN.T24752.*.deetsnap.gz'):
        if sha(p)==EXPECTED:return p
    raise FileNotFoundError('The exact complete frozen-prefix snapshot is required')

def null_actions():
    life='MI01_ACTUADOR_ANULADO_450';fork('E1_MI01_MAIN',life,checkpoint=prefix());original=motor._Worker
    class NullWorker(original):
        def __init__(self):super().__init__();self.actual_cuts=[]
        def call(self,op,**kw):
            if op=='step':
                self.actual_cuts.append({'requested_torque':kw['torque'],'actual_torque':0});kw={**kw,'torque':0}
            return super().call(op,**kw)
    atomic_json(E/'ACTUADOR_ANULADO_PROTOCOLO_450.json',{'prefix_sha256':EXPECTED,'intervention':'All motor commands intercepted AFTER native output; fixed executed torque0. Native outputs and both sensory timings kept. No controller/reference acts for E1.','windows':[(16,'closed','cost'),(15,'delay1','cost'),(16,'closed','omit')],'note':'External futures may differ after different actual actions. Only initial environment and exogenous scene/pending inputs are shared.'})
    motor._Worker=NullWorker
    try:
        for i,(steps,mode,feedback)in enumerate([(16,'closed','cost'),(15,'delay1','cost'),(16,'closed','omit')]):
            def fn(a,steps=steps,mode=mode,feedback=feedback,i=i):
                r=motor.run(a,steps=steps,mode=mode,feedback=feedback,transition=i==0,habitat=name,motor_codec='native_body_roles')
                for row in r['rows']:
                    row['bridge_torque_before_post_output_cut']=row['executed_torque'];row['executed_torque']=0;row['post_output_external_actuator_cut']=True
                r['causal_intervention']='Actual worker.step torque always0; primary native command unchanged. The row explicitly distinguishes requested and executed torque.';return r
            run(life,'MI01_45'+str(i)+'_ACTUADOR_ANULADO',fn,{'window':i,'post_native_output_cut':True})
    finally:motor._Worker=original

def stress():
    atomic_json(E/'ESTRES_SEVERO_PROTOCOLO_460.json',{'prefix_sha256':EXPECTED,'cases':['MI01_ESTRES_460','MI01_CONTROL_461'],'shock':'64 legal normal peripheral packets145,4fixed sites x16successive ticks around the first opportunity, total requested dose9280. No further shock escalation after that fixed pulse.','matched':'Same initial whole world, all frozen native body/private sources and eight nominal later events. External Pendulum remains paused in BOTH arms.','horizons':'Before/after pulse; first and second return; nine-opportunity end; drain67; free201; original code bank phase3 inspection without material probe.','limits':'Shared-parent deterministic branches, not64independent subjects. Baseline deterioration must not be attributed entirely to extra noise.'})
    for case,severe in[(460,True),(461,False)]:
        life='MI01_ESTRES_460'if severe else'MI01_CONTROL_461';fork('E1_MI01_MAIN',life,checkpoint=prefix())
        def fn(a,life=life,severe=severe):
            cfg=__import__('capacidades.mente_integral_mi01',fromlist=['saved']).saved(a);p=cfg['native_habitats'][name];q=p['plans'][0]['query_tick'];rr=[];S0=p['S']
            if severe:
                for j,v in enumerate([(1,1,1),(-1,1,-1),(1,-1,-1),(-1,-1,1)]):
                    site=n.move(S0,v,9);direction=[-x for x in v]
                    for k in range(16):rr.append(n.submit(a,'MI01.severe.'+str(j),site,direction,q-8+k,145))
            a.save(E/(life+'.BEFORE.deetsnap.gz'));stages=[]
            for tag,t in[('before_pulse',q-9),('after_pulse',q+8),('first_return',q+335),('second_return',q+670),('body_end',p['end_tick']),('drained',p['end_tick']+67),('free',p['end_tick']+268)]:
                v=body.advance(a,name=name,until=t);stages.append({'tag':tag,'tick':a.tick,'physical':physical(a.world,occupation=True),'selector':n.obs(a,S0),'frames':v['frames'],'failure_frames':v['failure_frames']})
                if tag in('after_pulse','drained','free'):a.save(E/(life+'.'+tag+'.deetsnap.gz'))
            phase=a.tick+(3-a.tick)%67;body.advance(a,name=name,until=phase)
            banks=[{'name':k,'native':n.obs(a,site)}for k,site in [('negative7',[31,59,26]),('positive7',[11,59,23]),('lateral7',[11,48,29]),('acquired145',[10,56,26])]]
            a.save(E/(life+'.FINAL.deetsnap.gz'))
            return{'shock_requests':n.receipts(a,rr),'stages':stages,'original_bank_phase3':banks,'final':physical(a.world,occupation=True),'external_paused':True,'no_repair_or_reteaching':True}
        run(life,'MI01_'+str(case)+'_ESTRES_CONTROL',fn,{'shock':severe,'same_prefix':EXPECTED})

if __name__=='__main__':
    if sys.argv[1]=='anulada':null_actions()
    elif sys.argv[1]=='estres':stress()
    else:raise ValueError('Explicit control required')
