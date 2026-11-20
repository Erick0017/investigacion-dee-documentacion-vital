"""Bounded two-compound native message bridge through one toroidal return.

The late source-content product of U1 is turned by a separately acquired relay
and reaches U2's comparator. U2 receives no external actual-consequence sensor.
Geometry/routing are designed; no callback reads a result and writes an input.
"""
from pathlib import Path
import argparse,json,sys,time,shutil
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,identity,interface,record,receipt,digest,operational,local_context,until
import order_memory,action_feedback,language
from action_feedback_access import deduplicate_requests
from architecture_screen import requests

DEPENDENCIES=('architecture_bridge.py','architecture_screen.py','common.py','order_memory.py','action_feedback.py','language.py','action_feedback_access.py')


def create():
    import dee_thinking as d
    first=order_memory.prepare_geometry()
    first_adapter=action_feedback.prepare_geometry(origin=first['geometry']['emission_site'])
    data=first_adapter['geometry']['branches']['right.mismatch']['sources']['Q']['information_site']
    relay=action_feedback.moved(data,(1,-1,0),7)
    second_hub=action_feedback.moved(relay,(1,0,1),52)
    second_origin=action_feedback.moved(second_hub,(1,-1,0),-10)
    second_center=action_feedback.moved(second_origin,(0,1,0))
    preparations=[];units={};ports=[];occupied={}
    for name,center in (('U1',(33,25,33)),('U2',second_center)):
        body=order_memory.prepare_geometry(center=center)
        adapter=action_feedback.prepare_geometry(origin=body['geometry']['emission_site'])
        names=language.prepare_geometry(adapter['geometry'])
        for p in body['placements']+adapter['placements']:
            q=(p.site.x,p.site.y,p.site.z)
            if q in occupied:raise ValueError('Initial prepared material overlap '+str((name,q,occupied[q])))
            occupied[q]=name;preparations.append(p)
        for item in body['interfaces']+adapter['interfaces']+names['interfaces']:
            c=item.channel;ports.append(interface(name+'.'+item.name,(c.injection_site.x,c.injection_site.y,c.injection_site.z),
                (c.direction.dx,c.direction.dy,c.direction.dz),c.state,c.semantic))
        units[name]={'body':body['geometry'],'adapter':adapter['geometry'],'language':names['geometry']}
    hub=action_feedback.moved(relay,(0,1,1),-27)
    for label,v in (('cue',(0,1,0)),('event',(0,0,1))):ports.append(interface('bridge.turn.'+label,action_feedback.moved(hub,v,-3),v))
    recipe=d.OrganizationRecipe.research(67,preparations,0);recipe.interfaces=ports;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    w=d.OrganizationalWorld.create(recipe)
    g={'schema':'CPC6.architecture_bridge.geometry.v1','N':67,'units':units,'bridge':{'source_site':data,'source_tick':23,
       'relay_site':relay,'relay_tick':30,'learned_relay_hub':hub,'relay_direction':[0,1,1],
       'second_hub':second_hub,'receive_tick':82,'second_cycle':{'comparison':82,'policy':86,'selection':87,'information':90,'late_read':100},
       'route_scope':'Specific U1.right.mismatch.Q information lane; no general native interlocutor selection claimed.',
       'recurrence':'U2 prepared rays and learned moving forecast/data are tested after one67tick toroidalreturn; not reset or retimed externally.'},
       'resources':{'prepared_support_sites':len(preparations),'interfaces':len(ports),'basic_buffer_bytes':32*67**3,
          'additional_exposures':'Two relay pulsesT0; separately acquiredU1sourceP/Q andU2sourceP/Q; no cloned learnedmemory.'}}
    return w,g


def capture(w,g,t):
    r={'tick':t,'units':{name:{'body':order_memory.observations(w,u['body']),'adapter':action_feedback.capture(w,u['adapter'])} for name,u in g['units'].items()}}
    b=g['bridge'];r['bridge_relay_site']=record(w,b['relay_site']);r['bridge_receiving_site']=record(w,b['second_hub'])
    if 23<=t<=30:r['predicted_path_candidate']=record(w,action_feedback.moved(b['source_site'],(1,-1,0),t-23))
    elif 30<t<=82:r['predicted_path_candidate']=record(w,action_feedback.moved(b['relay_site'],(1,0,1),t-30))
    return r


def stage_records(row,unit,field,directions):
    records=row['units'][unit]['adapter'][field];result={}
    for alias,r in records.items():
        if r['active'] and r['semantic']==1 and tuple(r['direction']) in directions:
            key=(tuple(r['site']),r['raw'],r['clock'])
            if key not in result:result[key]={'physical':r,'aliases':[]}
            result[key]['aliases'].append(alias)
    return list(result.values())


def run(case,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);start=time.monotonic();engine=identity();w,g=create();calls=[];aliases=[];rows=[];windows=[];snaps=[]
    def submit(items,label):
        norm=deduplicate_requests(w,items);aliases.append({'label':label,'call_tick':int(w.runtime.current_tick),**norm})
        for item in norm['requests']:
            value=getattr(w,item.get('kind','submit'))(item['port'],item['payload'],item['tick']);calls.append({**item,'id':int(value.id),'call_tick':int(w.runtime.current_tick)})
    def snap(t):
        path=out/(f'T{t}.deetsnap');w.runtime.set_snapshot_metadata('cpc6.architecture_bridge.v1',json.dumps({'geometry':g,'calls':calls,'tick':t},separators=(',',':')))
        w.save_snapshot(str(path));snaps.append({'file':path.name,'sha256':sha(path),'physical':digest(w)});put(out/'SNAPSHOTS.json',snaps)
    for name,u in g['units'].items():
        submit(requests(name,order_memory.experience('AB')),name+'.order_experience')
        submit(requests(name,[{'port':'order.read','payload':7,'tick':2,'kind':'probe','origin':'COMMON_READER'}]),name+'.read')
        values={'P':-1,'Q':1} if name=='U1' else {'P':1,'Q':-1}
        mode=case.get('U1_source_mode','paired') if name=='U1' else 'paired'
        submit(requests(name,action_feedback.source_protocol(u['adapter'],values,mode=mode)),name+'.source_experiences')
        submit(requests(name,action_feedback.query_protocol(u['adapter'])),name+'.same_initial_late_queries')
    if not case.get('relay_omitted'):
        submit([{'port':'bridge.turn.cue','payload':5,'tick':0,'kind':'submit','origin':'OPAQUE_RELAY_CUE'},
                {'port':'bridge.turn.event','payload':6,'tick':0,'kind':'submit','origin':'LOCAL_RELAY_EVENT'}],'bridge.relay_acquisition')
    put(out/'CONFIG.json',{'case':case,'geometry':g,'frozen_criterion':'U1action20/info23, bridgecandidate30/82, U2secondcyclepolicy86/action87/info90/late100. Allcandidateports captured; no response class supplied to Runtime.',
       'scope':'OneRuntime,twofreshphysicalcompounds. U2hasnoactualsensoreventfromhost. A secondcycleisphysicaltoroidalrecurrence, notsnapshotreset.'})
    snap(0)
    for t in range(106):
        until(w,t);rows.append(capture(w,g,t))
        if t==5:
            put(out/'PREDICCIONES.json',{'tick':5,'U1':rows[-1]['units']['U1']['body']['emission'],'U2':rows[-1]['units']['U2']['body']['emission'],
                'later_source_content_not_read_by_host':True,'actual_U1_requested_after_forecasts':True})
            submit(requests('U1',action_feedback.actual_protocol(g['units']['U1']['adapter'],-1)),'U1.current_actual')
        if t in (22,23,29,30,31,81,82,83,85,86,87,89,90,99,100):windows.append({'tick':t,'relay':local_context(w,g['bridge']['relay_site']),
            'receiver':local_context(w,g['bridge']['second_hub']),
            'U1_information':local_context(w,g['bridge']['source_site'])})
        if t in (5,23,30,82,90,100,105):snap(t)
        if t in (5,23,30,82,90,100,105):put(out/'INCREMENTAL.json',{'last_complete_tick':t,'rows':rows})
    at={r['tick']:r for r in rows};summary={}
    for unit,ticks in (('U1',{'selection':20,'information':23,'late_read':33}),('U2',g['bridge']['second_cycle'])):
        summary[unit]={}
        for stage,field,dirs in (('selection','actions',((0,0,1),(-1,-1,1))),('information','information',((-1,-1,0),(1,-1,0))),('late_read','late_queries',((-1,0,1),(1,0,1)))):
            summary[unit][stage]=stage_records(at[ticks[stage]],unit,field,dirs)
    result={'schema':'CPC6.architecture_bridge.case.v1','case':case,'engine':engine,'geometry':g,'rows':rows,'local_windows':windows,'snapshots':snaps,'summary':summary,
        'requests':[{**c,'receipt':receipt(w,c['id'])} for c in calls],'alias_groups':aliases,'final_physical':digest(w),'final_operative':operational(w),
        'preparations':1,'owner_runtimes':1,'host_output_to_input_callbacks':[],'host_RAW_clock_edits_after_T0':[],
        'coverage':'Fixed source,relay,receiving sites plus declared ballisticpathcandidates; latter notuniquegenealogycertificate. Moore27 atlistedboundaries.',
        'status':'MEASURED','elapsed_seconds':time.monotonic()-start}
    put(out/'MEASUREMENTS.json',result);print(json.dumps({'id':case['id'],'summary':summary,'bridge30':at[30]['bridge_relay_site'],'receiving82':at[82]['bridge_receiving_site']}),flush=True);return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf-8'));a.out.mkdir(parents=True,exist_ok=True)
    frozen=ROOT/'referencias/fuentes_congeladas'/cfg['source_cut'];frozen.mkdir(parents=True,exist_ok=False);hashes={}
    for name in DEPENDENCIES:
        source=Path(__file__).with_name(name);shutil.copy2(source,frozen/name);hashes[name]=sha(source)
    put(frozen/'SOURCE_MANIFEST.json',{'sources':hashes,'config_sha256':sha(a.config)})
    index=[]
    for case in cfg['cases']:
        r=run(case,a.out/case['id']);index.append({'id':case['id'],'summary':r['summary'],'evidence':str((a.out/case['id']/'MEASUREMENTS.json').relative_to(ROOT))})
        put(a.out/'INDEX.json',{'cases':index,'frozen_sources':str(frozen.relative_to(ROOT)),'source_hashes':hashes})
    final={name:sha(Path(__file__).with_name(name)) for name in DEPENDENCIES};put(a.out/'SOURCE_STABILITY.json',{'before':hashes,'after':final,'byte_exact':hashes==final});assert hashes==final


if __name__=='__main__':main()
