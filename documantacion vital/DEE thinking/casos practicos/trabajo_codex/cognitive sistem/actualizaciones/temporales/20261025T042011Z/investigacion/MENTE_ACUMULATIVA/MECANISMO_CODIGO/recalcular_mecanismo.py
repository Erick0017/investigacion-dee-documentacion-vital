"""Standard-library-only recalculation from exported primary JSON/GZIP.
No DEE import, snapshot restore, network, subprocess or native tick.
"""
import argparse,gzip,hashlib,json
from pathlib import Path
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decoded(r,payload=5):
    p=r['physical'];rr=r['receipt'];ok=rr['status']=='applied'and p['state']>0 and p['semantic']==1 and p['s_reg']>payload and p['direction']in([-1,-1,0],[-1,1,0])
    return p['direction'][1]if ok else None
def expected_from_receipts(rows,at):
    result={}
    for r in rows:
        if r.get('requested_tick',0)>at:continue
        for ch in r['receipt'].get('channels',[]):
            if '.event.'in ch:
                form=ch.split('.')[0];sign=1 if ch.endswith('.plus')else-1 if ch.endswith('.minus')else None
                if sign is not None:result[form]=sign
    return result
def panel_counts(panel,receipts):
    expected=expected_from_receipts(receipts,panel['read_tick']);values=[decoded(r,panel.get('payload',5))for r in panel['responses']]
    return {'requested':len(values),'admitted':sum(r['receipt']['status']=='applied'for r in panel['responses']),'answered':sum(v is not None for v in values),'correct_current_consequence':sum(v is not None and v==expected.get(r['form'])for r,v in zip(panel['responses'],values)),'rejected':sum(r['receipt']['status']!='applied'for r in panel['responses']),'values':dict((r['form'],v)for r,v in zip(panel['responses'],values))}
def qualified_action(p):return p['state']>0 and p['semantic']==1 and p['s_reg']>7 and p['direction'][0]in(-1,1)and p['direction'][1]in(-1,1)and p['direction'][2]==1
def native_chain(x):
    rows=x['rows'];q=next(r for r in rows if r['tick']==19)['physical']['sites'];a=next(r for r in rows if r['tick']==72)['physical']['sites'];bank=next(r for r in rows if r['tick']==70)['physical']['sites']
    questions={k:p['direction']for k,p in q.items()if k.startswith('question.')and p['state']>0 and p['semantic']==1 and p['s_reg']>13 and p['direction']in([-1,0,0],[1,0,0])}
    acts={k:{'direction':p['direction'],'s_reg':p['s_reg']}for k,p in a.items()if k.startswith('action.')and qualified_action(p)}
    return{'native_questions':questions,'native_actions':acts,'high_banks':{k:{'direction':p['direction'],'s_reg':p['s_reg']}for k,p in bank.items()if k.startswith('bank.')}}
def common_counts(x):
    queries=[r for r in x['rows']if r['kind']=='query'];results=[]
    dirs=x['geometry']['token_directions']
    for r in queries:
        receipt=next(v['receipt']for v in x['receipts']if v['name']=='common.token.'+str(r.get('request_token',r.get('i')))and v['tick']==r['input_tick'])
        admitted=receipt['status']=='applied';panel=r.get('post_fixed_panel',r.get('fixed_panel'));cand=[]
        if panel is not None:
            for j,p in enumerate(panel):
                ok=p['state']>0 and p['semantic']==1 and p['direction'][:2]==dirs[j][:2]and p['direction'][2]in(-1,1)
                if 'pre_fixed_panel'in r:ok=ok and r['pre_fixed_panel'][j]['raw']!=p['raw']
                if ok:cand.append(p['direction'][2])
        else:
            for sign,p in r['outputs'].items():
                if p['state']>0 and p['semantic']==1 and p['s_reg']>0 and p['direction'][2]==int(sign):cand.append(int(sign))
        results.append({'input_tick':r['input_tick'],'entry_admitted':admitted,'candidate_count':len(cand),'decoded':cand[0]if admitted and len(cand)==1 else None})
    return{'requested':len(results),'admitted':sum(r['entry_admitted']for r in results),'unambiguous_after_admission':sum(r['decoded']is not None for r in results),'ambiguous':sum(r['entry_admitted']and r['candidate_count']>1 for r in results),'results':results}
def calculate(directory,operatives=None):
    out={'schema':'MA.mechanism.recalculation.1','no_native_ticks':True,'files':{},'u0':{},'common_router':{},'continuations':{},'formed_question':{},'issues':[]}
    for p in sorted(directory.glob('*.json.gz')):
        x=read(p);out['files'][p.name]={'bytes':p.stat().st_size,'sha256':digest(p)}
        if x.get('schema','').startswith(('MA.U0.pilot','MA.U0.reserved','MA.U0.native_selector')):
            panels={}
            for row in x['rows']:
                detail=row.get('detail')
                if isinstance(detail,dict)and'responses'in detail and all(r.get('form')for r in detail['responses']):
                    panels[row['operation']]=panel_counts(detail,row['receipts'])
                    for rr in detail['responses']:
                        calc=decoded(rr,detail.get('payload',5))
                        if calc!=rr['value']:out['issues'].append(p.name+': decode mismatch '+rr['form'])
            item={'panels':panels,'snapshot':x.get('final_snapshot')}
            if x.get('schema')=='MA.U0.native_selector.1':item['native_chain']=native_chain(x)
            out['u0'][x.get('life',x.get('identifier'))]=item
        elif x.get('schema')=='MA.U0.continuation.1':
            query=x.get('first_retention_after_fifth',x.get('first_query_other_process'))
            out['continuations'][str(x['stage'])]={'tick_initial':x['tick_initial'],'tick_final':x['tick_final'],'values':dict((r['form'],decoded(r))for r in query['responses']),'requested':len(query['responses']),'admitted':sum(r['receipt']['status']=='applied'for r in query['responses']),'answered':sum(decoded(r)is not None for r in query['responses']),'snapshot':x['snapshot']}
        elif x.get('schema')=='MA.U0.formed_question.causal.v1':
            row=next(r for r in x['rows']if r['tick']==72);a=row['physical']['sites']
            out['formed_question'][x['mode']]={'native_actions':{k:p['direction']for k,p in a.items()if k.startswith('action.')and qualified_action(p)},'generic_supplies_present':sum(p['state']>0 and p['semantic']==1 and p['s_reg']>=7 for k,p in a.items()if k.startswith('action.')),'intervention':x['intervention']}
        elif x.get('label','').startswith('MA_COMMON_'):out['common_router'][x['label']]=common_counts(x)
    if operatives is not None:
        ops={};files={}
        for p in sorted(operatives.glob('U0_*.json.gz')):
            packet=read(p);files[p.name]={'bytes':p.stat().st_size,'sha256':digest(p)}
            item={'returncode':packet['returncode'],'native_result_present':'result'in packet}
            if packet['case']=='U0_51_QUERIES'and packet['returncode']==0:
                result=packet['result'];panel=result['result'];responses=panel['responses'];expected=out['continuations']['2']['values']
                values={r['form']:decoded(r)for r in responses}
                item.update(requested=len(responses),admitted=sum(r['receipt']['status']=='applied'for r in responses),answered=sum(v is not None for v in values.values()),correct_retained=sum(v is not None and v==expected.get(k)for k,v in values.items()),values=values,physical=result['physical'])
            elif packet['case']in('U0_52_RELOAD','U0_53_SAVE')and packet['returncode']==0:
                item['physical']=packet['result']['physical']
                item['life_id']=packet['result']['INSTRUMENTO']['life_id']
            elif packet['case']=='U0_50B_IMPORT'and packet['returncode']==0:
                item['source_complete_snapshot_sha256']=packet['argv'][-1]
            ops[packet['case']]=item
        same={k:ops[k]['physical']for k in('U0_51_QUERIES','U0_52_RELOAD','U0_53_SAVE')if k in ops}
        comparable=[{k:p[k]for k in('N','tick','RAW_sha256','clocks_sha256')}for p in same.values()]
        equality=len(comparable)==3 and comparable[0]==comparable[1]==comparable[2]
        out['operative_check']={'files':files,'cases':ops,'query_reload_save_same_physical':equality,'scope':'Archived recomputation of already executed operations, not a new native reproduction.'}
        if not equality:out['issues'].append('Operative query/reload/save physical mismatch or missing cases')
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--operativas',type=Path);p.add_argument('--salida',type=Path);a=p.parse_args();result=calculate(a.evidencia,a.operativas)
    text=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)
    if a.salida:
        if a.salida.exists():raise FileExistsError(a.salida)
        a.salida.write_text(text,encoding='utf8')
    else:print(text)
    raise SystemExit(bool(result['issues']))
