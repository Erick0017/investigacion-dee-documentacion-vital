from pathlib import Path
import sys,json,argparse,time,ctypes
ROOT=Path(__file__).resolve().parents[3];LAB=Path(__file__).resolve().parent;EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(LAB))
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
from capacidades.observador_causal_retrospectivo_01 import Snapshot
import ic_native as ic
def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['init','fork','train','loop','loop2','situated']);p.add_argument('--life',default='E1_INTEGRADO_MAIN');p.add_argument('--source',default='E1_SOCIAL_11');p.add_argument('--checkpoint');p.add_argument('--name',default='INIT');p.add_argument('--contexts',default='1,-1');p.add_argument('--mode',default='paired');p.add_argument('--steps',type=int,default=2);args=p.parse_args()
    b=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text(encoding='utf8'))
    if time.monotonic()>b['monotonic_deadline_seconds']:raise TimeoutError('Campaign deadline')
    protect_current();EV.mkdir(parents=True,exist_ok=True);store=Store()
    if args.command in('init','fork'):
        rec=store.fork(args.source,args.life,kind='EXACT_FORK'if args.command=='init'else'DIAGNOSTIC_COPY',checkpoint=args.checkpoint);print(json.dumps({'life':args.life,'tick':rec['physical']['tick'],'snapshot':rec['snapshot'],'sha256':rec['snapshot_sha256']}));return
    out=EV/(args.name+'.json')
    if out.exists():raise FileExistsError('No trial overwrite')
    def run(a):
        initial=physical(a.world,occupation=True)
        if args.command=='train':result=ic.train(a,episode=args.name,contexts=tuple(map(int,args.contexts.split(','))),feedback=args.mode)
        elif args.command=='situated':result=ic.situated(a,name=args.name,availability=tuple(map(int,args.contexts.split(','))),mode=args.mode,trace=True,compact=True,gap=0)
        else:result=(ic.loop2 if args.command=='loop2'else ic.loop)(a,name=args.name,steps=args.steps,mode=args.mode)
        return {'initial':initial,'native':result,'final':physical(a.world,occupation=True)}
    result=store.mutate(args.life,'IC01_'+args.command.upper(),run,{'condition':vars(args),'source_sha256':digest_file(LAB/'ic_native.py'),'runner_sha256':digest_file(__file__)})
    atomic_json(out,result);print(json.dumps({'life':args.life,'tick':result['INSTRUMENTO']['tick'],'file':str(out)}),flush=True)
if __name__=='__main__':main()
