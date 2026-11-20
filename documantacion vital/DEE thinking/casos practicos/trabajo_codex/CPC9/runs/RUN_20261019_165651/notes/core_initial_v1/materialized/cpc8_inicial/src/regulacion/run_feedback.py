"""Auditor runner: measures only after native evolution; no participant targets."""
from array import array
import argparse,hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.regulacion.native_feedback import prepare,record,neighborhood
from dee_thinking.persistence import save_world_snapshot

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--medium',type=int,choices=(-1,1),required=True)
    p.add_argument('--mode',default='intact');p.add_argument('--context',choices=('P','Q'),required=True)
    p.add_argument('--translation',type=int,default=0);p.add_argument('--N',type=int,default=67)
    p.add_argument('--single-lane',action='store_true');a=p.parse_args()
    out=ROOT/'resultados/regulacion'/a.case;out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();w,g=prepare(medium=a.medium,mode=a.mode,translation=(a.translation,0,0),n=a.N,lanes=(1,) if a.single_lane else (-1,1))
    manifest={'case_id':a.case,'individual':a.case,'parent':None,'architecture':'CPC8.native_consequence_regulation.v1',
        'geometry':g,'preparation_code_sha256':hashlib.sha256(Path(__file__).with_name('native_feedback.py').read_bytes()).hexdigest(),
        'evaluation_context_not_given_to_participant':a.context,'criterion_frozen':'Exact useful3 packet at(1,0,0)delivery receiver tick15; count only requested source class. Other streams and costs separately.'}
    (out/'CONFIG.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    frames=[];checkpoints=[]
    try:
        for tick in range(19):
            w.run_until(tick)
            if tick in (0,1,2,3,4,5,8,9,10,11,12,13,15,18):
                panel={k:record(w,q) for k,q in g['ports'].items()}
                frame={'tick':tick,'panel':panel}
                if tick in (4,5,8,9,11,12):
                    selected=[(k,q) for k,q in g['ports'].items() if
                        (tick in(4,5) and k.startswith('comparison.')) or
                        (tick in(8,9) and k.startswith('policy.')) or
                        (tick in(11,12) and k.startswith('interception.'))]
                    frame['Moore27']={k:neighborhood(w,q) for k,q in selected}
                frames.append(frame)
                (out/'OBSERVACIONES.json').write_text(json.dumps(frames,ensure_ascii=False,indent=2),encoding='utf-8')
            if tick in (0,9,18):
                checkpoints.append(save_world_snapshot(w,out/f'T{tick}.deetsnap.gz'))
        # Evaluation follows trajectories and never writes the native world.
        delivery=next(x['panel'] for x in frames if x['tick']==15)
        rows=[]
        for q in g['regulators']:
            r=delivery['delivery.'+q['id']]
            rows.append({'id':q['id'],'source':q['source'],'observed':r,
                'exact_useful_packet':r['state']>0 and r['semantic']!=5 and r['s_reg']==3 and r['direction']==[1,0,0]})
        result={'schema':'CPC8.native-regulatory-feedback.v1','case_id':a.case,'status':'EXECUTED',
            'elapsed_seconds':time.monotonic()-start,'delivery_by_route':rows,
            'requested_deliveries':sum(x['exact_useful_packet'] and x['source']==a.context for x in rows),
            'other_deliveries':sum(x['exact_useful_packet'] and x['source']!=a.context for x in rows),
            'checkpoints':checkpoints,'final_tick':int(w.runtime.current_tick),
            'final_RAW_sha256':hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest(),
            'final_clock_sha256':hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest(),
            'scope':'Research attempt. EXECUTED is not a positive capability verdict; inspect contacts, policy and paired controls.'}
        (out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({k:result[k] for k in ('case_id','status','requested_deliveries','other_deliveries','elapsed_seconds')}))
    except BaseException as error:
        (out/'ERROR.json').write_text(json.dumps({'error':repr(error),'elapsed_seconds':time.monotonic()-start}),encoding='utf-8')
        raise

if __name__=='__main__':main()
