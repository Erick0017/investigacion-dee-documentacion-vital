from pathlib import Path
import sys,json,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
import native_composition as c
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
cases=[('COMPOSE_R2_LOW_107',18,73,'full','COST_NATIVE_73'),('COMPOSE_R2_HIGH_108',45,73,'full','COST_NATIVE_73'),('COMPOSE_R2_NONE_109',18,73,'no_partner','COST_NATIVE_73'),('COMPOSE_R2_CUT_110',18,73,'cut','COST_NATIVE_73'),('COMPOSE_R2_SHAM_111',18,73,'sham','COST_NATIVE_73'),('COMPOSE_R2_RESERVE_LOW_112',18,76,'full','COST_NATIVE_73'),('COMPOSE_R2_RESERVE_HIGH_113',45,76,'full','COST_NATIVE_73'),('COMPOSE_R2_RESERVE_NONE_114',18,76,'no_partner','COST_NATIVE_73'),('COMPOSE_R2_OMIT_COST_115',18,73,'full','COST_RETURN_OMIT_74')]
for name,value,obj,mode,parent_name in cases:
    if time.monotonic()>deadline:raise TimeoutError('Deadline')
    out=EV/(name+'.json');life='IC01_'+name
    if out.exists():continue
    prefix=json.loads((EV/(parent_name+'.json')).read_text())['prefix_record'];s.fork('IC01_'+parent_name,life,kind='DIAGNOSTIC_COPY',checkpoint=prefix['snapshot'])
    r=s.mutate(life,'IC01_NATIVE_CONSEQUENCE_SOCIAL_CURRENT_COMPOSITION',lambda a:c.execute(a,name=name,value=value,obj=obj,mode=mode),{'source':digest_file(LAB/'native_composition.py'),'case':{'private_B':value,'public_object':obj,'mode':mode,'parent':parent_name},'frozen_before_all_cases':cases,'no_future_targets_in_participant':True});atomic_json(out,r);print(name+' '+str(r['INSTRUMENTO']['tick']),flush=True)
