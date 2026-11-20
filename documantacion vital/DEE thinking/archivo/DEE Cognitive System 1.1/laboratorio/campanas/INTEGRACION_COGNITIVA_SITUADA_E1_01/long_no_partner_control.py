"""Matched curriculum/horizon without the current private B acquisition.

Interactive environmental futures may differ after actions; no forced common
future. This is one dependent control, not a new independent learner.
"""
from pathlib import Path
import sys,json,time,subprocess
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';SYSTEM=ROOT/'sistema'
sys.path.insert(0,str(SYSTEM))
from app.lives import Store
from app.native_tools import atomic_json,digest_file,physical
from app.process_control import protect_current
from capacidades.integracion_situada_01 import ic_body as body,ic_external as ext,delayed_social as social
from capacidades.integracion_situada_01.regression import inherited_panel
protect_current();s=Store();life='IC01_CONTROL_SIN_B_LARGO_164';deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
if not s.life_dir(life).exists():s.fork('IC01_INTEGRATED_NO_B_134',life,kind='DIAGNOSTIC_COPY')
spec={'source':'IC01_INTEGRATED_NO_B_134:T5698, external36','curriculum_matches_positive':['native[-1,1] training','6native contexts[1,1,-1,-1,1,1] with6external','18no-noise external','2external, old-function material panel,1external','8x16external'],'no_new_B_private_content':True,'query_and_decoder_unchanged':True,'max_external_index':191,'criterion':'Count physically qualified social output at the same declared both-port motor wires; absence is not translated into a learned negation.','scope':'Late specificity control. Distinct action/environment feedback causes distinct native sensor/cost inputs, as required by closed-loop causality.'}
if not(EV/'LONG_NO_PARTNER_SPEC_164.json').exists():atomic_json(EV/'LONG_NO_PARTNER_SPEC_164.json',spec)
def coupled(a,n):return ext.run(a,steps=n,readout='magnitude',feedback='cost',reader='omit',codec=2,stop_invalid=3,social_ports=social.get(a)['plan']['banks'])
stages=[]
def native(a):
    train=body.ic.train(a,episode='CONTROL_SIN_B_164',contexts=(-1,1));armed=body.arm(a,name='CONTROL_SIN_B_164',contexts=(1,1,-1,-1,1,1),shunt='a_only');h=body.attach(a)
    try:r=coupled(a,6)
    finally:h['detach']()
    finish=body.finish(a);return{'training':train,'armed':armed,'native_frames':h['frames'],'external':r,'native_finish':finish,'final':physical(a.world,occupation=True)}
stages.append(('NATIVE6',native));stages.append(('NO_NOISE12',lambda a:coupled(a,12)));stages.append(('NO_NOISE6',lambda a:coupled(a,6)));stages.append(('BEFORE_PANEL2',lambda a:coupled(a,2)));stages.append(('OLD_PANEL',inherited_panel));stages.append(('AFTER_PANEL1',lambda a:coupled(a,1)))
for i in range(8):stages.append(('LONG'+str(i+1),lambda a:coupled(a,16)))
for name,fn in stages:
    if time.monotonic()>deadline-2400:raise TimeoutError('Respect closing reserve')
    out=EV/('NO_PARTNER_LONG_'+name+'_164.json')
    if out.exists():continue
    r=s.mutate(life,'IC01_MATCHED_LONG_CONTROL_WITHOUT_CURRENT_B',fn,{'spec':spec,'stage':name,'source':digest_file(__file__)});atomic_json(out,r);print('NO_B '+name+' '+str(r['INSTRUMENTO']['tick']),flush=True)
    er=r['result'].get('external',r['result'])
    if er.get('final_environment',{}).get('stop_reason'):break
atomic_json(EV/'NO_PARTNER_LONG_FINAL_164.json',{'spec':spec,'final_record':s.record(life)})
