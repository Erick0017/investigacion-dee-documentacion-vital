"""Finite native request/response route, with experience-dependent turn/content.

The laboratory declares ports and current physical experiences.  Once requested,
all inter-participant messages and turns are produced by v27 in one Runtime.
Neither the session nor its renderer consults an expected-answer table.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, BASE, identity, put, sha, record, interface, receipt, digest, operational, until, local_context

N = 67
KEY = 'cpc5.extension.dialogue.v1'


def move(q, d, count=1):
    return tuple((q[i] + d[i] * count) % N for i in range(3))


def geometry(case):
    tr = case.get('translation', [0, 0, 0])
    if len(tr) != 3 or any(type(v) is not int for v in tr):
        raise ValueError('Three integer translations required')
    translate = lambda q: move(q, tr)
    # Successful full-history route is a physical reference, not a decoder.
    stages = [
        {'id': 'U2.memory', 'participant': 'U2', 'target': (30,20,8), 'time': 11,
         'direction': (0,1,0), 'train': ((-1,0,0),(1,1,0)), 'role': 'response acquired from local experience'},
        {'id': 'U2.turn1', 'participant': 'U2', 'target': (35,25,8), 'time': 16,
         'direction': (-1,0,0), 'train': ((0,-1,0),(-1,1,0)), 'role': 'zero-load acquired routing support'},
        {'id': 'U2.turn2', 'participant': 'U2', 'target': (35,30,8), 'time': 21,
         'direction': (-1,-1,0), 'train': ((-1,0,0),(0,-1,0)), 'role': 'zero-load acquired routing support'},
        {'id': 'U1.context', 'participant': 'U1', 'target': (30,30,8), 'time': 26,
         'direction': (0,-1,0), 'train': ((-1,0,0),(1,-1,0)), 'role': 'acquired context for using returned answer'},
    ]
    shift=case.get('access_shift',0)
    if shift not in (0,44):raise ValueError('Only original and full-context-lap access preparations were tested')
    context_z=case.get('context_z',0)
    if context_z not in (0,1):raise ValueError('Only planar and one common z context drift were tested')
    late=134 if case.get('late_sender') else 0
    if late and (shift!=44 or context_z!=1):raise ValueError('Longitudinal late sender requires validated common-lap3D access')
    stages[3]['direction']=(0,-1,context_z)
    stages[3]['train']=((-1,0,0),(1,-1,context_z))
    for stage in stages:
        stage['time']+=shift+late
        # Geometry is identical for opposite histories; experience selects a
        # current event, never a different interface or expected-answer map.
        reference=stage['direction']
        stage['target'] = translate(stage['target'])
        stage['hub'] = move(stage['target'], reference, -(stage['time']-3))
    backups=[]
    for stage,z in ((stages[0],40),(stages[3],52)):
        item=dict(stage);item['id'] += '.backup';item['role']='independently experienced retained support'
        item['hub'] = translate((50 if stage['id']=='U1.context' and context_z else 40,15,z));item['target']=item['hub'];item['time']=70
        backups.append(item)
    banks = {'lower':translate((25,25,8+5*context_z)), 'upper':translate((25,35,8+5*context_z))}
    name_hubs={'lower':move(banks['lower'],(0,-1,context_z),11),'upper':move(banks['upper'],(0,1,context_z),11)}
    name_interval=case.get('name_interval',67)
    if name_interval not in (61,67):raise ValueError('Only same-hub67 and trajectory-sensitive61 read interfaces were prepared')
    name_query_targets={bank:move(hub,(-1,-1 if bank=='lower' else 1,context_z),name_interval) for bank,hub in name_hubs.items()}
    return {'N':N, 'stages':stages, 'backups':backups, 'request_site':translate((25,20,8)),
            'request_tick':6+shift+late, 'request_direction':[1,0,0], 'banks':banks,
            'access_shift':shift,'context_z':context_z,'late_sender_tick':late,'bank_tick':31+shift+late,'name_hubs':name_hubs,
            'name_learning_tick':42+shift+late,'name_probe_tick':42+shift+late+name_interval,
            'name_interval':name_interval,'name_query_targets':name_query_targets,
            'participants': {'U1':{'functions':['request','context','use','retained backup'], 'component_ids':['U1.context','U1.context.backup']},
                             'U2':{'functions':['local experience','response','return routing','retained backup'], 'component_ids':['U2.memory','U2.turn1','U2.turn2','U2.memory.backup']}},
            'prepared_material_sites':0, 'translation':tr,
            'scope':'Two finite communicating candidate compounds. Geometry and routing opportunities are designed; memory content and directional effects are acquired by submitted experiences. Not autonomous selection of interlocutor.'}


def interfaces_for(spec):
    ports=[]
    for item in spec['stages']+spec['backups']:
        # Both report directions are always declared; history chooses a current event.
        if item['id'].startswith(('U2.memory','U1.context')):
            z=item['direction'][2]
            pairs=[('cue',(-1,0,0)),('plus',(1,1,z)),('minus',(1,-1,z))]
        else:
            pairs=[('cue',item['train'][0]),('report',item['train'][1])]
        for label,direction in pairs:
            ports.append(interface(item['id']+'.'+label,move(item['hub'],direction,-3),direction))
        if item in spec['backups']:
            ports.append(interface(item['id']+'.query',move(item['hub'],(-1,0,0),-3),(-1,0,0)))
    ports.append(interface('U1.request',spec['request_site'],(1,0,0)))
    for label,target in spec['banks'].items():
        ports.append(interface('environment.'+label,move(target,(1,0,0),-3),(1,0,0)))
    for label,target in spec.get('name_hubs',{}).items():
        ports.append(interface('form.N0.'+label,move(target,(-1,0,0),-3),(-1,0,0)))
    for label,target in spec.get('name_query_targets',{}).items():
        ports.append(interface('form.N0.query.'+label,move(target,(-1,0,0),-3),(-1,0,0)))
    return ports


class DialogueSession:
    """Physical state plus recipe/operative call receipts, never expected outputs."""
    def __init__(self, world, spec, state):
        self.world,self.spec,self.state=world,spec,state

    @classmethod
    def create(cls, case=None):
        import dee_thinking as d
        case=case or {};spec=geometry(case)
        recipe=d.OrganizationRecipe.research(N,[],0)
        recipe.interfaces=interfaces_for(spec);recipe.execution=d.TickOptions(d.Backend.LAZY,1)
        world=d.OrganizationalWorld.create(recipe)
        session=cls(world,spec,{'version':1,'tick':0,'geometry':spec,'calls':[],
                    'scope':'Operative ports and input receipts only; no targets, learned answers, teaching map, or rollout oracle'})
        session.commit();return session

    def commit(self):
        self.state['tick']=self.world.runtime.current_tick
        self.world.runtime.set_snapshot_metadata(KEY,json.dumps(self.state,separators=(',',':')))

    def submit(self, port, payload, tick, probe=False, origin='CURRENT_EXTERNAL_EVENT'):
        if type(payload) is not int or not 0<=payload<=65535:raise ValueError('uint16 payload required')
        if type(tick) is not int or not self.world.runtime.current_tick<=tick<=512:raise ValueError('Monotone finite tick required')
        if port not in {p.name for p in self.world.interfaces}:raise ValueError('Undeclared port')
        r=(self.world.probe if probe else self.world.submit)(port,payload,tick)
        self.state['calls'].append({'id':r.id,'port':port,'payload':payload,'requested_tick':tick,
                    'call_tick':self.world.runtime.current_tick,'operation':'probe' if probe else 'submit','origin':origin})
        self.commit();return r.id

    def experience(self, item, loads, tick=0, mode='paired', direction_sign=None):
        if mode not in ('paired','unpaired','omitted'):raise ValueError('paired/unpaired/omitted required')
        if mode=='omitted':return []
        sign=item['direction'][1] if direction_sign is None else direction_sign
        if sign not in (-1,0,1):raise ValueError('Current direction event must be -1/0/+1')
        label='plus' if sign>0 else 'minus'
        if not item['id'].startswith(('U2.memory','U1.context')):label='report'
        ids=[self.submit(item['id']+'.cue',loads[0],tick+(mode=='unpaired'),origin='OPAQUE_CUE_EXPERIENCE'),
             self.submit(item['id']+'.'+label,loads[1],tick,origin='CURRENT_DIRECTIONAL_CONSEQUENCE')]
        return ids

    def form(self,tick,payload=5,probe=False):
        """One fixed opaque form = two equal physical pulses, not a classifier."""
        if not self.spec.get('name_hubs'):raise ValueError('This older preparation has no predeclared form ports')
        prefix='form.N0.query.' if probe and self.spec.get('name_query_targets') else 'form.N0.'
        return [self.submit(prefix+bank,payload,tick,probe,
                'OPAQUE_FORM_QUERY' if probe else 'POST_NATIVE_OPAQUE_FORM_EXPOSURE') for bank in ('lower','upper')]

    def learn(self,participant,cue,report,direction,tick=0,mode='paired',include_backup=True):
        """Prepare physical experiences through logical interfaces, not coordinates.

        U2 contains the response relation, U1 contains context. Additional backup
        exposures are always explicit calls and never free copies.
        """
        if participant not in ('U1','U2') or direction not in (-1,1):raise ValueError('U1/U2 and direction +/-1 required')
        key='U1.context' if participant=='U1' else 'U2.memory'
        selected=[x for x in self.spec['stages']+self.spec['backups'] if x['id']==key or (include_backup and x['id']==key+'.backup')]
        return [identifier for item in selected for identifier in self.experience(item,[cue,report],tick,mode,direction)]

    def request(self,payload=13,tick=None):
        return self.submit('U1.request',payload,self.spec['request_tick'] if tick is None else tick,True,'HUMAN_INDUCED_PHYSICAL_REQUEST')

    def observe(self):
        return {'tick':self.world.runtime.current_tick,
                'banks':{name:record(self.world,q) for name,q in self.spec['banks'].items()},
                'name_hubs':{name:record(self.world,q) for name,q in self.spec.get('name_hubs',{}).items()},
                'name_query_targets':{name:record(self.world,q) for name,q in self.spec.get('name_query_targets',{}).items()},
                'backups':{x['id']:record(self.world,x['hub']) for x in self.spec['backups']}}

    def run_until(self,tick):
        until(self.world,tick);self.commit()

    def save(self,path):
        path=Path(path)
        if path.exists():raise FileExistsError(path)
        path.parent.mkdir(parents=True,exist_ok=True);self.commit();self.world.save_snapshot(str(path))
        return {'file':path.name,'sha256':sha(path),'physical':digest(self.world),'operative':operational(self.world)}

    @classmethod
    def load(cls,path):
        import dee_thinking as d
        world=d.OrganizationalWorld.load_snapshot(str(path));state=json.loads(world.runtime.snapshot_metadata(KEY))
        if state['version']!=1 or state['tick']!=world.runtime.current_tick or world.runtime.dimension!=N:raise ValueError('Snapshot identity mismatch')
        spec=state['geometry'];actual={p.name:p.channel for p in world.interfaces};expected=interfaces_for(spec)
        if set(actual)!={p.name for p in expected}:raise ValueError('Changed ports')
        for p in expected:
            a,b=actual[p.name],p.channel
            if ((a.injection_site.x,a.injection_site.y,a.injection_site.z),(a.direction.dx,a.direction.dy,a.direction.dz),a.state,a.semantic)!=((b.injection_site.x,b.injection_site.y,b.injection_site.z),(b.direction.dx,b.direction.dy,b.direction.dz),b.state,b.semantic):raise ValueError('Changed port field')
        for call in state['calls']:
            r=world.runtime.receipt(call['id'])
            if r is None or r.requested_tick!=call['requested_tick'] or list(r.channels)!=[call['port']]:raise ValueError('Lost operative receipt')
        return cls(world,spec,state)


def run_case(case,out):
    import dee_thinking as d
    out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.monotonic();engine=identity()
    session=DialogueSession.create(case);spec=session.spec
    modes=case.get('modes',{});loads=case.get('loads',{'U2.memory':[3,9],'U1.context':[5,11]})
    put(out/'CONFIG.json',{'case':case,'geometry':spec,'source_sha256':sha(__file__),
            'criterion':'Fixed physical fields and arrival windows; direction/content/history contrasts evaluated after trajectories. No expected value supplied to session.',
            'resources':{'Runtime':1,'N':N,'basic_buffer_bytes':32*N**3,'components':6,'top_entities':2,'prepared_material_sites':0},
            'horizon':338 if case.get('late_sender') else (204 if case.get('names') else (137 if spec.get('access_shift') else 70))})
    snapshots=[session.save(out/'INITIAL_T0.deetsnap')];trace=[];windows=[];messages=[];edits=[]
    for item in spec['stages']+spec['backups']:
        key=item['id'].removesuffix('.backup');pair=loads.get(key,[0,0])
        sign=case.get('emitter_sign',1) if key=='U2.memory' else (case.get('receiver_sign',-1) if key=='U1.context' else None)
        lesson_tick=134 if case.get('late_sender') and key!='U1.context' else 0
        session.experience(item,pair,tick=lesson_tick,mode=modes.get(key,'paired'),direction_sign=sign)
    if not case.get('omit_request',False):session.submit('U1.request',case.get('query',13),spec['request_tick'],True,'HUMAN_INDUCED_PHYSICAL_REQUEST')
    for label in spec['banks']:
        session.submit('environment.'+label,case.get('resource',7),spec['bank_tick']-3,False,'EQUAL_TWO_BANK_ENVIRONMENTAL_OPPORTUNITY')
    backup_query_tick=335 if case.get('late_sender') else (201 if case.get('names') else (134 if spec.get('access_shift') else 67))
    if case.get('late_sender'):
        session.submit('U1.context.backup.query',case.get('early_query',5),67,True,'OLD_KNOWLEDGE_QUERY_BEFORE_NEW_SENDER_LEARNING')
    for item in spec['backups']:
        session.submit(item['id']+'.query',case.get('late_query',5),backup_query_tick,True,'POST_COMMUNICATION_RETENTION_QUERY_WITHOUT_REPORT')
    if case.get('names'):
        mode=case.get('name_mode','paired')
        if mode not in ('paired','unpaired','omitted'):raise ValueError('Unknown name experience mode')
        if mode!='omitted':session.form(spec['name_learning_tick']-3+(mode=='unpaired'),case.get('name_payload',5))
        session.form(spec['name_probe_tick']-3,case.get('name_probe_payload',5),True)
    horizon=backup_query_tick+3
    contact_times=[x['time'] for x in spec['stages']]
    decision_ticks=set([0,2,3,spec['bank_tick'],spec['bank_tick']-1,spec['bank_tick']+1,backup_query_tick-1,backup_query_tick,horizon])
    for t in contact_times:decision_ticks.update((t-1,t,t+1))
    if case.get('late_sender'):decision_ticks.update((66,67,69,70,133,134,136,137))
    if case.get('names'):decision_ticks.update((spec['name_learning_tick']-1,spec['name_learning_tick'],spec['name_learning_tick']+1,spec['name_probe_tick']-1,spec['name_probe_tick'],spec['name_probe_tick']+1))
    saved_ticks={0,spec['request_tick']+4,spec['request_tick']+7,spec['stages'][-1]['time']-1,
                 spec['stages'][-1]['time'],spec['bank_tick'],spec['bank_tick']+5,backup_query_tick-1,horizon}
    if case.get('names'):saved_ticks.update((spec['name_learning_tick']-1,spec['name_learning_tick'],spec['name_probe_tick']))
    if case.get('late_sender'):saved_ticks.update((70,133,137))
    name_edit=case.get('name_intervention')
    if name_edit:
        if not case.get('names') or name_edit.get('bank') not in ('lower','upper') or name_edit.get('kind') not in ('remove','sham'):raise ValueError('Name edit requires bank lower/upper and remove/sham')
        decision_ticks.add(spec['name_learning_tick']+2);saved_ticks.add(spec['name_learning_tick']+2)
    # All external events are fixed before advancing; message readouts never cause callbacks.
    for tick in range(horizon+1):
        session.run_until(tick)
        if name_edit and tick==spec['name_learning_tick']+2:
            bank=name_edit['bank'];direction=(-1,-1 if bank=='lower' else 1,spec.get('context_z',0))
            target=move(spec['name_hubs'][bank],direction,2)
            before=record(session.world,target);context=local_context(session.world,target)
            main=digest(session.world);op=operational(session.world)
            snapshots.append(session.save(out/f'BEFORE_NAME_EDIT_T{tick}.deetsnap'))
            edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*target);edit.label='Selective already-acquired opaque-form carrier '+name_edit['kind']
            edit.raw=0 if name_edit['kind']=='remove' else int(before['raw'])
            priorraw=session.world.runtime.raw_copy();priorclock=session.world.runtime.clock_copy();child=session.world.diagnostic_fork([edit],True)
            if digest(session.world)!=main or operational(session.world)!=op:raise AssertionError('Name lesion changed parent')
            count=sum(a!=b for a,b in zip(priorraw,child.runtime.raw_copy()))
            if count!=int(edit.raw!=int(before['raw'])) or child.runtime.clock_copy()!=priorclock:raise AssertionError('Name lesion changed undeclared fields')
            session.world=child;session.commit()
            edits.append({'tick':tick,'site':target,'before':before,'after':record(child,target),'Moore27_before':context,
                          'Moore27_after':local_context(child,target),'RAW_sites_changed':count,'clock_sites_changed':0,
                          'parent_physical_and_operative_unchanged':True,'mode':'DIAGNOSTIC_FORK','kind':'name_'+name_edit['kind']})
        if tick==spec['request_tick']+7 and case.get('intervention'):
            target=move(spec['stages'][0]['target'],(1,1,0),2)
            before=record(session.world,target);main=digest(session.world);op=operational(session.world)
            edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*target);edit.label='Selective already-emitted U2 answer '+case['intervention']
            raw=int(before['raw'])
            if case['intervention']=='remove':raw=0
            elif case['intervention']=='direction':raw=d.pack_record(before['state'],before['s_reg'],1,-1,0,before['semantic'])
            elif case['intervention']!='sham':raise ValueError('remove/direction/sham only')
            edit.raw=raw;priorraw=session.world.runtime.raw_copy();priorclock=session.world.runtime.clock_copy()
            child=session.world.diagnostic_fork([edit],True)
            if digest(session.world)!=main or operational(session.world)!=op:raise AssertionError('Parent changed by diagnostic')
            count=sum(a!=b for a,b in zip(priorraw,child.runtime.raw_copy()))
            if count!=int(raw!=int(before['raw'])) or child.runtime.clock_copy()!=priorclock:raise AssertionError('Undeclared edit')
            session.world=child;session.commit()
            edits.append({'tick':tick,'site':target,'before':before,'after':record(child,target),'RAW_sites_changed':count,
                          'clock_sites_changed':0,'parent_physical_and_operative_unchanged':True,'mode':'DIAGNOSTIC_FORK','kind':case['intervention']})
        if tick in decision_ticks or spec['request_tick']-1<=tick<=spec['bank_tick']+5:
            samples={p['id']:record(session.world, p['target'] if tick<=spec['bank_tick']+5 else p['hub']) for p in spec['stages']+spec['backups']}
            samples.update({'bank.'+name:record(session.world,q) for name,q in spec['banks'].items()})
            samples.update({'form.N0.'+name:record(session.world,q) for name,q in spec.get('name_hubs',{}).items()})
            samples.update({'form_probe.N0.'+name:record(session.world,q) for name,q in spec.get('name_query_targets',{}).items()})
            # Exact moving segment along the designed full-history route. Divergences remain measured.
            for i,item in enumerate(spec['stages']):
                if tick>=item['time']:
                    direction=((1,1,0),(0,1,0),(-1,0,0),(-1,case.get('receiver_sign',-1),spec.get('context_z',0)))[i]
                    samples[item['id']+'.outgoing']=record(session.world,move(item['target'],direction,tick-item['time']))
            trace.append({'tick':tick,'samples':samples})
        for item in spec['stages']:
            if tick in (item['time']-1,item['time']):
                windows.append({'stage':item['id'],'tick':tick,'phase':'pre' if tick<item['time'] else 'post',
                                'target':item['target'],'center':record(session.world,item['target']),
                                'Moore26_plus_center':local_context(session.world,item['target'])})
            if tick==item['time']:
                messages.append({'participant':item['participant'],'component':item['id'],'tick':tick,
                                 'physical':record(session.world,item['target']),
                                 'coverage':'Every tick on designed request/return window sampled plus exact pre/post Moore27. Other intervals selective, unique ancestry not assigned from load/proximity.'})
        if tick in saved_ticks and tick!=0:snapshots.append(session.save(out/f'T{tick}.deetsnap'))
        if tick in decision_ticks:put(out/'PROGRESS.json',{'tick':tick,'trace':trace,'messages':messages,'edits':edits})
    result={'schema':'CPC5.extension.native_dialogue.v1','case':case,'identity':engine,'code_sha256':sha(__file__),
            'geometry':spec,'modality':'DIAGNOSTIC_FORK' if edits else 'EXPERIENCE_PROTOCOL + NATIVE_EVOLUTION',
            'inputs':session.state['calls'],'receipts':[receipt(session.world,c['id']) for c in session.state['calls']],
            'trace':trace,'encounter_windows':windows,'messages':messages,'diagnostic_edits':edits,
            'checkpoints':snapshots,'final_physics':digest(session.world),'final_operative':operational(session.world),
            'resources':{'Runtime':1,'components':6,'top_entities':2,'N':N,'basic_buffer_bytes':32*N**3,
                         'input_calls':len(session.state['calls']),'native_ticks':horizon},
            'host_RAW_clock_writes_after_T0':[] if not edits else edits,
            'elapsed_seconds':time.monotonic()-started,'status':'MEASURED',
            'scope':'Human-induced request. Learned finite moving associations; prepared routing/roles and two equal bank opportunities. Backups acquired by additional experiences. No native autonomous questioning, arbitrary dictionary, or unlimited dialogue claim.'}
    put(out/'MEASUREMENTS.json',result)
    print(json.dumps({'case_id':case['id'],'seconds':result['elapsed_seconds'],
                     'messages':[m['physical']['s_reg'] if m['physical']['active'] else None for m in messages],
                     'banks_at_contact':next(t['samples'] for t in trace if t['tick']==spec['bank_tick'])}),flush=True)
    return result


def screen(config,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);index=[]
    for case in config['cases']:
        target=out/case['id'];path=target/'MEASUREMENTS.json'
        if path.exists():
            r=json.loads(path.read_text(encoding='utf-8'))
            if r['case']!=case or r['code_sha256']!=sha(__file__):raise RuntimeError('Refuse changed-code case reuse')
        else:r=run_case(case,target)
        row={'id':case['id'],'file':str(path.relative_to(ROOT)),'sha256':sha(path),'elapsed_seconds':r['elapsed_seconds'],
             'messages':[m['physical'] for m in r['messages']],
             'banks_at_contact':{k:v for k,v in next(x for x in r['trace'] if x['tick']==r['geometry']['bank_tick'])['samples'].items() if k.startswith('bank.')},
             'name_readout':{k:v for k,v in next((x for x in r['trace'] if x['tick']==r['geometry']['name_probe_tick']),{'samples':{}})['samples'].items() if k.startswith(('form.','form_probe.'))},
             'retention_final':{k:v for k,v in r['trace'][-1]['samples'].items() if k.endswith('.backup')}}
        index.append(row);put(out/'INDEX.json',{'configuration':config,'cases':index})
    return index


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--continue-snapshot',type=Path);a=p.parse_args()
    if a.continue_snapshot:
        case=json.loads(a.config.read_text(encoding='utf-8'));session=DialogueSession.load(a.continue_snapshot)
        out=a.out;out.mkdir(parents=True,exist_ok=False);before=digest(session.world);preop=operational(session.world)
        for item in case['inputs']:session.submit(item['port'],item['payload'],item['tick'],True,'OTHER_PROCESS_NEW_QUERY')
        captured=[]
        for tick in sorted(set(case.get('read_ticks',[])+[case['until']])):
            session.run_until(tick);captured.append(session.observe())
        state=session.save(out/'CONTINUED.deetsnap')
        put(out/'CONTINUATION.json',{'parent':str(a.continue_snapshot),'parent_sha256':sha(a.continue_snapshot),
                 'before':before,'operative_before':preop,'after':state,'observations':captured,'readouts':{p['id']:record(session.world,p['hub']) for p in session.spec['backups']},
                 'inputs':session.state['calls'],'receipts':[receipt(session.world,c['id']) for c in session.state['calls']]})
    else:screen(json.loads(a.config.read_text(encoding='utf-8')),a.out)


if __name__=='__main__':main()
