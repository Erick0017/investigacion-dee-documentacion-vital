import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
spec={'main':'E1_CICLO02_MAIN','before_required_tick':17289,
      'preparation':'Existing comparator phase20, no copied reference',
      'first_forces':[100,2,4,20,8,30,16,40,23],'first_wear':[6,6,6,6,11,11,11,11,11],
      'reserved_after_interleaving':{'forces':[31,45,12,55,36,65],'wear':[9,9,13,13,13,13]},
      'criterion':'Fixed native -X7 attempt/+X7 retreat. Useful=opens or valid retreat when force<=resistance; invalids and rejects counted. Reference and comparator law remain distinct.',
      'no_future_answer_or_native_field_edit':True,'expected_workflow':'New experiences in MAIN, not imported auxiliary learning.'}
atomic_json(EV/'MAIN_PROTOCOLO_PUERTA_Y_RESERVA.json',spec)
command('C02_MAIN_060_PREPARAR',['integrado-experiencia','--vida',spec['main'],'--tipo','puerta-preparar','--parametros',json.dumps({'name':'CICLO02_GATE_MAIN'})])
command('C02_MAIN_061_APRENDER',['integrado-experiencia','--vida',spec['main'],'--tipo','puerta','--parametros',json.dumps({'forces':spec['first_forces'],'wear':spec['first_wear']})])
command('C02_MAIN_062_RECARGA',['integrado-estado','--vida',spec['main']])
actual=Store().record(spec['main']);original=json.loads((EV/'C02_GATE_050_RETORNO.json').read_text(encoding='utf8'))['after']
atomic_json(EV/'C02_EQUIVALENCIA_IMPLEMENTACION_PUERTA.json',{'main':actual['physical'],'exploratory_reference':original['physical'],
    'equal_RAW_and_clocks':all(actual['physical'][k]==original['physical'][k]for k in('tick','RAW_sha256','clocks_sha256')),
    'not_independent_replication':'Same inherited prefix and declared curriculum; new MAIN actually lived the experiences through ordinary manager and persisted environment. No state was copied from the exploratory future.'})
