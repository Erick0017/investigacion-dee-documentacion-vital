"""Second and final bridge method: physically staged fresh U2, not recurrence.

U2 exists fromT0. Initial clocks and prepared-ray origins are declared then;
its new local experiences occurat60. U1's message is its only actual sensor.
"""
from pathlib import Path
import argparse,json,sys,time,shutil
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,identity,interface,receipt,digest,operational,local_context,until
import order_memory,action_feedback,language
from action_feedback_access import deduplicate_requests
from architecture_screen import requests
from architecture_bridge import capture,stage_records

DEPENDENCIES=('architecture_bridge_delayed.py','architecture_bridge.py','architecture_screen.py','common.py','order_memory.py','action_feedback.py','language.py','action_feedback_access.py')
DELAY=60


def prepare(*,late_support=False):
    import dee_thinking as d
    a1=action_feedback.prepare_geometry()
    data=a1['geometry']['branches']['right.mismatch']['sources']['Q']['information_site']
    relay=action_feedback.moved(data,(1,-1,0),7)
    second_hub=action_feedback.moved(relay,(1,0,1),45)
    origin=action_feedback.moved(second_hub,(1,-1,0),-10);center=action_feedback.moved(origin,(0,1,0))
    placements=[];ports=[];units={};occupied={};support_experiences=[]
    for name,c,delay in (('U1',(33,25,33),0),('U2',center,DELAY)):
        body=order_memory.prepare_geometry(center=c,phase=260-delay)
        adapter=action_feedback.prepare_geometry(origin=body['geometry']['emission_site'])
        names=language.prepare_geometry(adapter['geometry'])
        # A declared T0 preparation, not an edit of a living body's matter.
        for index,p in enumerate(adapter['placements']):
            r=d.decode_record(p.raw);q=(p.site.x,p.site.y,p.site.z)
            if name=='U2' and late_support:
                dr=(r.dx,r.dy,r.dz);relative_arrival=19 if 'normalizer' in p.role else 20
                target=action_feedback.moved(q,dr,relative_arrival)
                hub=action_feedback.moved(target,dr,-(relative_arrival-3))
                pair=((1,0,-1),(0,1,0)) if dr==(1,1,-1) else ((dr[0],1,0),(0,-1,dr[2]))
                if tuple((1 if pair[0][i]+pair[1][i]>0 else -1 if pair[0][i]+pair[1][i]<0 else 0) for i in range(3))!=dr:raise ValueError('Supportpairdoesnotrealizepreparedray')
                for label,v,load in (('cue',pair[0],5),('event',pair[1],r.s_reg-5)):
                    port=f'U2.support.{index}.{label}';ports.append(interface(port,action_feedback.moved(hub,v,-3),v))
                    support_experiences.append({'port':port,'payload':load,'tick':60,'kind':'submit','origin':'FIXED_SYMMETRIC_PREPARED_SUPPORT_EXPOSURE'})
            else:p.site=d.Coordinate(*action_feedback.moved(q,(r.dx,r.dy,r.dz),-delay))
        selected=body['placements']+([] if name=='U2' and late_support else adapter['placements'])
        for p in selected:
            q=(p.site.x,p.site.y,p.site.z)
            if q in occupied:raise ValueError('Prepared T0material collision '+str((q,name,occupied[q])))
            occupied[q]=name;placements.append(p)
        for item in body['interfaces']+adapter['interfaces']+names['interfaces']:
            p=item.channel;ports.append(interface(name+'.'+item.name,(p.injection_site.x,p.injection_site.y,p.injection_site.z),(p.direction.dx,p.direction.dy,p.direction.dz),p.state,p.semantic))
        adapter['geometry']['ticks']={k:v+delay for k,v in adapter['geometry']['ticks'].items()}
        body['geometry']['emission_tick']+=delay
        units[name]={'body':body['geometry'],'adapter':adapter['geometry'],'language':names['geometry'],'experience_onset':delay}
    relay_hub=action_feedback.moved(relay,(0,1,1),-27)
    for label,v in (('cue',(0,1,0)),('event',(0,0,1))):ports.append(interface('bridge.turn.'+label,action_feedback.moved(relay_hub,v,-3),v))
    recipe=d.OrganizationRecipe.research(67,placements,0);recipe.interfaces=ports;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    w=d.OrganizationalWorld.create(recipe)
    g={'schema':'CPC6.architecture_bridge_delayed.geometry.v1','N':67,'units':units,
       'bridge':{'source_site':data,'source_tick':23,'relay_site':relay,'relay_tick':30,'learned_relay_hub':relay_hub,
          'second_hub':second_hub,'receive_tick':75,'second_cycle':{'comparison':75,'policy':79,'selection':80,'information':83,'late_read':93}},
       'support_experiences':support_experiences,
       'preparation':{'U2phase':200,'U2experience_onset':60,'late_symmetric_support':late_support,
          'U2prepared_ray_origin_change':'BeforeT0, minus60*declared direction, modulo67, OR independently paired supportpulsesT60; all candidates supplied equally.',
          'support_sites':len(placements),'basic_buffer_bytes':32*67**3},
       'scope':'Second bounded method. Fresh U2 learns later in same world; nohistoricalmemory copied. Fixed message route chosen bydesigner, notnativeinterlocutorselection.'}
    return w,g


def run(case,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);start=time.monotonic();w,g=prepare(late_support=case.get('late_support',False));engine=identity();calls=[];aliases=[];rows=[];windows=[];snaps=[]
    def submit(items,label):
        normalized=deduplicate_requests(w,items);aliases.append({'operation':label,'call_tick':int(w.runtime.current_tick),**normalized})
        for r in normalized['requests']:
            v=getattr(w,r.get('kind','submit'))(r['port'],r['payload'],r['tick']);calls.append({**r,'id':int(v.id),'call_tick':int(w.runtime.current_tick)})
    def snap(t):
        path=out/(f'T{t}.deetsnap');w.runtime.set_snapshot_metadata('cpc6.architecture_bridge_delayed.v1',json.dumps({'geometry':g,'requests':calls,'tick':t},separators=(',',':')))
        w.save_snapshot(str(path));snaps.append({'file':path.name,'sha256':sha(path),'physical':digest(w)});put(out/'SNAPSHOTS.json',snaps)
    for name,u in g['units'].items():
        delay=u['experience_onset']
        history=case.get(name+'_history','AB')
        if history!='NONE':submit(requests(name,order_memory.experience(history,onset=delay,load=case.get(name+'_event_load',3))),name+'.order_experiences')
        submit(requests(name,[{'port':'order.read','payload':7,'tick':2+delay,'kind':'probe','origin':'COMMON_PHYSICAL_READER'}]),name+'.orderquery')
        values={'P':-1,'Q':1} if name=='U1' else {'P':1,'Q':-1}
        mode=case.get(name+'_source_mode','paired')
        sources=action_feedback.source_protocol(u['adapter'],values,mode=mode)
        submit(requests(name,[{**r,'tick':r['tick']+delay} for r in sources]),name+'.data_experiences')
        # query_protocol already reads the shifted adapter ticks only indirectly:
        # late_query items themselves retain original perport relative tick30.
        late=action_feedback.query_protocol(u['adapter'],case.get(name+'_query_payload',7))
        submit(requests(name,[{**r,'tick':r['tick']+delay} for r in late]),name+'.latequeries')
    if not case.get('relay_omitted'):submit([{'port':'bridge.turn.cue','payload':5,'tick':0,'kind':'submit','origin':'RELAY_LOCAL_CUE'},
            {'port':'bridge.turn.event','payload':6,'tick':0,'kind':'submit','origin':'RELAY_LOCAL_EVENT'}],'relay.acquire')
    if g['support_experiences']:submit(g['support_experiences'],'U2.symmetric_support_exposures')
    put(out/'CONFIG.json',{'case':case,'geometry':g,'frozen_criterion':'U1learnedcontent23->relay30->U2comparison75/action80/data83/latequery93. Fixedcandidatefields, nohostcomputedmessage or error.',
       'time_difference':'U2localexperienceT60/61/read62, initialphase200; adapterpreparedrayorigins shifted60ticks BEFORET0. This is not the earlierreturncandidate.'})
    snap(0)
    for t in range(99):
        until(w,t);rows.append(capture(w,g,t))
        if t==5:
            put(out/'PREDICCIONES.json',{'forecast5':rows[-1]['units']['U1']['body']['emission'],'target_tick':15,'actual_not_requested_yet':True})
            submit(requests('U1',action_feedback.actual_protocol(g['units']['U1']['adapter'],-1)),'U1.actual_sensor')
        if t in (22,23,29,30,64,65,74,75,76,78,79,80,82,83,92,93):windows.append({'tick':t,'relay':local_context(w,g['bridge']['relay_site']),
            'receiver':local_context(w,g['bridge']['second_hub'])})
        if t in (5,23,30,59,65,75,83,93,98):snap(t)
        if t in (5,23,30,59,65,75,83,93,98):put(out/'INCREMENTAL.json',{'last_tick':t,'rows':rows})
    at={r['tick']:r for r in rows};summary={}
    for name,ticks in (('U1',{'selection':20,'information':23,'late_read':33}),('U2',g['bridge']['second_cycle'])):
        summary[name]={stage:stage_records(at[ticks[stage]],name,field,dirs) for stage,field,dirs in (
            ('selection','actions',((0,0,1),(-1,-1,1))),('information','information',((-1,-1,0),(1,-1,0))),('late_read','late_queries',((-1,0,1),(1,0,1))))}
    r={'schema':'CPC6.architecture_bridge_delayed.case.v1','case':case,'engine':engine,'geometry':g,'rows':rows,'local_windows':windows,'snapshots':snaps,
       'requests':[{**r,'receipt':receipt(w,r['id'])} for r in calls],'alias_groups':aliases,'summary':summary,
       'final_physical':digest(w),'final_operative':operational(w),'owner_runtimes':1,'preparations':1,'host_output_to_input_callbacks':[],
       'host_RAW_clock_edits_after_T0':[],'status':'MEASURED','elapsed_seconds':time.monotonic()-start,
       'coverage':'Fixedcandidateports+receiving/relayareas everytick; projectedpathcandidate is notcertifiedgenealogy.'}
    put(out/'MEASUREMENTS.json',r);print(json.dumps({'id':case['id'],'summary':summary,'relay30':at[30]['bridge_relay_site'],'receiver75':at[75]['bridge_receiving_site']}),flush=True);return r


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf-8'));a.out.mkdir(parents=True,exist_ok=True)
    frozen=ROOT/'referencias/fuentes_congeladas'/cfg['source_cut'];frozen.mkdir(parents=True,exist_ok=False);hashes={}
    for name in DEPENDENCIES:
        path=Path(__file__).with_name(name);shutil.copy2(path,frozen/name);hashes[name]=sha(path)
    put(frozen/'SOURCE_MANIFEST.json',{'sources':hashes,'config_sha256':sha(a.config)});index=[]
    for case in cfg['cases']:
        r=run(case,a.out/case['id']);index.append({'id':case['id'],'summary':r['summary'],'evidence':str((a.out/case['id']/'MEASUREMENTS.json').relative_to(ROOT))});put(a.out/'INDEX.json',{'cases':index,'frozen_sources':str(frozen.relative_to(ROOT))})
    after={name:sha(Path(__file__).with_name(name)) for name in DEPENDENCIES};put(a.out/'SOURCE_STABILITY.json',{'before':hashes,'after':after,'byte_exact':hashes==after});assert hashes==after


if __name__=='__main__':main()
