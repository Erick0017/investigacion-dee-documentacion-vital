"""Finite physical comparison -> R14-derived source policy -> acquired data.

This module returns preparation elements for ONE owner Runtime. It does not
read U0 to select an interface or calculate an error. All possible lanes exist
before T0; an actual consequence is duplicated on two declared sensor lanes.
"""
from pathlib import Path
import argparse
import json
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,identity,interface,record,receipt,digest,operational,local_context,until


def moved(q,v,k=1,n=67):return tuple((int(q[i])+int(v[i])*k)%n for i in range(3))


def prepare_geometry(*,n=67,origin=(33,24,33),emission_tick=5,distance=10):
    """Return placements/interfaces/JSON geometry, never construct a Runtime.

    Contract incoming U0 record: semantic1, positive state, direction(s,-1,0),
    arriving at origin at emission_tick. Its load is not read by this builder.
    """
    import dee_thinking as d
    if n!=67 or emission_tick!=5 or distance!=10:raise ValueError('First CPC6 feedback cut is N67, emission5, distance10')
    origin=tuple(origin)
    if len(origin)!=3 or any(type(x) is not int for x in origin):raise ValueError('Three integer origin coordinates')
    placements=[];ports=[];occupied={};shared=[];hubs={};branches={};codecs={};late={}
    compare=emission_tick+distance;write=compare+4;select=write+1;info=select+3;read=info+10
    def place(q,load,dr,role):
        q=tuple(q);raw=d.pack_record(1,load,*dr,1)
        if q in occupied:
            if occupied[q]['raw']!=raw:raise ValueError('Conflicting initial adapter placement '+str(q))
            shared.append({'site':q,'existing':occupied[q]['role'],'shared':role});return
        p=d.InitialPlacement();p.site=d.Coordinate(*q);p.raw=raw;p.clock=0;p.role=role;placements.append(p)
        occupied[q]={'raw':raw,'role':role}
    def arrival(target,tick,dr,load,role):place(moved(target,dr,-tick,n),load,dr,role)
    for s in (-1,1):
        lane='left' if s<0 else 'right';hub=moved(origin,(s,-1,0),distance,n);hubs[lane]=hub
        for c in (-1,1):
            dr=(-c,0,1);name=f'feedback.actual.{lane}.{"plus" if c>0 else "minus"}'
            ports.append(interface(name,moved(hub,dr,-4,n),dr))
        for dx in (0,s):
            key=f'{lane}.{"match" if dx==0 else "mismatch"}'
            compare_direction=(dx,-1,1);policy_site=moved(hub,compare_direction,4,n)
            normalizer=(1,1,-1) if dx==0 else (-dx,0,-1)
            arrival(policy_site,write,normalizer,11,'Prepared finite R14 reflected-Y policy normalizer '+key)
            branches[key]={'lane':lane,'sign_reference':s,'comparison_direction_reference':compare_direction,
                           'policy_site':policy_site,'normalizer':normalizer,'sources':{}}
            for source,policy,action in (('P',(1,0,0),(0,0,1)),('Q',(0,-1,0),(-1,-1,1))):
                query_site=moved(policy_site,policy,1,n)
                arrival(query_site,select,(-1,0,1),17,'Prepared symmetric source query '+key+'.'+source)
                information=moved(query_site,action,3,n)
                branch={'query_site':query_site,'policy_direction':policy,'action_direction':action,
                        'information_site':information}
                branches[key]['sources'][source]=branch
                for v in (-1,1):
                    value='positive' if v>0 else 'negative';parts=[]
                    vectors=[(v,-1,-1)] if source=='P' else ([(0,0,-1)] if v<0 else [(1,0,-1),(1,0,0)])
                    for j,dr in enumerate(vectors):
                        # Data rays are learned by real paired cue/event inputs
                        # at0. Each candidate branch costs its own exposure.
                        hub_data=moved(information,dr,-(info-3),n)
                        if source=='P':pair=((0,-1,0),(v,0,-1))
                        elif dr==(0,0,-1):pair=((-1,0,0),(1,0,-1))
                        else:pair=((0,-1,0),(1,1,dr[2]))
                        base=f'feedback.source.{key}.{source}.{value}.{j}'
                        for label,direction in zip(('cue','event'),pair):ports.append(interface(base+'.'+label,moved(hub_data,direction,-3,n),direction))
                        parts.append({'base':base,'source':source,'value_direction':v,'part':j,'direction':dr,
                                      'hub':hub_data,'loads':[5,18+j],
                                      'scope':'One separately acquired current environmental-data carrier, not a free clone or a computed correct action'})
                    codecs[key+'.'+source+'.'+value]=parts
                    late_target=moved(information,(v,-1,0),10,n)
                    late_name=f'feedback.late.{key}.{source}.{value}'
                    ports.append(interface(late_name,moved(late_target,(0,1,1),-3,n),(0,1,1)))
                    late[late_name]={'site':late_target,'information_site':information,'value_direction':v,
                                     'source':source,'branch':key,'request_tick':read-3,'read_tick':read,
                                     'scope':'Common physical query of updated information carrier; unselected source rays differ in z and/or y'}
    g={'schema':'CPC6.action_feedback.geometry.v1','N':n,'origin':origin,'emission_tick':emission_tick,
       'ticks':{'comparison':compare,'policy':write,'selection':select,'information':info,'late_request':read-3,'late_read':read},
       'comparison_hubs':hubs,'branches':branches,'source_codecs':codecs,'late_queries':late,
       'prepared_material_sites':len(placements),'shared_identical_placements':shared,
       'prepared_function':'Finite reflected-Y comparison/R14 source controller with symmetric queries. Comparison, policy, action and received information are native state transitions, not host decisions.',
       'input_contract':'Incoming learned U0 output(s,-1,0). actual c is a current external observation encoded as(-c,0,+1), duplicated into two fixed lanes, never an error calculated by host.',
       'information_contract':'P/Q current contents use acquired directional source carriers taught at0; each physical opportunity receives separate exposures. Positive-Q code has two contributors and unequal codec cost.',
       'preservation_scope':'U0 order remains in its original body. Comparator dx0/s encodes match/mismatch; later information carries source value, not a permanent copy of the original participant/order tuple.'}
    return {'placements':placements,'interfaces':ports,'geometry':g}


def source_protocol(g,values=None,*,mode='paired',omit=()):
    values=values or {'P':1,'Q':-1}
    if set(values)!={'P','Q'} or any(v not in (-1,1) for v in values.values()):raise ValueError('Actual finite P/Q contents +/-1')
    if mode not in ('paired','unpaired'):raise ValueError('paired/unpaired source experience')
    entries=[]
    for key,parts in g['source_codecs'].items():
        source=parts[0]['source'];v=parts[0]['value_direction']
        if source in omit or v!=values[source]:continue
        for part in parts:
            entries.extend([{'port':part['base']+'.cue','payload':part['loads'][0],'tick':int(mode=='unpaired'),'kind':'submit','origin':'OPAQUE_CURRENT_SOURCE_CUE'},
                            {'port':part['base']+'.event','payload':part['loads'][1],'tick':0,'kind':'submit','origin':'CURRENT_SOURCE_DIRECTIONAL_OBSERVATION'}])
    return entries


def actual_protocol(g,c,payload=17):
    if c not in (-1,1):raise ValueError('Current actual consequence +/-1 required')
    return [{'port':f'feedback.actual.{lane}.{"plus" if c>0 else "minus"}','payload':payload,
             'tick':g['ticks']['comparison']-4,'kind':'submit','origin':'CURRENT_ACTUAL_CONSEQUENCE_DUPLICATED_FIXED_SENSOR'} for lane in ('left','right')]


def query_protocol(g,payload=7):
    return [{'port':name,'payload':payload,'tick':item['request_tick'],'kind':'probe','origin':'COMMON_LATE_INFORMATION_MEMORY_QUERY'} for name,item in g['late_queries'].items()]


def capture(world,g):
    return {'tick':world.runtime.current_tick,'comparison':{k:record(world,q) for k,q in g['comparison_hubs'].items()},
            'policies':{k:record(world,b['policy_site']) for k,b in g['branches'].items()},
            'actions':{k+'.'+source:record(world,p['query_site']) for k,b in g['branches'].items() for source,p in b['sources'].items()},
            'information':{k+'.'+source:record(world,p['information_site']) for k,b in g['branches'].items() for source,p in b['sources'].items()},
            'late_queries':{name:record(world,item['site']) for name,item in g['late_queries'].items()}}


def run_component(case,out):
    """Small learned-action component, not a replacement for ROOT's U0 MAIN."""
    import dee_thinking as d
    out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.monotonic();engine=identity()
    prep=prepare_geometry();g=prep['geometry'];ports=list(prep['interfaces']);origin=g['origin']
    for label,dr in (('cue',(0,-1,0)),('plus',(1,0,0)),('minus',(-1,0,0))):ports.append(interface('component.action.'+label,moved(origin,dr,-3),dr))
    recipe=d.OrganizationRecipe.research(67,prep['placements'],0);recipe.interfaces=ports;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    world=d.OrganizationalWorld.create(recipe);calls=[];rows=[];windows=[];snaps=[];edits=[]
    def save(t):
        p=out/(f'T{t}.deetsnap');world.save_snapshot(str(p));snaps.append({'file':p.name,'sha256':sha(p),'physical':digest(world)})
    save(0)
    entries=source_protocol(g,case.get('source_values'),mode=case.get('source_mode','paired'),omit=case.get('omit_sources',[]))
    if not case.get('actual_omitted'):entries+=actual_protocol(g,case.get('actual',1))
    entries+=query_protocol(g,case.get('late_payload',7))
    if not case.get('action_omitted'):
        entries += [{'port':'component.action.cue','payload':3,'tick':2,'kind':'submit','origin':'COMPONENT_LEARNED_ACTION_CUE'},
                    {'port':'component.action.'+('plus' if case.get('action_sign',1)>0 else 'minus'),'payload':4,'tick':2,'kind':'submit','origin':'COMPONENT_LEARNED_ACTION_DIRECTION_EVENT'}]
    for item in entries:
        r=getattr(world,item['kind'])(item['port'],item['payload'],item['tick']);calls.append({**item,'id':r.id,'call_tick':0})
    put(out/'CONFIG.json',{'case':case,'geometry':g,'source_sha256':sha(__file__),
                         'criterion':'Observe actual comparator, source policy, action, received data and later query fields. No terminal class supplied to participant.'})
    for tick in range(41):
        until(world,tick)
        row=capture(world,g);row['component_action_origin']=record(world,origin);rows.append(row)
        if tick in (4,5,14,15,18,19,20,22,23,32,33):
            windows.append({'tick':tick,'origin':local_context(world,origin),
                            'comparison':{k:local_context(world,q) for k,q in g['comparison_hubs'].items()},
                            'policy':{k:local_context(world,b['policy_site']) for k,b in g['branches'].items()}})
        if tick in (5,14,15,19,20,23,33,40):save(tick)
        if tick in (5,15,19,20,23,33,40):put(out/'INCREMENTAL.json',{'rows':rows,'last_tick':tick})
    at={r['tick']:r for r in rows};selected=[];received=[];late=[]
    for name,p in at[g['ticks']['selection']]['actions'].items():
        source=name.rsplit('.',1)[1];expected=(0,0,1) if source=='P' else (-1,-1,1)
        if p['active'] and p['direction']==list(expected):selected.append({'port':name,'source':source,'physical':p})
    for name,p in at[g['ticks']['information']]['information'].items():
        if p['active'] and p['direction'][0] in (-1,1) and p['direction'][1:]==[-1,0]:received.append({'port':name,'physical':p})
    for name,p in at[g['ticks']['late_read']]['late_queries'].items():
        if p['active'] and p['direction'][0] in (-1,1) and p['direction'][1:]==[0,1]:late.append({'port':name,'physical':p})
    result={'schema':'CPC6.action_feedback.component.v1','case':case,'engine':engine,'source_sha256':sha(__file__),
            'geometry':g,'calls':calls,'receipts':[receipt(world,c['id']) for c in calls],'rows':rows,'local_windows':windows,
            'snapshots':snaps,'selected_actions':selected,'received_information':received,'late_information_queries':late,
            'final_physical':digest(world),'external_operations':list(world.external_operations),'host_RAW_clock_writes_after_T0':[],
            'preparations':1,'scope':'Component uses a learned moving action7 formedat5, not the basal U0 under research. Finite prepared controller and acquired sources, no autonomous optimal-attention attribution.',
            'status':'MEASURED','elapsed_seconds':time.monotonic()-started}
    put(out/'MEASUREMENTS.json',result);print(json.dumps({'id':case['id'],'selected':[(x['source'],x['physical']['direction']) for x in selected],
               'received':[(x['port'],x['physical']['direction'],x['physical']['s_reg']) for x in received],
               'late':[(x['port'],x['physical']['direction'],x['physical']['s_reg']) for x in late]}),flush=True);return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    index=[]
    for case in json.loads(a.config.read_text(encoding='utf-8'))['cases']:
        target=a.out/case['id'];r=run_component(case,target)
        index.append({'id':case['id'],'source':str((target/'MEASUREMENTS.json').relative_to(ROOT)),
                      'selected':r['selected_actions'],'received':r['received_information'],'late':r['late_information_queries']})
        put(a.out/'INDEX.json',{'cases':index})


if __name__=='__main__':main()
