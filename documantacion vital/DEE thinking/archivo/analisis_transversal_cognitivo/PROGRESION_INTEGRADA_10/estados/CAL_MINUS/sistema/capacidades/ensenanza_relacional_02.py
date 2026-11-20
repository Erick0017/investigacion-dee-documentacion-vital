"""Shared post-event physical signal method for temporal and path relations.

Experimental system layer only. The geometry/word transducer is prepared;
native event encounters must supply Y/Z and the later cue supplies X/Z.
The +Y query cannot supply the missing X marker in the no-cue control.
"""
from pathlib import Path
import sys
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from capacidades import espanol_funcional_01 as e

def prepare(a,*,frame,mode='relative_path',origin=(38,50,8)):
    if mode not in('relative_path','event_order')or not frame.isascii()or not frame.replace('_','').isalnum():raise ValueError('Explicit finite relational frame/mode required')
    if len(origin)!=3 or any(type(v)is not int or not 0<=v<67 for v in origin):raise ValueError('Declared N67 physical origin required')
    g=e.prepare(a);frames=g.setdefault('relational_words_v2',{})
    if frame in frames:
        entry=frames[frame]
        if entry['mode']!=mode or entry['origin']!=list(origin):raise ValueError('Existing lived frame cannot be relabelled or relocated')
        return entry
    path=Path(__file__).resolve().parents[1]/'organizaciones/cpc9/front_relations/src'
    if str(path)not in sys.path:sys.path.insert(0,str(path))
    from tiled_order_parallel import component
    _,old=component(origin=tuple(origin));ports={};banks=[]
    def port(role,site,v,state=1,lead=0):
        name='EF01.RW2.'+frame+'.'+role
        if name in a.world.runtime.channel_names:raise ValueError('Relational channel collision')
        ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*e.move(site,v,-lead));ch.direction=d.Direction(*v);ch.state=state;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True
        p=d.InterfaceSpec();p.name=name;p.channel=ch;a.world.declare_interface(p);return name
    ports['A']=port('A',origin,(1,1,1),6043);ports['A_positions']={}
    if mode=='relative_path':
        for k in(-5,-3,-1,1,3,5):ports['A_positions'][str(k)]=port('A_position_'+str(k),e.move(origin,(1,1,1),k),(1,1,1),6043)
    ports['B']=[]
    for row in old['b_ports']:
        ports['B'].append({'delta':row['delta'],'on':port('B_'+str(row['delta']),row['site'],(-1,1,0),6201+row['delta']),
            'off':port('B_off_'+str(row['delta']),e.move(row['site'],(0,1,0),18),(-1,1,0),6201+row['delta'])})
    for b in old['surfaces']:
        k=b['delta'];hub=list(b['hub'])
        if mode=='relative_path'and k>0:hub=e.move(hub,(0,1,1),k)
        word=('más cerca del patrón'if k>0 else'más lejos del patrón')if mode=='relative_path'else('A antes de B'if k>0 else'A después de B')
        banks.append({'id':b['id'],'parameter':k,'word':word,'hub':hub,'effect':e.move(hub,(1,1,0),6),
            'cue':port(b['id']+'.cue',hub,(1,0,-1),lead=3),'query':port(b['id']+'.query',hub,(0,1,0),lead=3),
            'use':port(b['id']+'.use',e.move(hub,(1,1,0),6),(-1,0,0),lead=3)})
    entry={'schema':'DCS1.1.EF01.relational_word_method.r2','origin':list(origin),'mode':mode,'ports':ports,'banks':banks,'experiences':[],
        'phase':13,'used':False,'prepared':'Fixed six-carrier B physical reference pattern, frame, candidate recording/read/use paths, and fixed Spanish translation.',
        'acquired':'Only event-derivedY/Z plus later X/Z signal encounter qualifies; pure event, pure cue and +Y query separately lack the complete[1,1,0] signature.',
        'scope':'Relative flight-path geometry with simultaneous emissions, not Euclidean distance/orientation learned generally.'if mode=='relative_path'else'Two declared current physical event shapes in the fixed frame, not universal temporal semantics.'}
    frames[frame]=entry;a.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g));return entry

def experience(a,*,frame,parameter=3,a_load=3,b_load=3,signal=True,delay=0,event_a=True,event_b=True,offroute=False,additional=False):
    g=e.prepare(a)
    if frame not in g.get('relational_words_v2',{}):raise ValueError('Prepare a relational frame first')
    entry=g['relational_words_v2'][frame]
    if entry['used']:raise ValueError('Post-use protocol not validated')
    if entry['experiences']and not additional:raise ValueError('Explicit additional experience required; no hidden reset')
    if parameter not in(-5,-3,-1,1,3,5)or a_load not in(3,5)or b_load not in(3,5)or delay not in(0,1):raise ValueError('Finite declared physical parameter/load domain')
    start=e.tick_at_or_after(a.tick,phase=0,lead=5);req=[]
    def send(name,payload,t):
        r=a.world.submit(name,payload,t);req.append({'port':name,'payload':payload,'tick':t,'id':int(r.id)})
    if entry['mode']=='relative_path':
        at=bt=start;ap=entry['ports']['A_positions'][str(parameter)]
    else:
        at=start+max(0,-parameter);bt=start+max(0,parameter);ap=entry['ports']['A']
    if event_a:send(ap,a_load,at)
    if event_b:
        for row in entry['ports']['B']:send(row['off'if offroute else'on'],b_load,bt)
    if signal:
        for b in entry['banks']:send(b['cue'],5,start+10+delay)
    a.run_until(start+12);pre={b['id']:e.obs(a,b['hub'])for b in entry['banks']}
    a.run_until(start+13+delay);post={b['id']:e.obs(a,b['hub'])for b in entry['banks']}
    entry['phase']=(start+13+delay)%67;entry['experiences'].append({'start':start,'actual_A_tick':at,'actual_B_tick':bt,'A_port':ap,'signal':signal,'additional':additional})
    a.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g))
    return {'ENTORNO':{'mode':entry['mode'],'actual_A_port':ap,'actual_A_tick':at,'actual_B_tick':bt,'A_load':a_load,'B_load_each':b_load,'six_B_reference_carriers':event_b},
        'ENTE':{'pre_signal':pre,'post_signal':post},'INSTRUMENTO':{'teacher_cue_all_six_banks':signal,'delay':delay,'current_physical_parameter':parameter,'requests':[e.receipt_at(a.world,r)for r in req]},
        'INTERPRETACION':'Candidate acquired relation-word association; the environmental position/time parameter is never fed as an answer to a decoder.'}

def query(a,*,frame,use=False,payload=7):
    g=e.prepare(a)
    if frame not in g.get('relational_words_v2',{}):raise ValueError('Unknown relational frame')
    entry=g['relational_words_v2'][frame]
    if not entry['experiences']or entry['used']:raise ValueError('Requires lived pre-use relational history')
    if type(payload)is not int or not 0<=payload<=65535 or type(use)is not bool:raise ValueError('Exact material resource required')
    target=e.tick_at_or_after(a.tick,phase=entry['phase'],lead=3);req=[]
    for b in entry['banks']:
        r=a.world.probe(b['query'],payload,target-3);req.append({'port':b['query'],'payload':payload,'tick':target-3,'id':int(r.id)})
        if use:
            r=a.world.submit(b['use'],11,target+3);req.append({'port':b['use'],'payload':11,'tick':target+3,'id':int(r.id)})
    a.run_until(target);readings={b['id']:e.obs(a,b['hub'])for b in entry['banks']}
    if use:a.run_until(target+6)
    outputs={b['id']:e.obs(a,b['effect']if use else b['hub'])for b in entry['banks']};qualified=[]
    for b in entry['banks']:
        if e.valid(outputs[b['id']],(0,1,0)if use else(1,1,0)):qualified.append({'text':b['word'],'bank':b['id']})
    entry['used']=use;entry['last_query_tick']=target;a.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g))
    return {'ENTE':{'read':readings,'output':outputs},'SPANISH_DECODED':qualified,'INSTRUMENTO':{'query_tick':target,'requests':[e.receipt_at(a.world,r)for r in req],'use':use},
        'INTERPRETACION':'Fixed physical signature translation of acquired carriers, no host comparison of positions/times and no target lookup. Historical multiple banks do not assert simultaneous truth in the current scene.'}
