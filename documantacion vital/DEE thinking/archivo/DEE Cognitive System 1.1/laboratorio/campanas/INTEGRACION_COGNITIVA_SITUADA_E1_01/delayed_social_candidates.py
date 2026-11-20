from pathlib import Path
import sys,json,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import atomic_json,digest_file
from app.process_control import protect_current
import delayed_social as social
protect_current();s=Store();prefix=json.loads((EV/'COST_NATIVE_73.json').read_text())['prefix_record'];deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
cases=[('SOCIAL_DELAY_LOW_125',18,'full',True),('SOCIAL_DELAY_HIGH_126',45,'full',True),('SOCIAL_DELAY_NONE_127',18,'no_partner',True),('SOCIAL_DELAY_CUT_128',18,'cut',True),('SOCIAL_DELAY_SHAM_129',18,'sham',True),('SOCIAL_DELAY_UNPAIRED_130',18,'unpaired',True),('SOCIAL_DELAY_PASSIVE_131',18,'full',False)]
for name,value,mode,record in cases:
    if time.monotonic()>deadline:raise TimeoutError('Deadline')
    out=EV/(name+'.json');life='IC01_'+name
    if out.exists():continue
    s.fork('IC01_COST_NATIVE_73',life,kind='DIAGNOSTIC_COPY',checkpoint=prefix['snapshot'])
    def run(a):return social.advance(a,social.prepare(a,name=name,value=value,mode=mode,public_object=73),record=record)
    r=s.mutate(life,'IC01_RECEIVED_INFORMATION_BALLISTIC_RETENTION_AND_FIXED_RETRIEVAL',run,{'source':digest_file(LAB/'delayed_social.py'),'condition':{'private':value,'mode':mode,'passive_record':record},'fixed_before_reserves':cases});atomic_json(out,r);print(name+' '+str(r['INSTRUMENTO']['tick']),flush=True)
