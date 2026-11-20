"""Bounded new-acquisition/interference test after prolonged actual use."""
from pathlib import Path
import sys,json,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from app.native_tools import atomic_json,digest_file,physical,observe
from app.process_control import protect_current
from capacidades import integracion_situada_01 as system
from capacidades.integracion_situada_01 import delayed_social as social,ic_external as ext
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds'];parent=s.record('E1_INTEGRADO_CONTINUABLE_01')
cases=[('SAME',18,'full'),('OPPOSITE',45,'full'),('NO_NEW_B',18,'no_partner'),('CUT_OPPOSITE',45,'cut'),('SHAM_OPPOSITE',45,'sham')]
spec={'before_outcomes':True,'parent':parent['snapshot_sha256'],'parent_tick':parent['physical']['tick'],'parent_external_index':193,'cases':cases,'steps':6,'external_limit_index':199,'identical_both_port_readers':True,'hypotheses':'Renewing a material reader can alter a formerly accessible received carrier. Same/opposite current private B acquisition may add, transform, interfere or fail. Do not assume any outcome from directional arithmetic alone.','scope':'New late-learning branches, not repairs of the retained usable candidate. No old memory transplant or raw/clock edit.'}
if not(EV/'LATE_SOCIAL_UPDATE_SPEC_166.json').exists():atomic_json(EV/'LATE_SOCIAL_UPDATE_SPEC_166.json',spec)
for tag,value,mode in cases:
    name='LATE_SOCIAL_'+tag+'_166';life='IC01_'+name;out=EV/(name+'.json')
    if out.exists():continue
    if time.monotonic()>deadline-3000:raise TimeoutError('Reserve integration/closing')
    s.fork('E1_INTEGRADO_CONTINUABLE_01',life,kind='DIAGNOSTIC_COPY',checkpoint=parent['snapshot'])
    def run(a):
        old=social.get(a);before=[observe(a.world,b['target'])for b in old['plan']['banks']];plan=social.begin(a,name=name,value=value,mode=mode);h=system.attach(a)
        try:r=ext.run(a,steps=6,readout='magnitude',mode='closed',feedback='cost',codec=2,reader='omit',stop_invalid=3,social_ports=plan['banks'])
        finally:h['detach']()
        return{'spec':spec,'before_received_ports':before,'new_plan':plan,'new_social_progress':social.get(a),'passive_frames':h['social_frames'],'external':r,'final':physical(a.world,occupation=True),'attribution':'Private actual magnitude only enters B. Both association and query opportunities are generic zero loads. Mixed actuator wiring unchanged. Same/opposite content is an environmental manipulation, not a host-selected E1 action.'}
    r=s.mutate(life,'IC01_NEW_SOCIAL_EXPERIENCE_AFTER_LONG_USE',run,{'spec':spec,'case':tag,'source':digest_file(__file__)});atomic_json(out,r);print('LATE_SOCIAL '+tag+' '+str(r['INSTRUMENTO']['tick']),flush=True)
