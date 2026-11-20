"""Entorno escalar causal mínimo; DEE compara y el entorno no elige acciones.

No se modela metabolismo. Una compuerta adquiere resistencia por contactos.
La observación es fuerza disponible. La consecuencia material es desgaste
real causado por la acción, nunca la acción correcta ni una corrección de RAW.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import ic_native_core as core
FORCES=[100,2,4,20,8,30,16,40,23]
WEAR=[6,6,6,6,11,11,11,11,11]
CASES=[('C02_GATE_050_RETORNO','intact'),('C02_GATE_051_SIN_RETORNO','omit'),
       ('C02_GATE_052_ACCION_ANULADA','null_action'),('C02_GATE_053_SHAM','sham')]
atomic_json(EV/'PUERTA_PROTOCOLO_PREVIO_R1.json',{
    'cases':CASES,'parent':'E1_CICLO02_MAIN:T17289','reference_phase':20,'comparison_phase':23,
    'forces':FORCES,'wear':WEAR,'native_ticks_per_opportunity':134,'first_baseline_reference':0,
    'environment':'Scalar gate, resistance starts0. Attempt opens iff offered force exceeds current resistance. Every real attempt causes actual wear6/11. Retreat changes nothing. No robotics or competent Pendulum claim.',
    'sensor':'Only current force reaches object channels. Resistance and future forces never reach the participant as targets.',
    'actuator':'Pure native -X7=attempt; +X7=retreat; other fields=neutral. Mapping fixed before execution.',
    'return':'Actual wear amount via the admitted native reference cue0/resource channels. No utility, desired direction, optimal action or model resistance is supplied. Operator supplies a common known-zero initial reference at a fixed separate phase, not the future answer.',
    'prepared':'Existing gradient comparator, two fixed phases, baseline-zero preparation and wear-to-material codec. Acquired content is accumulated native wear, not an invented learning rule.',
    'utility_auditor_only':'Real opening+1, real jam-1, retreat/neutral0. Useful=opening or valid retreat when force<=resistance; invalid, neutral and rejected inputs remain denominators.',
    'change':'Wear increment changes after opportunity3 independently of E1 output. Environmental resistance evolves only from actual actions.',
    'control_future':'Same initial gate and force/wear sequence, not identical interactive futures after actions differ.'})

for name,mode in CASES:
    fork('E1_CICLO02_MAIN',name)
    def experiment(a):
        initial=physical(a.world,occupation=True);t0=20+67*max(0,(a.tick+8-20+66)//67)
        rr=[];rows=[];resistance=0
        for port,v in [('quantity.reference.cue',5),('quantity.reference.resource',0)]:
            r=a.quantity.input(port,v,t0);rr.append({'id':int(r['id']),'port':port,'payload':v,'tick':t0,'role':'DECLARED_COMMON_ZERO_BASELINE'})
        h=ic.attach(a,record=False)
        try:
            for i,(force,wear)in enumerate(zip(FORCES,WEAR)):
                t=t0+70+134*i;k=(t-90)//67
                a.quantity.present_object(force,reference_time=20,round_index=k)
                inputs=[dict(r)for r in a.quantity.state['requests'][-2:]]
                r=a.quantity.input('quantity.reader',7,t-1,True);inputs.append({'id':int(r['id']),'port':'quantity.reader','payload':7,'tick':t-1})
                a.run_until(t-1);pre={'reference':observe(a.world,a.quantity.geometry['reference_site']),'object':observe(a.world,a.quantity.geometry['object_site']),'center':observe(a.world,a.quantity.geometry['center'])}
                a.run_until(t);read=observe(a.world,a.quantity.geometry['center'])
                valid=read['state']==1 and read['semantic']==1 and read['s_reg']==7 and read['direction']in([1,0,0],[-1,0,0])
                native_action=(-read['direction'][0])if valid else 0 # +1 attempt, -1 retreat
                action=0 if mode=='null_action'else native_action
                before_r=resistance;opened=action==1 and force>before_r;jam=action==1 and not opened
                # World physics: contact creates wear regardless of success.
                returned_wear=wear if action==1 else 0
                resistance+=returned_wear
                outcome={'force':force,'resistance_before':before_r,'resistance_after':resistance,'opened':opened,'jam':jam,'wear':returned_wear}
                feedback_at=t+64;returns=[]
                if mode!='omit':
                    if mode=='sham':
                        for suffix,v in [('cue',0),('event',returned_wear)]:
                            port='quantity.other.'+suffix;r=a.quantity.input(port,v,feedback_at);returns.append({'id':int(r['id']),'port':port,'payload':v,'tick':feedback_at})
                    else:
                        for suffix,v in [('cue',0),('resource',returned_wear)]:
                            port='quantity.reference.'+suffix;r=a.quantity.input(port,v,feedback_at);returns.append({'id':int(r['id']),'port':port,'payload':v,'tick':feedback_at})
                rr.extend(inputs+returns)
                rows.append({'index':i,'tick':t,'force_sensor':force,'wear_available':wear,'native_pre':pre,'native_response':read,
                    'valid':valid,'native_action':native_action,'executed_action':action,'environment':outcome,
                    'utility_auditor_only':int(opened)-int(jam),'useful_auditor_only':bool(opened or(action==-1 and force<=before_r)),
                    'return_input_tick':feedback_at,'requests':inputs+returns,'host_does_not_return_utility_or_resistance':True})
                if i in(0,1,4):a.save(EV/(name+'.AFTER_ACTION_'+str(i)+'.deetsnap.gz'))
            # Drain the last declared return; do not erase pending events.
            a.run_until(rows[-1]['tick']+134)
        finally:h['detach']()
        return{'initial':initial,'phase':20,'baseline_tick':t0,'mode':mode,'rows':rows,'requests':core.receipts(a,rr),
               'final_environment':{'resistance':resistance,'next_opportunity':len(rows)},'final':physical(a.world,occupation=True),
               'scope':'Acquired native scalar memory used by a prepared comparator/actuator. This is not learning a general policy or computing a correct update in Python.'}
    run(name,name,experiment,{'spec':'PUERTA_PROTOCOLO_PREVIO_R1.json'})
