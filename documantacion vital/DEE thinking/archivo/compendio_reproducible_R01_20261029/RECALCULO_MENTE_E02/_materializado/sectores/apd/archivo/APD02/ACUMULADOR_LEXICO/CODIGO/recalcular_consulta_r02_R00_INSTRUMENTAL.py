"""Portable primary-only query autopsy; exact RAW/clocks, no engine imports."""
import argparse,gzip,hashlib,json
from pathlib import Path
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def fields(raw):
    if type(raw)is not int or not 0<=raw<2**64:raise ValueError('Exact uint64 RAW required')
    return {'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,'semantic':(raw>>60)&15,
        'direction':[((raw>>s)&15)-(16 if((raw>>s)&15)>=8 else 0)for s in(48,52,56)]}
def sign(panel):
    candidates=[]
    for obs in panel:
        f=fields(obs['raw'])
        if f['state']and f['semantic']==1 and f['direction'][:2]==[0,0]and f['direction'][2]in(-1,1):candidates.append(f['direction'][2])
    return candidates[0]if len(candidates)==1 else None
def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('Preserve previous recalculation')
    rows=[];issues=[];observations=0;sources=[];before=[]
    for path in sorted(a.evidence.glob('*/PRIMARIO.json.gz')):
        r=read(path);receipts=[];panels={};choices=[]
        for name in('old_before','queries','old_after'):
            values=[]
            for q in r.get(name,[]):
                rr=q['reader'];derived=sign(rr['panel']);values.append([q['form'],derived]);receipts.extend(q['requests']);observations+=len(rr['panel'])
                if derived!=rr['formed_native_command']:issues.append([r['arm'],q['form'],'RAW sign mismatch'])
                for frame in q['frames']:
                    for ob in frame['gates']:
                        observations+=1;f=fields(ob['raw'])
                        if any(f[k]!=ob[k]for k in f):issues.append([r['arm'],frame['tick'],ob['site'],'decoded fields mismatch'])
                        if type(ob['clock'])is not int or not 0<=ob['clock']<2**64:issues.append([r['arm'],'inexact clock'])
            panels[name]=values
        receipts.extend(r.get('preparation',{}).get('requests',[]));receipts.extend(r.get('lesson_B',{}).get('requests',[]));statuses={};rejects=[]
        for x in receipts:
            status=x.get('receipt',{}).get('status','missing');statuses[status]=statuses.get(status,0)+1
            if status!='applied':rejects.append(x)
        for name in('context_before_A','context_after_A','context_after_B'):
            for ob in r.get(name,{}).get('sites',[]):
                observations+=1;f=fields(ob['raw'])
                if any(f[k]!=ob[k]for k in f):issues.append([r['arm'],name,ob['site'],'context fields mismatch'])
        before.append(r['before_queries']['physical'])
        rows.append({'arm':r['arm'],'A_query':r['A_material_query'],'B_query':r['B_material_query'],
            'old_before':panels['old_before'],'queries':panels['queries'],'old_after':panels['old_after'],
            'old_before_valid':sum(x[1]in(-1,1)for x in panels['old_before']),'old_after_valid':sum(x[1]in(-1,1)for x in panels['old_after']),
            'requested':len(receipts),'admission':statuses,'rejected_details':rejects,'error':r['error'],
            'after_A_physical':r['after_A']['physical'],'after_B_physical':r['after_B']['physical'],'final':r['final']})
        sources.append({'path':str(path.relative_to(a.evidence)).replace('\\','/'),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    if len(rows)!=4:issues.append(['Expected four complete factorial arms',len(rows)])
    if before and any(x!=before[0]for x in before[1:]):issues.append(['Initial physical equality failed'])
    result={'schema':'APD02.lexical_query_autopsy.archive.R02','new_ticks':0,'engine_imported':False,'cases':rows,
        'initial_physical_equal':bool(before)and all(x==before[0]for x in before),'exact_RAW_observations':observations,
        'issues':issues,'sources':sources,'limits':['Four deterministic branches of one prefix, not four independent learned lives',
        'Causal factors are the complete material query protocols, not yet one isolated carrier or collision',
        'Physical RAW/clocks equality is not byte identity of documentary metadata or service SQLite',
        'Old read failures do not by themselves demonstrate global information destruction']}
    with a.output.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({'cases':len(rows),'RAW':observations,'issues':issues,'results':[{'arm':r['arm'],'queries':r['queries'],'old':r['old_after_valid'],'admission':r['admission']}for r in rows]},ensure_ascii=False))
    if issues:raise SystemExit(1)
if __name__=='__main__':main()
