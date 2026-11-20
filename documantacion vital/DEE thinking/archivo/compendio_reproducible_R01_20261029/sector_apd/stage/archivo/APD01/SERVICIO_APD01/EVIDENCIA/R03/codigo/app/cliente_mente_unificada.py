"""Local SQLite transport client; no DEE import, decision rule or public port."""
import argparse,json,sys,time,uuid
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cola_local import QueueDB


def request(store,life,operation,*,identifier=None,situations=None,ticks=None,actuator='closed',feedback='real',wait=30):
    """Manager entry. Store.record is metadata only: no second Runtime load."""
    record=store.record(life);path=store.state/'servicios_persistentes'/record['world_id']/'cola.sqlite3'
    if not path.is_file():return {'technical_status':'service_not_initialized','life_id':record['life_id'],
        'no_implicit_new_world':True,'start_command':'mente-unificada-iniciar --vida '+record['life_id']}
    q=QueueDB(path)
    if operation=='estado':
        status=q.get_meta('owner');age=None
        if status and status.get('wall_utc'):age=max(0,(datetime.now(timezone.utc)-datetime.fromisoformat(status['wall_utc'])).total_seconds())
        return {'observation':status,'cache_age_seconds':age,'instantaneous_native_clock':False,'no_material_probe':True}
    if operation=='resultado':
        if not identifier:raise ValueError('Existing transport ID required.')
        return {'request':q.get(identifier),'reexecuted':False}
    payload={'operacion':operation}
    if operation=='sesion':payload.update(situaciones=situations,actuador=actuator,retorno=feedback)
    elif operation=='avanzar':payload['ticks']=ticks
    identifier=identifier or uuid.uuid4().hex;admission=q.put(identifier,payload)
    if admission['admission'].startswith('rejected'):return admission
    deadline=time.monotonic()+max(0,wait)
    while time.monotonic()<deadline:
        row=q.get(identifier)
        if row and row['status']in('completed','failed_preserved','uncertain','rejected_invalid'):
            return {'admission':admission['admission'],'request':row,'native_result_not_replaced':True}
        time.sleep(.05)
    return {'id':identifier,'admission':admission['admission'],'status':'waiting_or_processing','no_automatic_retry':True}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cola',type=Path,required=True)
    p.add_argument('--id');p.add_argument('--esperar',type=float,default=30)
    p.add_argument('operacion',choices=('estado','resultado','pausar','reanudar','guardar','detener','exportar','sesion','avanzar'))
    p.add_argument('--situaciones');p.add_argument('--ticks',type=int);p.add_argument('--actuador',choices=('closed','nulled'),default='closed')
    p.add_argument('--retorno',choices=('real','omit'),default='real');a=p.parse_args()
    if not a.cola.is_file():raise FileNotFoundError('Start an explicit owner first; client never creates a life or hidden server.')
    q=QueueDB(a.cola)
    if a.operacion=='estado':print(json.dumps(q.get_meta('owner'),ensure_ascii=False));return
    if a.operacion=='resultado':
        if not a.id:raise ValueError('Existing transport ID required.')
        print(json.dumps(q.get(a.id),ensure_ascii=False));return
    req={'operacion':a.operacion}
    if a.operacion=='sesion':req.update(situaciones=json.loads(a.situaciones),actuador=a.actuador,retorno=a.retorno)
    elif a.operacion=='avanzar':req['ticks']=a.ticks
    identifier=a.id or uuid.uuid4().hex
    result=q.put(identifier,req)
    if result['admission'].startswith('rejected'):print(json.dumps(result,ensure_ascii=False));return 2
    deadline=time.monotonic()+max(0,a.esperar)
    while time.monotonic()<deadline:
        item=q.get(identifier)
        if item and item['status']in('completed','failed_preserved','uncertain','rejected_invalid'):
            print(json.dumps({'admission':result['admission'],'request':item},ensure_ascii=False));return 0 if item['status']=='completed'else 3
        time.sleep(.05)
    print(json.dumps({'id':identifier,'admission':result['admission'],'status':'waiting_or_processing','no_automatic_retry':True},ensure_ascii=False));return 0


if __name__=='__main__':raise SystemExit(main())
