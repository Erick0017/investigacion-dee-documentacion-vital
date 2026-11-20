"""Prepared native route from acquired tiled-order use to an untrained receiver.

No host reads an E output and reinjects a solution. All six receiver banks have
the same cue, reader and resource schedule. The output carrier itself travels
eight +Z steps to a later native encounter. Receiver is a simple region, not a
claim of a second complete mind. Added interfaces contain no initial matter.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from transferencia_magnitud.cts_integrado import prepare_magnitude_cts
from integracion.relational_pair import move
from tiled_order_parallel import component as source_component,TiledOrderParallelSession


def component(*,origin=(12,45,45)):
    source_ports,source=source_component(origin=origin);ports=[];specs={};banks=[]
    def port(name,site,vector):
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site)
        c.direction=d.Direction(*vector);c.state=1;c.semantic=1
        c.allow_experience=True;c.allow_probe=True
        p=d.InterfaceSpec();p.name=name;p.channel=c;ports.append(p)
        specs[name]={"site":list(site),"direction":list(vector),"state":1,"semantic":1};return name
    for item in source["surfaces"]:
        hub=move(item["effect"],(0,0,1),8);effect=move(hub,(0,1,-1),6);label=item["id"]
        banks.append({"id":label,"source_effect":item["effect"],"hub":hub,"effect":effect,
            "record_port":port("tile_social.record."+label,move(hub,(0,1,-1),-3),(0,1,-1)),
            "read_port":port("tile_social.read."+label,move(hub,(0,0,-1),-3),(0,0,-1)),
            "use_port":port("tile_social.use."+label,move(effect,(0,-1,0),-3),(0,-1,0))})
    return source_ports,source,ports,{"schema":"CPC9.order_social.geometry.v1","banks":banks,
        "specifications":specs,"source_tick":555,"record_tick":563,"query_tick":630,"use_tick":636,
        "resources":"18 neutral interfaces,zero additional initial matter;6 identical cues5,6 probes7,6 use resources11;18 requests,total138 payload. Native source carriers are not copied by host.",
        "prepared":"Fixed eight-step source+Z transport and all-bank receiver cue/read/use formats.",
        "acquired":"Source event-dependent carrier participates in a new receiver encounter; later receiver-only probe and use test whether its content remains functional."}


def schedule_receiver(session,*,receiver_form=True,receiver_probe=True,receiver_use=True):
    for item in session.geometry["order_social"]["banks"]:
        if receiver_form:session.input(item["record_port"],5,560,origin="IDENTICAL_RECEIVER_CUES_ALL_BANKS_NO_SOURCE_READBACK")
        if receiver_probe:session.input(item["read_port"],7,627,"probe","IDENTICAL_RECEIVER_ONLY_PROBES_AFTER_67_TICKS")
        if receiver_use:session.input(item["use_port"],11,633,origin="IDENTICAL_RECEIVER_USE_RESOURCES_ALL_BANKS")


def prepare(**options):
    origin=options.pop("origin",(12,45,45));recipe,g=prepare_magnitude_cts(**options)
    source_ports,source,ports,extra=component(origin=origin)
    recipe.interfaces=list(recipe.interfaces)+source_ports+ports
    if len({item.name for item in recipe.interfaces})!=len(recipe.interfaces):raise ValueError("Duplicate order-social interface")
    g["tiled_order"]=source;g["order_social"]=extra;g["resources"]["interfaces"]=len(recipe.interfaces)
    recipe.options={"CPC8R.relational_pair.geometry":encode_metadata(g)};return recipe,g


class OrderSocialSession(TiledOrderParallelSession):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.state.setdefault("order_social_observations",[])
    @classmethod
    def create(cls,identifier="CPC9_ORDER_SOCIAL",**options):
        recipe,g=prepare(**options);return cls(d.OrganizationalWorld.create(recipe),g,identifier=identifier)
    def curriculum(self,*,receiver_form=True,receiver_probe=True,receiver_use=True,**options):
        super().curriculum(**options);schedule_receiver(self,receiver_form=receiver_form,receiver_probe=receiver_probe,receiver_use=receiver_use)
    def capture_receiver(self,stage):
        rows=[]
        for item in self.geometry["order_social"]["banks"]:
            site=item["effect"]if stage.endswith("use")else item["hub"]
            rows.append({"id":item["id"],"physical":self.observe(site),
                "Moore27":[self.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
        self.state["order_social_observations"].append({"tick":self.tick,"stage":stage,"banks":rows})
    def run_until(self,tick):
        stages={562:"pre_record",563:"record",629:"pre_read",630:"read",635:"pre_use",636:"use"}
        for value in sorted(t for t in stages if self.tick<t<=tick):super().run_until(value);self.capture_receiver(stages[value])
        return super().run_until(tick)
