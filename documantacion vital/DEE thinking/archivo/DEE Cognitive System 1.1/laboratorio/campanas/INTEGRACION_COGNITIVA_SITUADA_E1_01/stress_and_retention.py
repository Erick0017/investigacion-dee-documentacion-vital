"""Fixed legal unmarked port perturbations, then withdrawal without restore."""
from pathlib import Path
import sys,json,time,random
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import atomic_json,digest_file,physical,observe
from app.process_control import protect_current
import ic_external as ext,delayed_social as social
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
parent=s.record('E1_INTEGRADO_COSTO_SOCIAL_01')
spec={'parent':parent['snapshot_sha256'],'parent_tick_required':6237,'steps':12,'recovery_steps':6,'first_after_stress':True,'noise_ports':['quantity.object.cue','quantity.object.resource','quantity.reader'],'noise_offsets':[0,1,2,3,4],'nominal_rate':2,'nominal_load_max':3,'severe_rate':24,'severe_load_max':16,'seed':81231,'stop':'3 consecutive out-of-domain magnitude outputs, then stop adding new perturbations. Pending physical inputs are not erased. Withdrawal does not restore memory.','primary_line':'Nominal stress then withdrawal continues the same candidate; severe shocks remain separate copies.','assistance':'Generic finite exogenous port schedule; labels and RNG state are audit/protocol metadata, never interpreted by native selector.'}
if not(EV/'STRESS_SPEC_144.json').exists():atomic_json(EV/'STRESS_SPEC_144.json',spec)
cases=[('STRESS_MATCHED_144','IC01_STRESS_MATCHED_144',0,0,'closed'),('STRESS_SEVERE_146','IC01_STRESS_SEVERE_146',24,16,'closed'),('STRESS_DELAY_147','IC01_STRESS_DELAY_147',2,3,'delay1'),('STRESS_NOMINAL_MAIN_145','E1_INTEGRADO_COSTO_SOCIAL_01',2,3,'closed')]
for name,life,rate,amplitude,mode in cases[:-1]:
    if not s.life_dir(life).exists():s.fork('E1_INTEGRADO_COSTO_SOCIAL_01',life,kind='DIAGNOSTIC_COPY',checkpoint=parent['snapshot'])
for name,life,rate,amplitude,mode in cases:
    if time.monotonic()>deadline:raise TimeoutError('Fixed deadline')
    if(EV/(name+'.json')).exists():continue
    def run(a,steps,active):
        rng=random.Random(81231);requests=[];initial=physical(a.world,occupation=True)
        # All exogenous requests are fixed before seeing any output. Different
        # action-dependent environmental futures are not forced to coincide.
        first=70+67*max(0,(a.tick+8-70+66)//67)
        if active:
            for i in range(steps):
                at=first+67*i-5
                for j in range(rate):
                    port=rng.choice(spec['noise_ports']);when=at+rng.randrange(5);load=rng.randrange(amplitude+1);rec=(a.world.probe if port.endswith('reader')else a.world.submit)(port,load,when);requests.append({'id':int(rec.id),'port':port,'tick':when,'payload':load,'unmarked_at_native_ingress':True})
        p=social.get(a);ports=p['plan']['banks']if p else None
        result=ext.run(a,steps=steps,mode=mode,readout='magnitude',feedback='cost',codec=2,reader='omit',stop_invalid=3,social_ports=ports)
        result.update({'noise_requests':[dict(r,receipt=ext.exact_receipt(a.world.runtime.receipt(r['id'])))for r in requests],'noise_active':active,'condition':{'rate':rate if active else 0,'load_max':amplitude if active else 0,'seed':81231,'mode':mode},'before_stress':initial,'reference':observe(a.world,a.quantity.geometry['reference_hub'])})
        return result
    r=s.mutate(life,'IC01_FIXED_LEGAL_PORT_STRESS',lambda a:run(a,12,True),{'spec':spec,'source':digest_file(__file__)});atomic_json(EV/(name+'.json'),r)
    recovered=s.mutate(life,'IC01_WITHDRAW_STRESS_NO_RESTORE_NO_RETEACH',lambda a:run(a,6,False),{'previous_snapshot':r['INSTRUMENTO']['snapshot_sha256'],'note':'Omit noise only, do not remove pending events, restore, change reader, or reintroduce reference/social content.'});atomic_json(EV/(name+'_WITHDRAW6.json'),recovered)
    print(name+' '+str(recovered['INSTRUMENTO']['tick']),flush=True)
