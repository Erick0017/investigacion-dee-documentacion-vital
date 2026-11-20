"""Declared social/current-life operations, never external target selection."""
from pathlib import Path
import sys,json,argparse
ROOT=Path(__file__).resolve().parents[3];LAB=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(LAB))
from app.lives import Store
from app.native_tools import physical,observe,atomic_json,digest_file,exact_receipt
from habitat import check_budget,inherited_panel
import social_habitat as social
import referencia_ambiental as ref
EV=ROOT/'evidencia/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01'
def main():
    p=argparse.ArgumentParser();p.add_argument('--life',required=True);p.add_argument('--name',required=True);p.add_argument('--kind',choices=['social','addition','passive'],default='social');p.add_argument('--mode',default='full');p.add_argument('--until',type=int);args=p.parse_args();check_budget()
    output=EV/(args.name+'.json')
    if output.exists():raise FileExistsError('Existing evidence protected')
    def run(a):
        initial=physical(a.world,occupation=True)
        if args.kind=='social':
            plan=social.make_plan(a,args.name,mode=args.mode,values=(18,45));result=social.run(a,plan)
        elif args.kind=='addition':
            plan=ref.plan(a,args.name,actual_addition=3,mode=args.mode);result=ref.schedule(a,plan);frames=[]
            for t in plan['suggested_passive_boundaries']:
                a.run_until(t);frames.append({'tick':t,'reference_hub':observe(a.world,plan['reference_hub']),'reference_site':observe(a.world,plan['reference_site']),'center':observe(a.world,plan['comparison_center'])})
            result['frames']=frames;result['later_panel']=inherited_panel(a,social=False,quantity=83,old=True)
        else:
            if args.until is None or args.until<a.tick:raise ValueError('Explicit forward horizon')
            a.run_until(args.until);result={'no_new_inputs':True,'until':args.until}
        return {'initial':initial,'operation':result,'final':physical(a.world,occupation=True)}
    result=Store().mutate(args.life,'HABITAT01_'+args.kind.upper(),run,{'condition':vars(args),'source_sha256':digest_file(__file__)})
    result['receipts']=[exact_receipt(x)for x in Store().load(args.life)[1].world.runtime.receipts];atomic_json(output,result);print(json.dumps({'life':args.life,'tick':result['INSTRUMENTO']['tick'],'file':str(output)}),flush=True)
if __name__=='__main__':main()
