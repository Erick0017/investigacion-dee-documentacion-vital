"""One-Runtime coexistence screen of fresh learned order/feedback compounds.

Each unit contains a fresh relative body and finite native action-feedback
controller with separately acquired environmental data. No unit output is read
to write another unit. Inter-unit cooperation is not assumed by co-location.
"""
from pathlib import Path
import argparse,json,sys,time,shutil
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,identity,interface,record,receipt,digest,operational,local_context,until
import order_memory,action_feedback,language
from action_feedback_access import deduplicate_requests

DEPENDENCIES=('architecture_screen.py','common.py','order_memory.py','action_feedback.py','language.py','action_feedback_access.py')
SHIFTS=((0,0,0),(0,0,20),(20,20,0),(20,20,20))


def translated(q,shift):return tuple((q[i]+shift[i])%67 for i in range(3))


def create(count):
    import dee_thinking as d
    if count not in (1,2,4):raise ValueError('Published finite screen supports1,2,4units')
    placements=[];ports=[];units={};occupied={};port_sites={}
    for i in range(count):
        label='U'+str(i+1);center=translated((33,25,33),SHIFTS[i]);body=order_memory.prepare_geometry(center=center)
        adapter=action_feedback.prepare_geometry(origin=body['geometry']['emission_site'])
        names=language.prepare_geometry(adapter['geometry'])
        for item in body['placements']+adapter['placements']:
            q=(item.site.x,item.site.y,item.site.z)
            if q in occupied:raise ValueError('Prepared material overlap across units '+str((label,q,occupied[q])))
            occupied[q]=label;placements.append(item)
        originals=body['interfaces']+adapter['interfaces']+names['interfaces']
        for item in originals:
            c=item.channel;q=(c.injection_site.x,c.injection_site.y,c.injection_site.z);v=(c.direction.dx,c.direction.dy,c.direction.dz)
            name=label+'.'+item.name;ports.append(interface(name,q,v,c.state,c.semantic));port_sites[name]={'site':q,'direction':v,'state':c.state,'semantic':c.semantic}
        units[label]={'body':body['geometry'],'adapter':adapter['geometry'],'language':names['geometry'],
           'center':center,'translation':SHIFTS[i],'prepared_support_sites':len(body['placements'])+len(adapter['placements']),
           'interfaces':len(originals),'composition':'Causal fresh relativebody -> comparison -> finitepolicy -> sourceuse -> receivedmemory, not an arbitrary label around independentmodules'}
    recipe=d.OrganizationRecipe.research(67,placements,0);recipe.interfaces=ports;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    world=d.OrganizationalWorld.create(recipe)
    geometry={'schema':'CPC6.architecture_screen.geometry.v1','N':67,'units':units,'declared_interfaces':port_sites,
       'resources':{'units':count,'prepared_support_sites':len(placements),'interfaces':len(ports),
          'basic_buffer_bytes':32*67**3,'resource_note':'Same Runtime buffer domain. Support/input/opportunity budgets grow perunit; no equalresource superiority inferred.'},
       'interunit_channel':'None intentionally installed in this screen; any crosstalk belongs to shared v27 geometry and is measured.'}
    return world,geometry


def requests(unit,values):return [{**r,'port':unit+'.'+r['port']} for r in values]


def capture(world,g):
    return {'tick':int(world.runtime.current_tick),'units':{name:{'body':order_memory.observations(world,u['body']),
            'adapter':action_feedback.capture(world,u['adapter'])} for name,u in g['units'].items()}}


def summarize(rows,g):
    at={r['tick']:r for r in rows};summary={}
    for name,u in g['units'].items():
        stages={}
        for stage,field,directions in (('selection','actions',((0,0,1),(-1,-1,1))),('information','information',((-1,-1,0),(1,-1,0))),('late_read','late_queries',((-1,0,1),(1,0,1)))):
            records=at[u['adapter']['ticks'][stage]]['units'][name]['adapter'][field];physical={}
            for alias,r in records.items():
                if r['active'] and r['semantic']==1 and tuple(r['direction']) in directions:
                    key=(r['tick'],tuple(r['site']),r['raw'],r['clock'])
                    if key not in physical:physical[key]={'physical':r,'aliases':[]}
                    physical[key]['aliases'].append(alias)
            stages[stage]=list(physical.values())
        summary[name]=stages
    return summary


def run(case,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.monotonic();engine=identity()
    world,g=create(case['units']);calls=[];aliases=[];rows=[];windows=[];snapshots=[];forecasts=[]
    def submit(items,label):
        normalized=deduplicate_requests(world,items);aliases.append({'call_tick':int(world.runtime.current_tick),'operation':label,**normalized})
        for item in normalized['requests']:
            result=getattr(world,item.get('kind','submit'))(item['port'],item['payload'],item['tick']);calls.append({**item,'id':int(result.id),'call_tick':int(world.runtime.current_tick)})
    def snap(t):
        path=out/(f'T{t}.deetsnap');world.runtime.set_snapshot_metadata('cpc6.architecture_screen.v1',json.dumps({'geometry':g,'calls':calls,'tick':t},separators=(',',':')))
        world.save_snapshot(str(path));snapshots.append({'file':path.name,'sha256':sha(path),'physical':digest(world)});put(out/'SNAPSHOTS.json',snapshots)
    for i,(name,u) in enumerate(g['units'].items()):
        history=('AB' if i%2==0 else 'BA') if not case.get('reverse_histories') else ('BA' if i%2==0 else 'AB')
        if not case.get('memory_omitted'):submit(requests(name,order_memory.experience(history,load=case.get('event_load',3))),name+'.acquire')
        submit(requests(name,[{'port':'order.read','payload':7,'tick':2,'kind':'probe','origin':'COMMON_READER'}]),name+'.read_order')
        if not case.get('source_omitted'):submit(requests(name,action_feedback.source_protocol(u['adapter'],case.get('source_values',{'P':1,'Q':-1}))),name+'.source_experiences')
        submit(requests(name,action_feedback.query_protocol(u['adapter'],case.get('query_payload',7))),name+'.late_queries')
    put(out/'CONFIG.json',{'case':case,'geometry':g,'frozen_criterion':'Exact active semantic1 fields at20,23,33. Physicalduplicateobserveraliases countedonce. Eachunit receives sameinputnumber and doses except declaredcontrol. Nativeforecast5 precedesactualrequest11.',
       'scope':'Coexistence/functional interference of integrated candidates, not demonstrated interunitdialogue. All prepared simultaneously inoneRuntime; multiplepreparationsnotmergedafterlearning.'})
    snap(0)
    for tick in range(41):
        until(world,tick);row=capture(world,g);rows.append(row)
        if tick==5:
            forecasts.append({'tick_emission':5,'target_tick':15,'units':{name:u['body']['emission'] for name,u in row['units'].items()},'source':'ENTE','actual_not_requested_yet':True});put(out/'PREDICCIONES.json',forecasts)
            if not case.get('actual_omitted'):
                for i,(name,u) in enumerate(g['units'].items()):
                    actual=(-1 if i%2==0 else 1) if not case.get('reverse_histories') else (1 if i%2==0 else -1)
                    submit(requests(name,action_feedback.actual_protocol(u['adapter'],actual)),name+'.current_actual')
        if tick in (4,5,14,15,19,20,22,23,32,33):windows.append({'tick':tick,'units':{name:{'body':local_context(world,u['body']['center']),'comparison':{key:local_context(world,q) for key,q in u['adapter']['comparison_hubs'].items()}} for name,u in g['units'].items()}})
        if tick in (5,23,33,40):snap(tick)
        if tick in (5,20,23,33,40):put(out/'INCREMENTAL.json',{'last_complete_tick':tick,'rows':rows})
    result={'schema':'CPC6.architecture_screen.case.v1','case':case,'engine':engine,'geometry':g,'rows':rows,'local_windows':windows,
      'calls':[{**q,'receipt':receipt(world,q['id'])} for q in calls],'alias_admission_groups':aliases,'predictions':forecasts,'snapshots':snapshots,
      'summary':summarize(rows,g),'final_physical':digest(world),'final_operative':operational(world),'elapsed_seconds':time.monotonic()-started,
      'preparations':1,'owner_runtimes':1,'individual_candidates':case['units'],'external_RAW_clock_edits_after_T0':[],
      'interunit_host_callbacks':[],'status':'MEASURED','coverage':'Allfixedcandidateports eachtick and Moore27listedboundaries; nogenealogyinventedacrossuncapturedsegments.'}
    put(out/'MEASUREMENTS.json',result);print(json.dumps({'id':case['id'],'summary':result['summary'],'seconds':result['elapsed_seconds']}),flush=True);return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    cfg=json.loads(a.config.read_text(encoding='utf-8'));a.out.mkdir(parents=True,exist_ok=True)
    frozen=ROOT/'referencias/fuentes_congeladas'/cfg['source_cut']
    frozen.mkdir(parents=True,exist_ok=False)
    hashes={}
    for name in DEPENDENCIES:
        source=Path(__file__).with_name(name);shutil.copy2(source,frozen/name);hashes[name]=sha(source)
    put(frozen/'SOURCE_MANIFEST.json',{'sources':hashes,'config_sha256':sha(a.config),'scope':'Exact code copied beforefirstnativeexecutionofthisscreen.'})
    index=[]
    for case in cfg['cases']:
        result=run(case,a.out/case['id']);index.append({'id':case['id'],'summary':result['summary'],'evidence':str((a.out/case['id']/'MEASUREMENTS.json').relative_to(ROOT))})
        put(a.out/'INDEX.json',{'cases':index,'frozen_sources':str(frozen.relative_to(ROOT)),'source_hashes':hashes})
    final={name:sha(Path(__file__).with_name(name)) for name in DEPENDENCIES}
    put(a.out/'SOURCE_STABILITY.json',{'before':hashes,'after':final,'byte_exact':hashes==final})
    assert hashes==final,'Sourcechangedwhileworkerexecuted; loadedcodecopyretained'


if __name__=='__main__':main()
