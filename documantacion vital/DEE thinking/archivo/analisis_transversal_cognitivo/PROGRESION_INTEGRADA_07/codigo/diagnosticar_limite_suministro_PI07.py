"""Passive source/primary analysis of the preserved34-versus32 failure."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=P/'control/DIAGNOSTICO_INCOMPATIBILIDAD_C2C34_PI07_R01.json'
 if out.exists():raise FileExistsError(out)
 system=P/'estados/candidato/sistema/capacidades'
 body=system/'pi04_coordinacion_central_C2C.py';extension=system/'pi07_c2c_ofertas_R01.py'
 protocol=system/'PROTOCOLO_PI07_C2C_34_R01.json';failure=P/'control/CIERRE_CONJUNTO_MATERIAL_PI07_R01.json'
 code=body.read_text(encoding='utf-8-sig');lines=code.splitlines()
 conditions=[{'line_1_based':i,'text':s.strip()}for i,s in enumerate(lines,1)if 'len(p["schedule"]) <= 32'in s]
 if len(conditions)!=1:raise ValueError('Do not guess an unknown source limit')
 p=json.loads(protocol.read_text(encoding='utf-8-sig'));f=json.loads(failure.read_text(encoding='utf-8-sig'))
 if len(p['schedule']) != 34 or f['new_Native_ticks'] != 0 or f['criteria_met'] is not False:
  raise ValueError('Actual preserved case differs from this diagnosis')
 result={'schema':'DEE.PI07.explicit_supply_incompatibility.static_diagnosis.v1','new_Native_ticks':0,
  'sources':[{'file':str(x),'bytes':x.stat().st_size,'sha256':sha(x)}for x in(body,extension,protocol,failure)],
  'source_clause':conditions[0],'proposed_schedule_length':34,'scientific_body_supported_maximum':32,
  'actual_attempt':{'status':f['status'],'closed':f['closed'],'criteria_met':f['criteria_met'],
    'before_tick':f['initial_tick'],'after_tick':f['final_tick'],'Native_ticks':f['new_Native_ticks'],
    'error':f['error'],'protected_main_hashes_equal':f['protected_main_before']==f['protected_main_after']},
  'causal_order_from_source':['The extension validates the old30 protocol and literal first30 preservation.',
    'prepare writes four explicit resource files and the device resource list, then changes the C2C protocol reference and appends journal records.',
    'The final effective-component dependency validation reads the34 protocol; the frozen body rejects schedule length34 above32.',
    'Failure preservation marks the extension uncertain. Saving/stopping also fails the same operational dependency check.'],
  'classification':'External P0 integration incompatibility, not a failed Native arithmetic/regulation performance test.',
  'not_executed':['Actual C2C opportunity30','Material R03 opportunity16 after the proposed final reopening'],
  'not_claimed':['A complete committed34-resource environment','A coherent reopened final experimental owner','Learning or resource gain from the partial supply','A promotion of the experimental life'],
  'preservation':'Do not retry, roll back or silently discard the partial future. Root alone checks the real owner and preserves the interrupted state; the selected PI05 principal remains protected.',
  'local_lesson':'The prepared34 protocol was not checked against the2..32 bound of the existing scientific body before sealing. Do not remove that bound retrospectively to call the original attempt valid.'}
 with out.open('x',encoding='utf-8')as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
 print(json.dumps({'proof':str(out),'sha256':sha(out),'Native_ticks':0,'integration_supported':False}))
if __name__=='__main__':main()
