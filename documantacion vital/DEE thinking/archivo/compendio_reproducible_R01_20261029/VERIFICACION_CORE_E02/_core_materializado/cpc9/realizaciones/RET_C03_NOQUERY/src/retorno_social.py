"""A native B comparison may teach a later reusable E1 return association.

No read/decide/write callbacks. Both direction banks, cue, reader and resources
are supplied identically. B sees actual objects, not already compared classes.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from transferencia_magnitud.cts_integrado import MagnitudeCTSSession, prepare_magnitude_cts
from integracion.relational_pair import move


def port(name, site, direction):
    c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site)
    c.direction=d.Direction(*direction);c.state=1;c.semantic=1
    c.allow_experience=True;c.allow_probe=True
    p=d.InterfaceSpec();p.name=name;p.channel=c
    return p


def prepare_return(**options):
    recipe,g=prepare_magnitude_cts(**options)
    center=g['magnitude_transfer']['quantity']['center']
    ports=list(recipe.interfaces);banks=[]
    for sign,label in ((-1,'minus'),(1,'plus')):
        hub=move(center,(sign,0,0),2)
        used=move(hub,(sign,0,1),5)
        delivery=move(used,(sign,1,1),4)
        for role,site,direction in (('record',hub,(0,1,0)),('read',hub,(0,-1,1)),
                                    ('use',used,(0,1,0))):
            ports.append(port('back.'+label+'.'+role,move(site,direction,-3),direction))
        banks.append({'id':label,'sign':sign,'message_site':move(hub,(sign,0,0),-1),
                      'hub':hub,'use_site':used,'delivery_site':delivery,
                      'message_tick':148,'association_tick':149,'query_tick':216,
                      'use_tick':221,'delivery_tick':225})
    if len({p.name for p in ports})!=len(ports):raise ValueError('Duplicate return interface')
    recipe.interfaces=ports
    g['cpc9_return']={'schema':'CPC9.return.v1','banks':banks,'initial_material_added':0,
                     'interfaces_added':6,'native_source':'B comparator at147',
                     'role':'Received E1 reference is combined with actual B object; native result travels back into an E1 association',
                     'not_claimed':'Two complete minds, general deictic YO/TU, learned scheduler or general comparison rule'}
    g['resources']['interfaces']=len(ports)
    g['finite_protocol']='CPC9.MCTS_return.v1.0_to616'
    recipe.options={'CPC8R.relational_pair.geometry':encode_metadata(g)}
    return recipe,g


class ReturnSession(MagnitudeCTSSession):
    @classmethod
    def create(cls,identifier='CPC9_RETURN',**options):
        r,g=prepare_return(**options)
        return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)

    def curriculum(self,*,back_form='paired',back_query=True,back_use=True,**options):
        if back_form not in ('paired','unpaired','omitted'):raise ValueError('Explicit recording control')
        super().curriculum(**options)
        for bank in self.geometry['cpc9_return']['banks']:
            prefix='back.'+bank['id']+'.'
            if back_form!='omitted':
                self.input(prefix+'record',5,146+int(back_form=='unpaired'),origin='IDENTICAL_POST_B_RESULT_RECORDING_OPPORTUNITY')
            if back_query:self.input(prefix+'read',7,213,'probe','IDENTICAL_RETURN_ASSOCIATION_READER')
            if back_use:self.input(prefix+'use',13,218,origin='IDENTICAL_RETURN_CONSEQUENCE_RESOURCE')

    def return_view(self):
        return [{'bank':bank['id'],**{key:self.observe(bank[key])for key in('message_site','hub','use_site','delivery_site')}}
                for bank in self.geometry['cpc9_return']['banks']]

