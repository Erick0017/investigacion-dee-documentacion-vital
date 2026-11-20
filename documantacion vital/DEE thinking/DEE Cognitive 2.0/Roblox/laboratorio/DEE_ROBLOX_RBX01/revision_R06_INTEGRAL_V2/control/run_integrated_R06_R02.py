"""Future block runner: original experiment loop, only World transport replaced.

Never use to repeat an already admitted block. Explicit Root CLI only.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[1]
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def execute(a):
    worlds=load(ROOT/'control/world_comprimido_R06.py','_r06_world_transport_zstd')
    original=worlds.BASE;instances=[]
    class World(worlds.CompressedWorld):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,expected_place=a.expected_place,**kwargs);instances.append(self)
    original.World=World
    try:return original.execute(a)
    finally:
        for instance in instances:instance.close()
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute-root-only',action='store_true')
    p.add_argument('--destination',type=Path);p.add_argument('--world',type=Path);p.add_argument('--output',type=Path)
    p.add_argument('--ledger',type=Path);p.add_argument('--studio-id');p.add_argument('--stop-cycle',type=int);p.add_argument('--session')
    p.add_argument('--expected-place',default='DEE_RBX01_INTEGRAL_V2_NATIVE.rbxlx')
    a=p.parse_args()
    if not a.execute_root_only or not all((a.destination,a.world,a.output,a.ledger,a.studio_id,a.stop_cycle)):p.error('All original explicit Root execution fields required')
    execute(a)
