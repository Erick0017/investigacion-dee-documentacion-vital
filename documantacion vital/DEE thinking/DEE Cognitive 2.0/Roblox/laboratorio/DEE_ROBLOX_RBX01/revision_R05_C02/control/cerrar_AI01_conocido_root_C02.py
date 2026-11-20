"""Close only the first, known AI transport failure; preserve its unacked ASK.

No Native import, queue edit, fabricated ACK, inference or decision replay.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, urllib.request, uuid

ROOT = Path(__file__).resolve().parents[1]
SID = '2bfcd7d04b9d497481b7a1ff23b596a2'
SERVER = 'studio_fd3c9be1-321a-48b3-b0b8-bebf9b1670fd'
OP = 'a2ff4f3c9309494aab3367eac9aa5077'

def main():
    p=argparse.ArgumentParser();p.add_argument('--root-run',action='store_true',required=True);p.parse_args()
    output=ROOT/'evidencia/CONVENTIONAL_AI_R06_PERIODO_01'
    intent=output/'ROOT_STOP_CONOCIDO_INTENT.json'
    if intent.exists():raise RuntimeError('Existing stop intent: reconcile, never resend')
    proof=output/'ESTADO_ADVERSO_NO_CONTINUABLE.json'
    if not proof.is_file():raise RuntimeError('Preserved adverse World proof required')
    policy=ROOT/'comparadores/CONVENTIONAL_AI_R06_01/POLICY_STATE_C02.json'
    raw=policy.read_bytes();state=json.loads(raw)
    if state['pending'] is not None or len(state['cache'])!=1 or OP not in state['cache']:
        raise RuntimeError('Only one completed policy decision, no pending operation allowed')
    config=ROOT/'configuracion_privada/conventional_ai_r06.json';c=json.loads(config.read_text('utf8'))
    if c['bind']!='127.0.0.1' or c['port']!=8895:raise RuntimeError('Fixed private loopback only')
    token=(config.parent/c['tokenFile']).read_text('ascii').strip()
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    def request(route,body):
        req=urllib.request.Request('http://127.0.0.1:8895/v1/'+route,
            data=json.dumps(body,separators=(',',':')).encode('ascii'),method='POST',
            headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
        with opener.open(req,timeout=10) as r:return json.load(r)
    base={'apiVersion':'RBX01.C02.v1','sessionId':SID,'serverInstanceId':SERVER}
    before=request('state',dict(base,requestId=uuid.uuid4().hex,operationId=OP))
    if not(before['sessionId']==SID and before['mode']=='CONVENTIONAL_AI' and
        before['status']=='ACTIVE' and before['phase']=='WAIT_ACK_QUERY' and before['seq']==1 and
        before['queueDepth']==0 and before['operation']['status']=='COMPLETED' and before['lastActionId']==OP):
        raise RuntimeError('Actual known completed, unapplied first ASK required')
    body=dict(base,requestId=uuid.uuid4().hex,reason='INFRASTRUCTURE')
    record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request':body,
        'before':before,'policy_before_sha256':hashlib.sha256(raw).hexdigest(),
        'unacknowledged_action_preserved':OP,'Native_calls':0,'inference_calls':0,'replay_allowed':False}
    with intent.open('x',encoding='utf8') as f:json.dump(record,f,ensure_ascii=False,indent=2)
    reply=request('stop',body)
    record['reply']=reply;record['policy_bytes_unchanged']=policy.read_bytes()==raw
    with (output/'ROOT_STOP_CONOCIDO_RESULTADO.json').open('x',encoding='utf8') as f:
        json.dump(record,f,ensure_ascii=False,indent=2)
    print(json.dumps({'status':reply['status'],'preserved':reply['preserved'],
        'unacked_action_not_forged_or_deleted':OP,'Native_calls':0,'model_calls':0}))

if __name__=='__main__':main()
