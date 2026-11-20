"""Root-only C02 R02 lifecycle, separate from preserved R01. Import and --help perform no Native/MCP operation.

Root prepares a running Config.NONE Studio Server. This driver performs one
explicit START_NATIVE (or one bound same-life resume), then only supervises.
Unknown writes are never retried. Joint packing/binding is deliberately manual
after SUSPENDED_CLOSED; the complete world is exported before stopping Play.
"""
from pathlib import Path
import argparse, datetime, hashlib, http.client, importlib.util, json, os
import re, sqlite3, subprocess, sys, time, uuid

ROOT = Path(__file__).resolve().parents[1]
CUTOFF = 1794738600
HARD_FINISH = 1794744900
EXPECTED_OWNER = 11981994305
EXPECTED_PLACE = 'DEE_RBX01_C02_R02.rbxlx'
WORLD_ID = 'RBX01_R05_C02_R02'
SCENES={WORLD_ID:EXPECTED_PLACE}

def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def need(ok, message):
    if not ok: raise RuntimeError(message)
def read(path): return json.loads(Path(path).read_text('utf-8-sig'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path, value):
    with Path(path).open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False); stream.write('\n')
def safe(path):
    p = Path(path).absolute()
    for part in (p, *p.parents):
        need(not part.is_symlink() and not (part.exists() and getattr(part.lstat(), 'st_file_attributes', 0) & 1024), 'No linked/reparse paths')
    p = p.resolve(); need(p.is_relative_to(ROOT), 'C02 subtree only'); return p
def load(relative, name):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod); return mod
def decode_tool(report):
    need(report.get('status') == 'REPLIED', 'Unknown MCP result preserved; no retry')
    reply = report.get('reply', {}); need('error' not in reply, 'MCP protocol error')
    result = reply.get('result', {}); need(not result.get('isError'), 'MCP tool error')
    for block in result.get('content', []):
        if block.get('type') == 'text':
            try:
                value = json.loads(block['text'])
                if isinstance(value, str): value = json.loads(value)
                if isinstance(value, (dict, list)): return value
            except (ValueError, TypeError): pass
    return result
def bridge_read(path):
    """Coherent RO transaction, including live WAL through SQLite; never copy it."""
    if not path.exists(): return None
    con = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=3); con.row_factory = sqlite3.Row
    try:
        con.execute('BEGIN')
        session = con.execute('SELECT * FROM session LIMIT 1').fetchone()
        counts = {r['status']: r['n'] for r in con.execute('SELECT status,COUNT(*) n FROM operation GROUP BY status')}
        feedback = con.execute("SELECT COUNT(*) FROM operation WHERE kind='feedback' AND status='COMPLETED'").fetchone()[0]
        boundary = con.execute('SELECT * FROM boundary LIMIT 1').fetchone()
        binding = con.execute('SELECT * FROM checkpoint_binding LIMIT 1').fetchone()
        action_pending = con.execute('SELECT COUNT(*) FROM action WHERE acknowledged=0').fetchone()[0]
        tool_pending = con.execute('SELECT COUNT(*) FROM tool_call WHERE acknowledged=0').fetchone()[0]
        result = dict(session=dict(session) if session else None, boundary=dict(boundary) if boundary else None,
                      checkpoint_binding=dict(binding) if binding else None,
                      operation_counts=counts, pending=sum(counts.get(k, 0) for k in ('QUEUED', 'RUNNING')),
                      uncertain=counts.get('UNCERTAIN', 0), unacknowledged_actions=action_pending,
                      unacknowledged_tools=tool_pending, feedback_operations_completed=feedback)
        con.rollback(); return result
    finally: con.close()
def owner_meta(destination, life):
    db = destination / 'sistema/estado/servicios_persistentes' / life / 'cola.sqlite3'
    con = sqlite3.connect(db.as_uri() + '?mode=ro', uri=True, timeout=3)
    try:
        row = con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()
        need(row is not None, 'Owner cached status absent'); return json.loads(row[0])
    finally: con.close()
def no_idle_equal(before, after, physical):
    return (all(before.get('physical', {}).get(k) == after.get('physical', {}).get(k) == physical.get(k)
                for k in ('N', 'tick', 'RAW_sha256', 'clocks_sha256'))
            and before.get('idle_ticks') == after.get('idle_ticks')
            and before.get('C02_host_event_driven') is True and after.get('C02_host_event_driven') is True)
def relay_observation(path):
    if not path.exists(): return {}
    with path.open('rb') as stream:
        stream.seek(0, 2); stream.seek(max(0, stream.tell() - 12000000)); lines = stream.read().splitlines()
    connected = False; events = []
    for line in reversed(lines):
        try:
            row = json.loads(line)
            if row.get('kind') == 'CONNECTED': connected = True
            if not events and row.get('kind') == 'PUBLIC_OBSERVER_SAMPLE' and row.get('event_log_raw'):
                events = json.loads(row['event_log_raw'])
        except (ValueError, UnicodeError, TypeError): continue
    return {'connected': connected, 'event_count': len(events),
            'feedback_events': sum(e.get('kind') == 'FEEDBACK_COMPLETED' for e in events),
            'suspended': next((e for e in reversed(events) if e.get('kind') == 'SESSION_SUSPENDED'), None),
            'closed': next((e for e in reversed(events) if e.get('kind') == 'SESSION_CLOSED'), None)}
def closure_proof(path, code, life):
    if code != 0 or not path.exists(): return None
    text = path.read_text('utf8', errors='replace')[-2000000:]; decoder = json.JSONDecoder(); found = None
    for index, char in enumerate(text):
        if char != '{': continue
        try: value, _ = decoder.raw_decode(text[index:])
        except ValueError: continue
        if isinstance(value, dict) and value.get('status') == 'CLOSED' and value.get('lifeId') == life and value.get('ownerClosed') is True and value.get('writerDrained') is True: found = value
    return found
def child_closed(destination, life):
    journal = destination / 'ENSAYOS.jsonl'; found = None
    if not journal.exists(): return None
    for line in journal.read_text('utf8', errors='replace').splitlines():
        try: row = json.loads(line)
        except ValueError: continue
        if row.get('kind') == 'OWNER_CLOSED' and row.get('life') == life: found = row
    if not found or found.get('exit_code') != 0 or (found.get('final_status') or {}).get('running') is not False: return None
    return found
def long_string(text):
    for n in range(20):
        marks = '=' * n
        if ']' + marks + ']' not in text: return '([' + marks + '[!' + text + ']' + marks + ']):sub(2)'
    raise ValueError('Unbounded Lua delimiter')
def client_control(command):
    need(command in ('START_NATIVE', 'SAVE_CLOSE_BOUNDARY'), 'Finite controls only')
    return ('local p=game:GetService("Players").LocalPlayer\nassert(p and p.UserId==11981994305,"AUTHORIZED_OPERATOR_REQUIRED")\n'
            'game:GetService("ReplicatedStorage"):WaitForChild("RBX01Control"):FireServer("' + command + '")\n'
            'return {requested=true,operatorControl="' + command + '",NativeActionSelected=false}')
def prepared_guard(max_cycles, suspend_after, participant='LIVE_NATIVE',world_id=WORLD_ID):
    need(world_id in SCENES,'Explicit C02 world allowlist only')
    return '''
assert(game:GetService("RunService"):IsStudio() and game:GetService("RunService"):IsRunning(),"PREPARED_SERVER_REQUIRED")
local p=game:GetService("ServerScriptService"):FindFirstChild("RBX01Server");assert(p,"C02_PACKAGE_REQUIRED")
local c=require(p.Config)
assert(c.OwnerUserId==11981994305 and c.WorldId=="WORLDIDENTITY" and c.Protocol=="RBX01.C02.v1","C02_IDENTITY")
assert(c.MaxCycles==MAXC and c.SuspendAfter==SUSPA and c.PermissionStock==200 and c.ResourceUnits==12,"C02_FINITE_WORLD")
assert(c.AutoStart=="NONE" and c.Participant=="PARTICIPANT" and c.ScenarioFingerprint~=string.rep("0",64),"C02_CONTROLLED_PREPARATION")
assert(p.Controller:IsA("Script") and not p.Controller.Disabled,"C02_SINGLE_CONTROLLER_REQUIRED")
assert(p:FindFirstChild("Body_C02") and p:FindFirstChild("EstadoPareja_C02"),"C02_MODULES_REQUIRED")
local remote=game:GetService("ReplicatedStorage"):FindFirstChild("RBX01Control");assert(remote and remote:IsA("RemoteEvent"),"CONTROL_REQUIRED")
local body=workspace:FindFirstChild("RBX01") and workspace.RBX01:FindFirstChild("DEE_Body")
assert(body and body.PrimaryPart and (body.PrimaryPart.Position-c.Positions[0]).Magnitude<0.01,"BODY_INITIAL_REQUIRED")
local owner=false;for _,player in ipairs(game:GetService("Players"):GetPlayers())do assert(player.UserId==11981994305,"UNEXPECTED_PLAYER");owner=true end;assert(owner,"OWNER_PLAYER_PENDING")
local raw=game:GetService("ReplicatedStorage"):FindFirstChild("RBX01Status");assert(raw and raw:IsA("StringValue"),"STATUS_REQUIRED")
local s=game:GetService("HttpService"):JSONDecode(raw.Value)
assert(s.participant=="PARTICIPANT" and s.mode=="WAIT" and s.nativeTick==0 and s.worldTime==0 and s.cycle==0 and s.completedCycles==0 and s.permissionStock==200,"WORLD_NOT_FRESH")
assert(s.sessionId=="" and not game:GetService("ServerStorage"):FindFirstChild("RBX01Mailbox_C02"),"START_ALREADY_ATTEMPTED")
assert(game:GetService("ServerStorage"):FindFirstChild("RBX01Checkpoint_C02") and game:GetService("ServerStorage"):FindFirstChild("RBX01Restore_C02"),"C02_BOUNDARY_API_REQUIRED")
return {verified=true,actualServerRunning=true,scenarioFingerprint=c.ScenarioFingerprint,maxCycles=c.MaxCycles,suspendAfter=c.SuspendAfter,NativeStarted=false}
'''.replace('MAXC', str(max_cycles)).replace('SUSPA', str(suspend_after)).replace('PARTICIPANT', participant).replace('WORLDIDENTITY',world_id)

def run(args):
    need(args.root_run, 'Explicit Root operation only')
    need(args.world_id in SCENES and args.expected_place==SCENES[args.world_id],'Explicit matched C02 scene/world allowlist only')
    destination, ledger, config_path, output = map(safe, (args.destination, args.ledger, args.config, args.output))
    need(output.is_relative_to(ROOT / 'evidencia') and not output.exists(), 'Fresh C02 evidence output required')
    need(time.time() < CUTOFF - 1800, 'No new trajectory without prospective Native margin')
    context = read(destination / 'CONTEXTO_EJECUCION.json'); life = context['life']
    scope = read(destination / 'sistema/capacidades/RBX02_NATIVE_SCOPE_C02_R02.json')
    scope_maximum = scope['max_cycles']; suspension = args.suspend_after
    maximum = scope_maximum if args.target_cycles is None else args.target_cycles
    need(scope_maximum in (4, 6, 48) and type(maximum)is int and 0<maximum<=scope_maximum
         and 0 <= suspension < maximum, 'Explicit finite C02 scope/target/boundary')
    if args.target_cycles is not None:
        need(scope_maximum==48 and args.world_id==WORLD_ID and (maximum,suspension)in((36,12),),
             'R02 target36/12 is MAIN_R02 only; Native scope/ledger supply remain48')
    config = read(config_path); private = ROOT / 'configuracion_privada'
    need(config_path.parent == private and config.get('port') == 8895 and config.get('worldId') == args.world_id
         and config.get('ownerUserId') == EXPECTED_OWNER and config.get('allowControl') is False, 'Fixed C02 private config only')
    database = safe(private / config['databaseFile'])
    need(not args.world_checkpoint or config.get('resumeAllowed') is True, 'Resume requires explicit bound private config')
    need(args.no_idle_seconds in (5, 61), 'No-idle observation is61first or5explicitreuse')
    actor_sha = sha(ROOT / 'fuentes/servicio_eventos_C02.py')
    if args.no_idle_seconds == 5:
        need(args.initial_no_idle_proof is not None, 'A five-second continuation check requires prior61second source proof')
        old = read(safe(args.initial_no_idle_proof))
        need(old.get('seconds', 0) >= 60 and old.get('physical_equal') is True and old.get('service_source_sha256') == actor_sha,
             'Prior61second no-idle source proof mismatch')
    output.mkdir(parents=True)
    def note(kind, **fields):
        with (output / 'supervisor.jsonl').open('a', encoding='utf8') as stream:
            stream.write(json.dumps({'utc': utc(), 'kind': kind, **fields}, ensure_ascii=False, allow_nan=False) + '\n'); stream.flush()
    operator = load('control/mcp_operator_C02.py', '_C02_root_operator')
    def mcp(tool, arguments, label, seconds=90):
        fields = dict(arguments)
        if tool != 'list_roblox_studios': fields['studio_id'] = args.studio_id
        extra = {'wait_file': args.expected_place} if tool == 'list_roblox_studios' else {}
        return decode_tool(operator.run(tool, fields, output / (label + '.json'), seconds, **extra))
    def health():
        con = http.client.HTTPConnection('127.0.0.1', config['port'], timeout=2)
        try:
            con.request('GET', '/health'); reply = con.getresponse(); value = reply.read(65537)
            return json.loads(value) if reply.status == 200 and len(value) <= 65536 else None
        finally: con.close()
    def capture_world(context, label, filename):
        # TransportR02: R01 failed known StringValue200k on DEV2. The scientific
        # checkpoint itself is unchanged; bounded hex chunks replace one value.
        transport=load('control/transporte_checkpoint_C02_R02.py','_C02_checkpoint_transport_R02')
        persistence=load('control/persistencia_C02.py','_C02_world_boundary_validation')
        return transport.capture_world(mcp,context,label,output/filename,persistence.validate_world)

    summary = dict(schema='DEE.RBX01.C02.orchestrator.R02', lifeId=life, studio_id=args.studio_id,
                   started_utc=utc(), Native_cutoff_epoch=CUTOFF, hard_finish_epoch=HARD_FINISH,
                   target_cycles=maximum, Native_scope_max_cycles=scope_maximum,
                   suspend_after=suspension, material_retries=0, owner_force_killed=False,
                   packaging_automated=False, same_life_resume_requested=bool(args.world_checkpoint))
    owner = relay = None; streams = []; play = False; close_sent = False
    owner_log = output / 'owner_utf8.log'; relay_log = output / 'relay_utf8.log'
    relay_events = output / 'relay.jsonl'; relay_stop = output / 'relay.stop'
    env = dict(os.environ, PYTHONUTF8='1', PYTHONUNBUFFERED='1', PYTHONDONTWRITEBYTECODE='1')
    def save_close(reason):
        nonlocal close_sent
        if close_sent or not play: return
        close_sent = True; note('SAVE_CLOSE_REQUESTED_ONCE', reason=reason)
        try: mcp('execute_luau', dict(datamodel_type='Client', code=client_control('SAVE_CLOSE_BOUNDARY')), 'save_close_once', 120)
        except BaseException as error: note('SAVE_CLOSE_UNKNOWN_PRESERVED', error_type=type(error).__name__, no_retry=True)
    def monitor():
        while owner.poll() is None:
            try:
                state = bridge_read(database); observed = relay_observation(relay_events)
                note('PROGRESS', bridge=state, world=observed, owner_pid=owner.pid, relay_returncode=relay.poll() if relay else None,
                     ledger=read(ledger))
                if state and state['uncertain']: save_close('UNCERTAIN_FUTURE_PRESERVED')
                if relay and relay.poll() is not None: save_close('RELAY_EXITED_NO_RETRY')
            except (OSError, sqlite3.Error, ValueError) as error: note('READONLY_PROGRESS_UNAVAILABLE', error_type=type(error).__name__)
            if time.time() >= CUTOFF - 1890: save_close('PROSPECTIVE_NEW_Q1_MARGIN')
            if time.time() >= HARD_FINISH - 30:
                note('HARD_FINISH_OWNER_PRESERVED', owner_pid=owner.pid); return False
            time.sleep(5)
        return True
    try:
        listing = mcp('list_roblox_studios', {}, '00_inventory')
        target = next((s for s in listing.get('studios', []) if s.get('id') == args.studio_id), None)
        need(target is not None and target.get('file') == args.expected_place, 'Exact C02 Studio file required')
        guard = mcp('execute_luau', dict(datamodel_type='Server', code=prepared_guard(maximum, suspension,world_id=args.world_id)), '01_prepared_guard')
        need(guard.get('verified') is True and guard.get('actualServerRunning') is True, 'Prepared running Server required')
        need(re.fullmatch('[0-9a-f]{64}',args.scenario_sha256) and guard.get('scenarioFingerprint')==args.scenario_sha256,
             'Explicit frozen scenario fingerprint mismatch')
        play = True
        relay_module = load('control/studio_mailbox_relay_C02_R02.py', '_C02_relay_preowner')
        relay_module.configure_profile(args.world_id,expected_place=args.expected_place,max_cycles=scope_maximum)
        account = mcp('execute_luau', dict(datamodel_type='Server', code=relay_module.ACCOUNT_CODE), '01B_preowner_account')
        need(account.get('studioUserId') == EXPECTED_OWNER and account.get('verified') is True, 'Authenticated Studio account guard')
        probe = mcp('execute_luau', dict(datamodel_type='Server', code=relay_module.PULL_CODE), '01C_mailbox_absent')
        need(probe.get('ready') is False and probe.get('reason') == 'MAILBOX_NOT_CREATED', 'Fresh unstarted mailbox required')
        card = read(destination / 'sistema/estado/vidas' / life / 'VIDA.json')
        if args.world_checkpoint:
            world_path = safe(args.world_checkpoint); world = read(world_path)
            need(sha(world_path) == args.world_checkpoint_sha256, 'External world checkpoint bytes mismatch')
            need(world['native_life_id'] == life and world['native_tick'] == card['physical']['tick'], 'Same-life current Native cut required')
            expected = {k: world[k] for k in ('world_id', 'scenario_sha256', 'native_life_id', 'native_tick', 'checkpoint_id')}
            expected.update(checkpoint_sha256=args.bound_checkpoint_sha256, owner_closed=True, bridge_quiescent=True)
            need(isinstance(args.bound_checkpoint_sha256, str) and re.fullmatch('[0-9a-f]{64}', args.bound_checkpoint_sha256), 'Externally bound checkpoint hash required')
            persistence = load('control/persistencia_C02.py', '_C02_before_restore_closed')
            persistence.closed_native_root(destination, life)
            saved_bridge = bridge_read(database)
            need(saved_bridge and saved_bridge['session']['status'] == 'SUSPENDED_BOUNDARY' and saved_bridge['pending'] == saved_bridge['uncertain'] == saved_bridge['unacknowledged_actions'] == saved_bridge['unacknowledged_tools'] == 0, 'Closed bound transport required')
            need(saved_bridge['session']['id']==world['bridge']['session_id'] and
                 saved_bridge['session']['server_id']==world['bridge']['server_id'] and
                 saved_bridge['checkpoint_binding'] and saved_bridge['checkpoint_binding']['checkpoint_id']==world['checkpoint_id'] and
                 saved_bridge['checkpoint_binding']['checkpoint_sha256']==args.bound_checkpoint_sha256,
                 'Offline checkpoint binding/logical transport identities mismatch')
            # StringValue chunks are transport only and never fed as Native sensors.
            raw = json.dumps(world, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
            count = (len(raw) + 23999) // 24000
            init = 'local s=game:GetService("ServerStorage");assert(not s:FindFirstChild("C02RestoreTransport"),"RESTORE_ALREADY_ATTEMPTED");local f=Instance.new("Folder");f.Name="C02RestoreTransport";f.Parent=s;return {prepared=true}'
            mcp('execute_luau', dict(datamodel_type='Server', code=init), '02_restore_transport_once')
            for i in range(count):
                chunk = raw[i*24000:(i+1)*24000]
                code = 'local f=game:GetService("ServerStorage").C02RestoreTransport;local name="c' + str(i) + '";assert(not f:FindFirstChild(name),"CHUNK_ALREADY_WRITTEN");local v=Instance.new("StringValue");v.Name=name;v.Value=' + long_string(chunk) + ';v.Parent=f;return {written=true}'
                mcp('execute_luau', dict(datamodel_type='Server', code=code), '02_restore_chunk_%04d' % i)
            code = ('local s=game:GetService("ServerStorage");local f=s.C02RestoreTransport;local t={};for i=0,' + str(count-1) + ' do table.insert(t,f["c"..i].Value)end;local h=game:GetService("HttpService");local state=h:JSONDecode(table.concat(t));local expected=h:JSONDecode(' + long_string(json.dumps(expected, separators=(',', ':'))) + ');return s.RBX01Restore_C02:Invoke(state,expected)')
            restored = mcp('execute_luau', dict(datamodel_type='Server', code=code), '02_world_restore_once', 120)
            need(restored.get('restored') is True and restored.get('native_tick') == world['native_tick'], 'Restore unknown; preserve and stop, no replay')
            summary['world_restore_reply'] = restored
            write(output / 'WORLD_RESTORE_APPLIED.json', restored)
            verify_context=dict(checkpoint_id=world['checkpoint_id'],native_life_id=life,
                                native_tick=world['native_tick'],bridge=world['bridge'])
            restored_world,restored_path,_=capture_world(verify_context,'02_restored','WORLD_RESTORED_BEFORE_NATIVE.json')
            comparison=persistence.compare_world_semantics(world,restored_world,geometry_tolerance=1e-5)
            write(output/'WORLD_RESTORE_COMPARISON.json',comparison)
            summary['world_restore_semantics_verified_before_owner']=True
        launcher = load('puente/run_live_native_C02_R02.py', '_C02_closed_preflight')
        need(launcher.preflight(destination, ledger, CUTOFF, config_path)[3] == life, 'Wrong preflight life')
        try: existing = health()
        except (OSError, http.client.HTTPException, ValueError): existing = None
        need(existing is None, 'Existing loopback listener; reconcile before writer')
        write(output / 'BEFORE.json', {'card': card, 'ledger': read(ledger), 'scope': scope, 'resume': bool(args.world_checkpoint)})
        stream = owner_log.open('xb'); streams.append(stream)
        command = [sys.executable, '-I', '-B', '-X', 'utf8', '-u', str(ROOT/'puente/run_live_native_C02_R02.py'), '--destination', str(destination), '--ledger', str(ledger), '--native-cutoff-utc-epoch', str(CUTOFF), '--config', str(config_path)]
        owner = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        note('ONE_OWNER_STARTED', pid=owner.pid, command=command)
        deadline = time.monotonic()+600
        while True:
            need(owner.poll() is None, 'Owner ended before health')
            try: ready = health()
            except (OSError, http.client.HTTPException, ValueError): ready = None
            if ready: break
            need(time.monotonic() < deadline, '600s health deadline; no retries'); time.sleep(.5)
        no_idle=load('control/verificar_no_idle_C02_R04.py','_C02_bounded_cached_observer_R04')
        observation=no_idle.observe(lambda:owner_meta(destination,life),lambda:owner.poll()is None,
                                    card['physical'],args.no_idle_seconds,maximum_seconds=75)
        observation.update(service_source_sha256=actor_sha,
                           inherited_proof=str(args.initial_no_idle_proof)if args.initial_no_idle_proof else None)
        # Durably record both sides BEFORE the assertion, including failure.
        write(output/'NO_IDLE_OBSERVACIONES.json',observation)
        need(observation['passed'],'Cached no-idle observation failed: '+observation['reason'])
        write(output/'NO_IDLE.json',observation)
        stream = relay_log.open('xb'); streams.append(stream)
        relay = subprocess.Popen([sys.executable, '-I', '-B', '-X', 'utf8', '-u', str(ROOT/'control/studio_mailbox_relay_C02_R02.py'), '--config', str(config_path), '--studio-id', args.studio_id, '--seconds', str(min(32400,max(5,int(HARD_FINISH-time.time())-10))), '--evidence', str(relay_events), '--stop-file', str(relay_stop)], cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        deadline = time.monotonic()+600
        while not relay_observation(relay_events).get('connected'):
            need(owner.poll() is None and relay.poll() is None, 'Owner/relay exited before start')
            need(time.monotonic()<deadline, '600s relay deadline; no start retry'); time.sleep(.5)
        write(output/'START_NATIVE_INTENT.json', dict(utc=utc(), studio_id=args.studio_id, command='START_NATIVE', single_attempt=True, replay_allowed=False, resume=bool(args.world_checkpoint)))
        try: summary['start_reply'] = mcp('execute_luau', dict(datamodel_type='Client', code=client_control('START_NATIVE')), '03_start_native_once', 120)
        except BaseException as error: summary['start_unknown_preserved'] = type(error).__name__; note('START_UNKNOWN_NO_REPLAY', error_type=type(error).__name__)
        monitor(); summary['status']='OWNER_EXITED_AWAITING_PROOF'
    except BaseException as error:
        summary.update(status='FAILED_PRESERVED', error_type=type(error).__name__, error=str(error)); note('EXCEPTION_PRESERVED', error_type=type(error).__name__)
        save_close('ORCHESTRATOR_EXCEPTION')
        if owner is not None and owner.poll() is None: monitor()
    finally:
        runner = closure_proof(owner_log, owner.poll() if owner else None, life)
        child = child_closed(destination, life) if runner else None
        proof = runner if child else None
        summary.update(owner_closed=proof is not None, writer_drained=proof is not None, runner_close_report=runner, owned_child_close_evidence=child, owner_returncode=owner.poll() if owner else None)
        if proof:
            write(output/'SOURCE_OWNER_CLOSED.json', dict(schema='DEE.RBX01.C02.closed_owner_witness.R01', lifeId=life, ownerClosed=True, writerDrained=True, exit_code=0, source_journal_event=child, runner=runner))
            try:
                state = bridge_read(database); final_ledger = read(ledger)
                need(state is not None and state['pending']==state['uncertain']==state['unacknowledged_actions']==state['unacknowledged_tools']==0, 'Transport not settled')
                need(final_ledger.get('intent') is None, 'Unresolved Native ledger intent')
                summary['bridge_closed_state']=state; summary['ledger_final']=final_ledger
                card = read(destination/'sistema/estado/vidas'/life/'VIDA.json')
                write(output/'AFTER.json', dict(card=card, ledger=final_ledger, bridge=state))
                boundary = state['boundary']; session=state['session']
                # HTTP shutdown may precede Controller's receipt by one poll.
                # Wait read-only for its actual boundary; do not retry a capture.
                deadline=time.monotonic()+45
                while True:
                    observed=relay_observation(relay_events)
                    event=observed.get('suspended')if session['status']=='SUSPENDED_BOUNDARY'else observed.get('closed')
                    if event:break
                    need(relay is not None and relay.poll()is None and time.monotonic()<deadline,
                         'World boundary not observed; Play preserved without capture retry')
                    time.sleep(.5)
                if session['status']=='SUSPENDED_BOUNDARY':
                    need(boundary and boundary['completed_cycles']==state['feedback_operations_completed'] and boundary['next_opportunity']==boundary['completed_cycles']+1, 'Suspended cursor mismatch')
                    checkpoint_id='C02_'+uuid.uuid4().hex
                    context = dict(checkpoint_id=checkpoint_id, native_life_id=life, native_tick=card['physical']['tick'], bridge=dict(session_id=session['id'], server_id=session['server_id'], phase=session['phase'], pending_count=0, uncertain_count=0, native_ticks_in_session=session['ticks']))
                    world,path,total=capture_world(context,'04_checkpoint','WORLD_CHECKPOINT.json')
                    write(output/'CHECKPOINT_LOCATOR.json',dict(checkpoint_id=checkpoint_id,world_file=str(path),world_sha256=sha(path),bytes=total,native_snapshot_sha256=card['snapshot_sha256'],native_root=str(destination),bridge_database=str(database),native_tick=card['physical']['tick'],complete_pair_not_yet_sealed=True))
                    summary.update(status='SUSPENDED_CLOSED',world_checkpoint=str(path),world_checkpoint_sha256=sha(path),next_opportunity=world['boundary']['next_opportunity'],pair_seal_bind_restore_tested=False)
                else:
                    summary['status']='HORIZON_CLOSED' if session['status']=='STOPPED' and state['feedback_operations_completed']==maximum else 'PARTIAL_CLOSED_PRESERVED'
                    if summary['status']=='HORIZON_CLOSED':
                        checkpoint_id='C02_'+uuid.uuid4().hex
                        context=dict(checkpoint_id=checkpoint_id,native_life_id=life,native_tick=card['physical']['tick'],
                                     bridge=dict(session_id=session['id'],server_id=session['server_id'],phase=session['phase'],
                                                 pending_count=0,uncertain_count=0,native_ticks_in_session=session['ticks']))
                        world,path,total=capture_world(context,'04_final','WORLD_FINAL.json')
                        summary.update(world_final=str(path),world_final_sha256=sha(path),world_final_bytes=total)
            except BaseException as error: summary['closed_export_error']=dict(type=type(error).__name__,message=str(error)); summary['status']='CLOSED_EXPORT_INCOMPLETE_PRESERVED'
        else: summary.update(reconciliation_required=owner is not None,Play_preserved=play,no_other_owner_may_start=owner is not None)
        if relay is not None and proof and relay.poll() is None:
            with relay_stop.open('x',encoding='ascii')as stream:stream.write('ROOT_RELAY_ONLY_STOP\n')
            try:relay.wait(timeout=45)
            except subprocess.TimeoutExpired:summary['relay_stop_pending_no_force_kill']=True
        # Never destroy the sole complete world if checkpoint export failed.
        if proof and play and (relay is None or relay.poll()is not None) and summary.get('status')in('SUSPENDED_CLOSED','HORIZON_CLOSED'):
            try:mcp('start_stop_play',dict(is_start=False),'05_play_stopped');summary['Play_stopped_after_export']=True
            except BaseException as error:summary['play_stop_unknown_preserved']=type(error).__name__
        summary['ended_utc']=utc()
        for stream in streams:stream.close()
        write(output/'RESULTADO.json',summary)
    return summary

def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root-run',action='store_true',required=True)
    for key in('destination','ledger','config','output'):p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--studio-id',required=True);p.add_argument('--suspend-after',type=int,required=True)
    p.add_argument('--target-cycles',type=int,default=36,help='R02 MAIN target36/12 only; Native scope supply48 retained')
    p.add_argument('--world-id',choices=tuple(SCENES),default=WORLD_ID)
    p.add_argument('--expected-place',choices=tuple(SCENES.values()),default=EXPECTED_PLACE)
    p.add_argument('--scenario-sha256',required=True,help='Frozen C.ScenarioFingerprint, separately sealed from Native source scope')
    p.add_argument('--suspend-only',action='store_true',help='Explicit manual sealing/binding after exported closed boundary; driver never auto-packs')
    p.add_argument('--world-checkpoint',type=Path);p.add_argument('--world-checkpoint-sha256')
    p.add_argument('--bound-checkpoint-sha256',help='Exact external hash previously bound offline to bridge, not a self hash')
    p.add_argument('--no-idle-seconds',type=int,default=61);p.add_argument('--initial-no-idle-proof',type=Path)
    return p
if __name__=='__main__':
    print(json.dumps(run(parser().parse_args()),ensure_ascii=False,indent=2))
