"""Root-only supervised PI04 E3 execution through the existing owner/queue.

One explicit diagnostic life, 18 fixed opportunities, no retry after an
uncertain operation, no selection of Native actions or resets of old stock.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,sys
P=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(P/'codigo'))
from servicio_ensayo import Owner

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--vida',required=True)
    ap.add_argument('--brazo',choices=('real','desacoplado'),required=True)
    ap.add_argument('--plan',type=Path);a=ap.parse_args()
    assert a.vida.startswith('ECI02_PI03_REPRO_PI04_')
    assert (a.plan is None)==(a.brazo=='real')
    protocol=P/'codigo/E3/PROTOCOLO_E3_R01.json'
    config=json.loads(protocol.read_text(encoding='utf-8-sig'))
    assert config['status']=='SEALED_FOR_NATIVE'
    for r in config['executed_code']:
        f=P/'estados/candidato/sistema'/r['file']
        assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256']
    registry=json.loads((P/'REGISTRO_CAMPANA.json').read_text(encoding='utf-8-sig'))
    assert datetime.datetime.now().astimezone()<datetime.datetime.fromisoformat(registry['closure_target_local'])
    tag='PI04_E3_'+('REAL'if a.brazo=='real'else'YOKE')+'_R01'
    out=P/'control'/('E3_'+a.brazo+'_R01.json');assert not out.exists()
    admit={'modo':'eci01-pi04-e3-admitir','brazo':a.brazo}
    if a.plan:
        f=a.plan.resolve(strict=True)
        assert f.is_relative_to(P/'control')and not f.is_symlink()
        admit['plan']=json.loads(f.read_text(encoding='utf-8-sig'))
    supplies={2:(-1,2),6:(1,4),10:(-1,2),14:(1,4)}
    results=[]
    with Owner(a.vida,tag)as owner:
        initial=owner.material(tag+'_ADMIT',admit,feedback='omit')
        assert initial['before_tick']==initial['after_tick']==775355
        for i in range(18):
            assert datetime.datetime.now().astimezone()<datetime.datetime.fromisoformat(registry['closure_target_local'])
            if i in supplies:
                connection,delay=supplies[i]
                owner.material(tag+'_SUPPLY_'+str(i),{'modo':'eci01-pi03-tarea-suministrar','cantidad':4,'conexion':connection,'demora_periodos':delay},feedback='omit')
            actual=owner.material(tag+'_OP_'+str(i),{'modo':'eci01-pi04-e3-oportunidad'},feedback='omit')
            row=actual['result']['rows'][0]
            results.append({'id':tag+'_OP_'+str(i),'before_tick':actual['before_tick'],'after_tick':actual['after_tick'],'choice':row['reader']['choice'],'useful':row['useful_product'],'actual_failed':row['actual_effect']['failed'],'returned_failed':row['returned_failed'],'E3':row['PI04_E3']})
            print(json.dumps(results[-1],ensure_ascii=False),flush=True)
            if row['reader']['choice']is None:raise RuntimeError('First NULL preserved; no next opportunity or automatic recovery')
            if not all(x['receipt']['status']=='applied'for x in row['requests']):raise RuntimeError('Unapplied Native input preserved; no next opportunity')
        final=owner.material(tag+'_FINAL',{'modo':'eci01-pi04-e3-estado'},feedback='omit')
        owner.control('guardar')
    r={'schema':'DEE.PI04.E3.executed.v1','life':a.vida,'arm':a.brazo,'included':18,'completed':len(results),'products':sum(x['useful']for x in results),'new_native_ticks':results[-1]['after_tick']-775355,'rows':results,'initial':initial,'final':final,'owner_closed':True,'prefix_shared_not_independent_replicates':True}
    with out.open('x',encoding='utf-8')as f:json.dump(r,f,ensure_ascii=False,indent=2)
    if a.brazo=='real':
        plan=final['result']['rows'][0]['replay_plan_encoded']
        with(P/'control/PLAN_E3_REAL_R01.json').open('x',encoding='utf-8')as f:json.dump(plan,f,ensure_ascii=False,indent=2)
    print(json.dumps({'proof':str(out),'products':r['products'],'Native_ticks':r['new_native_ticks']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
