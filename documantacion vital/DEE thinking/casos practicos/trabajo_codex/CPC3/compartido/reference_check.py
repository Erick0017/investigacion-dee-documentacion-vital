"""One short inherited cognition witness, source migrated inside CPC3."""
import hashlib,json,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root/'genealogia/CP02_B/src'))
from predictor import *

out=root/'resultados/referencia_heredada';out.mkdir(parents=True,exist_ok=True);log=AuditLog(out/'PREDICCIONES.jsonl')
s=PredictorSession(build(),PersistentTransportHabitat(True,80));inputs=s.experience_past_results();s.save(out/'HISTORIA_ADQUIRIDA_T34.deetsnap')
em=s.predict([60,100],log,'CPC3_REFERENCE_ONLY');s.save(out/'EXPECTATIVA_T37.deetsnap');e60=s.evaluate(60,log,'CPC3_REFERENCE_ONLY');e100=s.evaluate(100,log,'CPC3_REFERENCE_ONLY')
assert em['emission_tick']==37 and em['prediction_set']==[True]
assert e60['absolute_error_binary']==0 and e100['absolute_error_binary']==1
native=Path(d._native.__file__);identity={'version':d.__version__,'kernel':d.kernel_identity(),'module':d.__file__,'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest()}
assert identity['version']=='3.5.0' and identity['kernel']['kernel_version']==27 and identity['native_sha256']=='3b864bf8c5d4cee6940e3bb99bb647443548851def72df3c3b60ed69b4308585'
atomic_json(out/'REFERENCE_CHECK.json',{'mode':'HEREDITARY_TECHNICAL_REPRODUCTION_NOT_NEW_CPC3_MAIN','identity':identity,'input_receipts':inputs,'physical_emission':em,'evaluations':[e60,e100],'reference_matches':True,'historic_error_preserved':True})
print(json.dumps({'identity':identity,'tick':s.world.runtime.current_tick,'delta':panel(s.world)['delta'],'emission_tick':37,'errors':[0,1],'one_inherited_short_witness':True}))
