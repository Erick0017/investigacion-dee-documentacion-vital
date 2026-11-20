"""Root-authorized pure seal before first Native calibration; no DEE import."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
H=Path(__file__).resolve().parent;P=H.parent;out=H/'PROTOCOLO_PI10_R01.json'
expected='e3cabfac098f2d5c74aa84c10d94e3757801f2e175d7dd24d461b6d8a5b2f196'
b=out.read_bytes();assert hashlib.sha256(b).hexdigest()==expected,'Unexpected protocol: preserve rather than reseal'
v=json.loads(b);assert v['status']=='DRAFT'
old=P/'fuentes'/'PROTOCOLO_PI10_R01_BORRADOR_2_CALIBRACIONES.json';assert not old.exists();old.write_bytes(b)
pins={
 'pi10_consulta_adaptativa_R01.py':'bd80b69e5acf885a84731d84b252b5dbf84648bf15aff9f915a07ed930762be2',
 'pi10_dos_trazas_legales_R01.py':'139d9232d9261d699b1cbcfe5d7adf81e61f25110e432e622af6bd659f2edf90',
 'pi10_entorno_dos_puertas_R01.py':'43032d9cc6d62695ef1789dc08b80c8c4de7f0d036ad3a8ee10e60bb3d7c58b1',
 'pi10_transporte_ancestral_R01.py':'ad2d0a623f347a617a9329d055032884207ec43a3733290b96292f0e028c0577'}
for name,digest in pins.items():assert hashlib.sha256((H/name).read_bytes()).hexdigest()==digest,'Source changed: '+name
v['calibration_schedule']=[
 {'ordinal':0,'regime':'need','cue':'threat','role':'diagnostic_forced','left':18,'right':5},
 {'ordinal':1,'regime':'need','cue':'falsecue','role':'diagnostic_forced','left':19,'right':6},
 {'ordinal':2,'regime':'bypass','cue':'threat','role':'diagnostic_forced','left':20,'right':7}]
v['calibration_contract']='Two matched complete diagnostic clones globally force query true/false for three cases need/Z,need/X,bypass/Z. Both information contents, both routes and actual consequence polarity must be measured. Forced experiences are not imported into the candidate.'
v['status']='SEALED_FOR_CALIBRATION';v['sources_sha256']=pins;v['Root_must_pin_sources_before_material']=list(pins)
v['calibration_sealed_utc']=datetime.now(timezone.utc).isoformat()
v['calibration_seal_authority']='Root instruction before the first Native execution; three-case interface check, no change of evaluation18+future6 or adoption criteria.'
v['prior_draft_sha256']=expected
v['not_a_seal']='Calibration seal only: no Native result, learning, function or evaluation authorization is claimed. Evaluation requires a separately declared Root authorization after preserving this calibration protocol.'
out.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'protocol':str(out),'status':v['status'],'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'calibration_opportunities_per_forced_clone':3,'old_draft_preserved':str(old),'Native_executed':False}))
