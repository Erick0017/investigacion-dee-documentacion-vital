"""Root's reasoned closed conservation decision. No selector, world or operational code writes."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ev(name):
 p=P/'control'/name;return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 out=P/'control/DECISION_NO_ADOPCION_PI04.json';assert not out.exists()
 active=read(S/'estado/ACTIVO.json');card=read(S/'estado/vidas/ECI02_PI03_MAIN/VIDA.json')
 assert active['life_id']=='ECI02_PI03_MAIN' and card['physical']['tick']==775355
 assert card['snapshot_sha256']=='5581d3785bf7d7194b5bdb545827aab55f0659d8b3f2c00301425d89616cf07b'
 assert hashlib.sha256((S/card['snapshot']).read_bytes()).hexdigest()==card['snapshot_sha256']
 regression=read(P/'control/CONSERVACION_REGRESION_PI04_VERIFICADA.json')
 export=read(P/'control/EXPORTACION_ESTABLE_PI03_PI04_C2C_CONSERVACION_FALLIDA_T818074.json')
 assert export['completed'] and export['tick']==818074 and export['new_native_ticks']==0
 value={'schema':'DEE.PI04.reasoned_no_adoption.v1','decision_id':'PI04_NO_ADOPCION_REGRESION_FIPLUS_01','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'approved_for_adoption':False,'adoption_performed':False,
 'principal':{'life_id':'ECI02_PI03_MAIN','N':67,'tick':775355,'snapshot_sha256':card['snapshot_sha256'],'physical_parent':card['PI03_provenance'],'selection':'PRIOR_COMMITTED_PRESERVED'},
 'candidate':{'life_id':'ECI02_PI03_REPRO_PI04_MAIN_02','N':67,'tick':818074,'physical_parent':'ECI02_PI03_MAIN T775355','full_pair':export['destination'],'manifest_sha256':export['manifest_sha256']},
 'scope':'Useful acquired contextual selection in an externally sequenced two-Native-capability chain is recognized in its experimental history. It cannot replace the current principal because a previously accredited comparison fails the preregistered conservation gate.',
 'gates':{'functional_gain':{'satisfied':True,'scope':'Eight reserved products vs six constant-return, compared with the fixed and WSLS references in this finite set. Not a true-contingency advantage; yoked produces eight reserved and20/20 overall.'},'conservation':{'satisfied':False,'planned':12,'actually_tested':6,'correct':5,'incorrect':1,'not_executed':6,'failed_case':'FIplus 14 vs3','expected_evaluator_only':1,'observed_material':-1,'Native_inputs_unique':211,'Native_inputs_applied':211,'before_tick':817583,'after_tick':818074,'criterion':'Any material old-panel regression blocks promotion; stop at first error, do not re-teach or change the reader.'},'remaining_promotion_gates':{'status':'NOT_EXECUTED_AS_PROMOTION_GATES_AFTER_CONSERVATION_FAILURE','scope':'The diagnostic crossed use is a separate whole-state copy, not an original-main experience or a substitute for conservation.'}},
 'incorporation_permitted':'F1 external observation tool and actually verified C2C reproduction procedure/capsule/prefix/recipe in the existing Cognitive reproducibility tools, with explicit exclusion from principal knowledge. No deployment of the19 experimental operational code changes and no principal promotion.',
 'evidence':[ev('CONSERVACION_REGRESION_PI04_VERIFICADA.json'),ev('C2C_COLD20_NATIVE_VERIFICADA_R01.json'),ev('PI04_C2C_POSTPANEL_DIAG_CRUCE22_R01.json'),ev('EXPORTACION_ESTABLE_PI03_PI04_C2C_CONSERVACION_FALLIDA_T818074.json')],
 'causal_limit':'All176 FI inputs were admitted; a negative material response formed. The recorded aggregate lacks the17 contribution present in the earlier successful protocol. This localizes the discrepancy upstream of the late reader, without proving a unique interference mechanism or global information destruction.',
 'no_new_Native_ticks_for_this_decision':0,'no_control_memories_merged':True,'no_favourable_branch_substitution':True,'no_4th_scientific_design':True}
 with out.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2)
 print(json.dumps({'decision':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'adopted':False,'principal':'ECI02_PI03_MAIN T775355'}))
if __name__=='__main__':main()
