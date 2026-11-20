"""Root's bounded LOCAL_C02 byte relay: official MCP <-> loopback RBX01 HTTP.

No owner/Native imports, policy, navigation, game controls, secret-store calls,
public HTTP, Codex settings changes, or automatic recovery of unknown mutations.
Run on the host so the official local MCP is reachable. Closing this relay closes
only its MCP child; Root separately drains/closes the Native owner before Play.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import datetime
import hashlib
import http.client
import json
import os
import queue
import re
import stat
import sqlite3
import subprocess
import threading
import time

BASE = Path(__file__).resolve().parents[1]
EXE = Path("C:/Users/Erik/AppData/Local/Roblox/Versions/version-63eb6055af4e4688/StudioMCP.exe")
EXPECTED_OWNER = 11981994305
EXPECTED_PLACE = "DEE_RBX01_C02_R02.rbxlx"
API_VERSION = "RBX01.C02.v1"
HTTP_PORT = 8895
WORLD_ID = "RBX01_R05_C02_R02"
EXPECTED_PARTICIPANT = 'LIVE_NATIVE'
MAIN_PLACE_PARTICIPANTS = {
    'DEE_RBX01_C02_R02.rbxlx': 'LIVE_NATIVE',
    'DEE_RBX01_C02_R02_PROGRAMMED.rbxlx': 'PROGRAMMED',
    'DEE_RBX01_C02_R02_CONVENTIONAL_AI.rbxlx': 'CONVENTIONAL_AI',
}
PROFILES = {
    "RBX01_R05_C02_R02": {"place": "DEE_RBX01_C02_R02.rbxlx", "max_cycles": 48,
                          "suspend_after": 6, "target_cycles": 18},
}
PROTOCOL = "RBX01.MAILBOX.C02"
MAX_REQUEST_BYTES = 16384
MAX_RESPONSE_BYTES = 65536
ROUTES = frozenset("/v1/" + name for name in (
    "session/start", "observation", "decision", "query_sensor", "function", "tool_ack", "feedback",
    "ack", "state", "pause", "suspend", "resume", "stop"))
ID_RE = re.compile(r"[A-Za-z0-9_-]{8,80}\Z")
PULL_CODE = """
local run=game:GetService("RunService")
assert(run:IsStudio() and run:IsRunning(),"LOCAL_C02_REQUIRES_STUDIO_PLAY")
local package=game:GetService("ServerScriptService"):FindFirstChild("RBX01Server")
assert(package and package:FindFirstChild("Config"),"LOCAL_C02_WORLD_CONFIG_MISSING")
local config=require(package.Config)
assert(config.WorldId=="RBX01_R05_C02_R02" and config.Protocol=="RBX01.C02.v1" and config.Participant=="LIVE_NATIVE" and config.OwnerUserId==11981994305,"LOCAL_C02_WORLD_IDENTITY_MISMATCH")
local folder=game:GetService("ServerStorage"):FindFirstChild("RBX01Mailbox_C02")
if not folder then return {ready=false,reason="MAILBOX_NOT_CREATED"} end
assert(folder:GetAttribute("Protocol")=="RBX01.MAILBOX.C02","MAILBOX_PROTOCOL")
assert(folder:GetAttribute("OwnerUserId")==11981994305,"MAILBOX_OWNER")
local owner=false
for _,player in ipairs(game:GetService("Players"):GetPlayers()) do
    assert(player.UserId==11981994305,"UNEXPECTED_LOCAL_PLAYER")
    owner=true
end
if not owner then return {ready=false,reason="OWNER_PLAYER_PENDING"} end
assert(folder.Request:IsA("StringValue") and folder.Response:IsA("StringValue"),"MAILBOX_SLOTS")
local status=game:GetService("ReplicatedStorage"):FindFirstChild("RBX01Status")
local world=workspace:FindFirstChild("RBX01")
local body=world and world:FindFirstChild("DEE_Body")
local pose={}
if body and body:IsA("Model") then pose={body:GetPivot():GetComponents()} end
local log=game:GetService("ServerStorage"):FindFirstChild("RBX01EventLog_C02")
-- Auditor-only bounded view. This text is NEVER used as actor observation.
-- The full histories remain in Body.events and immutable generation chunks.
local eventLog=""
local eventLogInfo={representation="ABSENT",partial=true,pending=false}
local http=game:GetService("HttpService")
if log and log:IsA("StringValue") then
    assert(#log.Value<=200000,"C02_LEGACY_AUDIT_LOG_BOUND")
    local rows=http:JSONDecode(log.Value=="" and "[]" or log.Value)
    assert(type(rows)=="table","C02_LEGACY_AUDIT_LOG_SCHEMA")
    local first=math.max(1,#rows-63);local tail={}
    for i=first,#rows do table.insert(tail,rows[i])end
    eventLog=http:JSONEncode(tail)
    while #eventLog>16000 and #tail>0 do
        table.remove(tail,1);first+=1;eventLog=http:JSONEncode(tail)
    end
    eventLogInfo={representation="LEGACY_STRING_TAIL",totalRows=#rows,
        tailFirst=first,tailRows=#tail,partial=(#tail<#rows),pending=false}
elseif log and log:IsA("Folder") then
    assert(log:GetAttribute("Schema")=="DEE.C02.JSON_CHUNKS.R02","C02_AUDIT_FOLDER_SCHEMA")
    local serial=log:GetAttribute("LatestSerial")
    eventLogInfo={representation="CHUNKS_R02_TAIL",partial=true,pending=true,serial=serial}
    if type(serial)=="number" and serial%1==0 and serial>=1 then
        local generation=log:FindFirstChild(string.format("g%06d",serial))
        if generation and generation:IsA("Folder") and generation:GetAttribute("complete")==true then
            assert(generation:GetAttribute("Schema")=="DEE.C02.JSON_CHUNKS.R02" and generation:GetAttribute("serial")==serial,"C02_AUDIT_GENERATION_SCHEMA")
            local tail=generation:FindFirstChild("Tail")
            assert(tail and tail:IsA("StringValue") and #tail.Value<=16000,"C02_AUDIT_TAIL_BOUND")
            local copied=tail.Value
            if log:GetAttribute("LatestSerial")==serial then
                eventLog=copied
                local total=generation:GetAttribute("totalRows")
                local count=generation:GetAttribute("tailRows")
                eventLogInfo={representation="CHUNKS_R02_TAIL",totalRows=total,
                    totalBytes=generation:GetAttribute("totalBytes"),
                    tailFirst=generation:GetAttribute("tailFirst"),tailRows=count,
                    partial=(type(total)~="number" or type(count)~="number" or count<total),
                    serial=serial,pending=false}
            end
        end
    end
elseif log then
    error("C02_AUDIT_LOG_CLASS_MISMATCH")
end
return {ready=true,mailboxProtocol="RBX01.MAILBOX.C02",ownerUserId=11981994305,
    request=folder.Request.Value,response=folder.Response.Value,
    publicStatus=status and status:IsA("StringValue") and status.Value or "",
    bodyPose=pose,eventLog=eventLog,eventLogInfo=eventLogInfo}
"""
PREPARED_SERVER_CODE = """
assert(game:GetService("RunService"):IsStudio() and game:GetService("RunService"):IsRunning(),"PREPARED_SERVER_REQUIRED")
local p=game:GetService("ServerScriptService"):FindFirstChild("RBX01Server")
assert(p and p:FindFirstChild("Config"),"C02_PACKAGE_REQUIRED")
local c=require(p.Config)
assert(c.OwnerUserId==11981994305 and c.WorldId=="RBX01_R05_C02_R02" and c.Protocol=="RBX01.C02.v1","C02_IDENTITY")
assert(c.MaxCycles==18 and c.SuspendAfter==6 and c.ReserveStartsAtCycle==13 and c.PermissionStock==200 and c.ResourceUnits==12,"C02_FINITE_WORLD")
assert(c.AutoStart=="NONE" and type(c.ScenarioFingerprint)=="string" and #c.ScenarioFingerprint==64 and c.ScenarioFingerprint~=string.rep("0",64),"C02_CONTROLLED_PREPARATION")
assert(p.Controller:IsA("Script") and not p.Controller.Disabled and not p:FindFirstChild("ControlReferences_C02"),"C02_EXPLICIT_PARTICIPANT_ONLY")
assert(string.find(p.Bridge.Source,"REQUEST_TIMEOUT_SECONDS = 120",1,true) and string.find(p.Bridge.Source,"for poll=1,480 do",1,true),"C02_TRANSPORT_NOT_LOADED")
assert(string.find(p.Bridge.Source,"BOOTSTRAP_TIMEOUT_SECONDS = 600",1,true),"C02_BOOTSTRAP600_NOT_LOADED")
assert(string.find(p.Bridge.Source,'["/v1/function"]=true',1,true) and string.find(p.Bridge.Source,'["/v1/tool_ack"]=true',1,true) and string.find(p.Bridge.Source,'["/v1/suspend"]=true',1,true),"C02_TOOL_AND_BOUNDARY_TRANSPORT_REQUIRED")
local remote=game:GetService("ReplicatedStorage"):FindFirstChild("RBX01Control")
assert(remote and remote:IsA("RemoteEvent"),"EXISTING_REMOTE_REQUIRED")
local body=workspace:FindFirstChild("RBX01") and workspace.RBX01:FindFirstChild("DEE_Body")
assert(body and body:IsA("Model") and body.PrimaryPart,"PREPARED_BODY_REQUIRED")
assert((body.PrimaryPart.Position-c.Positions[0]).Magnitude<0.01,"BODY_NOT_AT_INITIAL_POSITION")
local owner=false
for _,player in ipairs(game:GetService("Players"):GetPlayers()) do assert(player.UserId==11981994305,"UNEXPECTED_PLAYER");owner=true end
assert(owner,"OWNER_PLAYER_PENDING")
local value=game:GetService("ReplicatedStorage"):FindFirstChild("RBX01Status")
assert(value and value:IsA("StringValue"),"STATUS_REQUIRED")
local s=game:GetService("HttpService"):JSONDecode(value.Value)
assert((c.Participant=="LIVE_NATIVE" or c.Participant=="PROGRAMMED" or c.Participant=="CONVENTIONAL_AI") and s.participant==c.Participant and s.mode=="WAIT" and s.nativeTick==0,"PRESTART_IDENTITY")
assert(s.worldTime==0 and s.moves==0 and s.queries==0 and s.cycle==0 and s.permissionStock==200,"WORLD_ALREADY_STARTED")
assert(s.sessionId=="" and not game:GetService("ServerStorage"):FindFirstChild("RBX01Mailbox_C02"),"SESSION_OR_MAILBOX_ALREADY_EXISTS")
return {verified=true,autoStart=c.AutoStart,ownerUserId=c.OwnerUserId,worldId=c.WorldId,maxCycles=c.MaxCycles,
 actualServerRunning=true,bodyInitial=true,remotePrepared=true,mailboxAbsent=true,NativeStarted=false}
"""
ACCOUNT_CODE = """
local studio=game:GetService("StudioService")
local id=studio:GetUserId()
assert(id==11981994305,"LOCAL_C02_STUDIO_ACCOUNT_MISMATCH")
assert(game:GetService("RunService"):IsStudio(),"STUDIO_REQUIRED")
return {verified=true,studioUserId=id,placeId=game.PlaceId,universeId=game.GameId}
"""
_PULL_CODE_TEMPLATE = PULL_CODE
_PREPARED_CODE_TEMPLATE = PREPARED_SERVER_CODE


def configure_profile(world_id, expected_place=None, max_cycles=None):
    """Select one closed, declared test identity; never inspect task solutions."""
    global WORLD_ID, EXPECTED_PLACE, EXPECTED_PARTICIPANT, PULL_CODE, PREPARED_SERVER_CODE
    if world_id not in PROFILES:
        raise ValueError('Explicit declared C02 world required')
    profile = PROFILES[world_id]
    place = expected_place or profile['place']
    places = MAIN_PLACE_PARTICIPANTS if world_id == 'RBX01_R05_C02_R02' else {profile['place']: 'LIVE_NATIVE'}
    if place not in places:
        raise ValueError('C02 world/place pair mismatch')
    allowed_cycles=(18,48)if world_id=='RBX01_R05_C02_R02'else(profile['max_cycles'],)
    if max_cycles is not None and max_cycles not in allowed_cycles:
        raise ValueError('C02 prospective cycle budget mismatch')
    WORLD_ID, EXPECTED_PLACE, EXPECTED_PARTICIPANT = world_id, place, places[place]
    PULL_CODE = (_PULL_CODE_TEMPLATE.replace('RBX01_R05_C02_R02', world_id)
        .replace('config.Participant=="LIVE_NATIVE"', 'config.Participant=="'+EXPECTED_PARTICIPANT+'"'))
    PREPARED_SERVER_CODE = (_PREPARED_CODE_TEMPLATE.replace('RBX01_R05_C02_R02', world_id)
        .replace('c.MaxCycles==48 and c.SuspendAfter==16',
                 'c.MaxCycles=='+str(profile['max_cycles'])+' and c.SuspendAfter=='+str(profile['suspend_after']))
        .replace('(c.Participant=="LIVE_NATIVE" or c.Participant=="PROGRAMMED" or c.Participant=="CONVENTIONAL_AI")',
                 'c.Participant=="'+EXPECTED_PARTICIPANT+'"'))
    return {'world_id': WORLD_ID, 'expected_place': EXPECTED_PLACE, 'participant': EXPECTED_PARTICIPANT, **profile}

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def canonical(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)

def strict_json(text):
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Nonfinite JSON")))

def require(ok, message):
    if not ok:
        raise ValueError(message)

def safe_path(path, parent):
    path, parent = Path(path).absolute(), Path(parent).resolve()
    require(path.resolve().is_relative_to(parent), "Path escaped its fixed local subtree")
    for item in (path, *path.parents):
        if item.exists() or item.is_symlink():
            details = item.lstat()
            require(not stat.S_ISLNK(details.st_mode) and
                    not (getattr(details, "st_file_attributes", 0) & 1024),
                    "Symlinks/reparse points are prohibited")
    return path

def load_credentials(config_path, *, world_id=None, expected_place=None):
    # Deliberately not called during import/tests. Never return them to Studio.
    private = BASE / "configuracion_privada"
    config_path = safe_path(Path(config_path), private)
    config = strict_json(config_path.read_text("utf-8-sig"))
    require(config.get("apiVersion") == API_VERSION and
            config.get("bind") == "127.0.0.1" and
            type(config.get("port")) is int and config["port"] == HTTP_PORT and
            config.get("ownerUserId") == EXPECTED_OWNER and
            config.get("worldId") in PROFILES,
            "Existing fixed RBX01 loopback/owner configuration required")
    require(world_id is None or world_id == config['worldId'], 'Explicit relay world differs from private configuration')
    configure_profile(config['worldId'], expected_place=expected_place)
    token_name = config.get("tokenFile")
    require(isinstance(token_name, str) and Path(token_name).name == token_name,
            "Token must be an existing private basename")
    token_file = safe_path(private / token_name, private)
    token = token_file.read_text("ascii").strip()
    require(32 <= len(token) <= 256 and re.fullmatch(r"[A-Za-z0-9_+/=-]+", token) is not None,
            "Existing private bearer has an invalid format")
    return token


def validate_resume_cut(world, participant, session_ticks):
    """Pure distinction between real Native cuts and comparator wire IDs."""
    tick=world.get('native_tick');state=world.get('S',{});life=world.get('native_life_id')
    require(type(tick)is int and tick==state.get('nativeTick')and life==state.get('lifeId'),
            'Restored participant cut/identity mismatch')
    require(participant in {'LIVE_NATIVE','PROGRAMMED','CONVENTIONAL_AI'},'Known resumed participant required')
    if participant=='LIVE_NATIVE':
        require(tick>0 and life=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_MAIN_R02',
                'Exact positive Native candidate cut required')
    else:
        prefix='COMPARATOR_'+participant+'_'
        require(tick==0 and type(session_ticks)is int and session_ticks==0 and
                world.get('bridge',{}).get('native_ticks_in_session')==0 and
                isinstance(life,str)and life.startswith(prefix)and
                re.fullmatch(r'[A-Za-z0-9_-]{1,96}',life[len(prefix):])is not None,
                'Comparator must preserve own wire identity and zero Native ticks')
    return participant


def resume_witness(config_path, witness_path):
    """Read-only coherent HTTP-transport snapshot plus frozen World witness."""
    private=BASE/'configuracion_privada'
    config_path=safe_path(Path(config_path),private)
    config=strict_json(config_path.read_text('utf-8-sig'))
    require(config.get('resumeAllowed')is True,'Explicit resumeAllowed configuration required')
    path=safe_path(Path(witness_path),BASE/'evidencia')
    world=strict_json(path.read_text('utf-8-sig'))
    require(world.get('schema')=='DEE.RBX01.C02.world_checkpoint.v1'and world.get('world_id')==WORLD_ID,
            'Exact restored World witness required')
    database=safe_path(private/config['databaseFile'],private)
    con=sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True)
    con.row_factory=sqlite3.Row
    try:
        con.execute('BEGIN')
        session=con.execute('SELECT * FROM session WHERE singleton=1').fetchone()
        boundary=con.execute('SELECT * FROM boundary WHERE singleton=1').fetchone()
        binding=con.execute('SELECT * FROM checkpoint_binding WHERE singleton=1').fetchone()
        pending=con.execute("SELECT count(*)FROM operation WHERE status IN('QUEUED','RUNNING','UNCERTAIN')").fetchone()[0]
        actions=con.execute("SELECT count(*)FROM action WHERE acknowledged!=1 OR execution_status!='EXECUTED'").fetchone()[0]
        tools=con.execute('SELECT count(*)FROM tool_call WHERE acknowledged!=1').fetchone()[0]
        require(session and boundary and binding and session['status']=='SUSPENDED_BOUNDARY'and
                session['phase']=='READY_QUERY'and pending==actions==tools==0,'Resumable quiescent bound HTTP transport required')
        require(session['mode']==EXPECTED_PARTICIPANT,'Resumed participant differs from exact scene profile')
        require(world['bridge']['session_id']==session['id']and world['bridge']['server_id']==session['server_id']
                and world['S']['sessionId']==session['id'],'Saved logical transport identity mismatch')
        require(world['boundary']['next_opportunity']==boundary['next_opportunity']and
                world['boundary']['completed_opportunities']==boundary['completed_cycles']and
                world['boundary']['last_action_id']==session['last_action_id']and
                world['boundary']['last_feedback_operation_id']==boundary['feedback_operation_id'],
                'World and HTTP boundary cursors differ')
        require(world['S']['completedCycles']==boundary['completed_cycles'],'Restored participant cycle mismatch')
        validate_resume_cut(world,EXPECTED_PARTICIPANT,session['ticks'])
        require(world['bridge']['native_ticks_in_session']==session['ticks'],'Saved transport tick total mismatch')
        require(binding['checkpoint_id']==world['checkpoint_id']and isinstance(binding['checkpoint_sha256'],str)
                and re.fullmatch(r'[0-9a-f]{64}',binding['checkpoint_sha256'])is not None,
                'External checkpoint binding identity/hash mismatch')
        return {'world':world,'session_id':session['id'],'server_id':session['server_id'],
                'checkpoint_id':binding['checkpoint_id'],'checkpoint_sha256':binding['checkpoint_sha256'],
                'witness_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    finally:con.close()


def resume_server_code(witness):
    """Auditor capture proves actual Controller BOUNDARY; no Native request."""
    world=witness['world'];state=world['S']
    context={'checkpoint_id':world['checkpoint_id'],'native_life_id':world['native_life_id'],
             'native_tick':world['native_tick'],'bridge':world['bridge']}
    expected={'session':witness['session_id'],'tick':world['native_tick'],
              'completed':world['boundary']['completed_opportunities'],
              'next':world['boundary']['next_opportunity'],'station':state['station'],
              'stock':state['permissionStock'],'lastAction':world['boundary']['last_action_id'],
              'worldTime':state['worldTime'],'pose':world['body_pose']}
    return '''
assert(game:GetService("RunService"):IsStudio()and game:GetService("RunService"):IsRunning(),"C02_RESUME_SERVER_REQUIRED")
local ss=game:GetService("ServerStorage");local p=game:GetService("ServerScriptService"):FindFirstChild("RBX01Server")
assert(p and p:FindFirstChild("Config"),"C02_RESUME_PACKAGE_REQUIRED")
local c=require(p.Config)
assert(c.OwnerUserId==11981994305 and c.WorldId==WORLD_LITERAL and c.Protocol=="RBX01.C02.v1"and c.Participant==PARTICIPANT_LITERAL,"C02_RESUME_IDENTITY")
assert(not ss:FindFirstChild("RBX01Mailbox_C02"),"C02_RESUME_MAILBOX_ALREADY_CREATED")
local owner=false;for _,player in ipairs(game:GetService("Players"):GetPlayers())do assert(player.UserId==11981994305,"UNEXPECTED_PLAYER");owner=true end
assert(owner,"OWNER_PLAYER_PENDING")
local http=game:GetService("HttpService");local expected=http:JSONDecode(EXPECTED_LITERAL)
local capture=assert(ss:FindFirstChild("RBX01Checkpoint_C02"),"C02_RESUME_BOUNDARY_CAPTURE_REQUIRED")
local actual=capture:Invoke(http:JSONDecode(CONTEXT_LITERAL))
assert(actual.boundary.phase=="BOUNDARY"and actual.boundary.native_phase=="IDLE"and actual.controller.phase=="BOUNDARY","C02_RESUME_CONTROLLER_NOT_BOUNDARY")
assert(actual.S.sessionId==expected.session and actual.S.nativeTick==expected.tick and actual.native_tick==expected.tick,"C02_RESUME_LIFE_TICK_SESSION")
assert(actual.S.completedCycles==expected.completed and actual.boundary.next_opportunity==expected.next and actual.boundary.last_action_id==expected.lastAction,"C02_RESUME_CURSOR")
assert(actual.S.station==expected.station and actual.S.permissionStock==expected.stock and math.abs(actual.S.worldTime-expected.worldTime)<0.00001,"C02_RESUME_WORLD_STATE")
assert(#actual.body_pose==#expected.pose,"C02_RESUME_POSE_LENGTH")
for i,v in ipairs(expected.pose)do assert(math.abs(actual.body_pose[i]-v)<0.0001,"C02_RESUME_POSE_MISMATCH")end
return{verified=true,actualServerRunning=true,resumeBoundary=true,NativeStarted=false,nativeTick=actual.native_tick,completed=actual.S.completedCycles,nextOpportunity=actual.boundary.next_opportunity}
'''.replace('WORLD_LITERAL',json.dumps(WORLD_ID)).replace('PARTICIPANT_LITERAL',json.dumps(EXPECTED_PARTICIPANT)).replace('EXPECTED_LITERAL',luau_long_string(canonical(expected))).replace('CONTEXT_LITERAL',luau_long_string(canonical(context)))

class Evidence:
    def __init__(self, path, token):
        self.path = safe_path(path, BASE / "evidencia")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.stream = self.path.open("x", encoding="utf-8")
        self.token = token
        self.count = 0

    def write(self, kind, **fields):
        row = {"schema": "DEE.RBX01.local_mailbox_relay_event.C02.R02",
               "index": self.count, "utc": utc(), "kind": kind, **fields}
        line = canonical(row)
        require(self.token not in line, "Credential detected in event; event not recorded")
        self.stream.write(line + "\n")
        self.stream.flush()
        self.count += 1

    def close(self):
        self.stream.close()

class MCPError(RuntimeError):
    def __init__(self, message, *, sdk_result=None, context=None):
        self.context = dict(context or {})
        self.original_text = ""
        self.sdk_error = None
        if isinstance(sdk_result, dict):
            raw = canonical(sdk_result)
            blocks = sdk_result.get("content", [])
            blocks = blocks if isinstance(blocks, list) else []
            texts = [str(b.get("text", ""))[:2048]
                     for b in blocks[:8]
                     if isinstance(b, dict) and b.get("type") == "text"]
            if isinstance(sdk_result.get("error"), dict):
                texts.append(str(sdk_result["error"].get("message", ""))[:2048])
            self.original_text = "\n".join(texts)
            self.sdk_error = {"isError": sdk_result.get("isError"),
                "protocol_error": isinstance(sdk_result.get("error"), dict),
                "raw_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
                "raw_bytes": len(raw.encode("utf-8")), "raw_excerpt": raw[:16384],
                "raw_excerpt_truncated": len(raw)>16384, "text_blocks": texts}
        super().__init__(message + (": " + self.original_text[:512] if self.original_text else ""))


def tool_error_context(name, arguments):
    code = arguments.get("code")
    return {"tool": name, "studio_id": arguments.get("studio_id"),
            "datamodel_type": arguments.get("datamodel_type"),
            "code_sha256": hashlib.sha256(code.encode("utf-8")).hexdigest() if isinstance(code, str) else None}


def transient_server_datamodel_error(error):
    # Only a known DataModel transition on this exact read-only PULL may wait.
    # Missing detail, transport uncertainty, permissions, identity and every
    # unclassified error STOP. The wrapper's own prose is never classified.
    if not isinstance(error, MCPError) or error.sdk_error is None:
        return False
    if error.sdk_error.get("isError") is not True and error.sdk_error.get("protocol_error") is not True:
        return False
    ctx = error.context
    if (ctx.get("tool") != "execute_luau" or ctx.get("datamodel_type") != "Server"
        or ctx.get("code_sha256") != hashlib.sha256(PULL_CODE.encode("utf-8")).hexdigest()):
        return False
    text = error.original_text.casefold()
    denial_text = text + " " + str(error.sdk_error.get("raw_excerpt", "")).casefold()
    if any(word in denial_text for word in ("permission", "denied", "unauthor", "forbidden",
            "not granted", "scope", "mismatch", "world_identity", "mailbox_protocol",
            "mailbox_owner", "unexpected_local_player", "studio_account")):
        return False
    if "local_c02_requires_studio_play" in text:
        return True  # Exact IsStudio/IsRunning guard in this read-only PULL.
    return re.search(r"\bdata\s*model(?:_type)?\b[^\n]{0,120}\b(?:unavailable|not\s+(?:(?:currently|yet)\s+)?available)\b", text) is not None


class MCPClient:
    """One persistent stdio connection, used only for inventory and fixed Luau."""
    def __init__(self, seconds, executable=EXE):
        self.deadline = time.monotonic() + seconds
        self.identifier = 0
        self.incoming = queue.Queue()
        self.stderr_hash, self.stderr_bytes = hashlib.sha256(), 0
        self.process = subprocess.Popen([str(executable)], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        self.threads = [
            threading.Thread(target=self._stdout, daemon=True),
            threading.Thread(target=self._stderr, daemon=True)]
        for thread in self.threads:
            thread.start()

    def _stdout(self):
        for raw in iter(self.process.stdout.readline, b""):
            try:
                self.incoming.put(strict_json(raw))
            except (ValueError, UnicodeError):
                self.incoming.put({"invalidProtocolLine": True})
        self.incoming.put({"transportEOF": True})

    def _stderr(self):
        for raw in iter(self.process.stderr.readline, b""):
            self.stderr_hash.update(raw)
            self.stderr_bytes += len(raw)

    def call(self, method, params=None, *, notification=False, timeout=20):
        self.identifier += 1
        identifier = self.identifier
        message = {"jsonrpc": "2.0", "method": method}
        if not notification:
            message["id"] = identifier
        if params is not None:
            message["params"] = params
        self.process.stdin.write((canonical(message) + "\n").encode("utf-8"))
        self.process.stdin.flush()
        if notification:
            return None
        deadline = min(self.deadline, time.monotonic() + timeout)
        while time.monotonic() < deadline:
            try:
                result = self.incoming.get(timeout=max(.01, deadline-time.monotonic()))
            except queue.Empty:
                break
            if result.get("transportEOF"):
                raise MCPError("Official MCP stdio closed; state preserved")
            if result.get("invalidProtocolLine"):
                raise MCPError("Official MCP emitted invalid protocol; state preserved")
            if result.get("id") == identifier:
                if "error" in result:
                    raise MCPError("Official MCP returned a protocol error; state preserved", sdk_result=result,
                        context=tool_error_context((params or {}).get("name"), (params or {}).get("arguments", {})))
                return result.get("result", {})
            # Server notifications are not commands or permission grants.
        raise TimeoutError("MCP result unknown at bounded deadline; do not repeat mutation automatically")

    def tool(self, name, arguments):
        require(name in {"list_roblox_studios", "execute_luau"}, "Relay tool closed list")
        # R05 changes only bounded waits for read-only SDK operations. The
        # exact compare-and-set mailbox PUSH retains20s and no replay path.
        read_only = name == "list_roblox_studios" or (name == "execute_luau" and
                    arguments.get("code") in (PULL_CODE, ACCOUNT_CODE, PREPARED_SERVER_CODE))
        result = self.call("tools/call", {"name": name, "arguments": arguments},
                           timeout=120 if read_only else 20)
        if result.get("isError"):
            raise MCPError("Studio tool rejected the operation", sdk_result=result,
                           context=tool_error_context(name, arguments))
        for item in result.get("content", []):
            if item.get("type") == "text":
                try:
                    value = strict_json(item["text"])
                    if isinstance(value, str):
                        value = strict_json(value)
                    if isinstance(value, dict):
                        return value
                except (ValueError, UnicodeError):
                    continue
        raise MCPError("Studio tool returned no expected JSON object; state preserved", sdk_result=result,
                       context=tool_error_context(name, arguments))

    def initialize(self, studio_id):
        result = self.call("initialize", {"protocolVersion": "2025-06-18",
            "capabilities": {}, "clientInfo": {"name": "RBX01-Local-Byte-Relay", "version": "C02"}}, timeout=120)
        require(isinstance(result, dict) and "serverInfo" in result, "MCP initialize failed")
        self.call("notifications/initialized", notification=True)
        discovery_deadline = min(self.deadline, time.monotonic() + 30)
        names = set()
        while time.monotonic() < discovery_deadline:
            listing = self.call("tools/list", {}, timeout=120)
            names = {row.get("name") for row in listing.get("tools", [])}
            if {"execute_luau", "list_roblox_studios"} <= names:
                inventory = self.tool("list_roblox_studios", {})
                found = inventory.get("studios", [])
                changed = [row.get("id") for row in found
                           if row.get("file") == EXPECTED_PLACE and row.get("id") != studio_id]
                if changed:
                    raise MCPError("Exact LOCAL_C02 file has a different Studio ID; no alternative selected. Actual IDs: " + repr(changed))
                target = next((row for row in found if row.get("id") == studio_id), None)
                if target:
                    require(target.get("file") == EXPECTED_PLACE,
                            "Exact explicit local RBX01 place required")
                    return target, sorted(names)
            time.sleep(.25)
        raise MCPError("Explicit Studio not connected after bounded discovery")

    def execute(self, studio_id, datamodel, code):
        return self.tool("execute_luau", {"studio_id": studio_id,
            "datamodel_type": datamodel, "code": code})

    def close(self):
        try:
            self.process.stdin.close()
        except OSError:
            pass
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.terminate()  # Only this MCP child, never Studio/Native.
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=3)
        for thread in self.threads:
            thread.join(timeout=.2)
        return {"mcp_exit_code": self.process.returncode,
                "stderr_bytes": self.stderr_bytes,
                "stderr_sha256": self.stderr_hash.hexdigest()}

def validate_ticket(raw):
    require(isinstance(raw, str) and len(raw.encode("utf-8")) <= MAX_REQUEST_BYTES + 32768,
            "Mailbox request envelope exceeds bound")
    ticket = strict_json(raw)
    require(isinstance(ticket, dict) and set(ticket) ==
            {"mailboxProtocol", "requestId", "path", "body", "attempt"},
            "Mailbox request envelope schema")
    require(ticket["mailboxProtocol"] == PROTOCOL and ticket["path"] in ROUTES,
            "Mailbox protocol or route rejected")
    require(isinstance(ticket["requestId"], str) and ID_RE.fullmatch(ticket["requestId"]) is not None,
            "Mailbox request ID rejected")
    require(type(ticket["attempt"]) is int and 1 <= ticket["attempt"] <= 4,
            "Mailbox retry attempt rejected")
    require(isinstance(ticket["body"], str) and
            len(ticket["body"].encode("utf-8")) <= MAX_REQUEST_BYTES,
            "Mailbox body bound")
    body = strict_json(ticket["body"])
    require(isinstance(body, dict) and body.get("apiVersion") == API_VERSION and
            body.get("requestId") == ticket["requestId"] and
            isinstance(body.get("serverInstanceId"), str) and
            ID_RE.fullmatch(body["serverInstanceId"]) is not None,
            "RBX01 request correlation rejected")
    if ticket["path"] == "/v1/session/start":
        require(body.get("ownerUserId") == EXPECTED_OWNER and
                body.get("worldId") == WORLD_ID and body.get("mode") == EXPECTED_PARTICIPANT and
                body.get("level") == "L4", "Only the explicitly authorized local C02 L4 session may start")
    return ticket

def forward_http(ticket, token, connection_factory=http.client.HTTPConnection):
    """Forward exact UTF-8 bytes only. No proxy, redirect or public network."""
    connection = connection_factory("127.0.0.1", HTTP_PORT, timeout=10)
    body = ticket["body"].encode("utf-8")
    try:
        connection.request("POST", ticket["path"], body=body,
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + token})
        response = connection.getresponse()
        payload = response.read(MAX_RESPONSE_BYTES + 1)
        require(len(payload) <= MAX_RESPONSE_BYTES, "Loopback response exceeds bound")
        text = payload.decode("utf-8")
        require(token not in text, "Credential in loopback response; preserved without forwarding")
        return {"mailboxProtocol": PROTOCOL, "requestId": ticket["requestId"],
                "path": ticket["path"], "requestBody": ticket["body"], "attempt": ticket["attempt"],
                "success": 200 <= response.status < 300, "statusCode": response.status, "body": text}
    except (OSError, http.client.HTTPException):
        # A POST may already have been admitted. Same ID/body is retained.
        return {"mailboxProtocol": PROTOCOL, "requestId": ticket["requestId"],
                "path": ticket["path"], "requestBody": ticket["body"], "attempt": ticket["attempt"],
                "success": False, "statusCode": 599, "body": "",
                "transportOutcome": "UNKNOWN_HTTP_RESULT_SAME_ID_REQUIRED"}
    finally:
        connection.close()

def luau_long_string(text):
    require(isinstance(text, str), "Luau transport literal requires text")
    for count in range(1, 24):
        marks = "=" * count
        if "]" + marks + "]" not in text:
            # Prefix prevents Luau long strings from dropping an initial LF.
            return "([" + marks + "[!" + text + "]" + marks + "]):sub(2)"
    raise ValueError("Cannot delimit bounded transport text")

def push_code(request_raw, response_raw):
    # No payload is interpolated as executable source: long string literals
    # carry raw JSON, and only the mailbox slots are writable here.
    return """
local folder=game:GetService("ServerStorage"):FindFirstChild("RBX01Mailbox_C02")
assert(folder and folder:GetAttribute("Protocol")=="RBX01.MAILBOX.C02","MAILBOX_MISSING")
assert(folder:GetAttribute("OwnerUserId")==11981994305,"MAILBOX_OWNER")
local expected=""" + luau_long_string(request_raw) + """
local response=""" + luau_long_string(response_raw) + """
if folder.Request.Value~=expected then
    return {accepted=false,reason="REQUEST_CHANGED_PRESERVED"}
end
if folder.Response.Value~="" and folder.Response.Value~=response then
    return {accepted=false,reason="RESPONSE_CONFLICT_PRESERVED"}
end
local duplicate=folder.Response.Value==response
folder.Response.Value=response
return {accepted=true,duplicate=duplicate}
"""

class Relay:
    def __init__(self, mcp, studio_id, token, evidence, http_forward=forward_http):
        self.mcp, self.studio_id = mcp, studio_id
        self.token, self.evidence = token, evidence
        self.http_forward = http_forward
        self.responses = {}  # Technical bytes only; never actor memory/policy.
        self.request_identity = {}
        self.delivered = set()
        self.transactions = 0
        self.last_observer_time = float("-inf")
        self.last_event_log_hash = None

    def step(self, guarded_view=None):
        view = guarded_view if guarded_view is not None else self.mcp.execute(self.studio_id, "Server", PULL_CODE)
        if not view.get("ready"):
            return "WAIT"
        require(view.get("mailboxProtocol") == PROTOCOL and
                view.get("ownerUserId") == EXPECTED_OWNER, "Mailbox owner/protocol changed")
        observer_now = time.monotonic()
        if observer_now-self.last_observer_time >= 10 or hashlib.sha256(str(view.get("eventLog", "")).encode("utf-8")).hexdigest() != self.last_event_log_hash:
            public_status = view.get("publicStatus", "")
            event_log = view.get("eventLog", "")
            log_info = view.get('eventLogInfo', {})
            require(isinstance(public_status, str) and isinstance(event_log, str),
                    "Public evaluator fields must be text")
            require(len(public_status.encode("utf-8")) <= 65536 and
                    len(event_log.encode("utf-8")) <= 16000,
                    "Public evaluator log exceeds bounded size")
            require(isinstance(log_info, dict), 'Auditor log provenance must be an object')
            observer = {"public_status_raw": public_status,
                        "body_pose_components": view.get("bodyPose", []),
                        "scope": "PASSIVE_PUBLIC_EVALUATOR_ONLY_NOT_NATIVE_INPUT",
                        'event_log_view': log_info,
                        'complete_event_history_claimed': log_info.get('partial') is False and log_info.get('pending') is False,
                        "Native_ticks_executed_by_observer": 0}
            event_hash = hashlib.sha256(event_log.encode("utf-8")).hexdigest()
            if event_log and event_hash != self.last_event_log_hash:
                observer.update(event_log_raw=event_log, event_log_sha256=event_hash)
            self.last_event_log_hash = event_hash
            self.evidence.write("PUBLIC_OBSERVER_SAMPLE", **observer)
            self.last_observer_time = observer_now
        raw = view.get("request")
        require(isinstance(raw, str) and isinstance(view.get("response"), str),
                "Mailbox slots must be text")
        if not raw:
            require(view["response"] == "", "Orphan mailbox response preserved")
            return "IDLE"
        ticket = validate_ticket(raw)
        require(self.token not in raw, "Credential present in request; not forwarded")
        identity = (ticket["path"], ticket["body"])
        previous = self.request_identity.setdefault(ticket["requestId"], identity)
        require(previous == identity, "Request ID changed route/body; preserved")
        key = (ticket["requestId"], ticket["attempt"])
        if view["response"]:
            # Already pushed; only the Controller may consume it.
            consumed = strict_json(view["response"])
            require(isinstance(consumed, dict) and
                    consumed.get("mailboxProtocol") == PROTOCOL and
                    consumed.get("requestId") == ticket["requestId"] and
                    consumed.get("path") == ticket["path"] and
                    consumed.get("requestBody") == ticket["body"] and
                    consumed.get("attempt") == ticket["attempt"],
                    "Pending response correlation mismatch; preserved")
            return "AWAITING_CONTROLLER_RECEIPT"
        existing = self.responses.get(key)
        if existing is not None:
            require(existing[0] == raw, "Same transport ID/attempt changed bytes; preserved")
            response_raw = existing[1]
        else:
            http_started = time.monotonic()
            response = self.http_forward(ticket, self.token)
            response_raw = canonical(response)
            require(self.token not in response_raw, "Credential in transport response; not forwarded")
            require(len(response_raw.encode("utf-8")) <= MAX_RESPONSE_BYTES + 32768,
                    "Response envelope exceeds mailbox bound; preserved")
            self.responses[key] = (raw, response_raw)
            self.evidence.write("HTTP_RETURNED", request_raw=raw, response_raw=response_raw,
                request_sha256=hashlib.sha256(raw.encode()).hexdigest(),
                response_sha256=hashlib.sha256(response_raw.encode()).hexdigest(),
                transport_uncertain=response.get("statusCode") == 599,
                loopback_latency_seconds=round(time.monotonic()-http_started, 6),
                no_Native_policy=True, authorization_header_recorded=False)
        # One exact compare-and-set. On timeout do not replay the mutation.
        pushed = self.mcp.execute(self.studio_id, "Server", push_code(raw, response_raw))
        require(pushed.get("accepted") is True, "Mailbox response not accepted; preserve and reconcile")
        if key not in self.delivered:
            self.delivered.add(key)
            self.transactions += 1
            self.evidence.write("MAILBOX_RESPONSE_DELIVERED", requestId=key[0], attempt=key[1],
                                duplicate=pushed.get("duplicate") is True)
        return "DELIVERED"

def confirmed_play_server(target):
    if not isinstance(target, dict) or target.get("mode") != "Play":
        return False
    state = target.get("state")
    if not isinstance(state, str):
        return False
    # Exact literals already observed from this official SDK; no inferred or
    # alternate mode names are treated as a running Server DataModel.
    for line in state.splitlines():
        line = line.strip()
        if line.startswith("- "):
            line = line[2:]
        if line.startswith("Available DataModels:"):
            return "Server" in {item.strip() for item in line.split(":", 1)[1].split(",")}
    return False

class StudioRuntimeGate:
    def __init__(self, studio_id, evidence, clock=time.monotonic):
        self.studio_id, self.evidence, self.clock = studio_id, evidence, clock
        self.transient_started = None
        self.last_log_time, self.last_signature = float("-inf"), None
        self.edit_file_bound = False
        self.server_file_bound = False

    def observe(self, inventory):
        now = self.clock()
        require(isinstance(inventory, dict) and isinstance(inventory.get("studios"), list),
                "Studio inventory schema changed; preserve")
        found = inventory["studios"]
        changed = [row.get("id") for row in found if isinstance(row, dict) and
                   row.get("file") == EXPECTED_PLACE and row.get("id") != self.studio_id]
        if changed:
            self.evidence.write("STUDIO_ID_CHANGED_PRESERVED", inventory_raw=inventory,
                                expected_studio_id=self.studio_id, actual_ids=changed)
            raise MCPError("Exact LOCAL_C02 file has a different Studio ID; no alternative selected. Actual IDs: " + repr(changed))
        target = next((row for row in found if isinstance(row, dict) and
                       row.get("id") == self.studio_id), None)
        file_confirmed = False
        if target is not None:
            filename = target.get("file")
            if filename not in (None, ""):
                if filename != EXPECTED_PLACE:
                    self.evidence.write("STUDIO_FILE_CHANGED_PRESERVED", inventory_raw=inventory,
                                        target_raw=target, actual_file=filename)
                    raise MCPError("Nonempty explicit Studio file changed; preserve. Actual file: " + str(filename))
                file_confirmed = True
                if target.get("mode") == "Edit":
                    self.edit_file_bound = True
            else:
                # SDK may omit file while switching Edit -> Play. Keep only
                # the same explicitly bound Studio; PULL rechecks Server world,
                # mailbox protocol and actual owner before any HTTP forwarding.
                file_confirmed = self.edit_file_bound or self.server_file_bound
        if target is not None and file_confirmed and target.get("mode") == "Edit":
            category = "EDIT_WAIT"
            self.transient_started = None
        elif file_confirmed and confirmed_play_server(target):
            category = "PLAY_SERVER_READY"
            self.transient_started = None
        else:
            category = "TARGET_MISSING_WAIT" if target is None else "UNKNOWN_OR_SERVER_PENDING_WAIT"
            if self.transient_started is None:
                self.transient_started = now
        transient_seconds = 0 if self.transient_started is None else now-self.transient_started
        signature = canonical({"category": category, "inventory": inventory})
        if signature != self.last_signature or now-self.last_log_time >= 1:
            self.evidence.write("STUDIO_STATE_OBSERVED", category=category,
                inventory_raw=inventory, target_raw=target, raw_mode=target.get("mode") if target else None,
                expected_studio_id=self.studio_id, transient_seconds=round(transient_seconds, 6),
                exact_Edit_file_previously_bound=self.edit_file_bound,
                exact_prepared_Server_previously_bound=self.server_file_bound,
                Native_or_mailbox_mutations=0)
            self.last_signature, self.last_log_time = signature, now
        if transient_seconds >= 600:
            raise TimeoutError("Unknown/missing Studio state persisted six hundred seconds; no mailbox mutation")
        return category, target

def runtime_inventory_step(mcp, studio_id, relay, gate):
    category, target = gate.observe(mcp.tool("list_roblox_studios", {}))
    if category == "PLAY_SERVER_READY":
        relay.step()
    elif (category == "UNKNOWN_OR_SERVER_PENDING_WAIT" and (gate.edit_file_bound or gate.server_file_bound)
          and isinstance(target, dict) and target.get("id") == studio_id):
        # Inventory mode may be absent while the real Server DataModel is ready.
        # PULL is read-only and asserts IsStudio/IsRunning/World/Owner/Protocol.
        # No HTTP or PUSH is allowed until that exact guarded response is ready.
        try:
            view = mcp.execute(studio_id, "Server", PULL_CODE)
        except MCPError as error:
            transient = transient_server_datamodel_error(error)
            gate.evidence.write("PASSIVE_SERVER_PROBE_REJECTED", target_raw=target,
                error_type=type(error).__name__, error=str(error),
                error_context=error.context, sdk_error=error.sdk_error,
                transient_datamodel_error=transient,
                HTTP_or_mailbox_mutations=0, bound_studio_id=studio_id)
            if not transient:
                raise
            return category, target
        require(isinstance(view, dict), "Guarded Server PULL response must be an object")
        if view.get("ready") is True:
            require(view.get("mailboxProtocol") == PROTOCOL and
                    view.get("ownerUserId") == EXPECTED_OWNER,
                    "Guarded Server PULL owner/protocol mismatch; preserve")
            gate.transient_started = None
            gate.evidence.write("PASSIVE_SERVER_PROBE_CONFIRMED", target_raw=target,
                bound_studio_id=studio_id, inventory_mode_unconfirmed=True,
                confirmation="SERVER_PULL_ISSTUDIO_RUNNING_WORLD_OWNER_PROTOCOL",
                HTTP_or_mailbox_mutations_during_probe=0)
            relay.step(guarded_view=view)
            category = "SERVER_PROBE_READY"
        else:
            gate.evidence.write("PASSIVE_SERVER_PROBE_NOT_READY", target_raw=target,
                reason=view.get("reason"), HTTP_or_mailbox_mutations=0,
                bound_studio_id=studio_id)
    return category, target

def explicit_resume_requested(configuration, resume_boundary):
    """Pure mode guard: permission does not itself request restored execution."""
    if resume_boundary is None:
        return False
    require(configuration.get('resumeAllowed')is True,
            'Explicit resume witness also requires private resumeAllowed')
    return True


def run(studio_id, seconds, evidence_path, stop_file=None, config_path=None, *, world_id=None, expected_place=None, resume_boundary=None):
    require(isinstance(studio_id, str) and re.fullmatch(r"[A-Za-z0-9_-]{8,80}", studio_id),
            "Explicit Studio ID required")
    require(type(seconds) is int and 5 <= seconds <= 32400, "Finite relay duration 5..32400 seconds required")
    event_path = safe_path(evidence_path, BASE / "evidencia")
    summary_path = safe_path(Path(evidence_path).with_suffix(".summary.json"), BASE / "evidencia")
    require(event_path.suffix == ".jsonl", "Evidence must be a new .jsonl event file")
    require(not event_path.exists() and not summary_path.exists(), "Preserve existing relay evidence")
    if stop_file is not None:
        stop_file = safe_path(stop_file, BASE / "evidencia")
        require(not stop_file.exists(), "Relay stop signal must be a new file")
    token = load_credentials(config_path, world_id=world_id, expected_place=expected_place)
    configuration=strict_json(Path(config_path).read_text('utf-8-sig'))
    resume=None
    # Permission to resume is not a request to do so. A fresh session may
    # retain that permission for a later boundary, without inventing a witness.
    if explicit_resume_requested(configuration, resume_boundary):
        resume=resume_witness(config_path,resume_boundary)
    evidence = Evidence(evidence_path, token)
    mcp = None
    summary = {"schema": "DEE.RBX01.local_mailbox_relay_summary.C02.R05", "studio_id": studio_id,
               "started_utc": utc(), "duration_limit_seconds": seconds,
               "Native_imported": False, "Native_owner_opened_by_relay": False,
               "navigation_or_policy_in_relay": False, "network_scope_used": False,
               "account_expected": EXPECTED_OWNER, "automatic_material_stop": False}
    summary['declared_profile'] = {'world_id': WORLD_ID, 'expected_place': EXPECTED_PLACE,
                                 'participant': EXPECTED_PARTICIPANT, **PROFILES[WORLD_ID]}
    summary['resume_boundary_verified_from_files']=resume is not None
    started = time.monotonic()
    try:
        mcp = MCPClient(seconds)
        target, names = mcp.initialize(studio_id)
        require(target.get("persistedToCloud") is False,
                "LOCAL_C02 expects the explicitly selected unpublished local place")
        gate = StudioRuntimeGate(studio_id, evidence)
        category, target = gate.observe({"studios": [target]})
        if resume is not None:
            prepared=mcp.execute(studio_id,'Server',resume_server_code(resume))
            require(prepared.get('verified')is True and prepared.get('resumeBoundary')is True,
                    'Actual restored Controller boundary mismatch; no resume request')
            gate.server_file_bound=True;gate.transient_started=None
            category='SERVER_PRESTART_READY'
            evidence.write('RESUMED_SERVER_BOUND',target_raw=target,guard=prepared,
                witness_sha256=resume['witness_sha256'],HTTP_or_Native_mutations=0)
        while category not in {"EDIT_WAIT", "PLAY_SERVER_READY", "SERVER_PRESTART_READY"}:
            require(time.monotonic()-started < min(600, seconds-1), "Finite prepared Server confirmation deadline")
            require(target is not None and target.get("id")==studio_id,
                    "Exact prepared Studio target required before owner/account guard")
            prepared = mcp.execute(studio_id, "Server", PREPARED_SERVER_CODE)
            require(prepared.get("verified") is True and prepared.get("actualServerRunning") is True,
                    "Prepared actual Server guard failed; no Native start")
            gate.server_file_bound = True
            gate.transient_started = None
            category = "SERVER_PRESTART_READY"
            evidence.write("PREPARED_SERVER_BOUND", target_raw=target, guard=prepared,
                inventory_mode_unconfirmed=True, Native_or_mailbox_mutations=0)

        # MCP execute_luau has command-bar permissions. An account mismatch or
        # unavailable query is a stop, never an implicit permission fallback.
        datamodel = "Edit" if target.get("mode") == "Edit" else "Server"
        account = mcp.execute(studio_id, datamodel, ACCOUNT_CODE)
        require(account.get("verified") is True and account.get("studioUserId") == EXPECTED_OWNER,
                "Authenticated Studio account guard failed")
        evidence.write("CONNECTED", target=target, account=account,
                       tools_available=len(names), fixed_tools_used=["list_roblox_studios", "execute_luau"])
        relay = Relay(mcp, studio_id, token, evidence)
        summary["status"] = "BOUNDED_RELAY_ENDED_STATE_PRESERVED"
        while time.monotonic()-started < seconds-1:
            if stop_file is not None and stop_file.exists():
                summary["status"] = "OPERATOR_STOP_FILE_ONLY_RELAY_CLOSED"
                break
            category, target = runtime_inventory_step(mcp, studio_id, relay, gate)
            time.sleep(.15 if category == "PLAY_SERVER_READY" else .25)
        summary["transactions_delivered"] = relay.transactions
        summary["requires_operator_reconciliation"] = True
    except BaseException as error:
        summary.update(status="FAILED_STATE_PRESERVED", error_type=type(error).__name__,
                       error=str(error), requires_operator_reconciliation=True,
                       no_automatic_retry_of_unknown_MCP_write=True)
        # Only static messages are raised by this client; no headers/token.
        if token in summary.get("error", ""):
            summary["error"] = "Private data suppressed"
        raise
    finally:
        if mcp is not None:
            summary["mcp_child"] = mcp.close()
        summary["elapsed_seconds"] = round(time.monotonic()-started, 3)
        summary["ended_utc"] = utc()
        evidence.write("RELAY_CLOSED_ONLY_MCP_CHILD", summary=summary)
        evidence.close()
        output = safe_path(Path(evidence_path).with_suffix(".summary.json"), BASE / "evidencia")
        with output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--studio-id", required=True)
    parser.add_argument("--seconds", type=int, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--stop-file", type=Path, default=None,
                        help="New evidence-subtree file used for cooperative relay-only shutdown")
    parser.add_argument('--world-id', choices=tuple(PROFILES), default=None)
    parser.add_argument('--expected-place', choices=tuple(set(MAIN_PLACE_PARTICIPANTS)|{p['place'] for p in PROFILES.values()}), default=None)
    parser.add_argument('--resume-boundary',type=Path,default=None,
                        help='Explicit restored-session request with frozen World witness; permission alone never selects resume')
    arguments = parser.parse_args()
    result = run(arguments.studio_id, arguments.seconds, arguments.evidence, arguments.stop_file, arguments.config,
                 world_id=arguments.world_id, expected_place=arguments.expected_place,
                 resume_boundary=arguments.resume_boundary)
    print(json.dumps(result, ensure_ascii=False, indent=2))

