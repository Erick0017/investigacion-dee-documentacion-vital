"""Local SQLite transport client; no DEE import, decision rule or public port."""
import argparse,json,sys,time,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cola_local import QueueDB


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cola',type=Path,required=True)
    p.add_argument('--id');p.add_argument('--esperar',type=float,default=30)
    p.add_argument('operacion',choices=('estado','resultado','pausar','reanudar','guardar','detener','sesion','avanzar'))
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
        if item and item['status']in('completed','failed_preserved','uncertain'):
            print(json.dumps({'admission':result['admission'],'request':item},ensure_ascii=False));return 0 if item['status']=='completed'else 3
        time.sleep(.05)
    print(json.dumps({'id':identifier,'admission':result['admission'],'status':'waiting_or_processing','no_automatic_retry':True},ensure_ascii=False));return 0


if __name__=='__main__':raise SystemExit(main())
