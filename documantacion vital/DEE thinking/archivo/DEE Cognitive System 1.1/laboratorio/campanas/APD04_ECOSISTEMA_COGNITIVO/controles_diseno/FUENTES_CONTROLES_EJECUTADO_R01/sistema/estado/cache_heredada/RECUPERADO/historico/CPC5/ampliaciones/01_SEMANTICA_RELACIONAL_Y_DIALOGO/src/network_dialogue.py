"""One native Runtime carrying 1..4 finite bidirectional-role candidates.

Only geometry/interfaces are reused from the frozen V3 dialogue. No learned
Runtime, snapshot, or response is copied when preparing the population.
"""
from pathlib import Path
import argparse
import json
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
from dialogue import geometry, interfaces_for, move
from common import ROOT, identity, put, sha, interface, record, receipt, digest, operational, local_context, until

N=67
KEY='cpc5.extension.network_dialogue.v1'


def prepare(case):
    import dee_thinking as d
    m=case['participants']
    if type(m) is not int or m not in (1,2,3,4):raise ValueError('1..4 candidate participants required')
    stagger=bool(case.get('staggered_roles'))
    if stagger and m!=2:raise ValueError('The longitudinal role variation was frozen for two participants only')
    loops=[];ports=[];sources={};overlaps=[]
    translations=case.get('translations',[[15*i,0,16*i] for i in range(m)])
    if len(translations)!=m:raise ValueError('One fixed translation per loop required')
    for i in range(m):
        spec=geometry({'translation':translations[i],'access_shift':44,'context_z':1,'name_interval':61,
                       'late_sender':stagger and i==1})
        # In loop i, Ui requests/uses context; U(i+1) supplies learned response.
        loop={'index':i,'requester':'U'+str(i+1),'responder':'U'+str((i+1)%m+1),'geometry':spec,
              'prefix':f'L{i}.','source_teaching_tick':134 if stagger and i==1 else 0}
        loops.append(loop)
        for p in interfaces_for(spec):
            c=p.channel;q=(c.injection_site.x,c.injection_site.y,c.injection_site.z);dr=(c.direction.dx,c.direction.dy,c.direction.dz)
            name=loop['prefix']+p.name
            ports.append(interface(name,q,dr,state=c.state,semantic=c.semantic))
            if q in sources:overlaps.append({'site':q,'first':sources[q],'second':name,'scope':'Shared injection site; Runtime admission, not last-write-wins, decides actual inputs'})
            sources[q]=name
    recipe=d.OrganizationRecipe.research(N,[],0);recipe.interfaces=ports;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    world=d.OrganizationalWorld.create(recipe)
    actors=[]
    for i in range(m):
        actors.append({'id':'U'+str(i+1),'context_and_backup_in_loop':i,'response_relays_and_backup_in_loop':(i-1)%m,
                       'components':6,'scope':'Prepared distributed two-role candidate, not evidence of unified agency or an internally recurrent policy'})
    spec={'N':N,'loops':loops,'actors':actors,'prepared_material_sites':0,'source_site_overlaps':overlaps,
          'physical_components':6*m,'loop_translations':translations,
          'scope':'Native response/context couplings across participants in one Runtime. Actor role assignment is prepared and distributed across loop regions; its two functions are not asserted to form a renewable universal individual.'}
    state={'version':1,'tick':0,'geometry':spec,'calls':[],
           'scope':'Prepared interfaces, actor bindings, operative input requests only; no expected outputs or learned answer map.'}
    world.runtime.set_snapshot_metadata(KEY,json.dumps(state,separators=(',',':')))
    return world,spec,state


def submit(world,state,port,payload,tick,probe=False,origin='CURRENT_EXTERNAL_EXPERIENCE'):
    if type(payload) is not int or not 0<=payload<=65535:raise ValueError('uint16 payload required')
    r=(world.probe if probe else world.submit)(port,payload,tick)
    state['calls'].append({'id':r.id,'port':port,'payload':payload,'requested_tick':tick,'call_tick':world.runtime.current_tick,
                           'operation':'probe' if probe else 'submit','origin':origin})
    return r.id


def commit(world,state):
    state['tick']=world.runtime.current_tick
    world.runtime.set_snapshot_metadata(KEY,json.dumps(state,separators=(',',':')))


def run_case(case,out):
    import dee_thinking as d
    out=Path(out);out.mkdir(parents=True,exist_ok=False);began=time.monotonic();engine=identity()
    world,spec,state=prepare(case);m=case['participants'];stagger=bool(case.get('staggered_roles'))
    actor_context=case.get('context_signs',[-1 if i%2==0 else 1 for i in range(m)])
    actor_memory=case.get('memory_loads',[[3,9+2*i] for i in range(m)])
    actor_context_loads=case.get('context_loads',[[5,11] for i in range(m)])
    queries=case.get('queries',[13]*m)
    if len(actor_context)!=m or any(s not in (-1,1) for s in actor_context):raise ValueError('One +/- context experience per actor')
    if any(len(x)!=m for x in (actor_memory,actor_context_loads,queries)):raise ValueError('One local history/query per actor required')
    horizon=338 if stagger else 204
    put(out/'CONFIG.json',{'case':case,'geometry':spec,'source_sha256':sha(__file__),
          'template_source_sha256':sha(Path(__file__).with_name('dialogue.py')),
          'criterion':'Record native transport/returned load and direction, transformed environmental banks, old/new backup availability and receipts. Increasing components/resources is separate from architecture advantage.',
          'horizon':horizon,'modalities':['EXPERIENCE_PROTOCOL','NATIVE_EVOLUTION','PASSIVE_OBSERVATION']})
    saved=[];rows=[];windows=[];encounters=[];edits=[]
    def save(label):
        commit(world,state);p=out/(label+'.deetsnap');world.save_snapshot(str(p))
        saved.append({'file':p.name,'sha256':sha(p),'physical':digest(world)})
    save('INITIAL_T0')
    for loop in spec['loops']:
        i=loop['index'];requester=i;responder=(i+1)%m;prefix=loop['prefix'];g=loop['geometry']
        for item in g['stages']+g['backups']:
            key=item['id'].removesuffix('.backup');is_context=key=='U1.context'
            pair=actor_context_loads[requester] if is_context else (actor_memory[responder] if key=='U2.memory' else [0,0])
            omitted=(not is_context and key=='U2.memory' and case.get('omit_memory_actor')==responder+1)
            if omitted:continue
            tick=0 if is_context else loop['source_teaching_tick']
            if key=='U1.context':report='plus' if actor_context[requester]>0 else 'minus'
            elif key=='U2.memory':report='plus'
            else:report='report'
            submit(world,state,prefix+item['id']+'.cue',pair[0],tick,origin='OPAQUE_LOCAL_CUE_EXPERIENCE')
            submit(world,state,prefix+item['id']+'.'+report,pair[1],tick,origin='CURRENT_LOCAL_DIRECTIONAL_EVENT')
        submit(world,state,prefix+'U1.request',queries[i],g['request_tick'],True,'HUMAN_INDUCED_NEIGHBOR_REQUEST')
        for bank in ('lower','upper'):
            submit(world,state,prefix+'environment.'+bank,7,g['bank_tick']-3,origin='EQUAL_ENVIRONMENTAL_BANK_OPPORTUNITY')
        if stagger:
            # Old contexts and the already taught first responder are used before
            # U1 acquires its response-side relation at134 in the opposite loop.
            for item in g['backups']:
                if item['id']=='U1.context.backup' or loop['source_teaching_tick']==0:
                    submit(world,state,prefix+item['id']+'.query',5,67,True,'FIRST_OLD_KNOWLEDGE_QUERY_BEFORE_ROLE_EXCHANGE')
        for item in g['backups']:
            submit(world,state,prefix+item['id']+'.query',5,335 if stagger else 201,True,'POST_COMMUNICATION_QUERY_WITHOUT_RETEACHING')
    commit(world,state)
    times={0,2,3,66,67,69,70,horizon-4,horizon-3,horizon-1,horizon}
    saved_ticks={3,54,55,69,70,75,horizon-4,horizon}
    for loop in spec['loops']:
        g=loop['geometry']
        times.update(range(g['request_tick']-1,g['bank_tick']+6))
        for item in g['stages']:times.update((item['time']-1,item['time']))
        saved_ticks.update((g['request_tick']+4,g['stages'][-1]['time']-1,g['stages'][-1]['time'],g['bank_tick']))
    if stagger:times.update((133,134,136,137));saved_ticks.update((70,133,137))
    intervention=case.get('message_intervention')
    if intervention:
        k=intervention['loop']
        if type(k) is not int or not 0<=k<m or intervention['kind'] not in ('remove','sham'):raise ValueError('A real loop and remove/sham required')
        edit_tick=spec['loops'][k]['geometry']['request_tick']+7;times.add(edit_tick);saved_ticks.add(edit_tick)
    else:edit_tick=None
    for tick in sorted(times):
        until(world,tick);commit(world,state)
        if tick==edit_tick:
            loop=spec['loops'][intervention['loop']];target=move(loop['geometry']['stages'][0]['target'],(1,1,0),2)
            before=record(world,target);parent=digest(world);op=operational(world);before_raw=world.runtime.raw_copy();before_clock=world.runtime.clock_copy()
            save('BEFORE_DIAGNOSTIC_T'+str(tick))
            edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*target);edit.raw=0 if intervention['kind']=='remove' else int(before['raw'])
            edit.label='Selective already emitted inter-actor response '+intervention['kind']
            child=world.diagnostic_fork([edit],True)
            count=sum(a!=b for a,b in zip(before_raw,child.runtime.raw_copy()))
            if count!=int(edit.raw!=int(before['raw'])) or child.runtime.clock_copy()!=before_clock:raise AssertionError('Undeclared network edit')
            if digest(world)!=parent or operational(world)!=op:raise AssertionError('Network diagnostic changed parent')
            edits.append({'tick':tick,'loop':loop['index'],'emitter':loop['responder'],'requester':loop['requester'],
                          'site':target,'before':before,'after':record(child,target),'RAW_sites_changed':count,'clock_sites_changed':0,
                          'parent_physical_and_operative_unchanged':True,'kind':intervention['kind'],'modality':'DIAGNOSTIC_FORK'})
            world=child;commit(world,state)
        per_loop={}
        for loop in spec['loops']:
            g=loop['geometry'];sample={x['id']:record(world,x['target']) for x in g['stages']}
            sample.update({x['id']:record(world,x['hub']) for x in g['backups']})
            sample.update({'bank.'+bank:record(world,q) for bank,q in g['banks'].items()})
            for stage_index,item in enumerate(g['stages']):
                if tick>=item['time']:
                    directions=[(1,1,0)] if stage_index==0 else ([(0,1,0)] if stage_index==1 else ([(-1,0,0)] if stage_index==2 else [(-1,-1,1),(-1,1,1)]))
                    for dr in directions:sample[item['id']+'.nominal_segment.'+str(dr)]=record(world,move(item['target'],dr,tick-item['time']))
                if tick in (item['time']-1,item['time']):
                    windows.append({'loop':loop['index'],'requester':loop['requester'],'responder':loop['responder'],
                                    'component':item['id'],'phase':'pre' if tick<item['time'] else 'post','tick':tick,
                                    'target':item['target'],'Moore26_plus_center':local_context(world,item['target'])})
                if tick==item['time']:
                    encounters.append({'loop':loop['index'],'requester':loop['requester'],'responder':loop['responder'],
                                       'component':item['id'],'tick':tick,'physical':record(world,item['target']),
                                       'coverage':'Exact prepared encounter and local pre/post context; nominal free segments sampled, no unique ancestry assigned after untraced transformation.'})
            if tick in (g['bank_tick']-1,g['bank_tick']):
                for bank,q in g['banks'].items():windows.append({'loop':loop['index'],'component':'environment.'+bank,
                          'phase':'pre' if tick<g['bank_tick'] else 'post','tick':tick,'target':q,'Moore26_plus_center':local_context(world,q)})
            per_loop[str(loop['index'])]=sample
        rows.append({'tick':tick,'loops':per_loop})
        if tick in saved_ticks:save('T'+str(tick))
        if tick in saved_ticks:put(out/'PROGRESS.json',{'last_tick':tick,'rows':rows,'encounters':encounters,'edits':edits})
    calculations=[]
    for loop in spec['loops']:
        i=loop['index'];g=loop['geometry'];requester=i;responder=(i+1)%m
        bank_row=next(x for x in rows if x['tick']==g['bank_tick'])['loops'][str(i)]
        late_row=rows[-1]['loops'][str(i)]
        expected_direction=actor_context[requester]
        # External post-trajectory comparison only. No expected values entered a
        # protocol, observer, decoder, message, or participant metadata.
        reference=queries[i]+sum(actor_memory[responder])+sum(actor_context_loads[requester])+7
        actual_banks={k:v for k,v in bank_row.items() if k.startswith('bank.')}
        matches=[k for k,v in actual_banks.items() if v['active'] and v['s_reg']==reference and v['direction']==[0,expected_direction,1]]
        calculations.append({'loop':i,'requester':loop['requester'],'responder':loop['responder'],
             'bank_tick':g['bank_tick'],'banks':actual_banks,'full_history_additive_reference':reference,
             'reference_formula':'request + two independently acquired local relation loads + environmental7, after native directional routing',
             'full_history_direction_reference':[0,expected_direction,1],'matches_full_history_reference':matches,
             'backup_readouts':{k:v for k,v in late_row.items() if k.endswith('.backup')},
             'scope':'Reference is evaluation only; missing/altered-history controls need not match it. This is not a semantic depth score.'})
    result={'schema':'CPC5.extension.network_dialogue.measurements.v1','case':case,'identity':engine,
            'code_sha256':sha(__file__),'template_source_sha256':sha(Path(__file__).with_name('dialogue.py')),
            'geometry':spec,'inputs':state['calls'],'receipts':[receipt(world,x['id']) for x in state['calls']],
            'rows':rows,'encounter_windows':windows,'encounters':encounters,'calculations':calculations,
            'diagnostic_edits':edits,'checkpoints':saved,'final_physical':digest(world),'final_operative':operational(world),
            'modality':'DIAGNOSTIC_FORK' if edits else 'EXPERIENCE_PROTOCOL + NATIVE_EVOLUTION',
            'resources':{'N':N,'Runtime':1,'basic_buffer_bytes':32*N**3,'top_level_candidates':m,'physical_components':6*m,
                         'input_calls':len(state['calls']),'API_probes':sum(c['operation']=='probe' for c in state['calls']),'native_ticks':horizon,
                         'prepared_material_sites':0,'training_and_query_information':'Per-actor private histories; costs scale with population, not an equal-inventory advantage comparison'},
            'status':'MEASURED','elapsed_seconds':time.monotonic()-began,
            'scope':'Physically shared native request-response loops with prepared distributed role assignments. Each actor has request/context and response/routing components; no adaptive routing, spontaneous question, universal renewable mind, or superiority from larger scalar output asserted.'}
    put(out/'MEASUREMENTS.json',result)
    print(json.dumps({'id':case['id'],'seconds':result['elapsed_seconds'],
                      'banks':[{'loop':x['loop'],'matches':x['matches_full_history_reference'],'banks':[(k,v['s_reg'],v['direction']) for k,v in x['banks'].items()]} for x in calculations]}),flush=True)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    cfg=json.loads(a.config.read_text(encoding='utf-8'));a.out.mkdir(parents=True,exist_ok=True);index=[]
    for case in cfg['cases']:
        path=a.out/case['id']/'MEASUREMENTS.json'
        if path.exists():
            r=json.loads(path.read_text(encoding='utf-8'))
            if r['case']!=case or r['code_sha256']!=sha(__file__):raise RuntimeError('Cannot reuse changed case/source')
        else:r=run_case(case,path.parent)
        index.append({'id':case['id'],'file':str(path.relative_to(ROOT)),'sha256':sha(path),'calculations':r['calculations'],
                      'resources':r['resources'],'elapsed_seconds':r['elapsed_seconds']})
        put(a.out/'INDEX.json',{'configuration':cfg,'cases':index})


if __name__=='__main__':main()
