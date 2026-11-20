from pathlib import Path
import argparse,json,sys,time,importlib.util,subprocess
ROOT=Path(__file__).resolve().parents[3];LAB=Path(__file__).resolve().parent;EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from app.native_tools import atomic_json,digest_file,physical
from capacidades import habitat_externo_01 as ext
def module(name,path):
    sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['panel','external']);p.add_argument('--life',required=True);p.add_argument('--name',required=True);p.add_argument('--steps',type=int,default=4);p.add_argument('--seed',type=int,default=81001);p.add_argument('--mode',default='closed');args=p.parse_args()
    b=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text(encoding='utf8'))
    if time.monotonic()>b['monotonic_deadline_seconds']:raise TimeoutError('Fixed budget')
    out=EV/(args.name+'.json')
    if out.exists():raise FileExistsError('Evidence exists')
    if args.command=='panel':
        h=module('_ic_habitat_reused_panel',ROOT/'laboratorio/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01/habitat.py');fn=lambda a:h.inherited_panel(a)
    else:fn=lambda a:ext.run(a,steps=args.steps,seed=args.seed,mode=args.mode)
    v=Store().mutate(args.life,'IC01_'+args.command.upper(),fn,{'condition':vars(args),'source_sha256':digest_file(__file__),'no_implicit_world_reset':True});atomic_json(out,v);print(json.dumps({'life':args.life,'tick':v['INSTRUMENTO']['tick'],'file':str(out)}),flush=True)
if __name__=='__main__':main()
