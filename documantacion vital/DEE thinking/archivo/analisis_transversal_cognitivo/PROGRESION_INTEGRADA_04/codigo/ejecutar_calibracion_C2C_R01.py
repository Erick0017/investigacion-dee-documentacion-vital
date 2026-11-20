"""Root-only three-value C2C calibration on a separate full C2CCAL clone.

No Native run on import. No EVAL/reserve values, teaching/consequences or motor
copy are sent. The original C2 halted state remains in the same genealogy.
"""
from pathlib import Path
import argparse,datetime,json,re,sys
P=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--vida',required=True);ap.add_argument('--tag',required=True)
    a=ap.parse_args()
    if not a.vida.startswith('ECI02_PI03_REPRO_PI04_C2CCAL_')or not re.fullmatch(r'PI04_[A-Z0-9_]{1,64}',a.tag):raise ValueError('Explicit C2CCAL clone/tag required')
    out=P/'control'/(a.tag+'.json')
    if out.exists():raise ValueError('Prior calibration retained; do not reuse request IDs')
    p=json.loads((P/'estados/candidato_R02/sistema/capacidades/PROTOCOLO_PI04_C2C_R01.json').read_text(encoding='utf-8-sig'))
    if p['status']!='SEALED_FOR_CALIBRATION'or p['calibration_values']!=[0,4,5]:raise ValueError('Frozen three-value C2C calibration required')
    budget=json.loads((P/'REGISTRO_CAMPANA.json').read_text(encoding='utf-8-sig'))
    if datetime.datetime.now().astimezone()>=datetime.datetime.fromisoformat(budget['closure_target_local']):raise ValueError('Campaign closure target reached')
    sys.path.insert(0,str(P/'codigo'))
    from ejecutar_C2C_R01 import closed_ticks
    if closed_ticks()+600>budget['budget']['Native_ticks_all_branches']:raise ValueError('Conservative three-calibration allowance unavailable')
    from servicio_ensayo_R02 import Owner
    rows=[]
    with Owner(a.vida,a.tag)as owner:
        initial=owner.material(a.tag+'_STATE_START',{'modo':'eci01-pi04-c2c-estado'},feedback='omit')
        if initial['result']['rows'][0].get('progress')is not None:raise ValueError('Calibration must start before new B preparation')
        prep=owner.material(a.tag+'_PREPARE',{'modo':'eci01-pi04-c2c-preparar'},feedback='omit')
        if prep['after_tick']!=prep['before_tick']:raise ValueError('B interface preparation unexpectedly consumed ticks')
        for value in(0,4,5):
            actual=owner.material(a.tag+'_Q_'+str(value),{'modo':'eci01-pi04-c2c-calibrar','valor':value},feedback='omit')
            r=actual['result']['rows'][0]
            if len(r['requests'])!=4 or not all(x['receipt']['status']=='applied'for x in r['requests']):raise ValueError('Actual B dose must be query/support3 + one original datum event, all admitted')
            data=[x for x in r['requests']if'datum'in x['channel']]
            if len(data)!=1 or any(x['payload']!=value for x in data)or len({x['requested_tick']for x in data})!=1:raise ValueError('Single original datum differs from fixed scalar/tick')
            rows.append({'input':value,'reader':r['reader'],'before_tick':actual['before_tick'],'after_tick':actual['after_tick'],
                         'after':r['after'],'requests':r['requests'],'feedback_inserted':r['feedback_inserted'],'efference_inserted':r['efference_inserted']})
            print(json.dumps({'input':value,'choice':r['reader']['choice'],'tick':actual['after_tick'],'Native_inputs':4},ensure_ascii=False),flush=True)
        final=owner.material(a.tag+'_STATE_FINAL',{'modo':'eci01-pi04-c2c-estado'},feedback='omit')
        owner.control('guardar')
    proof={'schema':'DEE.PI04.C2C.calibration.actual.R01','local_cut':datetime.datetime.now().astimezone().isoformat(),
        'life':a.vida,'initial':initial,'prepared':prep,'Q':rows,'final':final,'actual_owner_closed':True,
        'new_Native_ticks':final['after_tick']-initial['before_tick'],'old_C2_preserved':True,
        'Native_reserve_executed':False,'targets_or_desired_labels_sent':False,'generic_feedback_inserted':False,
        'scope':'Instrument calibration only on separate complete descendant; history never transferred to MAIN'}
    with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
    print(json.dumps({'proof':str(out),'Native_ticks':proof['new_Native_ticks']},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
