"""Locate query admission interference; diagnostic fork, never MAIN repair."""
import argparse,hashlib,json,shutil,sys,time
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent-dir',type=Path,required=True);p.add_argument('--mode',choices=['cut','sham'],required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source';shutil.copytree(a.parent_dir/'executed_source',bundle);shutil.copyfile(__file__,bundle/'full_spatial_access_diagnostic.py');sys.path.insert(0,str(bundle/'src'))
    from relaciones.full_spatial_e1 import FullSpatialE1Session
    from integracion.relational_pair import physical,move
    from dee_thinking import _native as d
    start=time.monotonic();parent=FullSpatialE1Session.load(a.parent_dir/'T110.deetsnap.gz');parent.run_until(136);before=physical(parent.world);q=parent.geometry['quantity']['center'];pre=parent.observe(q);requests=parent.receipts();r=next(x for x in requests if x['port']=='quantity.reader'and x['tick']==136)
    e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=int(pre['raw'])if a.mode=='sham'else 0;e.label='DIAGNOSTIC_ONLY_QUERY_ACCESS_'+a.mode
    # Refresh only external observer journals before attaching the existing fork.
    # This does not alter any physical record, clock, channel, queue or protocol.
    parent.spatial.state['modes']={k:deepcopy(s.state)for k,s in parent.spatial.modes.items()};parent.state['spatial']=deepcopy(parent.spatial.state);parent.state['mode']=deepcopy(parent.mode.state);parent.state['quantity']=deepcopy(parent.quantity.state)
    child=parent.world.diagnostic_fork([e],True);s=FullSpatialE1Session(child,parent.geometry,parent.state,identifier=a.out.name);post=s.observe(q);s.run_until(137);at137=s.observe(q);native_receipt=next(x for x in s.receipts()if x['id']==r['id'])
    statefields={'raw','clock','state','s_reg','direction','semantic','active'}
    m={'schema':'CPC8R.full_spatialE1.access_diagnostic.v1','case':{'id':a.out.name,'mode':a.mode,'prepared_decoder':'active semantic1(dx,0,0),load7; query Applied; new current45 against oldreference31 expects dx−1'},'status':'EXECUTED','preparations':0,'diagnostic_forks':1,'continuations':0,'source_sha256':{p.relative_to(bundle).as_posix():sha(p)for p in bundle.rglob('*.py')},'parent':{'snapshot':str(a.parent_dir/'T110.deetsnap.gz'),'sha256':sha(a.parent_dir/'T110.deetsnap.gz'),'loaded_tick':110,'continued_without_new_inputs_to':136},'parent_physical_before':before,'parent_physical_after':physical(parent.world),'parent_unchanged':before==physical(parent.world),'intervention':{'site':q,'pre':pre,'post':post,'clock_preserved':pre['clock']==post['clock'],'requested_RAW':str(e.raw),'MAIN_edit':False},'original_query_receipt_before_fork':r,'query_receipt_after_fork':native_receipt,'new_inputs_after_fork':[],'requests':s.receipts(),'quantity137':at137,'quantity137_Moore27':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)],'frozen_readout_valid':bool(native_receipt['receipt']['status']=='applied'and at137['active']and at137['semantic']==1 and at137['direction']==[-1,0,0]and at137['s_reg']==7),'physical':physical(child),'elapsed_seconds':time.monotonic()-start}
    (a.out/'MEASUREMENTS.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'id':a.out.name,'prefork_query_status':r['receipt']['status'],'query_status':native_receipt['receipt']['status'],'response_direction':at137['direction'],'valid':m['frozen_readout_valid'],'parent_unchanged':m['parent_unchanged']}))
if __name__=='__main__':main()
