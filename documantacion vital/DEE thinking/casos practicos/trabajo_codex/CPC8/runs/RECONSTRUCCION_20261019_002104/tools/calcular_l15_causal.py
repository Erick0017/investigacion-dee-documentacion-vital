"""Recalculate the local heritage diagnostic from exact primary observations."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'resultados/diagnostico_L15_causal/MEASUREMENTS.json'
def main():
 x=json.loads(P.read_text(encoding='utf-8'));r={c['condition']:c for c in x['conditions']}
 def cell(key,field):
  o=r[key][field]
  return {'tick':o['tick'],'site':o['site'],'raw':o['raw'],'clock':o['clock'],'state':o['state'],
   's_reg':o['s_reg'],'direction':o['direction'],'semantic':o['semantic']}
 rows=[{'condition':k,'join79':cell(k,'actual79'),'alternative82':cell(k,'alternate82'),'original_port134':cell(k,'original_port134')} for k in r]
 result={'schema':'CPC8R.heritage.L15.causal.calculations.v1','primary':P.relative_to(ROOT).as_posix(),
  'primary_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'counts':{'new_preparations':0,'audit_continuation_forks':len(r),'new_E1_individuals':0},
  'table':rows,'calculations':{
   'incoming_loads79':[o['s_reg']for o in x['incoming_to79']],
   'incoming_direction_sum79':[sum(o['direction'][i]for o in x['incoming_to79'])for i in range(3)],
   'cut_extraneous7_effect_on_load79':r['unaltered_fork']['actual79']['s_reg']-r['cut_extraneous7']['actual79']['s_reg'],
   'learned16_contribution_to_alternative82':r['late_alternative_reader']['alternate82']['s_reg']-r['late_reader_cut_memory16']['alternate82']['s_reg'],
   'alternative_reader_added_load82':r['late_alternative_reader']['alternate82']['s_reg']-r['unaltered_fork']['alternate82']['s_reg'],
   'unit':'s_reg field increments in this below-cap local reducer sector, not universal scalar difference of RAW',
   'denominator':'One historical saved world; six instrumented continuations, not six independent learned individuals.'},
  'checks':x['checks'],
  'interpretation':[
   {'capacity':'The learned16 component still causally affects a later response after the first encounter.','mechanism':'Native16+7 creates23with modified direction; a new physical reader9 at another declared access produces32. Cutting the16 contribution changes32to16.','evidence':'late_alternative_reader versus late_reader_cut_memory16 at82','domain':'One heritageN131 world and explicit instrumental probe, not autonomous recovery or E1 acquisition.'},
   {'capacity':'The first trajectory change is localized causally.','mechanism':'Only the7record aimed at the empty destination changes16to23and redirects the ray. IdenticalRAWsham and removing an equal7offpath preserve the23result.','evidence':'join79 and complete sham physical equality','domain':'Actual native transition and exact incoming neighborhood; state0was not excluded from source search, but these two incoming records both have state1.'},
   {'capacity':'A single early residue cut is insufficient to restore the original late access.','mechanism':'The corrected16ray survives through83on its uninteracted path; by130it is absent from that predicted position and the original134port contains onlyreader9.','evidence':'cut_extraneous7 frames83/130/134','domain':'The unobserved83–130 interval is not reconstructed here. This does not establish when/how all information is lost or its global impossibility.'}
  ],
  'observer_limit':'inspect_write_gate returned VOID_PRECEDENCE_UNRESOLVED. Its branch string is not treated as a completed transition proof; actual one-step states and kernel reducer plus causal controls provide that evidence.',
  'provenance':'INSTRUMENTO: diagnostics and causal explanation. No result or edited fork returns to an operative MAIN.'}
 out=ROOT/'revision/L15_ACCESO_VS_INTERFERENCIA.json';out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'primary_sha256':result['primary_sha256'],'cases':len(r),'contribution16':result['calculations']['learned16_contribution_to_alternative82']}))
if __name__=='__main__':main()
