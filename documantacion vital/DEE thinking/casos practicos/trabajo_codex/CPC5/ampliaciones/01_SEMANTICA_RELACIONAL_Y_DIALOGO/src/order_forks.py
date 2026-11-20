"""Explicit full-state causal forks; never writes a diagnosis into MAIN."""
from pathlib import Path
import argparse
import json
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,identity,put,sha,record,digest,operational,receipt,local_context

def run(case,out):
    import dee_thinking as d
    out=Path(out);out.mkdir(parents=True,exist_ok=False);start=time.monotonic();identity_value=identity()
    source=ROOT/'resultados/order_stream_discovery/STREAM_AB_D01'
    reference=json.loads((source/'MEASUREMENTS.json').read_text(encoding='utf-8'));s=reference['geometry']
    if case['boundary']=='pre_read':
        path=source/'INITIAL_T0.deetsnap';main=d.OrganizationalWorld.load_snapshot(str(path));main.run_until(2)
        a,b=record(main,s['A']),record(main,s['B']);sites=[s['A'],s['B']]
        assert a['active'] and b['active'] and a['s_reg']!=b['s_reg']
        if case['mode']=='swap_loads':newloads=[b['s_reg'],a['s_reg']]
        elif case['mode']=='equalize':newloads=[b['s_reg'],b['s_reg']]
        else:newloads=[a['s_reg'],b['s_reg']]
        edits=[];declared=[]
        for site,pre,new in zip(sites,[a,b],newloads):
            edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.raw=d.pack_record(pre['state'],new,*pre['direction'],pre['semantic']);edit.label='Explicit order-memory '+case['mode'];edits.append(edit)
            declared.append({'site':site,'before':pre,'requested_raw':str(edit.raw),'fields':['s_reg'] if new!=pre['s_reg'] else []})
    else:
        path=source/'T16.deetsnap';main=d.OrganizationalWorld.load_snapshot(str(path))
        row=next(x for x in reference['rows'] if x['tick']==15)
        products=[r for r in row['names'].values() if r['active'] and r['direction'][0]!=0 and r['s_reg']==12]
        assert len(products)==1
        past=products[0];site=[(past['site'][i]+past['direction'][i])%67 for i in range(3)];pre=record(main,site)
        assert pre['active'] and pre['s_reg']==12 and pre['direction']==past['direction']
        new=0 if case['mode']=='remove' else int(pre['raw'])
        if case['mode']=='turn':new=d.pack_record(pre['state'],pre['s_reg'],-pre['direction'][0],pre['direction'][1],pre['direction'][2],pre['semantic'])
        edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.raw=new;edit.label='Explicit formed-name '+case['mode'];edits=[edit]
        declared=[{'site':site,'before':pre,'requested_raw':str(new),'fields':['RAW'] if case['mode']=='remove' else ['direction.dx'] if case['mode']=='turn' else []}]
    original=digest(main);op=operational(main);raw=main.runtime.raw_copy();clock=main.runtime.clock_copy()
    w=main.fork() if case['mode']=='reference' else main.diagnostic_fork(edits,True)
    changed=[i for i,(a,b) in enumerate(zip(raw,w.runtime.raw_copy())) if a!=b]
    changed_clock=[i for i,(a,b) in enumerate(zip(clock,w.runtime.clock_copy())) if a!=b]
    assert not changed_clock
    assert list(w.runtime.channel_names)==list(main.runtime.channel_names)
    assert [receipt(w,x.id) for x in main.runtime.receipts]==[receipt(main,x.id) for x in main.runtime.receipts]
    for x in declared:x['after']=record(w,x['site'])
    put(out/'CONFIG.json',{'case':case,'parent':str(path.relative_to(ROOT)),'parent_sha256':sha(path),'source_sha256':sha(__file__),
        'prediction_registered_before_evolution':'Memory swap can reverse/readjust stream; equalization can remove discrimination; formed-name cut can suppress query access while leaving original relative support. Results may differ and are retained.',
        'modality':'INTACT_REPLAY_FORK' if case['mode']=='reference' else 'DIAGNOSTIC_FORK','interventions':declared})
    w.save_snapshot(str(out/'AFTER_INTERVENTION.deetsnap'));rows=[]
    times=[2,3,4,7,15,16,17,24,25,26,35,91,92,93,100]
    for tick in times:
        if tick<w.runtime.current_tick:continue
        w.run_until(tick);ar,br=record(w,s['A']),record(w,s['B'])
        rows.append({'tick':tick,'A':ar,'B':br,'delta':ar['s_reg']-br['s_reg'] if ar['active'] and br['active'] else None,
                     'comparator':record(w,s['center']),'names':{k:record(w,q) for k,q in s['name_hubs'].items()},
                     'queries':{k:record(w,q) for k,q in s['query_sites'].items()},
                     'intervention_context':{str(i):local_context(w,x['site']) for i,x in enumerate(declared)} if tick<=17 else {}})
    w.save_snapshot(str(out/'FINAL_T100.deetsnap'))
    unchanged=digest(main)==original and operational(main)==op;assert unchanged
    result={'schema':'CPC5.extension.order_fork.v1','case':case,'engine':identity_value,'parent':str(path.relative_to(ROOT)),'parent_sha256':sha(path),
            'source_sha256':sha(__file__),'modality':'INTACT_REPLAY_FORK' if case['mode']=='reference' else 'DIAGNOSTIC_FORK',
            'initial_physical':original,'final_physical':digest(w),'final_operative':operational(w),'rows':rows,
            'interventions':declared,'raw_sites_changed':changed,'clock_sites_changed':changed_clock,'MAIN_unchanged':unchanged,
            'calls':[],'receipts':[receipt(w,x.id) for x in w.runtime.receipts],
            'snapshots':[{'file':p.name,'sha256':sha(p)} for p in out.glob('*.deetsnap')],
            'preparations':0,'checkpoint_continuations':1,'elapsed_seconds':time.monotonic()-start}
    put(out/'MEASUREMENTS.json',result);print(json.dumps({'id':case['id'],'RAW_changes':len(changed),'MAIN_unchanged':unchanged}),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    for case in json.loads(a.config.read_text(encoding='utf-8'))['cases']:
        target=a.output/case['id']
        if (target/'MEASUREMENTS.json').exists():continue
        run(case,target)

if __name__=='__main__':main()
