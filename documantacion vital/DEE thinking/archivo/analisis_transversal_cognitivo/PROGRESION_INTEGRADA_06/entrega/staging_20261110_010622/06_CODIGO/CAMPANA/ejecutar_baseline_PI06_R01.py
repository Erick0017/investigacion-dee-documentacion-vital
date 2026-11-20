"""Finite Native baseline via the existing owned Cognitive scheduler only."""
from pathlib import Path
import argparse,datetime,hashlib,json,sys
P=Path(__file__).resolve().parents[1]; S=P/'estados/candidato/sistema'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(a):
    assert a.arm in ('normal','global') and a.vida.startswith('ECI02_PI03_REPRO_PI04_PI05_PI06_')
    assert not (S/'estado/ACTIVO.json').exists()
    out=P/'control'/('BASELINE_'+a.arm+'_PI06_R01.json');assert not out.exists()
    protocol=P/'control/PROTOCOLO_BASELINE_PI06_R01.json';pr=read(protocol);assert pr['status']=='PREREGISTERED_BEFORE_NATIVE'
    reg=read(P/'REGISTRO_CAMPANA.json');assert datetime.datetime.now().astimezone()<datetime.datetime.fromisoformat(reg['science_cutoff_local'])
    cf=S/'estado/vidas'/a.vida/'VIDA.json';before=read(cf);assert before['physical']['N']==67 and before['physical']['tick']==pr['parent_tick']
    sys.path.insert(0,str(P/'codigo'));from servicio_ensayo_PI06 import Owner
    literal={'modo':'eci01-pi05-esperar','ticks':938} if a.arm=='normal' else {'modo':'eci01-pi06-evolucion','ticks':938,'captura':'global'}
    owner=None;result=None;error=None
    try:
        with Owner(a.vida,'PI06_BASE_'+a.arm.upper()+'_R01') as owner:
            result=owner.material('PI06_BASE_'+a.arm.upper()+'_938_R01',literal,feedback='omit')
            assert result['before_tick']==824911 and result['after_tick']==825849
            owner.control('guardar')
    except Exception as e:error={'type':type(e).__name__,'message':str(e),'no_automatic_retry':True}
    closed=owner is not None and owner.proc is not None and owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running')
    after=read(cf)
    value={'schema':'DEE.PI06.baseline.actual.R01','arm':a.arm,'life_id':a.vida,'protocol_sha256':sha(protocol),'before_card':before,'closed_card':after,'owner_closed_coherently':bool(closed),'actual_new_ticks':after['physical']['tick']-before['physical']['tick'] if closed else None,'Native_material_inputs':0,'literal':literal,'result':result,'error':error,'status':'COMPLETED' if closed and error is None else 'STOPPED_PRESERVED','no_guard_or_state_edits':True,'no_promotion':True}
    with out.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
    print(json.dumps({'proof':str(out),'status':value['status'],'closed':closed,'actual_new_ticks':value['actual_new_ticks'],'error':error},ensure_ascii=False))
    return 0 if value['status']=='COMPLETED' else 2
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--vida',required=True);ap.add_argument('--arm',choices=('normal','global'),required=True);raise SystemExit(main(ap.parse_args()))
