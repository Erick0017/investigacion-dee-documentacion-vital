import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import ic_native_core as core
atomic_json(EV/'CORTE_CONSECUENCIA_DIAGNOSTICO_R2.json',{
    'diagnosis_R1':'Zplus diversion removed the later new-phase reference entirely, not only its acquired increment. Old comparison survived. Do not call R1 a clean selective subtraction of6.',
    'revision':'Counterflow [-1,0,-1] sends formed resource6 toward YplusZminus at x47, farther from the baseline Y orbit at x49.',
    'same_source':'C02_GATE_PRIMERA_CONSECUENCIA_089:T17376','query_tick':17510,'object':2,
    'intact_reference':'C02_CUT_092_INTACTO reused, not repeated'})
for name,mode in [('C02_CUT_093_DIAGONAL','cut'),('C02_CUT_094_DIAGONAL_SHAM','sham')]:
    fork('C02_GATE_PRIMERA_CONSECUENCIA_089',name)
    def test(a):
        ch=next(p.channel for p in a.world.interfaces if p.name=='quantity.reference.resource');site=[ch.injection_site.x,ch.injection_site.y,ch.injection_site.z];target=core.move(site,(1,1,0));rr=[];frames=[]
        rr.append(core.arrive(a,name+'.postformed',core.move(target,(0,0,1),19)if mode=='sham'else target,(-1,0,-1),17441,0))
        h=ic.attach(a,record=False)
        try:
            for t in(17439,17440,17441,17442,17443):
                a.run_until(t);frames.append({'tick':t,'injection':observe(a.world,site),'meeting':observe(a.world,target),
                    'reference_line':[observe(a.world,[49,y,35])for y in range(30,40)],'context125':[observe(a.world,core.move(target,(x,y,z)))for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)]})
                if t in(17440,17441):a.save(EV/(name+'.T'+str(t)+'.deetsnap.gz'))
            a.quantity.present_object(2,reference_time=20,round_index=(17510-90)//67);rr.extend(dict(r)for r in a.quantity.state['requests'][-2:]);r=a.quantity.input('quantity.reader',7,17509,True);rr.append({'id':int(r['id']),'port':'quantity.reader','payload':7,'tick':17509})
            a.run_until(17509);pre=observe(a.world,a.quantity.geometry['reference_site']);a.run_until(17510);answer=observe(a.world,a.quantity.geometry['center'])
            t=70+67*max(0,(a.tick+8-70+66)//67);a.quantity.present_object(82,round_index=(t-70)//67);r=a.quantity.input('quantity.reader',7,t-1,True);rr.extend(dict(r)for r in a.quantity.state['requests'][-3:]);a.run_until(t);old=observe(a.world,a.quantity.geometry['center'])
        finally:h['detach']()
        return{'mode':mode,'frames':frames,'reference_before_common':pre,'answer':answer,'old_comparison_after_cut':old,'requests':core.receipts(a,rr),'final':physical(a.world,occupation=True)}
    run(name,name,test,{'spec':'CORTE_CONSECUENCIA_DIAGNOSTICO_R2.json'})
