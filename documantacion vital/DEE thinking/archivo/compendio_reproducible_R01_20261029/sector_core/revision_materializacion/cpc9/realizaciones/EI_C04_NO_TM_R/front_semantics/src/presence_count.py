"""Contact-presence normalization using native gradients, never a host count.

Each real contact gives a variable positive material operand. A prepared native
reader of load7 emits a fixed load7 only along the contact branch's X direction;
without that operand it remains active zero-direction. Symmetric emissions
meet and sum natively. Resources/calibration are explicit, not learned rules.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation, exact_receipt
from dee_thinking.persistence import encode_metadata, decode_metadata, save_world_snapshot, load_world_snapshot
from relaciones.contact_cardinality import prepare as prepare_contact, move
from count_sign.session import port

KEY='CPC9.presence_normalized_contact_count.v3'


def prepare(case):
    recipe, cg = prepare_contact({k:case[k] for k in ('contacts','actor_state','medium_state','actor_load','unit_load') if k in case} | {'regulation':'branch_onpath'})
    initial=list(recipe.placements);ports=list(recipe.interfaces);normalizers=[]
    def fixed(q, role):
        p=d.InitialPlacement();p.site=d.Coordinate(*q);p.raw=d.pack_record(1,0,0,0,0,4);p.clock=0;p.role=role;initial.append(p)
    step=case.get('normalizer_step',1)
    if step not in(1,2):raise ValueError('Only two declared geometries, each separateT0')
    for name, branch in cg['branches'].items():
        sign=branch['sign'];reference=move(branch['base'],(sign,1,0),step);center=move(reference,(sign,0,0));prefix='presence.'+name+'.'
        for x in(-1,1):
            for y,z in((-1,-1),(1,1)):
                fixed(move(center,(x,y,z)),'Prepared zero-load passive comparator support')
        # Active zero is deliberately OFF the emitted +/-X line, not a wall at
        # its first destination. It supplies an existence anchor, no gradient.
        fixed(move(center,(sign,1,0)),'Prepared active-zero off-axis comparison operand')
        if case.get('retention_guards',True):
            off=12 if case.get('guard_geometry')=='off_path'else 0
            fixed(move(reference,(off,6,0)),'Prepared absorption of old variable teacher after first native normalization; not external deletion')
            fixed(move(center,(4*sign,off,4)),'Prepared interception of diagonal no-contact reader product, matched fixed resource')
        fv=(-sign,0,0);ports.extend((port(prefix+'format',move(reference,fv,-3),fv),port(prefix+'reader',center,(0,0,1))))
        normalizers.append({'name':name,'sign':sign,'reference_site':reference,'center':center,
                            'formatter_port':prefix+'format','reader_port':prefix+'reader',
                            'expected_mobile_direction':[sign,0,0]})
    collector=[25,20+step,20]
    for name,tick,load,vector in(('record',10,5,(0,0,1)),('query1',77,7,(0,1,0)),('query2',144,7,(0,0,-1))):
        ports.append(port('presence.'+name,move(collector,vector,-3),vector))
    sites=[(p.site.x,p.site.y,p.site.z)for p in initial]
    if len(sites)!=len(set(sites)):raise ValueError('Prepared material collision')
    recipe.placements=initial;recipe.interfaces=ports
    g={'schema':KEY,'N':67,'normalizer_step':step,'retention_guards':case.get('retention_guards',True),'guard_geometry':case.get('guard_geometry','on_path'),'ticks':{'reference':5+step,'normalized_output':6+step,'collector':10,'queries':[77,144]},'contact':cg,'normalizers':normalizers,'collector':collector,
       'resources':{'initial_materials':len(initial),'interfaces':len(ports),'normalizer_readers':2,'load_per_reader':7,'format_cue':5,'queries':2,'load_per_query':7,'basic_buffers_bytes':32*67**3},
       'prepared':'Two fixed presence comparisons against active-zero off-axis anchors, emitters each supplied7, symmetric convergence and fixed cue/query timings. No abstract number rule learned.',
       'history':'Actualcontactroutes determine whether positive variable operands arrive. Same inputs/readers supplied in all histories. No Pythonobservedcount or target is read.',
       'scope':'Contactevent count atfixedtwoopportunities with positivecontactmass, N67finite; testactor/mediumdose robustness, not unlimited cardinality or semanticONE/TWO by default.'}
    recipe.options={KEY:encode_metadata(g)}
    return recipe,g


class PresenceCountSession:
    def __init__(self,world,geometry,requests=None):self.world=world;self.geometry=deepcopy(geometry);self.requests=deepcopy(requests)if requests is not None else[]
    @classmethod
    def create(cls,case):r,g=prepare(case);return cls(d.OrganizationalWorld.create(r),g)
    @property
    def tick(self):return int(self.world.runtime.current_tick)
    def input(self,name,payload,tick,probe=False):
        rr=(self.world.probe if probe else self.world.submit)(name,payload,tick);self.requests.append({'id':int(rr.id),'port':name,'payload':payload,'tick':tick,'probe':probe})
    def curriculum(self,normalize=True,guard=True):
        if self.tick!=0:raise ValueError('Fresh curriculum only')
        if guard:
            for name in('A','B'):self.input('counter.free.guard.'+name,0,6)
        for n in self.geometry['normalizers']:
            self.input(n['formatter_port'],0,self.geometry['ticks']['reference']-3)
            if normalize:self.input(n['reader_port'],7,self.geometry['ticks']['reference'],True)
        self.input('presence.record',5,7)
        self.input('presence.query1',7,74,True);self.input('presence.query2',7,141,True)
        self.input('extra.cue',5,100);self.input('extra.event',11,100);self.input('extra.query',9,167,True)
    def observe(self,q):return exact_observation(self.world.runtime.observe(d.Coordinate(*q)))
    def run_until(self,tick):
        self.world.run_until(tick);g=self.geometry
        return {'tick':self.tick,'normalizers':[dict(n,reference=self.observe(n['reference_site']),output=self.observe(n['center']))for n in g['normalizers']],
                'collector':self.observe(g['collector']),'extra':self.observe(g['contact']['extra'])}
    def receipts(self):return[{**r,'receipt':exact_receipt(self.world.runtime.receipt(r['id']))}for r in self.requests]
    def save(self,path):
        self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'geometry':self.geometry,'requests':self.requests,'tick':self.tick}));return save_world_snapshot(self.world,path,compress=True)
    @classmethod
    def load(cls,path):
        w,_=load_world_snapshot(path,max_bytes=512*1024**2);m=decode_metadata(dict(w.runtime.snapshot_metadata_entries)[KEY]);return cls(w,m['geometry'],m['requests'])
