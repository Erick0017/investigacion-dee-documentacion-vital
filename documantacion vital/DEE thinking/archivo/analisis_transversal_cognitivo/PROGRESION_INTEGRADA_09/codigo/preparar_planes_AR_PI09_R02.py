"""Create four prospectively fixed documentary plans; stdlib, Native0."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, importlib.util, json

P = Path(__file__).resolve().parents[1]
P8 = P.parent/'PROGRESION_INTEGRADA_08'


def info(path):
    return {'path': str(path), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    source = P/'codigo/pi09_aritmetica_diagnostica_R01.py'
    spec = importlib.util.spec_from_file_location('F1_pure_forecast', source)
    f1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(f1)
    source_system = P8/'estados/C_R03/sistema'
    pins = {str(source): info(source)['sha256']}
    dependencies = [source_system/'capacidades'/name for name in (
        'aritmetica_directa_eci02.py', 'aritmetica_apd_01.py',
        'percepcion_cruda_fi01.py', 'mente_unificada_01.py')]
    pins.update({str(p): info(p)['sha256'] for p in dependencies})
    variants = [('AR0',0,True), ('AR36',36,True), ('AR64',64,True), ('AR0NOD',0,False)]
    manifests = []
    for name, wait, detailed in variants:
        steps = []
        tick = 884835
        for i, (op,left,right,label,normative) in enumerate((
            ('suma',6,7,'SUM_DEVELOP_6_7',13),
            ('suma',4,5,'SUM_RESERVED_4_5',9),
            ('suma',8,3,'SUM_RESERVED_8_3',11),
            ('diferencia',0,2,'DIF_ACTUAL_PREVIOUS_MINUS2',9))):
            literal = {'modo':'eci01-pi09-aritmetica' if detailed else 'eci01-aritmetica-directa',
                       'operacion':op,'izquierda':left,'derecha':right}
            if detailed: literal['espera'] = wait
            forecast = f1.forecast(tick, wait, True)
            step = {'label':label, 'literal':literal, 'max_ticks':208+wait,
                    'read_path':['result','rows',0,'numeric_result'],
                    'expected':normative,
                    'evaluator_expected_never_entered_actor':True,
                    'prospective_calendar':forecast,
                    'data_status':'development' if i==0 else 'reserved_before_Native'}
            if i == 3:
                step['actual_integer_binding'] = {'from_step':'SUM_RESERVED_8_3','field':'izquierda'}
                step['scope'] = ('Placeholder left0 is replaced only by the previous actual integer; '
                                 'NULL/noninteger stops without transport. Expected9 is evaluator-only '
                                 'normative chain criterion, not an independent subtraction failure claim.')
            steps.append(step)
            tick = forecast['predicted_native_pair_end_tick']
        plan = {
            'schema':'DEE.PI09.F1.prospective_arithmetic_phase_plan.R02',
            'prepared_utc':datetime.now(timezone.utc).isoformat(),
            'tag':'PI09_'+name+'_R02', 'system':str(P/'estados'/name/'sistema'),
            'life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_'+name+'_01',
            'initial_tick':884835, 'steps':steps, 'pins':pins,
            'source_life':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01',
            'source_tick':884835,
            'source_proof':str(P8/'control/PI08_C_EVALUAR_R04.json'),
            'source_proof_sha256':info(P8/'control/PI08_C_EVALUAR_R04.json')['sha256'],
            'source_full_pair_manifest':info(P/'pares/C_HEREDADA_T884835/EXPORTACION_SERVICIO.json'),
            'wait_applied_before_each_operation':wait,
            'detailed':detailed, 'reader_site':[12,17,18],
            'reader_direction':[1,-1,-1], 'reader_tick':'actual datum_tick-2',
            'comparison':('AR0 vs AR0NOD instrument comparison on complete matched source; '
                          'AR0/36/64 same four operations with fixed per-call waits. '
                          '391/782 phases change along with67: this does not isolate one modulus.'),
            'no_new_material_input_for_wait':True,
            'no_target_based_reader_or_calendar_selection':True,
            'no_auto_retry_or_restore':True,
            'Native_execution_by_this_preparer':0,
            'phase':'PREPARED_NO_NATIVE_EXECUTION', 'revision_reason':'Root exact transport allowlist IDs before any Native; R01 preserved unexecuted', 'prior_preparer_sha256':'f6772cfde8ca15aae4d9f21631371240fc8a1237cd4728d0f76216997249bf80'}
        path = P/'codigo'/('PLAN_'+name+'_R02.json')
        with path.open('x',encoding='utf-8') as stream:
            json.dump(plan,stream,ensure_ascii=False,indent=2);stream.write('\n')
        manifests.append(info(path))
    result = {'schema':'DEE.PI09.F1.four_plans_prepared.R02', 'plans':manifests,
              'Native':0, 'DEE_imports':0, 'worlds_planned':4,
              'future_results_claimed':False,
              'raw_clock_agenda_receipt_instrument_comparison':'Root must compare actual AR0 and AR0NOD physical/causal fields; no passivity assumed.'}
    path = P/'fuentes/PLANES_AR_PREPARADOS_PI09_R02.json'
    with path.open('x',encoding='utf8') as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__': main()
