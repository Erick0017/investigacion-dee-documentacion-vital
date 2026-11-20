"""Ask the authenticated local service to exit only a known failed boot; no Native."""
from pathlib import Path
import argparse
import json
import sys
import urllib.request
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sdk_common import RUNTIME, IDENTIFIER, atomic, canonical, instance_home, read

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--instance', required=True)
    p.add_argument('--operation-id', required=True); a = p.parse_args()
    if IDENTIFIER.fullmatch(a.operation_id) is None: raise ValueError('Explicit administrative operation ID')
    home,cfg = instance_home(a.instance); connection = read(RUNTIME / 'configuracion/CONEXION_PRIVADA.json')
    payload = {'instanceId':a.instance,'operationId':a.operation_id,'sessionId':cfg['sessionId']}
    # Intent is durable before the only POST. A timeout is not retried.
    atomic(home / ('STOP_FAILED_HTTP_INTENT_' + a.operation_id + '.json'), payload, new=True)
    req = urllib.request.Request('http://127.0.0.1:' + str(connection['port']) + '/v1/admin/stop-failed',
        data=canonical(payload).encode('utf8'), method='POST',
        headers={'Authorization':'Bearer '+connection['token'],'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=15) as response: value=json.load(response)
    atomic(home / ('STOP_FAILED_HTTP_REPLY_' + a.operation_id + '.json'), value, new=True)
    print(canonical(value))
