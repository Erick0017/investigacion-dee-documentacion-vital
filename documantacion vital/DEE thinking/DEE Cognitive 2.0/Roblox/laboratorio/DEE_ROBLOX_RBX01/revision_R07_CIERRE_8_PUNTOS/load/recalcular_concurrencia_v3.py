"""Passive, portable material-call overlap and declared-history isolation audit."""
from pathlib import Path
import argparse,datetime,hashlib,json
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def stamp(v):return datetime.datetime.fromisoformat(v.replace('Z','+00:00')).timestamp()
def intersect(a,b):
    return [(max(x,z),min(y,w))for x,y in a for z,w in b if max(x,z)<min(y,w)]
def phases(path):
    pending={};intervals=[];inputs=[]
    for line in path.read_text('utf8').splitlines():
        r=json.loads(line);kind=r.get('event');ctx=r.get('context',{});key=ctx.get('operation_id')
        if kind=='INTENT':
            need(key not in pending,'No duplicate material intent');pending[key]=r
        elif kind=='COMPLETED':
            a=pending.pop(key);need(a['context']==ctx,'Same original call identity')
            intervals.append((stamp(a['utc']),stamp(r['utc'])))
            inputs.append({'id':key,'kind':r['kind'],'seconds':r['elapsed_seconds'],'actual_result':r['result']})
    return intervals,inputs,list(pending)
def run(paths,out):
    need(len(paths)==3 and not out.exists()and out.parent.is_dir(),'Three closed worker dirs, one fresh result')
    reports=[];common=None;ids=set()
    for folder in paths:
        p=folder/'RESULTADO.json';r=read(p);need(r['closed']is True and r['pending_global_intent']is None,'Only closed coherent owners')
        need(r['life']not in ids,'Three separate lives');ids.add(r['life'])
        iv,outputs,uncertain=phases(folder/'FASES.jsonl');need(not uncertain,'No ambiguous material call')
        common=iv if common is None else intersect(common,iv)
        reports.append({'life':r['life'],'profile':r['profile'],'episodes':len(r['results']),'owner_pid':r['owner_pid'],
          'result_path':str(p),'result_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
          'phases_path':str(folder/'FASES.jsonl'),'phases_sha256':hashlib.sha256((folder/'FASES.jsonl').read_bytes()).hexdigest(),
          'intervals':iv,'calls':outputs,'lesson_and_actual_results':[{'tool':x['tool'],'actual':x['public_tool_result']}for x in r['results']]})
    result={'schema':'DEE.R07.load.material_overlap.R01','owners':reports,'common_material_call_overlap_seconds':sum(b-a for a,b in common),
      'common_material_call_intervals':common,'three_complete_episodes_each':all(x['episodes']==3 for x in reports),
      'scope':'Overlap of actual adapter.execute wall intervals in separate closed owners. No claim of simultaneous CPU instructions. Different lessons/actual function outputs are inspected, not merged into MAIN.',
      'Native_calls':0,'new_ticks':0}
    with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workers',type=Path,nargs=3,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(run(a.workers,a.output),ensure_ascii=False))
