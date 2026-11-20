"""Same reference contract, persistent byte-exact World transport only."""
from pathlib import Path
import argparse,importlib.util,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'control'))
import run_comparator_R06 as base
import world_comprimido_R06 as world
def execute(a):
 instances=[]
 class World(world.CompressedWorld):
  def __init__(self,*args,**kwargs):
   super().__init__(*args,expected_place=a.expected_place,**kwargs);instances.append(self)
 base.World=World
 try:return base.execute(a)
 finally:
  for x in instances:x.close()
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute-root-only',action='store_true')
 p.add_argument('--participant',required=True,choices=('PROGRAMMED','CONVENTIONAL_AI'))
 p.add_argument('--destination',type=Path,required=True);p.add_argument('--world',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True);p.add_argument('--studio-id',required=True)
 p.add_argument('--expected-place',required=True);p.add_argument('--stop-cycle',type=int,required=True)
 p.add_argument('--session');p.add_argument('--resume',action='store_true')
 a=p.parse_args();base.need(a.execute_root_only,'Explicit Root execution only');execute(a)
