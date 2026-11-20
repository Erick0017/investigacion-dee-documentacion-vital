"""Two exact diagnostic branches after native contact/name pairing.

The Y component is changed only on a fork. Inventory, state, s_reg, X/Z,
semantic and clocks remain; sham preserves complete RAW. MAIN is untouched.
"""
import argparse,copy,hashlib,json,sys
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--mode',choices=['cut_y','sham'],required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.parent/'executed_source/src'))
    from relaciones.contact_consequence import ContactSession,physical
    from dee_thinking import _native as d
    parent_path=a.parent/'T6.deetsnap.gz';parent=ContactSession.load(parent_path);before=physical(parent.world);before_receipts=parent.receipts();edits=[];records=[]
    for key,v in parent.geometry['parts'].items():
        q=v['hub'];old=parent.world.runtime.observe(d.Coordinate(*q));r=old.record
        new=int(old.raw) if a.mode=='sham' else d.pack_record(int(r.state),int(r.s_reg),int(r.dx),0,int(r.dz),int(r.semantic))
        e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=new;e.label='CPC8 fixed post-association Y '+a.mode;edits.append(e)
        records.append({'location':key,'site':q,'raw_before':str(old.raw),'raw_after_requested':str(new),'clock_preserved':str(old.clock),'changed':int(old.raw)!=new,
                        'preserved':['state','s_reg','dx','dz','semantic','clock'],'modified_field':'dy' if a.mode!='sham' else None})
    child=parent.world.diagnostic_fork(edits,True)
    if physical(parent.world)!=before or parent.receipts()!=before_receipts:raise AssertionError('Fork changed parent')
    s=ContactSession(child,parent.geometry,copy.deepcopy(parent.state));s.run_until(160);aux=s.observe(s.geometry['auxiliary_hub'])
    storage=s.save(a.out/'FINAL_T160.deetsnap.gz')
    result={'schema':'CPC8.contact_consequence.memory_fork.v1','case':{'id':a.out.name,'mode':a.mode},'preparations':0,'diagnostic_forks':1,'continuations':0,
      'parent':{'path':str(parent_path),'sha256':sha(parent_path),'physical':before,'parent_unchanged':physical(parent.world)==before and parent.receipts()==before_receipts},
      'source_sha256':sha(a.parent/'executed_source/src/relaciones/contact_consequence.py'),'interventions':records,'captures':s.state['captures'],'requests':s.receipts(),
      'new_inputs_after_fork':[],'auxiliary_memory_after_lesion':aux,'final_physical':physical(s.world),'checkpoint':{'path':'FINAL_T160.deetsnap.gz','storage':storage},'status':'EXECUTED',
      'scope':'Tests necessity of the Y representation/access component for this reader, not destruction of all knowledge: Z consequence and material load remain. New unrelated learning and read160 test general acquisition/read capacity.'}
    (a.out/'MEASUREMENTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'mode':a.mode,'changed_sites':sum(x['changed'] for x in records),'patterns':[len(c['decoded']) for c in result['captures']],'aux':aux['direction']}))
if __name__=='__main__':main()
