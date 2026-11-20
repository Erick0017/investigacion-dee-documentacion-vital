"""Finite one-Runtime specialist ensembles. No host arbitration or response table.

Every unit has independently acquired order memory, a physical discrepancy
adapter, its own data-source experiences and fixed native guards. Units coexist
in one torus, but no cross-unit cooperation or integrated intelligence is claimed.
"""
from pathlib import Path
import argparse,json,sys,time,shutil,traceback
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,identity,put,sha,interface,digest,operational,local_context
from integrated import Session
import order_memory,body_source,comparison_need,need_regulation_v3


def prepare(case):
    """Prepare every region before creation; reject overlapping initial RAW."""
    import dee_thinking as d
    placements=[];ports=[];geometry={};owners={};overlaps=[]
    for unit in case['units']:
        name=unit['id'];body=body_source.prepare_geometry(center=tuple(unit['center']),source_load=0)
        need=comparison_need.prepare_geometry(origin=body['geometry']['emission_site'],prefix=name+'.need')
        guard=need_regulation_v3.prepare_geometry(need['geometry'],mode='barrier')
        need['geometry']['regulation']=guard['geometry']
        newports=[]
        for p in body['interfaces']:
            ch=p.channel;q=ch.injection_site;dr=ch.direction
            newports.append(interface(name+'.'+p.name,(q.x,q.y,q.z),(dr.dx,dr.dy,dr.dz),ch.state,ch.semantic))
        newports+=need['interfaces']
        ps=body['placements']+need['placements']+guard['placements']
        for p in ps:
            q=(p.site.x,p.site.y,p.site.z)
            if q in owners:overlaps.append({'site':list(q),'first_owner':owners[q],'new_owner':name,'role':p.role})
            else:owners[q]=name
        placements+=ps;ports+=newports
        geometry[name]={'body':body['geometry'],'need':need['geometry'],'source_preparation':'zero-load preT0 source; no edits after creation',
                        'initial_placements':len(ps),'interfaces':len(newports)}
    names=[p.name for p in ports]
    if len(names)!=len(set(names)):raise ValueError('Duplicate fully prefixed interfaces')
    g={'schema':'CPC7.reference_specialist_ensemble.geometry.v1','units':geometry,'N':67,
       'classification':'REFERENCE_SPECIALIST_ENSEMBLE','preparations':1,'upperlevel_units':len(case['units']),
       'initial_placements':len(placements),'interfaces':len(ports),'overlaps':overlaps,
       'no_overwrite_policy':True,'base_buffers_bytes':32*67**3,
       'scope':'Coexisting specialists; integration and cross-unit communication are not supplied by this preparation.'}
    if overlaps:return None,g
    recipe=d.OrganizationRecipe.research(67,placements,0);recipe.interfaces=ports
    recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    return Session(d.OrganizationalWorld.create(recipe),g,identity=case['id']),g


def rename_body_requests(unit,requests):
    return [{**r,'port':unit+'.'+r['port']} for r in requests]


def readout(rows,unit):
    by={r['tick']:r['units'][unit] for r in rows}
    def selected(panel,kind):
        values=[]
        for key,o in panel.items():
            direction=o['direction']
            valid=o['active'] and o['semantic']==1 and direction[0] in (-1,1)
            if kind=='q':valid=valid and direction[1:]==[0,0]
            elif kind=='info':valid=valid and direction[1] in (-1,1) and direction[2]==0
            elif kind=='use':valid=valid and direction[1] in (-1,1) and direction[2]==1
            if valid:values.append({'panel_site':key,'record':o})
        return values
    q=selected(by[19]['need']['questions'],'q')
    information=selected(by[24]['need']['source_contacts'],'info')
    used=selected(by[29]['need']['later_use'],'use')
    return {'questions19':q,'information24':information,'use29':used,
            'order_emission5':by[5]['body']['emission'],
            'relational_delta5':by[5]['body']['delta'],'relational_delta72':by[72]['body']['delta'],
            'passive_relation_retained5_to72':by[5]['body']['delta']==by[72]['body']['delta'],
            'counts':{'q':len(q),'information':len(information),'use':len(used)}}


def run(case,out,config_sha):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);start=time.monotonic();engine=identity()
    s,g=prepare(case)
    put(out/'CONFIG.json',{'case':case,'geometry':g,'frozen_config_sha256':config_sha,'source_sha256':sha(__file__),
        'criterion':'Native X question at19; source-dependent X/Y information at24; physical X/Y/Z use at29; exact passive relation at72. No whole-network superiority criterion.',
        'horizon':72,'reserve_unit':'complete independently prepared world; multiple units and ticks are not independent world replicas'})
    for name in ('ensemble.py','comparison_need.py','need_regulation.py','need_regulation_v2.py','need_regulation_v3.py','body_source.py'):
        shutil.copyfile(Path(__file__).parent/name,out/name)
    if s is None:
        result={'case':case,'status':'BLOCKED_INITIAL_GEOMETRY_OVERLAP','geometry':g,'preparations':0,
                'attempted_worlds':1,'rows':[],'elapsed_seconds':time.monotonic()-start}
        put(out/'MEASUREMENTS.json',result);print(json.dumps({'id':case['id'],'status':result['status'],'overlaps':g['overlaps']}),flush=True);return result
    w=s.world
    for unit in case['units']:
        name=unit['id'];ng=g['units'][name]['need']
        s.stimulate(rename_body_requests(name,order_memory.experience(unit['history'])))
        s.stimulate([{'port':name+'.order.read','payload':7,'tick':2,'kind':'probe','origin':'COMMON_PREPARED_ORDER_READER'}])
        s.stimulate(comparison_need.source_protocol(ng,unit['source_value'],'paired'))
        s.stimulate(comparison_need.use_protocol(ng))
    rows=[];windows=[];snapshots=[]
    for tick in range(73):
        s.advance_to(tick)
        row={'tick':tick,'units':{name:{'body':order_memory.observations(w,ug['body']),
                                  'need':comparison_need.capture(w,ug['need'])} for name,ug in g['units'].items()}}
        # Prediction/emission is captured before injecting the current report.
        rows.append(row)
        if tick==5:
            for unit in case['units']:s.stimulate(comparison_need.actual_protocol(g['units'][unit['id']]['need'],unit['actual']))
        if tick in (4,5,14,15,18,19,20,23,24,28,29):
            windows.append({'tick':tick,'units':{name:{
                'body_center':local_context(w,ug['body']['center']),
                'comparison':{k:local_context(w,q) for k,q in ug['need']['comparison_hubs'].items()},
                'questions':{k:local_context(w,b['request_site']) for k,b in ug['need']['branches'].items()}}
                for name,ug in g['units'].items()}})
        if tick in (0,5,19,29,72):
            path=out/f'T{tick}.deetsnap';v=s.save(path);v['path']=path.name;snapshots.append(v)
            put(out/'INCREMENTAL.json',{'last_complete_tick':tick,'rows':rows,'requests':s.receipts()})
    panels={unit['id']:readout(rows,unit['id']) for unit in case['units']}
    receipts=s.receipts()
    result={'schema':'CPC7.reference_specialist_ensemble.measurements.v1','case':case,'engine':engine,'status':'MEASURED',
        'geometry':g,'preparations':1,'upperlevel_units':len(case['units']),'rows':rows,'panels':panels,
        'local_windows':windows,'snapshots':snapshots,'requests':receipts,'final_physical':digest(w),'final_operative':operational(w),
        'resources':{'N':67,'base_buffers_bytes':32*67**3,'initial_placements':g['initial_placements'],
            'interfaces':g['interfaces'],'requested_inputs':len(receipts),'requested_load':sum(r['payload'] for r in receipts)},
        'host_RAW_clock_writes_after_T0':[],'elapsed_seconds':time.monotonic()-start,
        'scope':'Resource expansion and coexistence screen, not matched-inventory advantage or native cooperation between upper-level units. Source states differ by declared experiences, not correct-answer feedback.'}
    put(out/'MEASUREMENTS.json',result)
    print(json.dumps({'id':case['id'],'status':'MEASURED','units':{u:p['counts'] for u,p in panels.items()},'seconds':result['elapsed_seconds']}),flush=True)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    config=json.loads(a.config.read_text(encoding='utf-8-sig'));a.out.mkdir(parents=True,exist_ok=True);index=[]
    for case in config['cases']:
        out=a.out/case['id'];target=out/'MEASUREMENTS.json'
        if target.exists():r=json.loads(target.read_text(encoding='utf-8'))
        else:
            try:r=run(case,out,sha(a.config))
            except Exception as e:
                out.mkdir(parents=True,exist_ok=True);r={'case':case,'status':'TECHNICAL_ERROR','error':str(e),'traceback':traceback.format_exc()}
                put(target,r);print(json.dumps({'id':case['id'],'status':'TECHNICAL_ERROR','error':str(e)}),flush=True)
        index.append({'id':case['id'],'status':r['status'],'preparations':r.get('preparations',0),'units':r.get('upperlevel_units',len(case['units'])),
                      'panels':r.get('panels',{}),'resources':r.get('resources',{}),'evidence':target.resolve().relative_to(ROOT).as_posix(),'sha256':sha(target)})
        put(a.out/'INDEX.json',{'classification':'REFERENCE_SPECIALIST_ENSEMBLE','cases':index})
    if any(x['status']=='TECHNICAL_ERROR' for x in index):raise SystemExit(1)

if __name__=='__main__':main()
