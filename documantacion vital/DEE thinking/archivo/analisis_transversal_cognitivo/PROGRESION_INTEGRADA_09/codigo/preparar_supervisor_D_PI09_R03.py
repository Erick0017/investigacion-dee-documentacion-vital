"""Create a technical supervisor revision; no actor/protocol or world writes."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
src=H/'ejecutar_D_PI09_R02.py';dst=H/'ejecutar_D_PI09_R03.py'
old=src.read_text('utf-8-sig')
assert hashlib.sha256(src.read_bytes()).hexdigest()=='6531b92dce3944722d8114024dcf2c2f1ee1b9b53abdfc01ca614ee2a10f9da6'
changes={
"steps.extend({'label':'D_EP%02d'%i,'ordinal':i,'literal':{'modo':EPISODE},'max_ticks':2510,":"steps.extend({'label':'D_EP%02d'%i,'ordinal':i,'literal':{'modo':EPISODE},'max_ticks':opportunity_bound(protocol,i),'protocol_external_wait_ticks':protocol['schedule'][i]['wait_ticks'],",
"DEE.PI09.D.prospective.finite_owned_plan.R02":"DEE.PI09.D.prospective.finite_owned_plan.R03",
"DEE.PI09.D.actual.finite_owner_phase.R02":"DEE.PI09.D.actual.finite_owner_phase.R03",
"'scientific_reader_decoder_return_unchanged':True":"'scientific_reader_decoder_return_unchanged':True,'technical_driver_revision':'R03: bound2110 plus actual prospective external wait; global whole bound2510 unchanged'",
}
new=old
for a,b in changes.items():
    assert new.count(a)==1,a
    new=new.replace(a,b)
anchor='def make_plan(seal,protocol,arm,system,tag,phase,start,hasta,tick,yoke_text=None,reproduction=False):'
helper="""def opportunity_bound(protocol,index):
    core=protocol['max_ticks_per_C_opportunity'];wait=protocol['schedule'][index]['wait_ticks']
    require(type(core)is int and core==2110 and type(wait)is int and wait in(0,400),'Exact prospective core bound2110 and declared external wait0/400')
    bound=core+wait
    require(bound<=protocol['max_ticks_per_whole_D_opportunity']==2510,'Never exceed or weaken the scientific whole-operation2510 cap')
    return bound

"""
assert new.count(anchor)==1
new=new.replace(anchor,helper+anchor)
ast.parse(new)
with dst.open('x',encoding='utf8',newline='\n')as f:f.write(new)
print(json.dumps({'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output':str(dst),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'Native_executed':False,'actor_protocol_written':False}))
