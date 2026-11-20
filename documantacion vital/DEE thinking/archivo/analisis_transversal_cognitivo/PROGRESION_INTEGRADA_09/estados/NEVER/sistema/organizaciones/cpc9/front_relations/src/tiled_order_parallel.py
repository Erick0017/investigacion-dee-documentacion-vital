"""F3 correction1: parallel probes avoid adjacent candidate-port collisions.

All banks use the same +Z reader and -Y current-use resource. No result is
inspected or selected to determine which input to send. The v1 failures remain
separate primary evidence. A new preparation is made from T0.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from transferencia_magnitud.cts_integrado import prepare_magnitude_cts
from integracion.relational_pair import move
from tiled_order import component as original_component,schedule,TiledOrderSession


def component(*,origin=(12,45,45)):
    ports,g=original_component(origin=origin);by_name={item.name:item for item in ports}
    for item in g["surfaces"]:
        item["effect"]=move(item["hub"],(0,1,1),6)
        for name,site,vector in((item["read_port"],move(item["hub"],(0,0,1),-3),(0,0,1)),
                (item["use_port"],move(item["effect"],(0,-1,0),-3),(0,-1,0))):
            old=by_name[name];c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site)
            c.direction=d.Direction(*vector);c.state=old.channel.state;c.semantic=old.channel.semantic
            c.allow_experience=old.channel.allow_experience;c.allow_probe=old.channel.allow_probe
            spec=d.InterfaceSpec();spec.name=name;spec.channel=c
            ports[ports.index(old)]=spec;by_name[name]=spec
            g["specifications"][name].update(site=site,direction=list(vector))
    g["schema"]="CPC9.tiled_order.geometry.v2.parallelZread.minusYuse"
    g["correction"]={"revision":2,"physical_change":"All six readers+Z, all six use resources-Y, corresponding effect sites changed consistently; current events, all recording cues, clocks, material, dates and resources unchanged.",
        "cause":"v1 adjacent AB candidate readers+X occupy each other's next destinations. Some BA +Z use entries also collide. Parallel directions avoid pointing into adjacent X-bank inputs.",
        "prepared_not_learned":True,"new_recipe_from_T0":True,"parent_v1_preserved":True}
    return ports,g


def prepare(**options):
    origin=options.pop("origin",(12,45,45));recipe,g=prepare_magnitude_cts(**options)
    ports,extra=component(origin=origin);recipe.interfaces=list(recipe.interfaces)+ports
    g["tiled_order"]=extra;g["resources"]["interfaces"]=len(recipe.interfaces)
    recipe.options={"CPC8R.relational_pair.geometry":encode_metadata(g)};return recipe,g


class TiledOrderParallelSession(TiledOrderSession):
    @classmethod
    def create(cls,identifier="CPC9_TILED_ORDER_PARALLEL",**options):
        recipe,g=prepare(**options);return cls(d.OrganizationalWorld.create(recipe),g,identifier=identifier)
