"""Auditor-only causal cuts, shams and exact native restoration of return."""
from pathlib import Path
from copy import deepcopy
import argparse,gc,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src')]
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from retorno_social import ReturnSession
from integracion.relational_pair import physical,move
from ejecutar_retorno import write,minimal_view

def operation(s):
    return {'channels':sorted(s.world.runtime.channel_names),'receipts':[exact_receipt(x)for x in s.world.runtime.receipts],
            'protocol_count':len(s.world.protocols)}

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',default='RET_D01_P');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False);source=ROOT/'resultados/retorno'/a.case
    original=json.loads((source/'MEDICIONES.json').read_text(encoding='utf-8'))
    snapshot=source/'T148.deetsnap.gz';before_file=hashlib.sha256(snapshot.read_bytes()).hexdigest()
    parent=ReturnSession.load(snapshot);parent_physics=physical(parent.world);parent_op=operation(parent)
    candidates=[(b,parent.observe(b['message_site']))for b in parent.geometry['cpc9_return']['banks']]
    messages=[(b,o)for b,o in candidates if o['active']and o['s_reg']==7 and o['direction']==[b['sign'],0,0]]
    if len(messages)!=1:raise ValueError('No unique qualified pre-recording B carrier, cannot perform claimed selective cut')
    bank,observed=messages[0];site=bank['message_site']
    config={'schema':'CPC9.return.causal.v1','source_primary':str((source/'MEDICIONES.json').relative_to(ROOT)),
        'source_sha256':hashlib.sha256((source/'MEDICIONES.json').read_bytes()).hexdigest(),'snapshot_sha256':before_file,
        'formed_B_message':observed,'intervention_site':site,'preparations':0,'diagnostic_forks':2,'restored_continuations':1,
        'prediction_before_evolution':'Cut formed7 carrier only: no direction-qualified E1 return use221. Sham: complete final RAW/clocks/receipts616 equal parent trajectory.',
        'clock_edited':False,'new_external_inputs':0}
    write(a.out/'CONFIG.json',config);rows=[];trace=[]
    for condition in ('restore','cut_message','sham_message'):
        if condition=='restore':world=parent.world.fork()
        else:
            edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site)
            edit.raw=0 if condition=='cut_message'else int(observed['raw']);edit.clock=None;edit.label=condition
            world=parent.world.diagnostic_fork([edit],True)
        s=ReturnSession(world,parent.geometry,deepcopy(parent.state),parent.identifier)
        row={'condition':condition,'pre_physical':physical(world),'pre_operation_equal':operation(s)==parent_op,
             'intervention':{'before':observed,'after':s.observe(site),'clock_preserved':s.observe(site)['clock']==observed['clock']},'frames':[]}
        for tick in range(148,226):
            # Complete interval passive coverage of both predicted moving paths;
            # neighbours justify branches, not unique ancestry by proximity.
            if condition=='restore'and 149<=tick<=216:
                for b in s.geometry['cpc9_return']['banks']:
                    target=move(b['hub'],(b['sign'],1,0),tick-149)
                    trace.append({'pre_tick':s.tick,'target_tick':tick,'bank':b['id'],'target':target,
                        'pre_Moore27':[s.observe(move(target,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
            s.run_until(tick)
            if condition=='restore'and trace and trace[-1]['target_tick']==tick:
                for item in trace[-2:]:item['post']=s.observe(item['target'])
            if tick in(148,149,210,211,212,213,214,215,216,220,221,225):row['frames'].append(minimal_view(s))
        s.run_until(616);row['frames'].append(minimal_view(s))
        row.update(final_physical=physical(world),final_operation=operation(s),
                   full_final_equal=physical(world)==original['final_physical'],
                   full_receipts_equal=operation(s)['receipts']==sorted([x['receipt']for x in original['requests']],key=lambda x:x['id']),
                   parent_unchanged=physical(parent.world)==parent_physics and operation(parent)==parent_op)
        if condition!='cut_message'and not(row['full_final_equal']and row['full_receipts_equal']):
            raise AssertionError('Restored/sham trajectory differs')
        if not row['parent_unchanged']or not row['intervention']['clock_preserved']:raise AssertionError('Parent or clock changed')
        rows.append(row);write(a.out/'INCREMENTAL.json',rows)
        del s,world;gc.collect()
    write(a.out/'MEDICIONES.json',{'schema':'CPC9.return.causal.result.v1','status':'MEASURED','configuration':config,
        'source_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'rows':rows,
        'trace':trace,'coverage':'Moore27 on both declared paths149–216 plus critical endpoint frames; no claim of global unique message genealogy',
        'source_file_unchanged':hashlib.sha256(snapshot.read_bytes()).hexdigest()==before_file})
    print(json.dumps({'case':a.case,'status':'MEASURED','conditions':[{'condition':r['condition'],'equal':r['full_final_equal'],'parent_unchanged':r['parent_unchanged']}for r in rows]}))
if __name__=='__main__':main()
