import argparse,json,inspect,sys,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from predictor import *


def run(root):
    root=Path(root);log=AuditLog(root/'PREDICCIONES_INFORMATION_AUDIT.jsonl');rows=[]
    for opened in (True,False):
        s=PredictorSession(build(),PersistentTransportHabitat(opened));s.world.run_until(34);s.habitat.advance(34,[])
        before=physical(s.world);em=s.predict([70],log,'INFORMATION_NO_EXPERIENCE_'+str(opened));ev=s.evaluate(70,log,'INFORMATION_NO_EXPERIENCE_'+str(opened));rows.append({'hidden_condition_auditor_only':opened,'before':before,'emission':em,'evaluation':ev,'after':physical(s.world)})
    checks={'same_hidden_world_native_initial_state':rows[0]['before']==rows[1]['before'],
            'same_hidden_world_native_forecast':rows[0]['emission']['physical_output']==rows[1]['emission']['physical_output'],
            'same_forecast_set':rows[0]['emission']['prediction_set']==rows[1]['emission']['prediction_set'],
            'future_outcomes_differ':rows[0]['evaluation']['outcome']['arrived']!=rows[1]['evaluation']['outcome']['arrived']}
    assert all(checks.values())
    actual=json.loads((root/'resultados'/'CONFIRMED.json').read_text(encoding='utf-8'));noforecast=[]
    for flag in (0,1):
        paired=next(x for x in actual['rows'] if x['id']=='PAIRED_gate'+str(flag));shadow=next(x for x in actual['rows'] if x['id']=='NO_FORECAST_GATE'+str(flag))
        noforecast.append({'condition':flag,'same_outcomes_with_without_prediction':all(e['outcome']['arrived']==shadow['world_outcomes'][str(e['target_tick'])]['arrived'] for e in paired['evaluations'])})
    assert all(x['same_outcomes_with_without_prediction'] for x in noforecast)
    decoder=inspect.getsource(decode_native_output)
    audit={'model':'MUNDO externo independiente + ENTE v27 + AUDITOR externo',
         'native_input':['past observed outcome encoded A/B, zero load','timestamp and fixed interface','physical common query'],
         'native_not_given':['hidden gate state','seed','future targets/outcomes','scenario id','expected answer','Python model rollout','GLOBAL RAW as sensory channel'],
         'native_writes':'only actual submit/probe receipts; no postT0 A/B edits in MAIN; diagnostic edits occur in labelled independent forks',
         'decoder_source':decoder,'decoder_sha256':hashlib.sha256(decoder.encode()).hexdigest(),
         'snapshot_privileges':'external habitat condition is serialized for operational restore; kernel consumes no snapshot metadata; decoder accepts only current native output and admission bool',
         'future_resolution_order':'predict validates target>current+3; nativeadvance3; current-worldadvance cannot reach target; append/flush/fsync EMISSION; only evaluate advances to target then resolves it',
         'assisted_observation':'descendant fork copies native historical state to run local common probe; does not rollout hidden environment; MAIN advances matching3ticks; no buffers or carrier copied back',
         'source_layout':'predictor.py build/submit/native evolution vs independent PersistentTransportHabitat and pure decode_native_output',
         'nonleak_checks':checks,'prediction_not_self_fulfilling':noforecast,'rows':rows,
         'limitations':['Fixed sign decoding and persistence are designed, not learned arbitrary associations','Reference branch and sensor acquisition phase are installed interface conditions','An uncertainty set is an external fixed interpretation, not learned confidence','Local physical probe in descendant is assisted, not autonomous introspection']}
    atomic_json(root/'AUDITORIA_INFORMACION.json',audit);print(json.dumps({'checks':checks,'no_self_fulfilling':noforecast}))


if __name__=='__main__':run(sys.argv[1])
