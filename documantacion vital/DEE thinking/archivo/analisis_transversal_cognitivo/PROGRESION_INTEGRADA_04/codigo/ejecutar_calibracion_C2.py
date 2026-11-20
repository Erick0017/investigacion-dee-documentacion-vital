"""Finite instrument calibration on a separate complete C2CAL copy only.

Six preregistered Q data, then two existing MU datum calls (0/32). No targets,
teaching labels, consequences, efference training or reserved cases are sent.
The calibration history is never transferred into the candidate.
"""
from pathlib import Path
import argparse,datetime,json,sys
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P/'codigo'))
from servicio_ensayo_R02 import Owner

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--vida',required=True);a=ap.parse_args()
    assert a.vida.startswith('ECI02_PI03_REPRO_PI04_C2CAL_')
    out=P/'control/C2_CALIBRACION_NATIVE_R02.json';assert not out.exists()
    protocol=json.loads((P/'estados/candidato_R02/sistema/capacidades/PROTOCOLO_PI04_C2_R01.json').read_text(encoding='utf-8-sig'))
    assert protocol['status']=='SEALED_FOR_CALIBRATION'
    rows=[];mu_rows=[]
    with Owner(a.vida,'PI04_C2CAL_R02')as owner:
        prep=owner.material('PI04_C2CAL_R02_PREPARE',{'modo':'eci01-pi04-c2-preparar'},feedback='omit')
        for v in (0,1,4,44,47,50):
            result=owner.material('PI04_C2CAL_R02_Q_'+str(v),{'modo':'eci01-pi04-c2-calibrar','valor':v},feedback='omit')
            actual=result['result']['rows'][0]
            rows.append({'input':v,'reader':actual['reader'],'before_tick':result['before_tick'],'after_tick':result['after_tick'],'after':actual['after'],'requests':actual['requests']})
            print(json.dumps({'sensor':'Q','input':v,'choice':actual['reader']['choice'],'tick':result['after_tick']},ensure_ascii=False),flush=True)
            assert all(x['receipt']['status']=='applied'for x in actual['requests']),'Incomplete datum admission is preserved, not retried'
        for v in (0,32):
            result=owner.material('PI04_C2CAL_R02_MU_'+str(v),{'modo':'dato','valor':v},feedback='omit')
            actual=result['result']['rows'][0]
            mu_rows.append({'input':v,'reader':actual['reader'],'before_tick':result['before_tick'],'after_tick':result['after_tick'],'requests':actual['requests']})
            print(json.dumps({'sensor':'MU','input':v,'choice':actual['reader']['choice'],'tick':result['after_tick']},ensure_ascii=False),flush=True)
        owner.control('guardar')
    proof={'schema':'DEE.PI04.C2.calibration.actual.v1','local_cut':datetime.datetime.now().astimezone().isoformat(),'life':a.vida,'scope':'Instrument development only on separate complete descendant; no history transferred to MAIN','prepared':prep,'Q':rows,'MU':mu_rows,'new_Native_ticks':mu_rows[-1]['after_tick']-prep['before_tick'],'actual_owner_closed':True,'Native_reserve_executed':False,'targets_or_desired_labels_sent':False,'generic_feedback_inserted':False}
    with out.open('x',encoding='utf-8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
    print(json.dumps({'proof':str(out),'Native_ticks':proof['new_Native_ticks']},ensure_ascii=False))
if __name__=='__main__':main()
