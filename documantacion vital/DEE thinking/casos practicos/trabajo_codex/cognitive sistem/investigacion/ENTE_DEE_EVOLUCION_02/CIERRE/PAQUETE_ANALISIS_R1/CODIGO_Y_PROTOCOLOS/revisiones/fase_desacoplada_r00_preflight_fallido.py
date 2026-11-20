"""One post-protocol diagnostic: matched total phase material, wrong timing.

Not a MAIN experience or a prospective repeat of R1. Worker workload remains
two raw values; its actual phase is private environment state. The spoofed
sensor only changes its fixed physical context packet, never the worker law.
"""
from pathlib import Path
import gzip,hashlib,json,os,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EV=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02'
sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from capacidades import ente_evolucion_02 as service,ente_evolucion_02_core as core,eo02_sensor_periferico as sensor
from capacidades import arquitectura_distribuida_mi02_r8 as body
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    protocol=HERE/'PROTOCOLO_FASE_DESACOPLADA44.json'
    if protocol.exists():raise FileExistsError('One finite causal diagnostic only')
    parent=json.loads(gzip.decompress((EV/'24B_RES1_B.json.gz').read_bytes()))['result']['INSTRUMENTO']['snapshot_sha256']
    paths=[p for p in(ROOT/'sistema/estado/checkpoints').glob('EO02_MAIN.T139667.*.gz')if sha(p)==parent]
    if len(paths)!=1:raise ValueError('Exact frozen R1 pre-C complete snapshot required')
    raw=[[1,15],[4,18],[7,21],[13,27],[16,30],[18,32]];bits=[1,0,1,0,1,0]
    protocol.write_text(json.dumps({'revision':'EO02.phase_yoked.1','frozen_monotonic':time.monotonic(),'parent':paths[0].relative_to(ROOT/'sistema').as_posix(),'sha256':parent,'observations_workload':raw,'sensor_phase_bits':bits,'real_R1_bits':[0,1,0,1,0,1],'matching':'Same initial matter/clock/queues, six opportunities, codec routes/ticks, three total phase units; actual consequences may diverge','criterion':'Compare acceptedsteps/wholetransactions with actual phase6/6,3; distinguish information correlation from a lower total numerical dose','not_a_policy_learning_claim':True},indent=2)+'\n',encoding='utf8')
    source=EV/'codigo_experimento'/sha(Path(__file__))
    source.mkdir(parents=True,exist_ok=True);(source/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    s=Store(ROOT/'sistema');rec=s.fork('EO02_MAIN','AUX_EO02_PHASE_YOKED',kind='DIAGNOSTIC_COPY',checkpoint=paths[0].relative_to(ROOT/'sistema'))
    def run(a):
        state=service.saved(a);old=state['environments'].get('transaccion')
        if old is not None:state['closed_environments'].append(old)
        env={'domain':'transaccion','reference':14,'created_at_tick':int(a.tick),'attempts':0,'completed_steps':0,'completed_transactions':0,'pending_transaction':None,'environment_not_cognitive_memory':True,'reset_never_resets_native_state':True,'storage_epoch':'phase_yoked44_'+str(a.tick)}
        state['environments']['transaccion']=env;rows=[]
        for pair,bit in zip(raw,bits):
            actual_phase=int(env.get('pending_transaction')is not None);physical_raw=pair+[0,bit]
            state['inflight']={'domain':'transaccion','raw':physical_raw,'workload':pair,'start_tick':int(a.tick)};service.put(a,state)
            extra=sensor.submit_extra(a,physical_raw)
            adapter=service.LocalEnvironment(env,s.state/'servicios_locales/AUX_EO02_PHASE_YOKED'/env['storage_epoch'],pair,lambda:service.put(a,state))
            result=core.external_episode(a,public=pair,reference=14,environment=adapter)
            extra['request_receipts']=body.receipts(a,extra['requests'])
            result.update({'raw_components':physical_raw,'workload_components':pair,'sensory_extra':extra,'domain':'transaccion','local_service':adapter.last,'phase_visibility':{'enabled':False,'yoked_diagnostic':True,'sensor_bit':bit,'actual_generic_phase_not_injected':actual_phase,'previous_worker_not_injected':True,'no_target_given':True}})
            state['total_attempts']+=1;state['last_tick']=int(a.tick);state['last_domain']='transaccion';state.pop('inflight',None);service.put(a,state);rows.append(result)
        return {'revision':'EO02.phase_yoked.1','rows':rows,'final':service.state(a),'scope':'Prepared sensor ablation with matched total phase material, not acquired phase policy'}
    started=time.monotonic();result=s.mutate('AUX_EO02_PHASE_YOKED','EO02_PHASE_YOKED_DIAGNOSTIC',run,{'protocol_sha256':sha(protocol),'operator_programmed_context_bits_not_native_strategy':True})
    primary={'case':'44_PHASE_YOKED','started_monotonic':started,'elapsed_seconds':time.monotonic()-started,'returncode':0,'stderr':'','result':result,'code_exact_path':str(source/Path(__file__).name),'code_sha256':sha(Path(__file__)),'not_a_MAIN_experience':True}
    with gzip.open(EV/'44_PHASE_YOKED.json.gz','wt',encoding='utf8',compresslevel=6)as f:json.dump(primary,f,ensure_ascii=False,allow_nan=False)
    print(json.dumps({'case':primary['case'],'returncode':0,'ticks_final':result['INSTRUMENTO']['tick'],'elapsed_seconds':primary['elapsed_seconds']}))
if __name__=='__main__':main()
