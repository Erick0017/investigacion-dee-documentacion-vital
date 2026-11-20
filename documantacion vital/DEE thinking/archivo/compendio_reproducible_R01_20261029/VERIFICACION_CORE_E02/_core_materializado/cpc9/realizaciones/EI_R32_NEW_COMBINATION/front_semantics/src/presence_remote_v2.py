"""Second memory family: native capture before the known local shadow encounter.

The sourcePNv3 is unchanged. All three fixed route hypotheses receive identical
format opportunities and later thresholds; no observed count selects a bank.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from presence_count import prepare as source_recipe, PresenceCountSession
from integracion.quantity_core import prepare as quantity_recipe
from count_sign.session import port,move

KEY='CPC9.presence_remote.second_memory_family.v2'


def prepare(case):
    recipe,source=source_recipe(case);initial=list(recipe.placements);ports=list(recipe.interfaces);branches=[]
    for heading in(-1,0,1):
        q12=move(source['collector'],(heading,0,1),2)
        q15=move(q12,(0,1,0),3)
        q23=move(q15,(heading,1,1),8)
        prefix='presence.remote.'+str(heading)+'.'
        transfers=[]
        for label,target,vector,tick,lead in(('capture',q12,(-heading,1,-1),12,3),('spread',q15,(heading,0,1),15,1),('settle',q23,(-heading,1,-1),23,3)):
            injection=move(target,vector,-lead)
            if case.get('transfer_path')=='off_path':injection=move(injection,(0,12,0))
            name=prefix+label;ports.append(port(name,injection,vector));transfers.append({'name':name,'target':target,'vector':list(vector),'at':tick,'lead':lead,'request_tick':tick-lead})
        center=move(q23,(1,-1,0));qr,qg=quantity_recipe(center,profile='transient',guards='on_path');initial+=list(qr.placements)
        for interface in qr.interfaces:
            interface.name=prefix+interface.name;channel=interface.channel;channel.name=prefix+channel.name;interface.channel=channel;ports.append(interface)
        branches.append({'heading':heading,'prefix':prefix,'capture12':q12,'spread15':q15,'reference_hub23':q23,
                         'transfers':transfers,'quantity':qg})
    sites=[(p.site.x,p.site.y,p.site.z)for p in initial]
    if len(sites)!=len(set(sites)):raise ValueError('Remote newT0 initial overlap')
    if len({p.name for p in ports})!=len(ports):raise ValueError('Remote interface collision')
    recipe.placements=initial;recipe.interfaces=ports
    g={'schema':KEY,'N':67,'source':source,'branches':branches,'transfer_path':case.get('transfer_path','on_path'),
       'resources':{'initial_materials':len(initial),'interfaces':len(ports),'remote_comparators':3,'basic_buffers_bytes':32*67**3},
       'prepared':'Three fixed capture/spread/settle paths and three native comparisons; equal thresholds16/8/5. SourcePNv3unchanged. Allbanks stimulatedregardlessobservedsource. Capturebeforeknownshadowencounter13.',
       'acquired':'Actual native normalized contact consequence is transported into a mobile remote reference; no external reference input or count label supplied.',
       'domain':'AuxiliaryN67/T0-224, finite0/1/2eventcount and late functional comparisons. Not learned arithmetic rule or NSMmastery.'}
    recipe.options={KEY:encode_metadata(g)};return recipe,g


class RemotePresenceSession(PresenceCountSession):
    @classmethod
    def create(cls,case):r,g=prepare(case);return cls(d.OrganizationalWorld.create(r),g)
    def curriculum(self,normalize=True,guard=True,transfer=True):
        # Temporary view is a protocol adapter only. No world/state/cue is
        # recreated, copied or chosen from observations.
        geometry=self.geometry
        self.geometry=geometry['source']
        try:super().curriculum(normalize,guard)
        finally:self.geometry=geometry
        for branch in geometry['branches']:
            if transfer:
                for step in branch['transfers']:self.input(step['name'],0,step['request_tick'])
            for at,material in((85,11),(152,3),(219,0)):
                self.input(branch['prefix']+'quantity.object.cue',5,at)
                self.input(branch['prefix']+'quantity.object.resource',material,at)
                self.input(branch['prefix']+'quantity.reader',7,at+4,True)
    def run_until(self,tick):
        self.world.run_until(tick);g=self.geometry;source=g['source']
        return {'tick':self.tick,'source_collector':self.observe(source['collector']),
            'source_normalizers':[{'name':n['name'],'reference':self.observe(n['reference_site']),'output':self.observe(n['center'])}for n in source['normalizers']],
            'extra':self.observe(source['contact']['extra']),
            'remote':[{'heading':b['heading'],'capture12':self.observe(b['capture12']),'spread15':self.observe(b['spread15']),
                       'hub23':self.observe(b['reference_hub23']),
                       'reference':self.observe(b['quantity']['reference_site']),'object':self.observe(b['quantity']['object_site']),
                       'output':self.observe(b['quantity']['center'])}for b in g['branches']]}
