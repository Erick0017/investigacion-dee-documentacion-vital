"""Explicit pre-material horizon change only; archive exact36 sources first."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]

def main():
    archive=ROOT/'protocolo/pre_horizon18';archive.mkdir(exist_ok=False)
    records=[]
    names=('mundo/Config_C02_R02.luau','mundo/Body_C02_R02.luau','mundo/construir_escena_C02_R02.py')
    for name in names:
        path=ROOT/name;raw=path.read_bytes();destination=archive/path.name;destination.write_bytes(raw)
        records.append({'path':name,'preserved':str(destination.relative_to(ROOT)),'before_sha256':hashlib.sha256(raw).hexdigest()})
    p=ROOT/names[0];s=p.read_text('utf-8')
    s=s.replace('R02 prospective environment:36 opportunities, boundary12, reserve25..36.','R02 prospective environment:18 opportunities, boundary6, reserve13..18.')
    s=s.replace('C.MaxCycles=36','C.MaxCycles=18').replace('C.SuspendAfter=12','C.SuspendAfter=6').replace('cursor continues13.','cursor continues7.').replace('C.ReserveStartsAtCycle=25','C.ReserveStartsAtCycle=13')
    s=re.sub(r'function C.PhaseAtCycle\(cycle\).*?\nend','function C.PhaseAtCycle(cycle)\n    if cycle>=17 then return 4 end\n    if cycle>=15 then return 3 end\n    if cycle>=12 then return 2 end\n    if cycle>=9 then return 1 end\n    return 0\nend',s,count=1,flags=re.S)
    s=s.replace('cycle>=14 and cycle<27','cycle>=8 and cycle<14')
    operands='''function C.OperandsAtCycle(cycle)
    if cycle<13 then return {aLeft=9,aRight=3,bRight=4,variant="FAMILIAR"} end
    local b=({[13]=false,[14]=true,[15]=true,[16]=false,[17]=true,[18]=false})[cycle]
    if b then return {aLeft=8,aRight=3,bRight=2,variant="RESERVE_B"} end
    return {aLeft=11,aRight=4,bRight=7,variant="RESERVE_A"}
end'''
    s=re.sub(r'function C.OperandsAtCycle\(cycle\).*?\nend',lambda _:operands,s,count=1,flags=re.S);p.write_text(s,encoding='utf-8')
    p=ROOT/names[1];s=p.read_text('utf-8');assert s.count('if cycle==14 or cycle==27 then')==1
    p.write_text(s.replace('if cycle==14 or cycle==27 then','if cycle==8 or cycle==14 then'),encoding='utf-8')
    p=ROOT/names[2];s=p.read_text('utf-8');assert 'choices=(36,),default=36'in s and 'choices=(12,),default=12'in s
    p.write_text(s.replace('choices=(36,),default=36','choices=(18,),default=18').replace('choices=(12,),default=12','choices=(6,),default=6'),encoding='utf-8')
    for r in records:r['after_sha256']=hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()
    result={'reason':'Root prospectively fixed18/6 from measured6.25min/op before any R02 material opportunity; hard deadlines unchanged.',
        'R02_material_opportunities_before_change':0,'actor_decoder_runner_changed':False,'records':records,'Native_Roblox_model_calls':0}
    with(archive/'PROCEDENCIA.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
    print(json.dumps(result))

if __name__=='__main__':main()
