"""Isolated bounded local worker. It implements a service, never an E1 policy.

Only loopback-free stdin/stdout and a caller-created experiment directory are
used. There is no native-world access, training code, network or controller.
"""
from pathlib import Path
import base64,hashlib,json,sys,time,zlib
def process(q):
    started=time.time_ns();worker=q['executed_worker'];public=q['raw_observations'];left,right=public
    folder=Path(q['output_directory']).resolve(strict=True)
    if worker not in(-1,1):raise ValueError('A real native command must choose one worker')
    if len(public)!=2 or any(type(v)is not int or not 0<=v<=64 for v in public):raise ValueError('Bounded raw service observations')
    # The worker enforces its own modelled eligibility law. It never chooses
    # a route for E1. This particular law is isomorphic to the source task.
    eligible=1 if left+q['capacity_credit']>=right else -1
    pending=q.get('pending_transaction')
    verify=q['domain']=='transaccion'and pending is not None
    if verify:
        payload=base64.b64decode(pending['payload_base64']);digest=hashlib.sha256(payload).hexdigest()
        accepted=worker!=pending['prepared_by']and digest==pending['payload_sha256']
        operation='verify_commit'
    else:
        payload=(bytes((left,right))*max(1,32+left));digest=hashlib.sha256(payload).hexdigest()
        accepted=worker==eligible
        operation='prepare'if q['domain']=='transaccion'else'execute_service'
    output=zlib.compress(payload,9)if worker==1 else hashlib.sha256(payload).digest()
    name='attempt_'+str(q['attempt']).zfill(5)+('_left.zlib'if worker==1 else'_right.sha256')
    path=folder/name
    if path.exists():raise FileExistsError('Preserve earlier service output')
    path.write_bytes(output)
    readback=path.read_bytes();assert readback==output
    transaction_completed=bool(accepted and verify)
    next_pending=pending
    if q['domain']=='transaccion'and accepted:
        next_pending=None if verify else{'prepared_by':worker,'payload_base64':base64.b64encode(payload).decode('ascii'),'payload_sha256':digest,'prepared_at_native_tick':q['native_tick']}
    return{'schema':'EO02.local_worker.receipt.v1','worker':worker,'operation':operation,'accepted':accepted,'transaction_completed':transaction_completed,'pending_transaction':next_pending,'raw_observations':public,'input_bytes':len(payload),'input_sha256':digest,'output_name':name,'output_bytes':len(output),'output_sha256':hashlib.sha256(output).hexdigest(),'read_back_verified':True,'host_started_ns':started,'host_finished_ns':time.time_ns(),'native_tick':q['native_tick'],'modelled_capacity_credit_not_actor_input':q['capacity_credit'],'law_scope':'Modelled admission constraints plus actual bounded local file operation; not hardware throughput or a robot.','decision_origin':'Native material direction supplied by parent; worker never chooses a different route.'}
def main():
    q=json.load(sys.stdin);print(json.dumps(process(q),ensure_ascii=False))
if __name__=='__main__':main()
