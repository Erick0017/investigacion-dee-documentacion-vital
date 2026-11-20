"""Native replenished opportunity and counterflow, explicitly fixed control.

Neither source is learned or an autonomous uncertainty classifier. This family
tests whether a prepared internal source can keep presenting a physical access
opportunity, and whether zero-load directional context suppresses its passage.
"""
from pathlib import Path
import argparse,json,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import identity,put,sha,record,digest,operational,local_context


def prepare_geometry(mode='none',translation=(0,0,0),n=67):
    import dee_thinking as d
    if n!=67 or mode not in ('none','counterflow','sham','same_direction'):raise ValueError('Finite declared controller mode')
    add=lambda q:tuple((q[i]+translation[i])%n for i in range(3))
    source=add((20,20,20));counter=add((20,36,26 if mode=='sham' else 20));gate=add((20,30,20))
    placements=[]
    for q,load,direction,role in [(source,7,(0,1,0),'Fixed internal replenished opportunity')]+([] if mode=='none' else [(counter,0,(0,1,0) if mode=='same_direction' else (0,-1,0),'Fixed zero-load counterflow context')]):
        p=d.InitialPlacement();p.site=d.Coordinate(*q);p.raw=d.pack_record(6100,load,*direction,4);p.clock=23;p.role=role;placements.append(p)
    return {'placements':placements,'interfaces':[],'geometry':{'N':n,'mode':mode,'source':source,'counter_source':counter,'gate':gate,
        'outlet':add((20,32,20)),'local_meeting':add((20,28,20)),
        'interpretive_contract':'Prepared source/opposing context, not acquired availability or learned attention; positive-Y active carrier is an opportunity, not automatically a semantic question.'}}


def run(case,out):
    import dee_thinking as d
    out=Path(out);out.mkdir(parents=True,exist_ok=False);start=time.monotonic();engine=identity()
    prep=prepare_geometry(case['mode'],tuple(case.get('translation',[0,0,0])));g=prep['geometry']
    recipe=d.OrganizationRecipe.research(67,prep['placements'],0);recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    w=d.OrganizationalWorld.create(recipe);rows=[];windows=[];snaps=[]
    put(out/'CONFIG.json',{'case':case,'geometry':g,'source_sha256':sha(__file__),
        'horizon':100,'criterion':'Current raw +Y opportunity at gate/outlet per exact tick; count eligible ticks, not independent samples'})
    for tick in range(101):
        w.run_until(tick)
        row={'tick':tick,**{k:record(w,g[k]) for k in ('source','counter_source','gate','outlet','local_meeting')}};rows.append(row)
        if tick in (7,8,9,10,11,12,13,14,15,66,67,68,99,100):windows.append({'tick':tick,'meeting':local_context(w,g['local_meeting']),'gate':local_context(w,g['gate'])})
        if tick in (0,15,67,100):
            p=out/f'T{tick}.deetsnap';w.save_snapshot(str(p));snaps.append({'file':p.name,'sha256':sha(p),'physical':digest(w)})
        if tick in (15,67,100):put(out/'INCREMENTAL.json',{'last_complete_tick':tick,'rows':rows})
    decoded=[r['tick'] for r in rows if r['gate']['active'] and r['gate']['direction']==[0,1,0]]
    result={'schema':'CPC7.recurrent_opportunity.measurements.v1','case':case,'engine':engine,'geometry':g,
        'rows':rows,'local_windows':windows,'snapshots':snaps,'positive_Y_gate_ticks':decoded,
        'positive_Y_outlet_ticks':[r['tick'] for r in rows if r['outlet']['active'] and r['outlet']['direction']==[0,1,0]],
        'calculations':{'gate_eligible_ticks_10_to100':sum(t>=10 for t in decoded),'denominator_ticks':91,'independent_preparations':1},
        'final_physical':digest(w),'final_operative':operational(w),'host_inputs_after_T0':[],
        'host_RAW_clock_writes_after_T0':[],'elapsed_seconds':time.monotonic()-start,
        'scope':'Native renewal/inhibition calibration only. A directional stream is not by itself acquired meaning, detection of incomplete information or an independently selected query.'}
    put(out/'MEASUREMENTS.json',result);print(json.dumps({'id':case['id'],'gate_ticks':result['calculations']['gate_eligible_ticks_10_to100'],'seconds':result['elapsed_seconds']}),flush=True);return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);index=[]
    for case in json.loads(a.config.read_text(encoding='utf-8-sig'))['cases']:
        out=a.out/case['id'];r=json.loads((out/'MEASUREMENTS.json').read_text(encoding='utf-8')) if (out/'MEASUREMENTS.json').exists() else run(case,out)
        index.append({'id':case['id'],'calculations':r['calculations'],'evidence':str((out/'MEASUREMENTS.json').resolve()),'sha256':sha(out/'MEASUREMENTS.json')});put(a.out/'INDEX.json',{'cases':index})

if __name__=='__main__':main()
