"""Fixed-codec bidirectional E1/Pendulum trial. No control policy in host."""
from pathlib import Path
import sys,json,subprocess,argparse,time
ROOT=Path(__file__).resolve().parents[3];LAB=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(LAB))
from app.lives import Store
from app.native_tools import physical,observe,moore27,atomic_json,digest_file,exact_receipt
from app.process_control import protect_current
from habitat import qround,decode_action,emit,check_budget
from dee_thinking.persistence import encode_metadata,decode_metadata
EV=ROOT/'evidencia/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01'
PY=r'C:\Users\Erik\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
KEY='DEE.Cognitive.System.1.1.habitat01.external_bridge.v1'
class Worker:
    def __init__(self):self.p=subprocess.Popen([PY,'-I','-B',str(LAB/'external/pendulum_worker.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf8')
    def call(self,op,**kwargs):
        self.p.stdin.write(json.dumps({'op':op,**kwargs})+'\n');self.p.stdin.flush();line=self.p.stdout.readline()
        if not line:raise RuntimeError('External worker died: '+self.p.stderr.read())
        result=json.loads(line)
        if not result['ok']:raise RuntimeError(str(result))
        return result
    def close(self):
        try:self.call('close')
        finally:self.p.wait(timeout=5)

def main():
    p=argparse.ArgumentParser();p.add_argument('--life',required=True);p.add_argument('--name',required=True);p.add_argument('--steps',type=int,default=16);p.add_argument('--seed',type=int,default=71001);p.add_argument('--mode',choices=['closed','nulled','delay1'],default='closed');p.add_argument('--reset-environment',action='store_true');p.add_argument('--g',type=float,default=10.0);args=p.parse_args()
    protect_current();check_budget()
    if args.life=='E1_SOCIAL_11':raise ValueError('Protected parent')
    output=EV/(args.name+'.json')
    if output.exists():raise FileExistsError('Existing trial protected')
    worker=Worker();identity=worker.call('info')
    def run(a):
        entries=dict(a.world.runtime.snapshot_metadata_entries);saved=decode_metadata(entries[KEY])if KEY in entries else None
        if saved and not args.reset_environment:
            bridge=json.loads(saved['bridge_state_json']);initial=worker.call('restore',snapshot=bridge['environment']);obs=initial['observation'];previous=bridge['previous_observation'];index=bridge['index']
        else:
            initial=worker.call('reset',seed=args.seed,g=args.g);obs=initial['observation'];previous=list(obs);index=0
        initial_snapshot=worker.call('snapshot')['snapshot'];rows=[];start=physical(a.world,occupation=True)
        for i in range(args.steps):
            check_budget();k,t,at=qround(a.tick);visible=previous if args.mode=='delay1'else obs
            unbounded=round(73+40*visible[1]);q=max(1,min(145,unbounded))
            a.quantity.present_object(q,round_index=k);requested=[dict(x)for x in a.quantity.state['requests'][-2:]]
            requested.append(emit(a,'quantity.reader',7,at-1,True,'FIXED_EXTERNAL_SENSOR_READER'))
            a.run_until(at);native=observe(a.world,a.quantity.geometry['center']);action=decode_action(native)
            torque=0 if args.mode=='nulled'else action['command'];host_start=time.perf_counter();response=worker.call('step',torque=torque);latency=time.perf_counter()-host_start
            row={'index':index,'tick':a.tick,'observation_before':list(obs),'codec':{'value':q,'unclipped':unbounded,'saturated':q!=unbounded,'delay':1 if args.mode=='delay1'else 0,'discarded':['cos(theta)','angular_velocity'],'no_reward_or_hidden_state_to_E1':True},'native_read':native,'actuator':action,'executed_torque':torque,'environment_response':response,'requests':[exact_receipt(a.world.runtime.receipt(x['id']))for x in requested],'host_worker_seconds':latency,'context':moore27(a.world,a.quantity.geometry['center']),'physical':physical(a.world,occupation=True)}
            with (EV/(args.name+'.rows.jsonl')).open('a',encoding='utf8')as f:f.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n')
            rows.append(row);previous=list(obs);obs=response['observation'];index+=1
            environment=worker.call('snapshot')['snapshot'];bridge={'environment':environment,'previous_observation':previous,'last_observation':obs,'index':index,'mode':args.mode,'ticks_per_step':67,'delay_buffer':previous,'explicit_environment_reset_without_DEE_reset':bool(args.reset_environment)}
            a.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'bridge_state_json':json.dumps(bridge,ensure_ascii=False,allow_nan=False)}))
            if i%8==7:
                cp=ROOT/'sistema/estado/checkpoints'/('ECO_EXTERNAL_BUFFER.'+args.name+'.T'+str(a.tick)+'.deetsnap.gz');a.save(cp)
        return {'condition':vars(args),'identity':identity,'initial_native':start,'initial_environment':{'seed':args.seed,'g':args.g,'reset_or_restore':initial,'snapshot':initial_snapshot},'rows':rows,'final_environment':bridge,'final_native':physical(a.world,occupation=True),'attribution':'Only fixed sin quantization and direction-to-torque transduction. Prepared comparison with inherited material reference, not learned Pendulum policy. Neutral silence is fixed0. No optimal action, hidden state, seed or reward supplied to E1.'}
    try:
        result=Store().mutate(args.life,'HABITAT01_EXTERNAL',run,{'source_sha256':digest_file(__file__),'worker_sha256':digest_file(LAB/'external/pendulum_worker.py'),'condition':vars(args)})
        atomic_json(output,result);print(json.dumps({'life':args.life,'tick':result['INSTRUMENTO']['tick'],'file':str(output)}),flush=True)
    finally:worker.close()
if __name__=='__main__':main()
