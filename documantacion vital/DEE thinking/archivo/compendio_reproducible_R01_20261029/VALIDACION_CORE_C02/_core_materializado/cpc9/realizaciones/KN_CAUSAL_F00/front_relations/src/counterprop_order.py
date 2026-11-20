"""Actual event-order is encoded by native encounter position, not a target bit.

Opposed current event carriers have an odd separation. Their order at a fixed
interval changes the location of their v27 encounter. Identical zero-load
reader opportunities, arbitrary later cues and use resources are offered to
every candidate location. All physical inputs are declared before evolution.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from transferencia_magnitud.cts_integrado import MagnitudeCTSSession,prepare_magnitude_cts
from integracion.relational_pair import move


def component(*, origin=(12,50,50), first_tick=469, interval=5, separation=11):
    if interval not in(1,3,5)or separation!=11 or first_tick not in(468,469,470):
        raise ValueError("Frozen event-domain parameters")
    if (separation+interval)%2:
        raise ValueError("Integer empty-target meeting required")
    ports=[];specs={}
    def port(name,site,vector,state=1):
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*vector)
        c.state=state;c.semantic=1;c.allow_experience=True;c.allow_probe=True
        p=d.InterfaceSpec();p.name=name;p.channel=c;ports.append(p)
        specs[name]={"site":list(site),"direction":list(vector),"state":state,"semantic":1};return name
    a=list(origin);b=move(a,(1,0,0),separation)
    port("pair_order.event.A",a,(1,0,0),6043);port("pair_order.event.B",b,(-1,0,0),6201)
    travel=(separation+interval)//2;meeting_tick=first_tick+travel
    surfaces=[]
    for name,xoffset in(("first_A",travel),("first_B",separation-travel)):
        meeting=move(a,(1,0,0),xoffset);hub=move(meeting,(0,0,1),4)
        record_vector=(0,1,-1);query_vector=(1,0,0)
        effect=move(hub,(1,1,0),6)
        surfaces.append({"id":name,"meeting":meeting,"hub":hub,"effect":effect,
            "opportunity_port":port("pair_order.opportunity."+name,move(meeting,(0,0,1),-3),(0,0,1)),
            "record_port":port("pair_order.record."+name,move(hub,record_vector,-3),record_vector),
            "read_port":port("pair_order.read."+name,move(hub,query_vector,-3),query_vector),
            "use_port":port("pair_order.use."+name,move(effect,(0,0,1),-3),(0,0,1))})
    return ports,{"schema":"CPC9.counterprop_order.geometry.v1","origin":a,"other_origin":b,
        "separation":separation,"first_tick":first_tick,"interval":interval,"meeting_tick":meeting_tick,
        "record_tick":meeting_tick+4,"query_tick":meeting_tick+71,"use_tick":meeting_tick+77,
        "surfaces":surfaces,"specifications":specs,
        "prepared":"Ten inert interfaces, zero added initial material; fixed counterpropagation/reader/cue/use geometry. No answer table or trained snapshot.",
        "physical_question":"Whether actual order AB/BA changes a both-events-dependent encounter location and later use after physical sign pairing; must compare omitted events and equal materials.",
        "interface_modality":"All candidate locations receive identical opportunities; native learned port selection is not claimed."}


def prepare(**options):
    own={key:options.pop(key)for key in tuple(options)if key in("origin","first_tick","interval","separation")}
    recipe,geometry=prepare_magnitude_cts(**options);ports,extra=component(**own)
    recipe.interfaces=list(recipe.interfaces)+ports;geometry["counterprop_order"]=extra
    geometry["resources"]["interfaces"]=len(recipe.interfaces)
    recipe.options={"CPC8R.relational_pair.geometry":encode_metadata(geometry)}
    return recipe,geometry


def schedule(session,*,pair_order="AB",event_a=True,event_b=True,a_load=3,b_load=3,
             form="paired",probe=True,use=True,experience_interval=None):
    if pair_order not in("AB","BA")or form not in("paired","unpaired","omitted"):
        raise ValueError("Declared physical experience conditions")
    g=session.geometry["counterprop_order"]
    if experience_interval is not None and experience_interval not in(1,3,5):
        raise ValueError("Declared actual event interval")
    actual_interval=g["interval"]if experience_interval is None else experience_interval
    event_times={pair_order[0]:g["first_tick"],pair_order[1]:g["first_tick"]+actual_interval}
    for label,enabled,load in(("A",event_a,a_load),("B",event_b,b_load)):
        if enabled:session.input("pair_order.event."+label,load,event_times[label],origin="ACTUAL_CURRENT_EVENT_CARRIER_NO_ORDER_BIT")
    for item in g["surfaces"]:
        session.input(item["opportunity_port"],0,g["meeting_tick"]-3,origin="IDENTICAL_ZERO_LOAD_CURRENT_READER_OPPORTUNITY_ALL_POSITIONS")
        if form!="omitted":session.input(item["record_port"],5,g["record_tick"]-3+int(form=="unpaired"),origin="POST_ENCOUNTER_ARBITRARY_CUE_IDENTICAL_ALL_POSITIONS")
        if probe:session.input(item["read_port"],7,g["query_tick"]-3,"probe","LATER_CUE_ONLY_PROBE_IDENTICAL_ALL_POSITIONS")
        if use:session.input(item["use_port"],11,g["use_tick"]-3,origin="IDENTICAL_CURRENT_MATERIAL_USE_RESOURCE_ALL_POSITIONS")


class CounterpropOrderSession(MagnitudeCTSSession):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.state.setdefault("counterprop_observations",[])
        self.mode.state.setdefault("captures",[]);self.initiative.state.setdefault("captures",[])
        self.quantity.state.setdefault("observations",[]);self.transferred_quantity.state.setdefault("observations",[])
    @classmethod
    def create(cls,identifier="CPC9_COUNTERPROP",**options):
        recipe,geometry=prepare(**options);return cls(d.OrganizationalWorld.create(recipe),geometry,identifier=identifier)
    def curriculum(self,*,pair_order="AB",event_a=True,event_b=True,a_load=3,b_load=3,form="paired",probe=True,use=True,experience_interval=None,**options):
        super().curriculum(**options)
        schedule(self,pair_order=pair_order,event_a=event_a,event_b=event_b,a_load=a_load,b_load=b_load,form=form,probe=probe,use=use,experience_interval=experience_interval)
    def capture_pair(self,stage):
        g=self.geometry["counterprop_order"];field="meeting"if stage.endswith("meeting")else"effect"if stage.endswith("use")else"hub"
        rows=[]
        for item in g["surfaces"]:
            site=item[field];rows.append({"id":item["id"],"physical":self.observe(site),"Moore27":[self.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
        self.state["counterprop_observations"].append({"tick":self.tick,"stage":stage,"surfaces":rows})
    def run_until(self,tick):
        g=self.geometry["counterprop_order"];stages={}
        for key,stage in(("meeting_tick","meeting"),("record_tick","record"),("query_tick","read"),("use_tick","use")):
            stages[g[key]-1]="pre_"+stage;stages[g[key]]=stage
        for value in sorted(t for t in stages if self.tick<t<=tick):super().run_until(value);self.capture_pair(stages[value])
        return super().run_until(tick)
    def save(self,path):
        maps=[self.state,self.mode.state,self.quantity.state,self.initiative.state,self.transferred_quantity.state];removed=[]
        for mapping in maps:
            for key in list(mapping):
                if any(word in key.lower()for word in("observation","capture","window")):
                    removed.append((mapping,key,mapping[key]));mapping[key]=[]
        try:return super().save(path)
        finally:
            for mapping,key,value in removed:mapping[key]=value
