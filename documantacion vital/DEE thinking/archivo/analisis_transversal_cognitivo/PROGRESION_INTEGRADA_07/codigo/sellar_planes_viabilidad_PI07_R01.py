"""Freeze the four paired operator-forced viability cases before execution."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
P=Path(__file__).resolve().parents[1]

def main():
    source=P/'codigo/PROTOCOLO_PI07_R01.json'
    p=json.loads(source.read_text(encoding='utf8'))
    assert p['status']=='SEALED_FOR_VIABILITY' and not p['evaluation_authorized_by_this_version']
    rows=[]
    for case in p['viability']['cases']:
        name=case['id'];plan=P/'control'/('PLAN_'+name+'_PI07_R01.json')
        d={'schema':'DEE.PI07.fixed_phase_plan.v1','status':'SEALED','initial_tick':824914,
           'max_native_ticks':1300,'description':'Operator-forced physical viability only, from the identical complete post-P0 prefix. Not acquired selection or a held-out result.',
           'registration_utc':datetime.now(timezone.utc).isoformat(),
           'source_proof':'control/PREFLIGHT_FINITO_TC_PI07_R03.json',
           'steps':[{'label':'EPISODIO','literal':{'modo':'eci01-pi07-calibrar','forzar':case['forced_action']},'max_native_ticks':1300}]}
        with plan.open('x',encoding='utf8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
        rows.append({'life':'ECI02_PI03_REPRO_PI04_PI05_PI07_'+name,'plan':str(plan),'plan_sha256':hashlib.sha256(plan.read_bytes()).hexdigest(),
                     'tag':'PI07_'+name+'_R01','environment_case':case})
    out=P/'control/PLANES_VIABILIDAD_PI07_R01.json'
    with out.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI07.four_case_viability.preregistered.v1','created_utc':datetime.now(timezone.utc).isoformat(),
        'protocol_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'same_prepared_prefix':'PI07_PREADQUISICION_TC_T824914','plans':rows,'Native_ticks_this_operation':0},f,ensure_ascii=False,indent=2)
    print(json.dumps({'plans':len(rows),'index':str(out),'Native_ticks':0}))

if __name__=='__main__':main()
