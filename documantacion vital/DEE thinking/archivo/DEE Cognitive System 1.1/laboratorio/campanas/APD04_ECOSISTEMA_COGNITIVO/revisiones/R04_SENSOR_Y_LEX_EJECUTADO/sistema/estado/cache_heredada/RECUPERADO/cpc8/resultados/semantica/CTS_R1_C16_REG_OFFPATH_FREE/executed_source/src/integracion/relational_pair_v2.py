"""New preT0 access representation, never a repair of an old MAIN.

First order read formatsY=0; a separate preserving reader later leaves it0.
Contact geometry follows that physical plane and a fixed zero-load guard
intercepts the unused opportunity in offpath worlds. Both memories still
contribute natively to the commonX/Zresponse, not a Python combination.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from .relational_pair import prepare,PairSession,move


def prepare_v2(**options):
    r,g=prepare(**options);n=67;contact_roles={'Current zero-load actuator','Common zero-load opportunity','Current medium'}
    placements=list(r.placements)
    for p in placements:
        if p.role in contact_roles:p.site=d.Coordinate(*move([p.site.x,p.site.y,p.site.z],(0,-26,0)))
    contact_fields=('hub','query_site','effect_site','renewed_site','renewed_effect')
    g['contact_base']=move(g['contact_base'],(0,-26,0));g['contact_join']=move(g['contact_join'],(0,-26,0))
    for p in g['contact'].values():
        for field in contact_fields:p[field]=move(p[field],(0,-26,0))
    g['common_join']=move(g['common_join'],(0,-26,0));interfaces=list(r.interfaces);by_name={p.name:p for p in interfaces}
    def change(name,site,vector):
        old=by_name[name];c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*vector);c.state=old.channel.state;c.semantic=old.channel.semantic
        c.allow_experience=old.channel.allow_experience;c.allow_probe=old.channel.allow_probe;p=d.InterfaceSpec();p.name=name;p.channel=c
        interfaces[interfaces.index(old)]=p;by_name[name]=p
    for p in list(interfaces):
        if p.name.startswith('contact.'):
            q=p.channel.injection_site;change(p.name,move([q.x,q.y,q.z],(0,-26,0)),[p.channel.direction.dx,p.channel.direction.dy,p.channel.direction.dz])
    for key,p in g['order'].items():
        target=p['query_site'];old=by_name[p['query_port']];c=d.ChannelSpec();c.name='order.repeat.'+key;c.injection_site=old.channel.injection_site;c.direction=old.channel.direction
        c.state=old.channel.state;c.semantic=old.channel.semantic;c.allow_experience=True;c.allow_probe=True;i=d.InterfaceSpec();i.name=c.name;i.channel=c;interfaces.append(i);by_name[i.name]=i;p['repeat_port']=i.name
        change(p['query_port'],move(target,(0,1,0),-3),(0,1,0))
    for key,p in g['joint_names'].items():
        sign=p['order_axis'];z=p['consequence_component'];use=move(g['common_join'],(sign,1,z),4);delivery=move(use,(sign,0,z),4);cue=(-sign,1,-z)
        p['use_site']=use;p['delivery_site']=delivery;p['name_cue_direction']=list(cue)
        change(p['use_port'],move(use,(0,-1,0),-3),(0,-1,0));change(p['name_port'],move(delivery,cue,-3),cue);change(p['query_port'],move(delivery,(0,0,1),-3),(0,0,1))
    if options.get('include_contact',True):
        q=move(g['contact_join'],(-1,0,1),8);guard=d.InitialPlacement();guard.site=d.Coordinate(*q);guard.raw=d.pack_record(1,0,0,0,0,4);guard.clock=0;guard.role='Prepared unused opportunity interception';placements.append(guard)
        g['unused_opportunity_guard']={'site':q,'load':0,'semantic':4,'modality':'FIXED_DESIGN_NOT_LEARNED_POLICY'}
    sites=[(p.site.x,p.site.y,p.site.z)for p in placements]
    if len(sites)!=len(set(sites)):raise ValueError('V2initial material overlap')
    g['representation_version']=2;g['resources']['initial_material_sites']=len(placements);g['resources']['interfaces']=len(interfaces)
    g['access_representation']='First+Yformats order into(s,0,+1), later+Zpreserves it. Native common206 combines with(0,+1,z), resource−Y210tests use, cue214normalizes toYmemory.'
    r.placements=placements;r.interfaces=interfaces;r.options={'CPC8R.relational_pair.geometry':encode_metadata(g)};r.domain=g['modality']+' '+g['access_representation']
    return r,g


class PairV2(PairSession):
    @classmethod
    def create(cls,identifier='PAIR_V2',**options):r,g=prepare_v2(**options);return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
    def curriculum(self,*,order='AB',order_name='paired',contact_name='paired',joint_name='paired',include_order=True,include_contact=True,extra_value=1):
        if self.tick!=0 or order not in('AB','BA')or extra_value not in(-1,1):raise ValueError('Fresh declared curriculum required')
        for mode in(order_name,contact_name,joint_name):
            if mode not in('paired','unpaired','omitted'):raise ValueError('Explicit cue condition')
        if include_order:
            self.input('order.'+order[0],3,0,origin='FIRST_CURRENT_EVENT');self.input('order.'+order[1],3,1,origin='SECOND_CURRENT_EVENT');self.input('order.read',7,2,'probe','COMMON_ORDER_READER')
            for p in self.geometry['order'].values():
                if order_name!='omitted':self.input(p['name_port'],5,8+int(order_name=='unpaired'),origin='POST_ORDER_OPAQUE_CUE')
                self.input(p['query_port'],7,28,'probe','FIRST_FORMATTING_ORDER_QUERY');self.input(p['repeat_port'],7,162,'probe','SECOND_PRESERVING_ORDER_QUERY')
        if include_contact:
            for p in self.geometry['contact'].values():
                if contact_name!='omitted':self.input(p['name_port'],5,6+int(contact_name=='unpaired'),origin='POST_CONTACT_OPAQUE_CUE')
                self.input(p['query_port'],5,73,'probe','CONTACT_SIGNAL_QUERY');self.input(p['use_port'],7,79,'probe','FIXED_CONTACT_USE_RESOURCE')
                self.input(p['renew_port'],5,142,'probe','RENEWED_CONTACT_QUERY');self.input(p['reuse_port'],7,146,'probe','FIXED_SECOND_CONTACT_USE_RESOURCE')
        self.input('extra.signal',5,100,origin='ADDITIONAL_RELATION_CUE');self.input('extra.event.'+('plus'if extra_value==1 else'minus'),11,100,origin='ADDITIONAL_CURRENT_EVENT');self.input('extra.signal',9,167,'probe','ADDITIONAL_RELATION_QUERY')
        for p in self.geometry['joint_names'].values():
            self.input(p['use_port'],7,207,'probe','ALL_CANDIDATE_COMMON_USE_OPPORTUNITIES')
            if joint_name!='omitted':self.input(p['name_port'],5,211+int(joint_name=='unpaired'),origin='LATER_ALL_CANDIDATE_JOINT_OPAQUE_CUE')
            self.input(p['query_port'],7,278,'probe','ALL_CANDIDATE_JOINT_SIGNAL_QUERY')
