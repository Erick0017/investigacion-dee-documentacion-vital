"""Explicit Root operator client for the official StudioMCP stdio interface.

Not part of DEE's actor. No credentials/cookies, Codex config or Native imports.
Arguments are operator-owned JSON; never feed game observations to this client.
Run on the host (outside network-isolated sandbox) to reach the Studio server.
"""
from pathlib import Path
import argparse, base64, hashlib, json, queue, subprocess, threading, time, sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf8')

EXE = Path('C:/Users/Erik/AppData/Local/Roblox/Versions/version-63eb6055af4e4688/StudioMCP.exe')
ALLOWED = {'list_roblox_studios','get_studio_state','inspect_instance','search_game_tree',
           'script_read','script_search','script_grep','get_console_output',
           'execute_luau','multi_edit','start_stop_play','save_place'}
EXPLICIT_LOCAL_R03_ID = '200b7c2c-9c8e-4e51-b296-d1b9ec9087f0'
EXPLICIT_LOCAL_R03_FILE = 'DEE_RBX01_L4_LOCAL_R03.rbxlx'


def select_explicit_studio(found, requested_id, expected_file=None):
    """Other windows are readiness noise, never an alternative target."""
    if expected_file:
        changed = [row.get('id') for row in found
                   if row.get('file') == expected_file and row.get('id') != requested_id]
        if changed:
            raise RuntimeError('Exact local file has a different Studio ID; no mutation. Actual IDs: '+repr(changed))
    target = next((row for row in found if row.get('id') == requested_id), None)
    if target is not None and expected_file and target.get('file') != expected_file:
        raise RuntimeError('Explicit Studio ID has an unexpected file; no mutation')
    return target


def run(tool, arguments, output, seconds, wait_file=None):
    if tool not in ALLOWED or not isinstance(arguments, dict) or not 1 <= seconds <= 300:
        raise ValueError('Closed operator tool or bounded timeout required')
    if output.exists():
        raise FileExistsError('Preserve existing operator result; choose a new output name')
    received = queue.Queue()
    process = subprocess.Popen([str(EXE)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
    stderr_hash = hashlib.sha256(); stderr_bytes = [0]
    def stdout():
        for line in iter(process.stdout.readline, b''):
            try: received.put(json.loads(line))
            except (ValueError, UnicodeError): pass
        received.put({'eof':True})
    def stderr():
        for line in iter(process.stderr.readline, b''):
            stderr_hash.update(line); stderr_bytes[0] += len(line)
    threads = [threading.Thread(target=stdout, daemon=True), threading.Thread(target=stderr, daemon=True)]
    for thread in threads: thread.start()
    deadline = time.monotonic() + seconds; identifier = 0
    def call(method, params=None, notification=False):
        nonlocal identifier
        identifier += 1
        message = {'jsonrpc':'2.0','method':method}
        if not notification: message['id'] = identifier
        if params is not None: message['params'] = params
        process.stdin.write((json.dumps(message,separators=(',',':'))+'\n').encode('utf8'))
        process.stdin.flush()
        if notification: return None
        while time.monotonic() < deadline:
            reply = received.get(timeout=max(.01,deadline-time.monotonic()))
            if reply.get('eof'): raise RuntimeError('Official MCP closed transport')
            if reply.get('id') == identifier: return reply
        raise TimeoutError('Official MCP bounded deadline; do not blindly repeat mutations')
    report = {'schema':'DEE.RBX01.official_MCP_operator_call.C02','tool':tool,
              'arguments':arguments,'Native_imported_by_client':False,'credentials_read':False}
    try:
        initialized = call('initialize', {'protocolVersion':'2025-06-18','capabilities':{},
                            'clientInfo':{'name':'RBX01-Operator','version':'R02'}})
        if 'result' not in initialized: raise RuntimeError('MCP initialization rejected')
        call('notifications/initialized', notification=True)
        discovery_deadline = min(deadline - 5, time.monotonic() + 30)
        descriptor = None
        while time.monotonic() < discovery_deadline:
            listing = call('tools/list', {})
            descriptions = listing.get('result',{}).get('tools',[])
            descriptor = next((v for v in descriptions if v['name']==tool),None)
            if descriptor is not None: break
            time.sleep(.25)
        if descriptor is None: raise RuntimeError('Tool absent: check host network and Studio MCP connection')
        report['tool_schemas'] = descriptions
        report['selected_tool_schema'] = descriptor
        required = descriptor.get('inputSchema',{}).get('required',[])
        if not set(required) <= arguments.keys(): raise ValueError('Required tool arguments: '+repr(required))
        if tool != 'list_roblox_studios':
            ready = False
            inventories = []
            report['discovery'] = inventories
            expected_file = EXPLICIT_LOCAL_R03_FILE if arguments.get('studio_id') == EXPLICIT_LOCAL_R03_ID else None
            while time.monotonic() < discovery_deadline:
                inventory = call('tools/call', {'name':'list_roblox_studios','arguments':{}})
                inventories.append(inventory)
                found = []
                for block in inventory.get('result',{}).get('content',[]):
                    if block.get('type') == 'text':
                        try: found.extend(json.loads(block['text']).get('studios',[]))
                        except (ValueError,AttributeError): pass
                report['actual_inventory'] = found
                if select_explicit_studio(found, arguments.get('studio_id'), expected_file) is not None:
                    ready = True
                    break
                time.sleep(.5)
            report['discovery'] = inventories
            if not ready: raise RuntimeError('No connected target Studio after bounded discovery; no mutation attempted')
        report['reply'] = call('tools/call', {'name':tool,'arguments':arguments})
        if tool == 'list_roblox_studios' and wait_file:
            snapshots = []
            while time.monotonic() < deadline - 3:
                snapshots.append(report['reply'])
                found = []
                for block in report['reply'].get('result',{}).get('content',[]):
                    if block.get('type') == 'text':
                        try: found.extend(json.loads(block['text']).get('studios',[]))
                        except (ValueError,AttributeError): pass
                if any(item.get('file') == wait_file for item in found):
                    break
                time.sleep(.5)
                report['reply'] = call('tools/call', {'name':tool,'arguments':arguments})
            report['bounded_inventory_snapshots'] = snapshots
            report['expected_file'] = wait_file
        for index, block in enumerate(report['reply'].get('result',{}).get('content',[])):
            if block.get('type') == 'image':
                raw = base64.b64decode(block.pop('data'), validate=True)
                suffix = '.png' if block.get('mimeType') == 'image/png' else '.jpg'
                image_path = output.with_name(output.stem+'_image_'+str(index)+suffix)
                image_path.write_bytes(raw)
                block.update(local_image=str(image_path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
        report['status'] = 'TOOL_ERROR' if report['reply'].get('result',{}).get('isError') else 'REPLIED'
    except BaseException as error:
        report.update(status='FAILED_PRESERVED',error_type=type(error).__name__,error=str(error),
                      no_automatic_retry=True)
        raise
    finally:
        process.stdin.close()
        try: process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.terminate(); process.wait(timeout=3)
        for thread in threads: thread.join(timeout=.2)
        report.update(stderr_bytes=stderr_bytes[0],stderr_sha256=stderr_hash.hexdigest(),mcp_exit_code=process.returncode)
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return report


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool',choices=sorted(ALLOWED),required=True)
    parser.add_argument('--arguments',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--timeout',type=int,default=60)
    parser.add_argument('--wait-file',default=None)
    args=parser.parse_args()
    result=run(args.tool,json.loads(args.arguments.read_text('utf-8-sig')),args.output,args.timeout,args.wait_file)
    print(json.dumps({'status':result['status'],'tool':args.tool,'output':str(args.output),
                      'result':result.get('reply',{}).get('result')},ensure_ascii=False)[:16000])
