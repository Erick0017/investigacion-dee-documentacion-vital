"""One fresh E1: acquired contact consequence teaches another physical region.

Only inert interfaces are added beforeT0. The original contact query/use417 and
478/484 occur unchanged. Its post-use product travels natively to B; no callback
copies its state. Prepared complementary cue/read phases expose acquired Z.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from integracion.initiative_use_e1 import InitiativeUseE1Session,prepare_initiative_use_e1
from integracion.relational_pair import move

def prepare_contact_social_e1(**options):
    recipe,g=prepare_initiative_use_e1(**options);ports=list(recipe.interfaces);receivers=[]
    def port(name,site,v):
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*v);c.state=77;c.semantic=1;c.allow_experience=True;c.allow_probe=True
        p=d.InterfaceSpec();p.name=name;p.channel=c;ports.append(p);return name
    for kind,z in(('changed',0),('free',-1)):
        source=g['contact']['right.'+kind]['renewed_effect'];memory=move(source,(0,1,z),3);use=move(memory,(0,1,z),5);delivery=move(use,(0,1,z+1),4)
        prefix='contact_social.'+kind
        receivers.append({'id':kind,'source_interface':'contact.right.'+kind,'source_site':source,'source_tick':484,'source_direction':[0,1,z],'message_before_teaching_site':move(memory,(0,1,z),-1),'message_tick':486,'memory_site':memory,'teach_tick':487,'query_tick':554,'teach_port':port(prefix+'.record',move(memory,(-1,0,0),-3),(-1,0,0)),'query_port':port(prefix+'.read',move(memory,(1,0,0),-3),(1,0,0)),'use_site':use,'use_tick':559,'use_port':port(prefix+'.use',move(use,(0,0,1),-3),(0,0,1)),'delivery_site':delivery,'delivery_tick':563,'expected_content_z':z})
    if len({p.name for p in ports})!=len(ports):raise ValueError('Contact social duplicate interface')
    recipe.interfaces=ports;g['contact_social']={'schema':'CPC8R.contact_social.geometry.v1','receivers':receivers,'new_material':0,'new_interfaces':len(ports)-g['resources']['interfaces'],'participants':{'A':'Existing contact acquisition/query/use region in the same fresh InitiativeUseE1 world.','B':'Two initially unassociated receiving opportunities; source content may teach one by native contact.'},'source':'Post-use484 native product; no original retransmission for the Bquery554. All ports and operations fixed beforeT0.','format':'Recording−X and complementary reading+X are prepared protocol roles, identical across both histories and banks; they are not an arbitrary learned dictionary. The acquired content is nativeZ, while nativeY distinguishes the message from cue energy alone.','claim_scope':'Communication and later use of operational contact/free-consequence content, not agency, identity or universalTOUCH.'}
    g['resources']['interfaces']=len(ports);g['finite_protocol']='CPC8R.contactSocialE1.0_to616.v1';g['representation_version']+=' +contactSocial1'
    recipe.options={'CPC8R.relational_pair.geometry':encode_metadata(g)};return recipe,g

class ContactSocialE1Session(InitiativeUseE1Session):
    def __init__(self,*args,**kw):super().__init__(*args,**kw);self.state.setdefault('contact_social_observations',[])
    @classmethod
    def create(cls,identifier='CONTACT_SOCIAL_E1',**options):
        r,g=prepare_contact_social_e1(**options);return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
    def curriculum(self,*,communication_name='paired',communication_query=True,communication_use=True,communication_cue_load=5,communication_probe_load=7,communication_use_load=13,word616=True,**options):
        if communication_name not in('paired','unpaired','omitted'):raise ValueError('Declared cue condition')
        super().curriculum(**options)
        for r in self.geometry['contact_social']['receivers']:
            if communication_name!='omitted':self.input(r['teach_port'],communication_cue_load,r['teach_tick']-3+int(communication_name=='unpaired'),origin='POST_ACQUIRED_CONTACT_NATIVE_MESSAGE_SAME_RECORDING_CUE_ALL_BANKS')
            if communication_query:self.input(r['query_port'],communication_probe_load,r['query_tick']-3,'probe','COMPLEMENTARY_OPAQUE_SIGNAL_NO_ORIGINAL_CONTACT_RETRANSMISSION')
            if communication_use:self.input(r['use_port'],communication_use_load,r['use_tick']-3,origin='SAME_CURRENT_USE_RESOURCE_ALL_BANKS_NOT_CORRECT_CONTENT')
        if word616:
            for p in self.geometry['joint_names'].values():self.input(p['query_port'],13,613,'probe','FIFTH_OLD_JOINT_WORD_QUERY_WITHOUT_RETEACHING')
    def capture_contact_social(self,tick):
        for r in self.geometry['contact_social']['receivers']:
            site=r['source_site']if tick==484 else r['message_before_teaching_site']if tick==486 else r['memory_site']if tick in(487,553,554)else r['use_site']if tick in(558,559)else r['delivery_site']
            phase='SOURCE_POST_OLD_USE'if tick==484 else'MESSAGE_IN_FLIGHT'if tick==486 else'ACQUIRED_MEMORY'if tick==487 else'PRE_QUERY'if tick==553 else'QUERY'if tick==554 else'PRE_USE'if tick==558 else'USE'if tick==559 else'DELIVERY'
            physical=self.observe(site);p=physical['direction'];row={'tick':tick,'receiver':r['id'],'phase':phase,'physical':physical,'Moore27':[self.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}
            if tick==554:
                calls=[x for x in self.state['requests']if x['port']==r['query_port']and x['tick']==551];receipt=self.world.runtime.receipt(calls[-1]['id'])if calls else None;applied=receipt is not None and str(receipt.status)=='applied';probe=calls[-1]['payload']if calls else None
                covered=bool(applied and physical['active']and physical['semantic']==1 and p[0]==0 and p[1]==1 and p[2]in(-1,0)and physical['s_reg']>probe)
                row.update(request_id=int(receipt.id)if receipt is not None else None,request_applied=applied,covered=covered,content=('CONTACT_EFFECT'if p[2]==0 else'FREE_MEDIUM_EFFECT')if covered else None)
            self.state['contact_social_observations'].append(row)
    def run_until(self,tick):
        if type(tick)is not int or tick<self.tick:raise ValueError('Monotone world required')
        for t in sorted(x for x in(484,486,487,553,554,558,559,563)if self.tick<x<=tick):super().run_until(t);self.capture_contact_social(t)
        super().run_until(tick);return self.view()
    def view(self):
        v=super().view();v['contact_social']=[{'receiver':r['id'],'memory':self.observe(r['memory_site']),'use':self.observe(r['use_site']),'delivery':self.observe(r['delivery_site'])}for r in self.geometry['contact_social']['receivers']];return v
