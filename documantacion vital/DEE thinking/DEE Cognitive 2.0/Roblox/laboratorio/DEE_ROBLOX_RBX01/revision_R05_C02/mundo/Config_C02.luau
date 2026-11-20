-- C02 prepared environment. Private tables below are NOT participant observations.
local C={}
C.Protocol="RBX01.C02.v1"
C.WorldId="RBX01_R05_C02_V1"
C.OwnerUserId=11981994305
C.AutoStart="NONE"
C.Participant="LIVE_NATIVE" -- Same Body, separate declared policy adapters.
C.ScenarioFingerprint=string.rep("0",64) -- Root seals source/config before evaluation.
C.MaxCycles=48
C.SuspendAfter=16 -- One deliberate save/reopen boundary; cursor continues17.
C.ReserveStartsAtCycle=33
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
    if cycle>=43 then return 4 end
    if cycle>=37 then return 3 end
    if cycle>=26 then return 2 end
    if cycle>=19 then return 1 end
    return 0
end
function C.SignsAtCycle(cycle)
    if cycle>=18 and cycle<35 then return {luma=-1,nara=1} end
    return {luma=1,nara=-1}
end
-- Each new key captures a tuple from this exogenous calendar. Policy RNG is
-- never consulted; an unfinished round keeps its actual tuple between stations.
function C.OperandsAtCycle(cycle)
    if cycle<33 then return {aLeft=9,aRight=3,bRight=4,variant="FAMILIAR"} end
    local b=({[33]=false,[34]=true,[35]=true,[36]=false,[37]=true,[38]=false,
        [39]=false,[40]=true,[41]=false,[42]=true,[43]=true,[44]=false,
        [45]=false,[46]=true,[47]=false,[48]=true})[cycle]
    if b then return {aLeft=8,aRight=3,bRight=2,variant="RESERVE_B"} end
    return {aLeft=11,aRight=4,bRight=7,variant="RESERVE_A"}
end
return C
