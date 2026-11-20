"""CPC9 late actual-event sensors and native transient export, no clock edits.

The two Z-shifted event ports and complementary candidate recording surfaces
are inert at T0. The first/second events are physical inputs, never an injected
AB/BA bit. Whether both events are necessary is an experimental question.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from transferencia_magnitud.cts_integrado import MagnitudeCTSSession, prepare_magnitude_cts
from integracion.relational_pair import move


def component(geometry, *, sensor_z=1, association_distance=5):
    if sensor_z not in (0,1,-1) or association_distance not in (3,5,7):
        raise ValueError("Bounded declared sensor/association families")
    ports, specifications = [], {}
    def port(name, site, direction, state=1):
        channel=d.ChannelSpec(); channel.name=name; channel.injection_site=d.Coordinate(*site)
        channel.direction=d.Direction(*direction); channel.state=state; channel.semantic=1
        channel.allow_experience=True; channel.allow_probe=True
        spec=d.InterfaceSpec(); spec.name=name; spec.channel=channel; ports.append(spec)
        specifications[name]={"site":site,"direction":list(direction),"state":state,"semantic":1}
        return name
    for letter, dy, state in (("A",-1,6043),("B",1,6201)):
        site=move(geometry["body"][letter],(0,dy,sensor_z))
        port("late_export.event."+letter,site,(0,dy,0),state)
    surfaces=[]
    # For sensor_z0 the anticipated branch has Z0; new ±Z sensors add the
    # physically opposite gradient component, not a semantic answer.
    z=-sensor_z
    for sign,label in ((-1,"minus"),(1,"plus")):
        vector=(sign,sign,z)
        hub=move(geometry["body"]["center"],vector,association_distance)
        cue=(0,-sign,-z)
        record=port("late_export.record."+label,move(hub,cue,-3),cue)
        query=port("late_export.read."+label,move(hub,(0,0,1),-3),(0,0,1))
        effect=move(hub,(sign,0,1),6)
        use=port("late_export.use."+label,move(effect,(0,1,0),-3),(0,1,0))
        surfaces.append({"id":label,"sign":sign,"vector_before_record":list(vector),
            "hub":hub,"record_port":record,"query_port":query,"effect":effect,"use_port":use})
    geometry_new={"schema":"CPC9.late_order_export.v1","sensor_z":sensor_z,
        "association_distance":association_distance,"specifications":specifications,
        "first_event_tick":469,"second_event_tick":470,"transient_tick":470,
        "association_tick":470+association_distance,"query_tick":537+association_distance,
        "use_tick":543+association_distance,"surfaces":surfaces,
        "prepared":"Eight inert ports, unchanged initial MCTS material and clocks. All candidate surfaces receive identical cue/query/use opportunities.",
        "claim":"Actual-event-dependent export is a candidate temporal mechanism; omission controls decide whether second-event dependence is demonstrated. No automatic BEFORE assignment."}
    return ports,geometry_new


def schedule_late(session, *, new_order="AB", first_event=True, second_event=True,
                  form="paired", first_tick=469, interval=1):
    if new_order not in ("AB","BA") or form not in ("paired","unpaired","omitted") or interval not in (1,2,3):
        raise ValueError("Finite experience/label conditions")
    g=session.geometry["late_order_export"]
    if first_event:
        session.input("late_export.event."+new_order[0],3,first_tick,
            origin="FIRST_CURRENT_EVENT_ON_PHYSICAL_Z_SHIFTED_SENSOR")
    if second_event:
        session.input("late_export.event."+new_order[1],3,first_tick+interval,
            origin="SECOND_CURRENT_EVENT_ON_PHYSICAL_Z_SHIFTED_SENSOR")
    for item in g["surfaces"]:
        if form!="omitted":
            session.input(item["record_port"],5,g["association_tick"]-3+int(form=="unpaired"),
                origin="POST_ACTUAL_TRANSIENT_FIXED_ARBITRARY_CUE_ALL_BANKS")
        session.input(item["query_port"],7,g["query_tick"]-3,"probe",
            "LATER_CUE_ONLY_QUERY_ALL_CANDIDATE_BANKS")
        session.input(item["use_port"],11,g["use_tick"]-3,
            origin="FIXED_CURRENT_USE_RESOURCE_ALL_CANDIDATE_BANKS")


def prepare(*, sensor_z=1, association_distance=5, **options):
    recipe, geometry=prepare_magnitude_cts(**options)
    ports, added=component(geometry,sensor_z=sensor_z,association_distance=association_distance)
    interfaces=list(recipe.interfaces)+ports
    if len({item.name for item in interfaces})!=len(interfaces):
        raise ValueError("Late export duplicate interface")
    recipe.interfaces=interfaces; geometry["late_order_export"]=added
    geometry["resources"]["interfaces"]=len(interfaces)
    recipe.options={"CPC8R.relational_pair.geometry":encode_metadata(geometry)}
    return recipe,geometry


class LateExportSession(MagnitudeCTSSession):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.state.setdefault("late_export_observations",[])
        self.mode.state.setdefault("captures",[]);self.initiative.state.setdefault("captures",[])
        self.quantity.state.setdefault("observations",[]);self.transferred_quantity.state.setdefault("observations",[])
    @classmethod
    def create(cls,identifier="CPC9_LATE_EXPORT",**options):
        recipe,geometry=prepare(**options)
        return cls(d.OrganizationalWorld.create(recipe),geometry,identifier=identifier)
    def curriculum(self,*,new_order="AB",first_event=True,second_event=True,form="paired",first_tick=469,interval=1,**options):
        super().curriculum(**options)
        schedule_late(self,new_order=new_order,first_event=first_event,second_event=second_event,
            form=form,first_tick=first_tick,interval=interval)
    def capture_late(self,stage):
        g=self.geometry["late_order_export"]
        rows=[]
        for item in g["surfaces"]:
            site=item["effect"] if stage in("pre_use","use") else item["hub"]
            rows.append({"id":item["id"],"physical":self.observe(site),
                "Moore27":[self.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
        self.state["late_export_observations"].append({"tick":self.tick,"stage":stage,"surfaces":rows})
    def run_until(self,tick):
        g=self.geometry["late_order_export"];boundaries={}
        for key,stage in(("association_tick","record"),("query_tick","read"),("use_tick","use")):
            boundaries[g[key]-1]="pre_"+stage;boundaries[g[key]]=stage
        for value in sorted(t for t in boundaries if self.tick<t<=tick):
            super().run_until(value);self.capture_late(boundaries[value])
        return super().run_until(tick)
    def save(self,path):
        originals=[self.state,self.mode.state,self.quantity.state,self.initiative.state,self.transferred_quantity.state]
        removed=[]
        for mapping in originals:
            for key in list(mapping):
                if any(word in key.lower()for word in("observation","capture","window")):
                    removed.append((mapping,key,mapping[key]));mapping[key]=[]
        try:return super().save(path)
        finally:
            for mapping,key,value in removed:mapping[key]=value
