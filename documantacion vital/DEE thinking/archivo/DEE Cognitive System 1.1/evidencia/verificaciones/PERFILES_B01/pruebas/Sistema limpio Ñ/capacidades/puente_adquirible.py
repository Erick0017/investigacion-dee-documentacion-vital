"""Prepared native opportunities for acquired directional forms and return learning.

This is an experimental apparatus, not learned language or an external policy.
All branches receive the same cue/read/use opportunities. No readout is used
to choose an answer, receiver or subsequent input.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from dee_thinking.consolidated import exact_receipt
KEY='DEE.Cognitive.System.1.1.social_bridge.v1'
def move(p,v,k=1,n=67):return[(p[i]+v[i]*k)%n for i in range(3)]
def declare(world,*,count=8):
    if int(world.runtime.dimension)!=67 or not 1<=count<=8:raise ValueError('Experimental bridge revision1 has N67 and1–8forms only')
    if KEY in dict(world.runtime.snapshot_metadata_entries):raise ValueError('Bridge already registered; never recreate learned matter')
    forms=[];interfaces=[]
    def port(name,target,vector,lead=3):
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*move(target,vector,-lead));c.direction=d.Direction(*vector);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True;p=d.InterfaceSpec();p.name=name;p.channel=c;world.declare_interface(p);interfaces.append(name);return name
    for i in range(count):
        label='S%02d'%i;hub=[1+8*i,8,(7+17*i)%67];f={'id':label,'A_hub':hub,'ports':{},'branches':[]}
        for role,v in(('cue',(-1,0,0)),('event.plus',(1,1,0)),('event.minus',(1,-1,0)),('read',(0,0,1))):f['ports'][role]=port('DCS11.social.'+label+'.A.'+role,hub,v)
        for sign,name in((-1,'minus'),(1,'plus')):
            vector=(0,sign,1);b=move(hub,vector,5);c=move(b,vector,6);use=move(c,vector,6);row={'id':name,'direction_y':sign,'B_hub':b,'C_hub':c,'use_site':use,'ports':{}}
            for role,target,v in(('Bcue',b,(1,0,0)),('Bread',b,(-1,0,0)),('Ccue',c,(-1,0,0)),('Cread',c,(1,0,0)),('use',use,(1,0,0))):row['ports'][role]=port('DCS11.social.'+label+'.'+name+'.'+role,target,v)
            f['branches'].append(row)
        forms.append(f)
    g={'schema':'DCS1.1.native_social_apparatus.r1','N':67,'forms':forms,'interfaces':interfaces,'new_initial_matter':0,'modality':'External instrumental registration of empty opportunities; subsequent matter must arrive through actual nativeinputs','not_claimed':'NSMmeaning, learned routing policy, role-relativeYO/TU, generaldialogue','ownership':{'E1':['A_hub','C_hub','use_site'],'B':['B_hub']},'teaching_tick':None,'roundtrip':None}
    world.runtime.set_snapshot_metadata(KEY,encode_metadata(g));return g
def geometry(world):return decode_metadata(dict(world.runtime.snapshot_metadata_entries)[KEY])
def teach(world,events,tick,*,omit_event=False,cue=5,teacher=11):
    g=geometry(world)
    if len(events)!=len(g['forms'])or any(x not in(-1,1)for x in events):raise ValueError('Actual physical event directions required for every supplied source form')
    receipts=[]
    for form,event in zip(g['forms'],events):
        receipts.append(exact_receipt(world.submit(form['ports']['cue'],cue,tick)))
        if not omit_event:receipts.append(exact_receipt(world.submit(form['ports']['event.plus'if event==1 else'event.minus'],teacher,tick)))
    g['teaching_tick']=tick;g['environmental_event_count']=len(events);world.runtime.set_snapshot_metadata(KEY,encode_metadata(g));return receipts
def roundtrip(world,source_read_tick,*,omit_B_cue=False,omit_C_cue=False):
    g=geometry(world);requests=[]
    def send(name,load,at,probe=False):requests.append(exact_receipt((world.probe if probe else world.submit)(name,load,at)))
    for form in g['forms']:
        send(form['ports']['read'],7,source_read_tick-3,True)
        for branch in form['branches']:
            p=branch['ports']
            if not omit_B_cue:send(p['Bcue'],5,source_read_tick+2)
            send(p['Bread'],7,source_read_tick+69,True)
            if not omit_C_cue:send(p['Ccue'],5,source_read_tick+75)
            send(p['Cread'],7,source_read_tick+142,True)
            send(p['use'],11,source_read_tick+148)
    g['roundtrip']={'A_read':source_read_tick,'B_record':source_read_tick+5,'B_read':source_read_tick+72,'C_record':source_read_tick+78,'C_read':source_read_tick+145,'use':source_read_tick+151,'opportunities':'All branches equally and externally supplied; native acquired content determines actual transport'}
    world.runtime.set_snapshot_metadata(KEY,encode_metadata(g));return requests
