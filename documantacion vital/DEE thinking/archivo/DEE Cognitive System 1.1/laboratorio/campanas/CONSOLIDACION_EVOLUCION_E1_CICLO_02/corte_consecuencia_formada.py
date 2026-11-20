"""Corte nativo de una consecuencia ya formada, no omisión desde T0."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import ic_native_core as core
s=Store();src=EV/'C02_GATE_050_RETORNO.AFTER_ACTION_0.deetsnap.gz'
assert src.exists()
source_id='C02_GATE_PRIMERA_CONSECUENCIA_089'
if not s.life_dir(source_id).exists():s.import_state(src,source_id,'cpc9_integral_n67',digest_file(src))
spec={'source_full_snapshot':str(src),'sha256':digest_file(src),'past_tick':17376,
      'actual_pending_return':'Native cue0/resource6 already scheduled for17440 by the first actually executed opening',
      'intervention':'Zero Z+ at the one-step resource6 transit17441, after its native admission17440; sham19z away',
      'common_future_object':2,'comparison_tick':17510,'old_function_object':82,
      'scope':'Causal native propagation control, not a new learning episode or state restored into MAIN.'}
atomic_json(EV/'CORTE_CONSECUENCIA_PROTOCOLO_090.json',spec)
for name,mode in [('C02_CUT_090_RETORNO','cut'),('C02_CUT_091_SHAM','sham'),('C02_CUT_092_INTACTO','none')]:
    fork(source_id,name)
    def experiment(a):
        assert a.tick==17376
        ch=next(p.channel for p in a.world.interfaces if p.name=='quantity.reference.resource')
        injection=[ch.injection_site.x,ch.injection_site.y,ch.injection_site.z];vin=[ch.direction.dx,ch.direction.dy,ch.direction.dz]
        target=core.move(injection,vin,1);rr=[];frames=[]
        if mode!='none':rr.append(core.arrive(a,name+'.postformed_resource_diversion',core.move(target,(0,0,1),19)if mode=='sham'else target,(0,0,1),17441,0))
        h=ic.attach(a,record=False)
        try:
            for t in(17439,17440,17441,17442,17443):
                a.run_until(t);frames.append({'tick':t,'injection':observe(a.world,injection),'meeting':observe(a.world,target),
                    'native_reference':observe(a.world,a.quantity.geometry['reference_hub']),
                    'context125':[observe(a.world,core.move(target,(x,y,z)))for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)]})
                if t in(17440,17441):a.save(EV/(name+'.T'+str(t)+'.deetsnap.gz'))
            a.quantity.present_object(2,reference_time=20,round_index=(17510-90)//67);rr.extend(dict(r)for r in a.quantity.state['requests'][-2:])
            r=a.quantity.input('quantity.reader',7,17509,True);rr.append({'id':int(r['id']),'port':'quantity.reader','payload':7,'tick':17509})
            a.run_until(17509);pre=observe(a.world,a.quantity.geometry['reference_site']);a.run_until(17510);answer=observe(a.world,a.quantity.geometry['center'])
            t=70+67*max(0,(a.tick+8-70+66)//67)
            a.quantity.present_object(82,round_index=(t-70)//67);r=a.quantity.input('quantity.reader',7,t-1,True);rr.extend(dict(r)for r in a.quantity.state['requests'][-3:])
            a.run_until(t);old=observe(a.world,a.quantity.geometry['center'])
        finally:h['detach']()
        return{'mode':mode,'frames':frames,'common_object':2,'reference_before_common':pre,'answer':answer,
               'old_comparison_after_cut':old,'requests':core.receipts(a,rr),'final':physical(a.world,occupation=True)}
    run(name,name,experiment,{'spec':'CORTE_CONSECUENCIA_PROTOCOLO_090.json'})
