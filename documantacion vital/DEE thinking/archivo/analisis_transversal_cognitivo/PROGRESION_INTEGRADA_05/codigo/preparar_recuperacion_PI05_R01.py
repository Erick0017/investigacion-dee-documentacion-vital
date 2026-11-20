"""Seal a recovery diagnostic protocol only; no Native/owner/application."""
from pathlib import Path
import ast,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    runner=H/'ejecutar_RECUPERACION_PI05_R01.py';ast.parse(runner.read_text('utf8'))
    spec=importlib.util.spec_from_file_location('PI05_recovery_calendar_pure',runner);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    source=P/'control/PI05_REAL_FI_GLOBAL_R01.json';packet=json.loads(source.read_text('utf8'));v=packet['actual']['committed_snapshot']['physical']
    actual={k:v[k]for k in('N','tick','RAW_sha256','clocks_sha256')};assert actual['tick']==818074
    guard=H/'FUENTES_GUARDIA_PI05_R01_SELLADAS/capacidades'
    p={'schema':'DEE.PI05.P0_recovery_runner.protocol.R01','status':'PREREGISTERED_BEFORE_NATIVE','runner_sha256':sha(runner),
        'source_physical':actual,'source_adverse_primary':{'file':str(source),'sha256':sha(source),'scope':'Correctness failure, not missing/incoherent world'},
        'dependencies_sha256':{str(f):sha(f)for f in(H/'ejecutar_FI_PI05_R01.py',H/'servicio_ensayo_PI05.py',C/'reproducibilidad/observador_pasivo.py')},
        'guard_module_sha256':sha(guard/'pi05_guardia_transito_R01.py'),'guard_protocol_sha256':sha(guard/'PROTOCOLO_PI05_GUARDIA_R01.json'),
        'conditions':['guardia','sham'],'prepare_ticks':0,'prepare_input_count':1,'FI_inputs':176,'total_native_input_count':177,
        'source_tick':818074,'phase_calendar_rule':'Original FI128 root -19 -> requestedq=start+56; original MU R3P0 391 boundary rule read from inherited metadata. No answer/target arguments.',
        'predicted_calendar_when_existing_phase_guard_enabled':m.planned_calendar(818074,True),
        'maximum_new_Native_ticks_per_arm':600,'wait_ticks':0,
        'functional_response_evaluated_only_after_Native':True,'NULL_is_not_zero':True,
        'scope':'Historical clone diagnosis of operator-preparedP0 support. Guard/sham sameage,dose,calendar; not readquisition/autonomous recovery or adoption.',
        'outcomes_not_assumed':'Both arms may recover with changed phase; no causal support benefit claimed without comparison. No universal67tick revival.'}
    out=P/'control/PROTOCOLO_RECUPERACION_PI05_R01.json';assert not out.exists();out.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'runner':str(runner),'runner_sha256':sha(runner),'protocol':str(out),'protocol_sha256':sha(out),'Native_executed':False,'calendar':p['predicted_calendar_when_existing_phase_guard_enabled']}))
if __name__=='__main__':main()
