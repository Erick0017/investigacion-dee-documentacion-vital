"""A motor-code reappearance is not automatically restored comparison."""
from pathlib import Path
import sys,json,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from app.native_tools import atomic_json,digest_file,physical,observe,exact_receipt
from app.process_control import protect_current
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
spec={'before_new_cases':True,'parent':'IC01_STRESS_SEVERE_146:T7440','cases':[None,1,400],'question':'Post-queue severe continuation emitted a state1 SEM1 -X load9, unlike the former7. Does it use a new current magnitude, or only reproduce a motor-compatible carrier?','controls':'Same reached prefix and pending queue; vary only current object experience; no new reader or reference','not_claimed':'A changed payload does not alone invalidate a function, nor does an accepted actuator direction alone demonstrate its recovery.'}
if not(EV/'SEVERE_CODE_SPEC_175.json').exists():atomic_json(EV/'SEVERE_CODE_SPEC_175.json',spec)
for value in(None,1,400):
    name='SEVERE_CODE_'+('NO_OBJECT'if value is None else str(value))+'_175';out=EV/(name+'.json');life='IC01_'+name
    if out.exists():continue
    if time.monotonic()>deadline-2400:raise TimeoutError('Closing reserve')
    s.fork('IC01_STRESS_SEVERE_146',life,kind='DIAGNOSTIC_COPY')
    def run(a):
        before=physical(a.world,occupation=True);t=70+67*max(0,(a.tick+8-70+66)//67);rr=[]
        if value is not None:a.quantity.present_object(value,round_index=(t-70)//67);rr=[dict(r)for r in a.quantity.state['requests'][-2:]]
        frames=[]
        for at in range(t-6,t+1):
            a.run_until(at);frames.append({'tick':at,'fields':{k:observe(a.world,p)for k,p in a.quantity.geometry.items()if isinstance(p,list)and len(p)==3 and all(type(v)is int for v in p)},'context':[observe(a.world,[(a.quantity.geometry['center'][i]+d[i])%67 for i in range(3)])for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)for d in[(x,y,z)]]})
        return{'spec':spec,'current_object':value,'requests':[dict(r,receipt=exact_receipt(a.world.runtime.receipt(r['id'])))for r in rr],'frames':frames,'quantity':observe(a.world,a.quantity.geometry['center']),'final':physical(a.world,occupation=True),'initial':before}
    r=s.mutate(life,'IC01_TEST_POST_STRESS_MOTOR_CODE_FUNCTION_NOT_JUST_SIGNATURE',run,{'spec':spec,'source':digest_file(__file__)});atomic_json(out,r);print(name+' '+str(r['INSTRUMENTO']['tick']),flush=True)
