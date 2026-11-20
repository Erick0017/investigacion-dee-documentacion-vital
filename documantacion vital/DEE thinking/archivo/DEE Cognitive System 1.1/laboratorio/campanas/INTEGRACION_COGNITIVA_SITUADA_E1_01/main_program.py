from pathlib import Path
import sys,json,argparse,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB)]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
import ic_body as body,ic_external as ext
def main():
    p=argparse.ArgumentParser();p.add_argument('operation',choices=['train','arm','finish','external','panel']);p.add_argument('--life',default='E1_INTEGRADO_MAIN');p.add_argument('--name',required=True);p.add_argument('--contexts',default='1,-1');p.add_argument('--steps',type=int,default=4);p.add_argument('--mode',default='closed');p.add_argument('--seed',type=int,default=81017);p.add_argument('--feedback',default='cost');p.add_argument('--readout',default='body');args=p.parse_args()
    if time.monotonic()>json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']:raise TimeoutError('Original deadline')
    protect_current();out=EV/(args.name+'.json')
    if out.exists():raise FileExistsError('No overwrite')
    s=Store()
    def run(a):
        initial=physical(a.world,occupation=True)
        if args.operation=='train':result=body.ic.train(a,episode=args.name,contexts=tuple(map(int,args.contexts.split(','))))
        elif args.operation=='arm':result=body.arm(a,name=args.name,contexts=tuple(map(int,args.contexts.split(','))))
        elif args.operation=='finish':result=body.finish(a)
        elif args.operation=='external':
            h=body.attach(a)if args.readout=='body'else None
            try:result=ext.run(a,steps=args.steps,seed=args.seed,mode=args.mode,feedback=args.feedback,readout=args.readout)
            finally:
                if h:h['detach']()
            if h:result['native_frames']=h['frames']
        else:
            sys.path.insert(0,str(ROOT/'laboratorio/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01'));from habitat import inherited_panel
            h=body.attach(a)if body.get(a)and a.tick<body.get(a)['end_tick']else None
            try:result=inherited_panel(a)
            finally:
                if h:h['detach']()
            if h:result['native_frames']=h['frames']
        return{'initial':initial,'operation':args.operation,'data':result,'final':physical(a.world,occupation=True)}
    result=s.mutate(args.life,'IC01_MAIN_'+args.operation.upper(),run,{'arguments':vars(args),'sources':{f.name:digest_file(f)for f in[LAB/'ic_native_core.py',LAB/'ic_body.py',LAB/'ic_external.py',LAB/'PROTOCOLO_MAIN_CONGELADO.json']}})
    atomic_json(out,result);print(json.dumps({'life':args.life,'tick':result['INSTRUMENTO']['tick'],'file':str(out)}),flush=True)
if __name__=='__main__':main()
