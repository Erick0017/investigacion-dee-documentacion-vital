"""Fixed native event shape supports interval variation without retimed readers.

This is the final temporal method family. A is one current carrier; B is a
declared six-carrier tilted shape, identical for AB/BA and every interval.
Their non-opposite directions yield a moving native encounter result.
All candidate signal and use ports remain fixed for intervals1,3,5.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from transferencia_magnitud.cts_integrado import MagnitudeCTSSession,prepare_magnitude_cts
from integracion.relational_pair import move


def component(*,origin=(12,45,45)):
    a=list(origin);ports=[];specs={}
    def port(name,site,vector,state):
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*vector)
        c.state=state;c.semantic=1;c.allow_experience=True;c.allow_probe=True
        p=d.InterfaceSpec();p.name=name;p.channel=c;ports.append(p)
        specs[name]={"site":list(site),"direction":list(vector),"state":state,"semantic":1};return name
    aport=port("tile_order.event.A",a,(1,1,1),6043);bports=[]
    for delta in(-5,-3,-1,1,3,5):
        site=move(a,(1,0,0),11);site=move(site,(0,1,0),delta);site=move(site,(0,0,1),(11+delta)//2)
        name=port("tile_order.event.B."+str(delta),site,(-1,1,0),6201+delta)
        off=port("tile_order.event.B.offroute."+str(delta),move(site,(0,1,0),18),(-1,1,0),6201+delta)
        bports.append({"delta":delta,"port":name,"offroute_port":off,"site":site})
    surfaces=[]
    for delta in(-5,-3,-1,1,3,5):
        travel=(11+delta)//2;meeting=move(a,(1,1,1),travel)
        # With initial event469 and delta=t_B−t_A, the native pair has
        # reached this current site by the single fixed recording tick482.
        if delta>0:
            hub=[meeting[0],(a[1]+13)%67,(a[2]+13)%67]
        else:
            hub=[meeting[0],(a[1]+13+delta)%67,(a[2]+13+delta)%67]
        label="d"+str(delta);cue=(0,0,-1);read=(1,0,0);effect=move(hub,(1,1,0),6)
        surfaces.append({"id":label,"delta":delta,"hub":hub,"effect":effect,
            "record_port":port("tile_order.record."+label,move(hub,cue,-3),cue,1),
            "read_port":port("tile_order.read."+label,move(hub,read,-3),read,1),
            "use_port":port("tile_order.use."+label,move(effect,(0,0,1),-3),(0,0,1),1),
            "meeting":meeting,"meeting_tick":469+(11+abs(delta))//2})
    return ports,{"schema":"CPC9.tiled_order.geometry.v1","origin":a,"a_port":aport,"b_ports":bports,
        "first_tick":469,"record_tick":482,"query_tick":549,"use_tick":555,"surfaces":surfaces,
        "specifications":specs,"prepared":"31inert interfaces(7actualevent+6equalmaterialoffroutecontrols+18cue/query/use),zero addedinitialmaterial. Same all readers/opportunities for intervals1,3,5, both orders. B is an explicit six-carrier shape, not a free clone from one engine packet.",
        "acquired":"At most one A/B shape element encounter product per current event pair. Native directions preserve moving Y/Z content. The later opaque cue normalizes Y+Z into Y for circulation; no externally injected order bit.",
        "scope":"Order of occurrences of these two declared physical event shapes in this fixed reference frame, not arbitrary human temporal semantics or learned source selection."}


def schedule(session,*,tile_order="AB",interval=5,event_a=True,event_b=True,a_load=3,b_load=3,
             form="paired",b_route="onpath",probe=True,use=True):
    if tile_order not in("AB","BA")or interval not in(1,3,5)or form not in("paired","unpaired","omitted")or b_route not in("onpath","offroute"):
        raise ValueError("Frozen tiled current-event domain")
    g=session.geometry["tiled_order"];times={tile_order[0]:469,tile_order[1]:469+interval}
    if event_a:session.input(g["a_port"],a_load,times["A"],origin="CURRENT_EVENT_A_PHYSICAL_CARRIER")
    if event_b:
        for item in g["b_ports"]:
            session.input(item["port"if b_route=="onpath"else"offroute_port"],b_load,times["B"],
                origin="CURRENT_EVENT_B_FIXED_SIX_CARRIER_SHAPE_NOT_ORDER_BIT")
    for item in g["surfaces"]:
        if form!="omitted":session.input(item["record_port"],5,479+int(form=="unpaired"),origin="POST_CURRENT_ENCOUNTERS_IDENTICAL_OPAQUE_CUE_ALL_SIX_BANKS")
        if probe:session.input(item["read_port"],7,546,"probe","IDENTICAL_CURRENT_READERS_ALL_SIX_BANKS")
        if use:session.input(item["use_port"],11,552,origin="IDENTICAL_CURRENT_USE_RESOURCE_ALL_SIX_BANKS")


def prepare(**options):
    origin=options.pop("origin",(12,45,45));recipe,g=prepare_magnitude_cts(**options);ports,extra=component(origin=origin)
    interfaces=list(recipe.interfaces)+ports
    if len({p.name for p in interfaces})!=len(interfaces):raise ValueError("Duplicate tile-order port")
    recipe.interfaces=interfaces;g["tiled_order"]=extra;g["resources"]["interfaces"]=len(interfaces)
    recipe.options={"CPC8R.relational_pair.geometry":encode_metadata(g)};return recipe,g


class TiledOrderSession(MagnitudeCTSSession):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.state.setdefault("tiled_order_observations",[])
        self.mode.state.setdefault("captures",[]);self.initiative.state.setdefault("captures",[])
        self.quantity.state.setdefault("observations",[]);self.transferred_quantity.state.setdefault("observations",[])
    @classmethod
    def create(cls,identifier="CPC9_TILED_ORDER",**options):
        recipe,g=prepare(**options);return cls(d.OrganizationalWorld.create(recipe),g,identifier=identifier)
    def curriculum(self,*,tile_order="AB",interval=5,event_a=True,event_b=True,a_load=3,b_load=3,form="paired",b_route="onpath",probe=True,use=True,**options):
        super().curriculum(**options);schedule(self,tile_order=tile_order,interval=interval,event_a=event_a,event_b=event_b,a_load=a_load,b_load=b_load,form=form,b_route=b_route,probe=probe,use=use)
    def capture_tile(self,stage):
        rows=[]
        for item in self.geometry["tiled_order"]["surfaces"]:
            site=item["effect"]if stage.endswith("use")else item["hub"]
            rows.append({"id":item["id"],"physical":self.observe(site),"Moore27":[self.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
        self.state["tiled_order_observations"].append({"tick":self.tick,"stage":stage,"surfaces":rows})
    def run_until(self,tick):
        stages={481:"pre_record",482:"record",548:"pre_read",549:"read",554:"pre_use",555:"use"}
        for value in sorted(t for t in stages if self.tick<t<=tick):super().run_until(value);self.capture_tile(stages[value])
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
