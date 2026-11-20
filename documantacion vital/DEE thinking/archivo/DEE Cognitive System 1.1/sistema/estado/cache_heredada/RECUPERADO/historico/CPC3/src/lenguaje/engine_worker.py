"""Único propietario mutable del MAIN durante toda una conversación."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from core.entity import Entity
from lenguaje.session import CommunicationSession


def main():
    p=argparse.ArgumentParser();p.add_argument('--sesion',type=Path,required=True);p.add_argument('--cargar',type=Path)
    p.add_argument('--native-events',type=Path)
    p.add_argument('--perfil',choices=['continuidad','comparacion','politica'],default='continuidad')
    a=p.parse_args()
    factory=Entity
    if a.perfil=='comparacion':
        from core.comparison_entity import CentralComparisonEntity
        factory=CentralComparisonEntity
    elif a.perfil=='politica':
        from core.policy_session import FinitePolicySession
        factory=FinitePolicySession
    session=CommunicationSession(factory,directory=a.sesion)
    if a.cargar:session.execute('Carga '+str(a.cargar))
    if session.entity is not None and a.native_events:session.entity.event_sink=a.native_events
    print(json.dumps({'worker_ready':True,'pid':__import__('os').getpid(),'single_writer':True,'main_in_ram':True,'profile':a.perfil}),flush=True)
    for line in sys.stdin:
        request=json.loads(line)
        try:out=session.execute(request['text'])
        except (ValueError,RuntimeError,TypeError,OSError,KeyError) as exc:out={'attribution':'INTERFAZ','text':str(exc),'error':type(exc).__name__}
        if session.entity is not None and a.native_events:session.entity.event_sink=a.native_events
        print(json.dumps({'id':request['id'],'response':out},ensure_ascii=True,default=str),flush=True)
        if out.get('exit'):break


if __name__=='__main__':main()
