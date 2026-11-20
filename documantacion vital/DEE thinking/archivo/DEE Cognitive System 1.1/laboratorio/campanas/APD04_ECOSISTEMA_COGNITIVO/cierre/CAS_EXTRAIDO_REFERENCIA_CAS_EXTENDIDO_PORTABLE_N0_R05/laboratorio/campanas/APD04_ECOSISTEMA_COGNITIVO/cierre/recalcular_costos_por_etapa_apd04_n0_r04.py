"""Recálculo N0 de costes desde primarios indexados CAS; sin motor ni cronometraje nuevo."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path


def digest(data): return hashlib.sha256(data).hexdigest()
def dump(path,value):
    with path.open('x',encoding='utf8',newline='\n') as f:
        json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2); f.write('\n')


def calculate(cas, comparator=None, source_index=None, source_root=None):
    index_bytes=(source_index or cas/'RUTAS_Y_HASHES.json').read_bytes()
    index=json.loads(index_bytes); sources={r['source_original']:r for r in index['sources']}
    used={}; rows=[]; aliases=[]
    def read(name):
        r=sources[name]; data=((source_root/name) if source_root is not None else (cas/r['object'])).read_bytes()
        assert digest(data)==r['sha256'] and len(data)==r['bytes']
        used[name]={'source_original':name,'cas_object':r['object'],'sha256':r['sha256'],'bytes':r['bytes']}
        return gzip.decompress(data) if name.endswith('.gz') else data
    def resource(identifier,stage,name,j,wall=None,scope='OUTER_JOB',parent=None,pointer='/',note=None):
        cpu=[j.get('cpu_user_seconds'),j.get('cpu_kernel_seconds')]
        rows.append({'id':identifier,'stage':stage,'scope':scope,'parent_cost_row':parent,
            'source':name,'json_pointer':pointer,'wall_seconds':wall,
            'cpu_user_seconds':cpu[0],'cpu_kernel_seconds':cpu[1],
            'cpu_total_seconds':sum(cpu) if all(v is not None for v in cpu) else None,
            'peak_job_committed_bytes':j.get('peak_job_committed_bytes'),
            'peak_process_committed_bytes':j.get('peak_process_committed_bytes'),
            'actual_worker_peak_working_set_bytes':j.get('actual_worker_peak_working_set_bytes'),
            'job_memory_limit_bytes':j.get('job_memory_limit',j.get('memory_limit_bytes')),
            'job_total_processes':j.get('job_total_processes'),'job_active_processes_at_sample':j.get('job_active_processes'),
            'logical_IO_class8':j.get('job_io_class8'),'physical_disk_bytes':None,
            'energy':'NO_MEDIDA','not_additive_to_parent_or_overlapping_rows':True,'note':note})
    seen={}
    for name,r in sources.items():
        if not name.endswith(('.json','.json.gz')): continue
        is_outer=(name.endswith('/RESULTADO_SUPERVISION.json') or name.endswith('/SUPERVISION.json.gz')
             or name.endswith('/WRAPPER_RESULTADO_SUPERVISION.json.gz') or name.endswith('/WRAPPER_RESULT.json.gz'))
        is_worker=name.endswith('/RECURSOS_DRIVER.json') or name.endswith('/08_RECURSOS_DRIVER.json')
        if not(is_outer or is_worker): continue
        obj=json.loads(read(name))
        if r['sha256'] in seen:
            aliases.append({'source':name,'same_exact_bytes_as_row':seen[r['sha256']]}); continue
        if is_outer and 'final_total_job' in obj:
            ident='outer_'+str(len(rows)); seen[r['sha256']]=ident
            resource(ident,name.split('/')[-2],name,obj['final_total_job'],obj.get('actual_wall_seconds'),pointer='/final_total_job',
                note='This exact Job and descendants; include launcher/driver/polling and children. Do not add its Native subtree or per-event deltas.')
            rows[-1].update(exit_code=obj.get('exit_code'),monitor_cpu_ns=obj.get('monitor_cpu_ns'),job_name=obj.get('job_name'))
        elif is_worker and 'cpu_user_seconds' in obj:
            ident='worker_'+str(len(rows));seen[r['sha256']]=ident
            resource(ident,name.split('/')[-2],name,obj,scope='ACTUAL_WORKER_OWNED_JOB_RECORDED',
                note='Worker-owned Job aggregate at recorded sample. Wall absent. Parent relationship not sufficient to add this to another job. Do not equate worker Job with one CPU core.')
            rows[-1].update(job_name=obj.get('self_job_name'),parent_job_checked=obj.get('parent_job_checked'))
    for name in sources:
        if not(name.endswith('/TRAYECTORIA/RESULTADO.json') or name.endswith('/PRIMARIOS/DRIVER_RESULT.json.gz')):continue
        obj=json.loads(read(name));j=obj.get('final_native_job')
        if not isinstance(j,dict):continue
        resource('native_'+str(len(rows)),name.split('/')[-3],name,j,scope='NESTED_NATIVE_JOB',pointer='/final_native_job',
            note='Nested subtree, not additive to enclosing outer Job. Wall for Native-only scope was not separately measured.')
        rows[-1].update(driver_wall_seconds_including_host=obj.get('driver_wall_seconds'),
            driver_self_cpu_seconds=obj.get('driver_cpu_ns',0)/1e9 if obj.get('driver_cpu_ns') is not None else None,
            owner_stop_confirmed=obj.get('owner_stop_confirmed'))
    event_name=next(n for n in sources if n.endswith('MAIN_ADQUISICION_R01/TRAYECTORIA/EVENTOS.jsonl'))
    events=[json.loads(x) for x in read(event_name).splitlines() if x]
    first=next(e for e in events if e['kind']=='owner_started_paused')
    resource('MAIN_ACQUISITION_STARTUP','startup',event_name,first['native_job'],first['driver_seconds'],
        'NESTED_NATIVE_CUMULATIVE_AT_START',pointer='/JSONL/seq='+str(first['seq']),
        note='Wall is driver start through owner started paused; CPU and peaks belong to Native cumulative Job at that point, not a standalone fresh-machine startup benchmark.')
    for e in events:
        if e['kind']!='scheduled_material_result':continue
        before=e.get('native_job_before',{});after=e.get('native_job_after',{})
        rid=e.get('requested_id');phase='teaching' if 'lesson_' in str(rid) else 'retention_use' if 'retained_' in str(rid) else 'prior_knowledge_panel' if 'old_panel' in str(rid) else 'new_signal_use' if 'first_' in str(rid) else 'environmental_use_or_preparation'
        delta={}
        for key in ('cpu_user_seconds','cpu_kernel_seconds'):
            delta[key]=after[key]-before[key] if key in before and key in after else None
            assert delta[key] is None or delta[key]>=0
        if all('job_io_class8' in x for x in (before,after)):
            delta['job_io_class8']={k:after['job_io_class8'][k]-before['job_io_class8'][k] for k in before['job_io_class8']}
        resource('MAIN_EVENT_'+str(e['seq']),phase,event_name,delta,e.get('elapsed_ns',0)/1e9 if e.get('elapsed_ns') is not None else None,
            'NESTED_NATIVE_INTERVAL_DELTA',parent='MAIN acquisition outer Job',pointer='/JSONL/seq='+str(e['seq']),
            note='Same Native Job before/after one material transaction. Host wall includes queue/wait/commit; CPU delta excludes unrelated outer polling. Disjoint intervals within this journal, nested in acquisition total. Peak RAM cannot be differenced.')
        rows[-1].update(request_id=rid,peak_job_committed_cumulative_after=after.get('peak_job_committed_bytes'),
            peak_process_committed_cumulative_after=after.get('peak_process_committed_bytes'))
    rows.append({'id':'COMPLETE_IMPORT_N0','stage':'copy_import','scope':'ADMINISTRATIVE_N0_NOT_TIMED',
        'wall_seconds':None,'cpu_total_seconds':None,'peak_job_committed_bytes':None,'energy':'NO_MEDIDA',
        'source':None,'note':'No separate chronometer for complete copy/import is present in this selected CAS. N0 means no Native ticks, not zero CPU cost.'})
    if comparator is not None:
        b=comparator.read_bytes();obj=json.loads(b)
        comparator_name='laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/controles_diseno/REFERENCIAS_CUATRO_NIVELES_CERRADO_R03/RESULTADOS_Y_RECURSOS.json'
        used[comparator_name]={'source_original':comparator_name,'sha256':digest(b),'bytes':len(b),'outside_CAS_explicit_locator':True}
        reports=obj['reports']; before=obj['whole_process_resources_before'];after=obj['whole_process_resources_after']
        summary=[]
        for dose in sorted({r['config']['dose_arm'] for r in reports}):
            for n in sorted({r['config']['sources'] for r in reports}):
                for policy in sorted({r['policy'] for r in reports}):
                    group=[r for r in reports if r['config']['dose_arm']==dose and r['config']['sources']==n and r['policy']==policy]
                    summary.append({'dose_arm':dose,'sources':n,'policy':policy,'trajectories':len(group),
                        'seeds':[r['config']['seed'] for r in group],
                        **{k:sum(r['metrics'][k] for r in group) for k in ('opportunities','useful','correct_classifications','incorrect_classifications','new_facts')}})
        rows.append({'id':'COMPARATOR_REFERENCE','stage':'external_reference_executor','scope':'REFERENCE_NOT_PHYSICAL_HEAD_TO_HEAD',
            'source':comparator_name,'cpu_total_seconds':obj['whole_process_cpu_ns']/1e9,
            'wall_seconds':obj['whole_process_wall_ns']/1e9,'peak_job_committed_bytes':None,
            'peak_process_committed_bytes':after['peak_committed_process_bytes'],
            'peak_process_working_set_bytes':after['peak_working_set_bytes'],
            'logical_IO_class8':{k:after['logical_IO'][k]-before['logical_IO'][k] for k in before['logical_IO']},
            'trajectories':len(reports),'opportunities':sum(r['metrics']['opportunities'] for r in reports),
            'grouped_scientific_results':summary,'installed_criterion':20,'new_native_ticks':0,'energy':'NO_MEDIDA',
            'note':'48 trajectories with preinstalled20, no acquisition. Executor wall/CPU are not a physical Native comparison or an ability score.'})
    return {'schema':'APD04.costs_by_stage.N0.R01','status':'DRAFT_CLOSED_PRIMARY_SCOPES_ONLY',
        'cas_index_sha256':digest(index_bytes),'rows':rows,'exact_aliases_not_double_counted':aliases,'sources':list(used.values()),
        'rules':{'no_total_summed':True,'outer_plus_nested_forbidden':True,'peak_RAM_not_additive':True,
            'logical_IO_is_not_physical_disk':True,'physical_energy':'NO_MEDIDA',
            'cpu_threads1':'Requested for Native/OMP settings, not an enforced global one-CPU limit for this process tree.',
            'parallelism':'Root reports up to two simultaneous Native owners; the selected scope records do not establish a global CPU-thread cap or per-core attribution.',
            'CPU_wall_not_competence':True,'not_a_campaign_wide_resource_audit':True},'new_Native_ticks':0}


def render(obj):
    lines=['# Costes por etapa APD04: alcances observados','','Recálculo N0 desde primarios ya indexados. No se ejecutaron experimentos ni se midió energía. Las cifras no califican competencia cognitiva.','','## Contabilidad','','No se suman Jobs externos y subárboles Native: se superponen. Los deltas de transacciones MAIN son intervalos interiores del mismo Job. RAM es memoria comprometida de Job/proceso, no memoria física cognitiva; los picos no se suman ni se restan. IO Class8 cuenta operaciones y transferencias lógicas, no bytes escritos físicamente al disco.','','`cpu_threads1` fue una solicitud Native/OMP, no un límite efectivo de una CPU para todo el árbol. Root informa hasta dos propietarios Native simultáneos; no se deduce el máximo de hilos global de estos resúmenes. Energía: **NO_MEDIDA**.','','## Filas con tiempos cuantificados','','| Etapa / alcance | Pared s | CPU s | Pico Job B | Pico proceso B | Fuente |','|---|---:|---:|---:|---:|---|']
    def v(x):return 'no medido' if x is None else str(round(x,6)) if isinstance(x,float) else str(x)
    for row in obj['rows']:
        if row.get('scope')=='ACTUAL_WORKER_OWNED_JOB_RECORDED':continue
        lines.append('|'+str(row.get('stage'))+' / '+str(row['scope'])+'|'+v(row.get('wall_seconds'))+'|'+v(row.get('cpu_total_seconds'))+'|'+v(row.get('peak_job_committed_bytes'))+'|'+v(row.get('peak_process_committed_bytes'))+'|'+str(row.get('source'))+(('#'+row['json_pointer']) if row.get('json_pointer') else '')+'|')
    lines.extend(['','El JSON conserva los campos originales, CPU usuario/kernel, límites, número de procesos, IO y localizadores SHA. Los costes sin cronometraje independiente permanecen null; N0 no significa coste cero. No se extrapola una fila al presupuesto completo de la campaña.'])
    return '\n'.join(lines)+'\n'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cas',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--comparator',type=Path)
    p.add_argument('--source-index',type=Path);p.add_argument('--source-root',type=Path);p.add_argument('--json-only',action='store_true')
    a=p.parse_args();assert not a.out.exists()
    obj=calculate(a.cas,a.comparator,a.source_index,a.source_root)
    if a.json_only:
        dump(a.out,obj);print(json.dumps({'rows':len(obj['rows']),'new_Native_ticks':0}));return
    a.out.mkdir(parents=True);dump(a.out/'COSTOS_POR_ETAPA_APD04.json',obj)
    with (a.out/'COSTOS_POR_ETAPA_APD04.md').open('x',encoding='utf8',newline='\n') as f:f.write(render(obj))
    print(json.dumps({'rows':len(obj['rows']),'sources':len(obj['sources']),'new_Native_ticks':0,'no_global_sum':True}))


if __name__=='__main__':main()
