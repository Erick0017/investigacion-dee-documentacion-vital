-- DEVELOPMENT INTERFACE CHECK ONLY. Not a reserved evaluation.
-- C02 prepared environment. Private tables below are NOT participant observations.
local C={}
C.Protocol="RBX01.C02.v1"
C.WorldId="RBX01_INTEGRAL_V2_R06"
C.OwnerUserId=11981994305
C.AutoStart="NONE"
C.Participant="LIVE_NATIVE" -- Same Body, separate declared policy adapters.
C.ScenarioFingerprint="0a21455c746e20a1e01c47292a914929fc97db41158fcce05c80ad6dbcf0b849"
C.MaxCycles=28
C.SuspendAfter=10 -- One deliberate save/reopen boundary; cursor continues17.
C.ReserveStartsAtCycle=11
C.PermissionStock=200
C.ResourceUnits=12
C.TollCost=2
C.QueryCost=1
C.MoveSeconds=8
C.QuerySeconds=2
C.SkipSeconds=1
C.WaitSeconds=1
C.BlockSeconds=3
C.ToolSeconds=.25
C.RenderTimeScale=2
C.PoseSamplesPerWallSecond=20
C.MaxPoseSamples=25000
C.EventLogName="RBX01EventLog_C02"
C.PoseTraceName="RBX01PoseTrace_C02"
C.Positions={
    [0]=Vector3.new(-54,8,38),[1]=Vector3.new(-54,8,-32),
    [2]=Vector3.new(-5,8,54),[3]=Vector3.new(0,8,-38),
    [4]=Vector3.new(51,8,38),[5]=Vector3.new(53,8,-29),
}
C.Edges={
    [0]={[0]=1,[1]=3},[1]={[0]=2,[1]=0},[2]={[0]=4,[1]=3},
    [3]={[0]=5,[1]=2},[4]={[0]=5,[1]=1},[5]={[0]=0,[1]=4},
}
C.ZoneNames={[0]="BASE / ENTREGA",[1]="ARCHIVO / SEÑALES",[2]="CÁLCULO A",
    [3]="ATAJO / INFORMACIÓN",[4]="CÁLCULO B",[5]="RECURSO / CERRADURA"}
C.FreePorts={
    [0]={[0]=-1,[1]=-1,[2]=-1,[3]=-1,[4]=-1,[5]=-1},
    [1]={[0]=0,[1]=-1,[2]=1,[3]=-1,[4]=0,[5]=0},
    [2]={[0]=1,[1]=0,[2]=-1,[3]=0,[4]=1,[5]=-1},
    [3]={[0]=-1,[1]=1,[2]=0,[3]=1,[4]=-1,[5]=0},
    [4]={[0]=0,[1]=-1,[2]=0,[3]=-1,[4]=1,[5]=0},
}
function C.PhaseAtCycle(cycle)
 if cycle>=23 then return 2 end
 if cycle>=17 then return 1 end
 return 0
end
function C.SignsAtCycle(cycle)
 if cycle>=17 then return {luma=1,nara=-1} end
 return {luma=-1,nara=1}
end
-- Each new key captures a tuple from this exogenous calendar. Policy RNG is
-- never consulted; an unfinished round keeps its actual tuple between stations.
function C.OperandsAtCycle(cycle)
 if cycle>=26 then return {aLeft=9,aRight=2,bRight=1,variant="RESERVE_D"} end
 if cycle>=21 then return {aLeft=11,aRight=4,bRight=7,variant="RESERVE_C"} end
 if cycle>=16 then return {aLeft=8,aRight=3,bRight=2,variant="RESERVE_B"} end
 if cycle>=11 then return {aLeft=7,aRight=3,bRight=2,variant="RESERVE_A"} end
 return {aLeft=6,aRight=2,bRight=1,variant="FAMILIAR"}
end
return C
