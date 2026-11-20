-- R07 prospective common environment; no prepared route or goal-selection policy.
-- C02 prepared environment. Private tables below are NOT participant observations.
local C={}
C.Protocol="RBX01.R07.v1"
C.WorldId="RBX01_CIERRE8_R07"
C.SourceWorldId="RBX01_INTEGRAL_V2_R06"
C.ParentNativeTick=991187
C.ParentCompletedCycles=28
C.OwnerUserId=11981994305
C.AutoStart="NONE"
C.Participant="LIVE_NATIVE" -- Same Body, separate declared policy adapters.
C.ScenarioFingerprint="c2240b0026baafc0e94cbfa8838af0ef52a5fa4bb966dc32aa35f99b666f9883"
C.MaxCycles=52
C.SuspendAfter=34 -- Six NEW opportunities after the preserved parent28.
C.ReserveStartsAtCycle=35
C.PermissionStock=164
C.ResourceUnits=9
C.TollCost=2
C.QueryCost=1
C.MoveSeconds=8
C.QuerySeconds=2
C.SkipSeconds=1
C.WaitSeconds=1
C.BlockSeconds=3
C.ToolSeconds=.25
C.RenderTimeScale=1
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
C.PathMotor={WalkSpeed=16,AgentRadius=2,AgentHeight=5,AgentCanJump=false,
    WaypointSpacing=4,ArrivalRadius=2,WaypointTimeout=8,MaxRecomputes=2,MaxWallSeconds=45}
C.MotorFloor={center=Vector3.new(0,4.5,10),size=Vector3.new(220,1,220)}
C.MotorObstacles={
    {name="ObstaculoCentral",center=Vector3.new(0,8,10),size=Vector3.new(12,6,18)},
    {name="ObstaculoLateral",center=Vector3.new(27,8,-5),size=Vector3.new(8,6,13)},
}
C.PortTollLaw="CHOSEN_PORT_ATTEMPT_BEFORE_PATH; NO_GEOMETRIC_TOLL_BYPASS"
C.ToolContactLaw="SELECTED_DESTINATION_ARRIVAL_ONLY; NO_INTERMEDIATE_PICKUPS"
C.AllowDiagnosticTools=true -- additionally requires explicit diagnostic identity in API.
function C.PhaseAtCycle(cycle)
    if cycle>=41 then return 3 end -- exogenous change after twelve NEW opportunities.
    return 2
end
function C.SignsAtCycle(cycle)
    if cycle>=41 then return {luma=-1,nara=1} end
    return {luma=1,nara=-1}
end
function C.OperandsAtCycle(cycle)
    if cycle>=41 then return {aLeft=7,aRight=3,bRight=2,variant="R07_RESERVE_B"} end
    if cycle>=35 then return {aLeft=9,aRight=2,bRight=1,variant="R07_RESERVE_A"} end
    return {aLeft=8,aRight=3,bRight=2,variant="PARENT_TUPLE"}
end
return C
