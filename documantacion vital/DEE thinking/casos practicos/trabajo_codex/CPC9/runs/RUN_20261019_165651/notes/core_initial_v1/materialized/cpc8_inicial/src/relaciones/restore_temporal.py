"""Load the exact guarded order individual and request a third opaque query."""
import argparse,hashlib,json,sys,time
from pathlib import Path
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.parent/'executed_source/src'))
    from relaciones.temporal_roles import TemporalSession,physical
    s=TemporalSession.load(a.parent/'FINAL_T234.deetsnap.gz');before=physical(s.world);start=time.monotonic();nold=len(s.state['requests'])
    read=s.geometry['ticks']['query']+262;input_tick=read-3
    for q in s.geometry['lanes'].values():s.input(q['query_port'],11,input_tick,'probe','NEW_USER_OPAQUE_QUERY_AFTER_RESTORATION')
    s.run_until(read);observations={k:s.observe(q['query_site']) for k,q in s.geometry['lanes'].items()};decoded=[]
    for key,r in observations.items():
        v=r['direction']
        if r['active'] and r['semantic']==1 and v[0] in(-1,1) and v[1:]==[-1,1]:decoded.append({'location':key,'value':v[0],'physical':r})
    path=a.out/('FINAL_T'+str(read)+'.deetsnap.gz');proof=s.save(path)
    result={'schema':'CPC8.temporal_roles.restore_new_query.v1','preparations':0,'continuations':1,'parent':{'path':str(a.parent/'FINAL_T234.deetsnap.gz'),'sha256':sha(a.parent/'FINAL_T234.deetsnap.gz'),'physical':before},
        'source_sha256':sha(a.parent/'executed_source/src/relaciones/temporal_roles.py'),'identifier':s.identifier,'input_tick':input_tick,'read_tick':read,'requests':s.receipts()[nold:],
        'observations':observations,'decoded':decoded,'final_physical':physical(s.world),'checkpoint':{'path':path.name,'storage':proof},
        'host_RAW_clock_edits_on_MAIN':[],'scope':'Third same opaque query; fixed preserving decoder. No history/result JSON or teaching map is opened by the participant.','elapsed_seconds':time.monotonic()-start,'status':'EXECUTED'}
    (a.out/'MEASUREMENTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'read_tick':read,'values':[q['value'] for q in decoded]}))
if __name__=='__main__':main()
