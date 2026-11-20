"""External calculation of the frozen DIRECT panel; no DEE import or rollout.

CTX and ORDER remain conventional-only cohorts and are never represented as
executed native comparisons. Extra native revision requests remain explicit.
"""
from __future__ import annotations
import collections,hashlib,json,os,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src/comparadores'))
from evaluate_common import evaluate_file


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);pending=path.with_name(path.name+'.pending.'+str(os.getpid()))
    pending.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n');os.replace(pending,path)
def summed(rows):
    statuses=collections.Counter()
    for row in rows:statuses.update(row.get('status_counts',{}))
    return {'planned_queries':sum(x['planned_queries'] for x in rows),'measured_queries':sum(x['measured_queries'] for x in rows),
            'valid_responses':sum(x['valid_responses'] for x in rows),'correct':sum(x['correct'] for x in rows),
            'absent_or_invalid':sum(x['absent_or_invalid'] for x in rows),'not_measured':sum(x['not_measured'] for x in rows),
            'status_counts':dict(statuses),
            'nonvalid_scope':'Legacy aggregate of unavailable valid response; admission rejection, invalid decoder, abstention and missing measurement retain their own status_counts and primary query rows.'}


def main():
    fixed=ROOT/'configuraciones/comparadores/fixtures_v1';dest=ROOT/'resultados/comparadores';cases=[];pending=[]
    methods=('ordinary','double_teacher','symmetric_counterflow')
    for method in methods:
        for seed in (101,211):
            for mode in ('paired','unpaired','virgin'):
                cid=f'DIR_{seed}_{mode}';primary=ROOT/'resultados/native_direct'/(method+'_'+cid)/'MEASUREMENTS.json'
                if not primary.exists():pending.append(str(primary.relative_to(ROOT)).replace('\\','/'));continue
                m=read(primary);v=evaluate_file(primary,fixed/'RESERVED'/cid/'STREAM.json',fixed/'RESERVED'/cid/'EVALUATOR.json')
                sourcecalls=m['calls'];rr=m['receipts'];aux=[c for c in sourcecalls if c['port'].startswith('revision.')]
                v.update(method=method,model_family='DEE',primary=str(primary.relative_to(ROOT)).replace('\\','/'),
                    native_world_resources_reported=m['resources'],
                    physical_inputs={'requested':len(sourcecalls),'statuses':dict(collections.Counter(r['status'] for r in rr)),
                    'auxiliary_requests':len(aux),'auxiliary_payload_sum':sum(c['payload'] for c in aux),
                    'auxiliary_zero_payload_requests':sum(c['payload']==0 for c in aux),
                    'warning':'Zero payload does not imply no physical effect; extra requests are not free and are not in the common logical base stream.'},
                    common_base_stream_identical=True,no_additional_native_revision_requests=not bool(aux),
                    physical_dose_equal_to_conventional_models='NOT_APPLICABLE_DIFFERENT_IMPLEMENTATIONS')
                path=dest/('NATIVE_COMMON_'+method+'_'+cid+'.json');put(path,v);cases.append(v)
    for profile in ('B1_FINAL','B2_FINAL','B2_NO_REPLAY'):
        for seed in (101,211):
            for mode in (('paired',) if profile=='B2_NO_REPLAY' else ('paired','unpaired','virgin')):
                cid=f'DIR_{seed}_{mode}';primary=dest/profile/cid/'TRAJECTORY.json'
                if not primary.exists():pending.append(str(primary.relative_to(ROOT)).replace('\\','/'));continue
                m=read(primary);v=evaluate_file(primary,fixed/'RESERVED'/cid/'STREAM.json',fixed/'RESERVED'/cid/'EVALUATOR.json')
                v.update(method=profile,model_family='CONVENTIONAL',primary=str(primary.relative_to(ROOT)).replace('\\','/'),
                    conventional_training_resources={k:m['resources'][k] for k in ('training_events_seen','training_examples','gradient_steps','gradient_examples','replay_examples','stored_examples','parameter_scalars')},
                    common_base_stream_identical=True,no_additional_native_revision_requests=None,
                    physical_dose_equal_to_conventional_models='NOT_APPLICABLE_DIFFERENT_IMPLEMENTATIONS')
                cases.append(v)
    aggregates=[]
    for method in methods+('B1_FINAL','B2_FINAL','B2_NO_REPLAY'):
        for mode in ('paired','unpaired','virgin'):
            cohort=[c for c in cases if c['method']==method and c['mode']==mode]
            if not cohort:continue
            performance=summed([c['performance'] for c in cohort]);performance['accuracy_all_measured']=performance['correct']/performance['measured_queries'] if performance['measured_queries'] else None
            performance['coverage_among_measured']=performance['valid_responses']/performance['measured_queries'] if performance['measured_queries'] else None
            aggregates.append({'method':method,'mode':mode,'preparations':len(cohort),'input_histories':len({c['stream_sha256'] for c in cohort}),
                'performance':performance,'retention':{key:summed([c['retention'][key] for c in cohort]) for key in ('old8_after_new8','revised_L01','other15_after_revision')},
                'budgets':{'within_measured_limits':sum(c['resources_common_bounds']['within_both_measured_limits'] is True for c in cohort),
                  'unmeasured_resource_cases':sum(c['resources_common_bounds']['within_both_measured_limits'] is None for c in cohort),
                  'wall_seconds_sum':sum(c['resources_common_bounds']['wall_seconds'] or 0 for c in cohort),
                  'peak_worker_rss_bytes':max((c['resources_common_bounds']['peak_process_working_set_bytes'] or 0 for c in cohort),default=0),
                  'wall_limit_seconds_per_preparation':120,'rss_limit_bytes_per_preparation':256*1024**2},
                'auxiliary_requests':sum(c.get('physical_inputs',{}).get('auxiliary_requests',0) for c in cohort)})
    value={'schema':'CPC7.review.common_method_comparison.v1','generated_utc':datetime.now(timezone.utc).isoformat(),
        'comparison_task':'DIRECT_ONLY','native_context_or_order_executed':False,'cases_compared':len(cases),'pending_primary_paths':pending,
        'aggregates':aggregates,'cases':cases,'calculation_source_sha256':sha(__file__),
        'lectura_provisional':[
          'En este panel finito, B1 resolvió las80 consultas emparejadas mediante memoria de claves observables adquirida. Es un comparador útil y no se provocó su fallo para favorecer a DEE.',
          'DEE ordinario conservó las otras15 correspondencias después de la revisión, pero las dos consultas de la relación revisada fueron rechazadas por ocupación del puerto. B2 con replay obtuvo el mismo78/80 por una causa distinta: emitió la clase anterior en esas dos consultas. Rechazo de entrada, ausencia, lectura inválida e incorrección no son el mismo dato.',
          'Los dos métodos nativos auxiliares actualizaron la relación solicitada y conservaron las otras15 en las dos historias. Uno añadió un segundo portador docente; el otro añadió dos pulsos contraflujo de carga cero con realización v27. Son protocolos preparados, no elecciones reguladoras autónomas demostradas.',
          'B2 sin replay actualizó la clave revisada en ambas historias y conservó19/30 de las otras claves, frente a30/30 con replay. Es una disyuntiva local de este modelo y presupuesto, no un límite de las redes neuronales.',
          'Los controles sin experiencia o desacoplados no produjeron respuesta válida en B1 ni en los tres protocolos DEE. B2 emitió clases desde su inicialización y acertó40/80 en cada control; esos aciertos no se atribuyen a adquisición.',
          'Los límites de tiempo y memoria fueron comunes, pero las representaciones, persistencia y operaciones internas no son equivalentes. No se midió electricidad y no se formula una ventaja universal de arquitectura.',
          'Las cohortes convencionales de contexto y orden no tienen un brazo nativo ejecutado en esta tabla. La trayectoria central endógena conserva su propio criterio e historia y se analiza por separado.'
        ],
        'comparison_limits':['Two reserved input histories per method/mode; queries are not independent statistical replicates.',
          'The extra native methods repeat a teacher or add two counterflow requests. Their base stream is common but physical exposure/resources differ from the ordinary/B1/B2 arms.',
          'All methods retain absent, rejected and invalid readings; no alternate decoder was introduced by this calculation.',
          'The120second/256MiB limits are common measured eligibility bounds, not a claim of equal computation, equivalent internal state, or universal advantage.',
          'CTX/ORDER conventional results are indexed separately and not entered into this native table.',
          'The endogenous integrated central trajectory has different interaction history and is not a competitive row in this fixed-stream panel.',
          'No electrical power or energy consumption was measured.']}
    put(ROOT/'revision/COMPARACION_METODOS.json',value)
    print(json.dumps({'compared':len(cases),'pending':len(pending),'native':sum(c['model_family']=='DEE' for c in cases)}))


if __name__=='__main__':main()
