"""Synthetic auditor-only fixtures, not a native run or measured hour."""
import argparse,copy,importlib.util,json
from pathlib import Path
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    path=Path(__file__).with_name('recalcular_tiempo_reserva_apd02.py');spec=importlib.util.spec_from_file_location('synthetic_time_audit',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    base={'pid':101,'epoch':8,'runtime_loads_in_this_process':1,'running':True,'paused':False,'tick':100,'idle_ticks':50,'wall_utc':'2026-01-01T00:00:01+00:00','uncertain_external_result':False}
    last={**base,'tick':300,'idle_ticks':150,'wall_utc':'2026-01-01T00:59:51+00:00'}
    x={'initial':{'life_id':'FIXTURE','world_id':'FIXTURE','snapshot_sha256':'a'*64},'final':{'life_id':'FIXTURE','world_id':'FIXTURE'},'owner_initial':{**base,'paused':True},'owner_final':{**last,'paused':True,'running':False},'owner_samples':[{'seconds':0,'owner':base},{'seconds':3590,'owner':last}],'resume':{'finished_execution_utc':'2026-01-01T00:00:01+00:00'},'pause':{'started_utc':'2026-01-01T01:00:01+00:00'},'enabled_seconds':3600.1,'host_seconds':3620,'records':{},'new_ticks_before_start':0,'sources_unchanged':True,'owner_returncode':0,'pending':[],'job_before_cleanup':{'job_active_processes':0,'cpu_user_seconds':2.,'cpu_kernel_seconds':1.,'job_memory_limit':536870912}}
    protocol={'life':'FIXTURE','snapshot_sha256':'a'*64,'enabled_seconds':3600,'one_owner_required':True,'idle_quantum_ticks':1}
    logs=[{'id':str(j),'payload':{'operacion':op},'enabled_seconds':time}for j,(op,time)in enumerate([('reanudar',None),('pausar',3600.1),('exportar',3601),('detener',3610)])]
    cases=[]
    def test(name,y,expected,clean=None):
        r=m.calculate(y,protocol,logs);ok=r['hour_criterion_supported']==expected and(clean is None or r['clean_closure_separate']['supported']==clean);cases.append({'name':name,'ok':ok,'hour_supported':r['hour_criterion_supported'],'issues':r['issues'],'clean_closure_supported':r['clean_closure_separate']['supported']})
    test('synthetic_positive_not_actual_hour',copy.deepcopy(x),True,True)
    y=copy.deepcopy(x);y['owner_samples'][1]['owner']['paused']=True;test('unexpected_pause_not_hour',y,False)
    y=copy.deepcopy(x);y['owner_samples'][1]['owner']['pid']=202;test('two_owners_not_summed',y,False)
    y=copy.deepcopy(x);y['owner_samples'][1]['owner']['tick']=100;test('no_tick_progress_not_vacuous',y,False)
    y=copy.deepcopy(x);y['owner_samples'][1]['owner']['idle_ticks']=50;test('closure_idle_cannot_fill_window',y,False)
    y=copy.deepcopy(x);y['owner_samples'][1]['owner']['running']=False;test('sample_stopped_rejects_hour',y,False)
    y=copy.deepcopy(x);y['enabled_seconds']=3599;test('short_duration_not_hour',y,False)
    y=copy.deepcopy(x);y['forced_own_job_close']=True;test('hour_not_same_as_clean_close',y,True,False)
    y=copy.deepcopy(x);y['job_before_cleanup'].pop('cpu_user_seconds');r=m.calculate(y,protocol,logs);cases.append({'name':'absent_CPU_is_not_measured','ok':not r['resources']['cpu_integral_measured_from_owned_job']})
    result={'synthetic_fixtures_only':True,'new_native_ticks':0,'cases':cases,'issues':[v['name']for v in cases if not v['ok']]}
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'cases':len(cases),'issues':result['issues'],'new_native_ticks':0}));return bool(result['issues'])
if __name__=='__main__':raise SystemExit(main())
