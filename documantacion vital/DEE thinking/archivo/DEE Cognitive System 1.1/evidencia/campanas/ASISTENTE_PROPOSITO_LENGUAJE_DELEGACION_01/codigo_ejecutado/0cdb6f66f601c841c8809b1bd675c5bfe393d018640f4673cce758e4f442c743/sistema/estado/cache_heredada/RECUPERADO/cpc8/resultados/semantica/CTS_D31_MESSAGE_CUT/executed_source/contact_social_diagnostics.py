"""Causal message interventions outside MAIN, no regenerated original contact."""
import argparse,hashlib,json,shutil,sys,time
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent-dir',type=Path,required=True);p.add_argument('--mode',choices=['cut','sham','content'],required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source';shutil.copytree(a.parent_dir/'executed_source',bundle);shutil.copyfile(__file__,bundle/Path(__file__).name);sys.path.insert(0,str(bundle/'src'))
    from comunicacion.contact_social_regulated import RegulatedContactSocialE1Session
    from integracion.relational_pair import physical
    from dee_thinking import _native as d
    start=time.monotonic();parent=RegulatedContactSocialE1Session.load(a.parent_dir/'T484.deetsnap.gz');parent.run_until(486);before=physical(parent.world);edits=[];records=[]
    for r in parent.geometry['contact_social']['receivers']:
        q=r['message_before_teaching_site'];pre=parent.observe(q);raw=int(pre['raw'])
        if a.mode=='cut':raw=0
        elif a.mode=='content'and pre['active']and pre['semantic']==1 and pre['direction'][1]==1:
            v=list(pre['direction']);v[2]=-1 if v[2]==0 else 0;raw=int(d.pack_record(pre['state'],pre['s_reg'],*v,pre['semantic']))
        e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=raw;e.label='DIAGNOSTIC_CONTACT_MESSAGE_'+a.mode;edits.append(e);records.append({'receiver':r['id'],'pre':pre,'requested_RAW':str(raw),'clock_edit':None})
    parent.state['quantity']=deepcopy(parent.quantity.state);parent.state['mode']=deepcopy(parent.mode.state);parent.state['initiative']=deepcopy(parent.initiative.state)
    child=parent.world.diagnostic_fork(edits,True);s=RegulatedContactSocialE1Session(child,parent.geometry,parent.state,identifier=a.out.name);old=len(s.state['contact_social_observations'])
    for record,r in zip(records,parent.geometry['contact_social']['receivers']):record['post']=s.observe(r['message_before_teaching_site'])
    s.run_until(616);path=a.out/'T616.deetsnap.gz';storage=s.save(path)
    m={'schema':'CPC8R.contact_socialE1.diagnostic.v1','case':{'id':a.out.name,'mode':a.mode},'status':'EXECUTED','preparations':0,'diagnostic_forks':1,'continuations':0,'parent':{'snapshot':str(a.parent_dir/'T484.deetsnap.gz'),'sha256':sha(a.parent_dir/'T484.deetsnap.gz'),'loaded_tick':484,'continued_without_new_inputs_to':486},'source_sha256':{p.relative_to(bundle).as_posix():sha(p)for p in bundle.rglob('*.py')},'parent_physical_before':before,'parent_physical_after':physical(parent.world),'parent_unchanged':before==physical(parent.world),'edits':records,'same_load_state_semantic_clock_for_content_control':all(all(x['pre'][k]==x['post'][k]for k in('s_reg','state','semantic','clock'))for x in records)if a.mode=='content'else None,'new_inputs_after_fork':[],'requests':s.receipts(),'contact_social_observations_after_fork':s.state['contact_social_observations'][old:],'final_word':s.view()['joint'],'physical':physical(child),'snapshot':{'path':path.name,'sha256':sha(path),'storage':storage},'elapsed_seconds':time.monotonic()-start,'scope':'Only formed message records are intervened diagnostically. Fixed future teaching/query/use requests and original MAIN remain intact. Direction intervention can change routing as well as learned content; no arbitrary convention claim.'}
    (a.out/'MEASUREMENTS.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'id':a.out.name,'parent_unchanged':m['parent_unchanged'],'queries':[(x['receiver'],x['covered'],x['content'])for x in m['contact_social_observations_after_fork']if x['phase']=='QUERY'],'content_inventory_equal':m['same_load_state_semantic_clock_for_content_control']}))
if __name__=='__main__':main()
