"""Create R02 files only; preserve every frozen R01 byte. No runtime import."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]

def put(source,target,transform):
    original=ROOT/source;destination=ROOT/target
    if destination.exists():raise RuntimeError('R02 target already exists: '+str(destination))
    before=original.read_bytes();text=before.decode('utf-8-sig');changed=transform(text)
    destination.write_text(changed,encoding='utf-8')
    assert original.read_bytes()==before
    return {'source':source,'target':target,'original_sha256':hashlib.sha256(before).hexdigest(),'sha256':hashlib.sha256(destination.read_bytes()).hexdigest()}

def config(s):
    s=s.replace('C.WorldId="RBX01_R05_C02_V1"','C.WorldId="RBX01_R05_C02_R02"')
    s=re.sub(r'C.MaxCycles=\d+','C.MaxCycles=36',s);s=re.sub(r'C.SuspendAfter=\d+','C.SuspendAfter=12',s)
    s=re.sub(r'C.ReserveStartsAtCycle=\d+','C.ReserveStartsAtCycle=25',s)
    s=s.replace('cursor continues17.','cursor continues13.')
    s=re.sub(r'function C.PhaseAtCycle\(cycle\).*?\nend','function C.PhaseAtCycle(cycle)\n    if cycle>=34 then return 4 end\n    if cycle>=29 then return 3 end\n    if cycle>=22 then return 2 end\n    if cycle>=15 then return 1 end\n    return 0\nend',s,count=1,flags=re.S)
    s=re.sub(r'function C.SignsAtCycle\(cycle\).*?\nend','function C.SignsAtCycle(cycle)\n    if cycle>=14 and cycle<27 then return {luma=-1,nara=1} end\n    return {luma=1,nara=-1}\nend',s,count=1,flags=re.S)
    operands='''function C.OperandsAtCycle(cycle)
    if cycle<25 then return {aLeft=9,aRight=3,bRight=4,variant="FAMILIAR"} end
    local b=({[25]=false,[26]=true,[27]=true,[28]=false,[29]=true,[30]=false,
        [31]=false,[32]=true,[33]=false,[34]=true,[35]=true,[36]=false})[cycle]
    if b then return {aLeft=8,aRight=3,bRight=2,variant="RESERVE_B"} end
    return {aLeft=11,aRight=4,bRight=7,variant="RESERVE_A"}
end'''
    s=re.sub(r'function C.OperandsAtCycle\(cycle\).*?\nend',lambda _:operands,s,count=1,flags=re.S)
    return '-- R02 prospective environment:36 opportunities, boundary12, reserve25..36.\n'+s

def body(s):
    old='local actual=output.numeric_result;local present=formedInteger(actual)'
    assert s.count(old)==1;s=s.replace(old,'local actual=output.numeric_result;local present=output.formed~=false and formedInteger(actual)')
    old='''        if not present then self.S.functionNoResult+=1;result.invalidAction=true;result.outcome="TOOL_NO_RESULT";executionStatus="NO_RESULT"end
    end
    self:emit("FUNCTION_APPLIED"'''
    new='''        if not present then self.S.functionNoResult+=1;result.invalidAction=true;result.outcome="TOOL_NO_RESULT";executionStatus="NO_RESULT"end
    elseif pending.kind=="LESSON"and(output.reason=="NATIVE_PARTIAL_ADMISSION"or output.capability_execution_admitted==false)then
        -- Partial/rejected admission remains an actual failure; never fill a
        -- word or pretend the whole lesson was acquired. Native partial physics
        -- is preserved by its owner; only transport continues after NO_RESULT.
        self.S.functionNoResult+=1;result.invalidAction=true
        result.outcome="TOOL_NO_RESULT";executionStatus="NO_RESULT"
    end
    self:emit("FUNCTION_APPLIED"'''
    assert s.count(old)==1;s=s.replace(old,new)
    s=s.replace('if cycle==18 or cycle==35 then self:emit("CUE_CONTINGENCY"','if cycle==14 or cycle==27 then self:emit("CUE_CONTINGENCY"')
    return '-- R02: declared NO_RESULT on incomplete lesson, actual generic failure.\n'+s

def builder(s):
    s=s.replace('"Config_C02.luau"','"Config_C02_R02.luau"').replace('"Body_C02.luau"','"Body_C02_R02.luau"').replace('"Controller_C02.server.luau"','"Controller_C02_R02.server.luau"')
    s=s.replace('default="DEE_RBX01_C02.rbxlx"','default="DEE_RBX01_C02_R02.rbxlx"')
    s=s.replace('target.name.startswith("DEE_RBX01_C02")','target.name.startswith("DEE_RBX01_C02_R02")')
    s=s.replace('choices=(4,6,42,48)','choices=(36,),default=36').replace('choices=(2,3,14,16)','choices=(12,),default=12')
    return s

def runner(s):
    s=s.replace("'puente/run_comparador_C02.py'","'puente/run_comparador_C02_R02.py'")
    old="('RBX01_R05_C02_V1','RBX01_R05_C02_DEV4','RBX01_R05_C02_CTRL6')"
    assert old in s;s=s.replace(old,"('RBX01_R05_C02_R02',)")
    s=s.replace("default='RBX01_R05_C02_V1'","default='RBX01_R05_C02_R02'")
    return '# R02 wrapper: same frozen non-Native policies, separate world/history.\n'+s

def main():
    records=[]
    for source,target,transform in[
        ('mundo/Config_C02.luau','mundo/Config_C02_R02.luau',config),
        ('mundo/Body_C02.luau','mundo/Body_C02_R02.luau',body),
        ('mundo/Controller_C02.server.luau','mundo/Controller_C02_R02.server.luau',lambda s:'-- R02 file identity; common opportunity/order controller unchanged.\n'+s),
        ('mundo/construir_escena_C02.py','mundo/construir_escena_C02_R02.py',builder),
        ('puente/run_comparador_C02.py','puente/run_comparador_C02_R02.py',runner)]:records.append(put(source,target,transform))
    path=ROOT/'protocolo/ARCHIVOS_VARIANTE_R02.json'
    with path.open('x',encoding='utf-8')as f:json.dump({'created_files':records,'R01_originals_preserved':True,'Native_or_Roblox_or_model_executed':False},f,indent=2)
    print(json.dumps(records))

if __name__=='__main__':main()
