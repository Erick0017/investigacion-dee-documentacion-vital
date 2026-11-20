"""Preserve R01 and prepare a final descriptive resource/public-use refinement."""
from pathlib import Path
import ast,hashlib
H=Path(__file__).resolve().parent
def main():
 old=H/'sincronizar_cierre_actual_PI09_R01.py';new=H/'sincronizar_cierre_actual_PI09_R02.py'
 if new.exists():raise FileExistsError('Prior revision preserved')
 t=old.read_text('utf-8-sig')
 a=' return life,active,card,cardfile,snapshot,protected';b=""" resources={}
 for label,key,total in(('PI09_R02','DEE.Cognitive.PI09.selective_registered_consultation.R02',18),('D','DEE.Cognitive.PI09.persistent_environment.D.R02',12),('FI8','DEE.Cognitive.PI09.explicit_FI_eight_offer_lot.R01',8),('FI_prior','DEE.Cognitive.PI07.regulated_FI_access.R01',8),('C2C','DEE.Cognitive.PI04.C2C.coordination.R01',32)):
  if key not in view['metadata']:continue
  value=json.loads(view['metadata'][key]);ordinal=value.get('ordinal')
  if type(ordinal)is not int:continue
  resources[label]={'ordinal':ordinal,'total_declared':total,'remaining':total-ordinal,'access':'historical_readonly'if life.endswith('DISCOVERY_01')and label in('PI09_R02','FI_prior')else'current_declared_finite_stock','supply_or_stock_is_not_Native_energy_or_learning':True}
 return life,active,card,cardfile,snapshot,protected,resources"""
 if t.count(a)!=1:raise ValueError('Actual-current return anchor changed')
 t=t.replace(a,b).replace('life,active,card,cardfile,snapshot,protected=current()','life,active,card,cardfile,snapshot,protected,resources=current()')
 t=t.replace("'final_facts':ref(factsfile),'closed_writer_scope':wp}","'final_facts':ref(factsfile),'closed_writer_scope':wp,'finite_resources_at_actual_current_snapshot':resources}")
 a="   use=a.use_proof" # Real source uses two-space indentation; exact below.
 needle="project['latest_selected_use']=ref(use);continuity['latest_operational_use']=ref(use);principal['latest_actual_selected_use']=ref(use)"
 if t.count(needle)!=1:raise ValueError('Actual public-use binding anchor changed')
 t=t.replace(needle,needle+";project['selected_operational_use_pending']=False")
 needle=" if a.publication:\n  manual,comp=publication"
 before=""" for entry in catalog.get('entries',[]):
  if any(v.get('life_id')==life for v in entry.get('validated_lives',[])if isinstance(v,dict)):
   entry['PI09_latest_available_state']=info;entry['PI09_final_evidence']=ref(factsfile)
 if a.publication:
  manual,comp=publication"""
 if t.count(needle)!=1:raise ValueError('Final catalog/publication anchor changed')
 t=t.replace(needle,before).replace('SINCRONIZACION_FINAL_PI09_R01','SINCRONIZACION_FINAL_PI09_R02').replace('SINCRONIZACION_FINAL_ACTUAL_PI09_R01','SINCRONIZACION_FINAL_ACTUAL_PI09_R02').replace('final_current_metadata.CAS_plan.R01','final_current_metadata.CAS_plan.R02').replace('final_current_metadata.applied.R01','final_current_metadata.applied.R02')
 ast.parse(t);new.write_text(t,'utf8');print(new.name,hashlib.sha256(new.read_bytes()).hexdigest())
if __name__=='__main__':main()
