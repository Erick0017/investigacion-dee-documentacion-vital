"""One bounded alternate-reader diagnosis, never a new MAIN protocol.

Both moving ±X/+Y hypotheses receive the same fixed probes in every bank and
history. RAW is read only for explicit all-bank cut/sham interventions; it never
selects an input or turns a predicted answer into an experience.
"""
import argparse,hashlib,json,os,shutil,sys,time
from copy import deepcopy
from pathlib import Path
from array import array
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def physical(w):
 r=w.runtime;return{'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--cut',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);cut=a.out/'executed_source';shutil.copytree(a.parent/'executed_source',cut);shutil.copyfile(__file__,cut/'diagnostic_reader.py');sys.path.insert(0,str(cut/'src'))
 from count_sign.branch_session import BranchCountSignSession
 from count_sign.session import move
 from dee_thinking import _native as d
 from dee_thinking.consolidated import exact_receipt
 parent=BranchCountSignSession.load(a.parent/'T94.deetsnap.gz');before=physical(parent.world);edits=[];interventions=[]
 for bank in parent.geometry['names']:
  q=bank['memory_site'];pre=parent.observe(q);e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=0 if a.cut else int(pre['raw']);e.label='ALL_FIXED_FORM_BANKS_CUT'if a.cut else'ALL_FIXED_FORM_BANKS_EXACT_SHAM';edits.append(e);interventions.append({'site':q,'before':pre,'requested_RAW':str(e.raw),'clock_edit':None})
 world=parent.world.diagnostic_fork(edits,True);s=BranchCountSignSession(world,parent.geometry,deepcopy(parent.state),a.out.name);new=[];readers=[];seen={}
 # Existing probes are queued in the parent. Deduplicate by public interface
 # identity and literal request fields, never by observed memory or class.
 specifications={p.name:p.channel for p in world.interfaces};inherited={}
 for call in s.state['requests']:
  if call['tick']!=111 or call['payload']!=7 or call['kind']!='probe':continue
  c=specifications[call['port']];q=c.injection_site;v=c.direction
  key=(q.x,q.y,q.z,v.dx,v.dy,v.dz,c.state,c.semantic)
  inherited[key]=call
 for bank in s.geometry['names']:
  for heading in(-1,1):
   target=move(bank['memory_site'],(heading,1,0),20);inject=move(target,(0,0,1),-3);key=tuple(inject)
   if key not in seen:
    same=inherited.get((*inject,0,0,1,77,1))
    if same is not None:
     seen[key]=same['port'];new.append({'id':same['id'],'port':same['port'],'payload':7,'tick':111,'call_tick':94,'input_site':inject,'fixed_direction':[0,0,1],'inherited_identical_request_alias':True})
    else:
     name='AUDITOR.COUNT_ALTERNATIVE.'+str(len(seen));seen[key]=name;ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*inject);ch.direction=d.Direction(0,0,1);ch.state=77;ch.semantic=1;ch.allow_probe=True;ch.allow_experience=False;world.runtime.register_channel(ch);rr=world.runtime.probe(name,111,7);new.append({'id':int(rr.id),'port':name,'payload':7,'tick':111,'call_tick':94,'input_site':inject,'fixed_direction':[0,0,1],'inherited_identical_request_alias':False})
   readers.append({'route_axis_candidate':bank['route_axis_candidate'],'candidate_comparator_x':bank['candidate_comparator_x'],'fixed_heading':heading,'target':target,'physical_port':seen[key]})
 registration={'physical_before':physical(world),'equal_parent_before_except_explicit_edits':not a.cut and physical(world)==before,'scope':'Native Runtime channels added only in diagnostic fork, never to operating MAIN. Dedup uses fixed coordinate identity only.'}
 frames=[]
 for t in(94,100,103,110,111,113,114):
  s.run_until(t);row={'tick':t,'readers':[dict(r,physical=s.observe(r['target']))for r in readers]}
  if t in(113,114):row['Moore27']=[{'center':r['target'],'readings':[s.observe(move(r['target'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for r in readers]
  frames.append(row)
 final=frames[-1]['readers'];qualified=[r for r in final if r['physical']['active']and r['physical']['semantic']==1 and r['physical']['s_reg']>7 and r['physical']['direction']==[r['fixed_heading'],1,1]]
 snap=a.out/'T114.deetsnap.gz';storage=s.save(snap)
 m={'schema':'CPC8R.count_sign.alternative_diagnostic.v1','case':{'id':a.out.name,'cut':a.cut},'preparations':0,'diagnostic_forks':1,'continuations':0,'parent':{'snapshot':str((a.parent/'T94.deetsnap.gz').relative_to(ROOT)),'sha256':sha(a.parent/'T94.deetsnap.gz'),'case_id':a.parent.name},'interventions':interventions,'registration':registration,'fixed_readers_all_banks_both_headings':readers,'new_requests':[{**r,'receipt':exact_receipt(world.runtime.receipt(r['id']))}for r in new],'inherited_requests':s.receipts(),'frames':frames,'qualified_alternative114':qualified,'parent_before':before,'parent_after':physical(parent.world),'parent_unchanged':before==physical(parent.world),'snapshot':{'path':snap.name,'sha256':sha(snap),'storage':storage},'status':'MEASURED','scope':'Assisted diagnostic access only. Original114/148main failure is preserved, no new E2 protocol result; no branch is returned to MAIN.'}
 (a.out/'MEASUREMENTS.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'id':a.out.name,'alternative_valid':len(qualified),'qualified':qualified,'parent_unchanged':m['parent_unchanged']}))
