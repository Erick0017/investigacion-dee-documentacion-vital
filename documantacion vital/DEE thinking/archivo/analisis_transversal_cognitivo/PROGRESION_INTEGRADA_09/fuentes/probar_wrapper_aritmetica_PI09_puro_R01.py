"""Pures de contrato/orquestación. No Native ni resultados físicos simulados como reales."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import sys

P = Path(__file__).resolve().parents[1]


def main():
    path = P/'codigo/pi09_aritmetica_diagnostica_R01.py'
    imported = []
    def audit(event, args):
        if event == 'import' and str(args[0]).split('.')[0] in {'dee_thinking','app','capacidades','_native'}:
            imported.append(str(args[0])); raise RuntimeError('Forbidden Native import')
    sys.addaudithook(audit)
    spec = importlib.util.spec_from_file_location('pi09_f1_pure_plugin', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    checks = []
    def ok(name): checks.append({'name':name,'passed':True})
    for wait in (0,36,64):
        row = {'modo':'eci01-pi09-aritmetica','operacion':'suma','izquierda':6,'derecha':7,'espera':wait}
        assert module.validate_literal(row) is row
    for mutation in ({'espera':True},{'espera':1},{'izquierda':True},{'izquierda':33},{'target':13}):
        row = {'modo':'eci01-pi09-aritmetica','operacion':'suma','izquierda':6,'derecha':7,'espera':0,**mutation}
        try: module.validate_literal(row)
        except ValueError: pass
        else: raise AssertionError(mutation)
    ok('exact_independent_operand_and_declared_wait_contract')
    source=P.parents[2]/'DEE Cognitive 2.0/sistema/capacidades/mente_unificada_01.py'
    tree=ast.parse(source.read_text(encoding='utf-8'))
    function=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='calendar_query_timing')
    ns={'PHASE_PROTECTION_VERSION':'MUFI01.sensor_calendar.R3P0','VERSION':'MOCK_UNUSED'}
    exec(compile(ast.Module(body=[function],type_ignores=[]),str(source),'exec'),ns)
    for requested in range(2,1175):
        for guard in (True,False):
            old=ns['calendar_query_timing'](requested,guard); new=module.calendar_query_timing(requested,guard)
            assert (old['effective_query_tick'],old['wait_ticks'])==(new['effective_query_tick'],new['wait_ticks'])
    ok('integer_forecast_matches_literal_R3P0_rule_2346_cases')
    forecasts=[module.forecast(884835,w)for w in (0,36,64)]
    assert [x['effective_query_tick']for x in forecasts]==[884891,884927,884955]
    assert [x['query_moduli']['67']for x in forecasts]==[22,58,19]
    ok('fixed_C_source_three_prospective_wait_calendars')
    class Fake:
        def __init__(self): self.tick=884835; self.world=self; self.calls=[]
        def run_until(self,tick): self.calls.append(('legal_wait',tick)); self.tick=tick
    for wait in (0,36,64):
        a=Fake();calls=[]
        def physical(world):return{'N':67,'tick':world.tick,'scope':'MOCK_NO_NATIVE'}
        def pair(adapter,operation,left,right,*,detailed):
            calls.append((operation,left,right,detailed,adapter.tick))
            query=module.forecast(adapter.tick,0)['effective_query_tick'];adapter.tick=query+142
            return{'native_trial':{'query_tick':query},'numeric_reader':{'numeric_result':None,'scope':'MOCK_NULL_NO_EXPECTED_ANSWER'}}
        row={'modo':'eci01-pi09-aritmetica','operacion':'suma','izquierda':6,'derecha':7,'espera':wait}
        value=module._perform(a,row,native_pair=pair,physical=physical,protected=True)
        assert calls==[('suma',6,7,True,884835+wait)]
        assert value['numeric_result']is None and value['legal_wait_advanced']==wait
        assert value['actual_query_moduli']==module.forecast(884835,wait)['query_moduli']
    ok('one_legal_wait_then_literal_native_pair_no_host_result_or_retry')
    assert module.operational_dependencies(None,None)['present']is False
    assert module.uncertain(None)is False
    assert all(isinstance(p,Path)for p in module.code_files())
    ok('startup_stateless_API_does_not_require_Native_or_unprepared_protocol')
    result={'schema':'DEE.PI09.F1.pure_arithmetic_wrapper_tests.R01','all_passed':True,'checks':checks,
            'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'Native_ticks':0,'DEE_imports':imported,
            'fixtures_are_MOCK_NOT_Native':True,'prospective_forecasts':forecasts,
            'scope':'Contract/integer calendar/orchestration only; not Native numerical behavior or observer-passivity validation.'}
    out=P/'fuentes/PRUEBAS_PURAS_WRAPPER_ARITMETICA_PI09_R01.json'
    assert not out.exists();out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'checks':len(checks),'source_sha256':result['source_sha256'],'Native':0,'DEE_imports':imported},ensure_ascii=False))


if __name__=='__main__':main()
