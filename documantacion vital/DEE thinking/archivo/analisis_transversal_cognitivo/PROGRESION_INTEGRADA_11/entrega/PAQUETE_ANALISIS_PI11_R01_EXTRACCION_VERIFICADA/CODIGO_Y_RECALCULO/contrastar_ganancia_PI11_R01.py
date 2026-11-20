"""Passive sealed tradeoff check on two complete sixteen-op trajectories."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
P=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(a):
 base=P/'fuentes/PRIMARIOS_CERRADOS_R01';sets={}
 for slug in('MAIN01','HEREDADO01'):
  closure=read(base/slug/'CIERRE_DOCUMENTAL.json');assert closure['closed_for_documentary_read']
  rows=[read(base/slug/('episodio_%04d.json'%n))for n in range(16)]
  assert all(r['ordinal']==n and r['before_tick']==947395+1564*n and r['after_tick']==947395+1564*(n+1)for n,r in enumerate(rows))
  sets[slug]=rows
 m,b=sets['MAIN01'],sets['HEREDADO01'];ms=sum(r['resource']['attributed_useful']for r in m);bs=sum(r['resource']['attributed_useful']for r in b);mf=sum(r['second_stage']['refresh_FI']for r in m);bf=sum(r['second_stage']['refresh_FI']for r in b)
 useful_reuses=sum(r['resource']['attributed_useful']and not r['resource']['do_refresh']for r in m)
 positive=mf;negative=len(m)-mf;loss=bs-ms;reduction=100*(bf-mf)/bf
 differences=[]
 for n,(x,y)in enumerate(zip(m,b)):
  if x['resource']['attributed_useful']!=y['resource']['attributed_useful']:
   differences.append({'ordinal':n,'main':x['resource'],'inherited':y['resource'],'Native_choices_same':x['first_stage']['reader']['choice']==y['first_stage']['reader']['choice']and x['second_stage']['reader']['choice']==y['second_stage']['reader']['choice'],'sample_observation_equal':x['first_stage']['register']['actual_observation']==y['first_stage']['register']['actual_observation']})
 prototype=P/'codigo/PROTOCOLO_PI11_EVALUACION_R01.json'
 assert sha(prototype)=='649ce851ea75489c417496e4ca541e6df7c075399081bda160cd871a61b937b1'
 value={'schema':'DEE.PI11.sealed_functional_tradeoff_check.R01','at_utc':datetime.now(timezone.utc).isoformat(),'Native_executed':False,'opportunities_each':16,'shared_initial_prefix_not_independent_organisms':True,'main_attributed':ms,'inherited_attributed':bs,'useful_delivery_loss':loss,'main_FI':mf,'inherited_FI':bf,'FI_reduction_percent':reduction,'main_useful_prior_certificate_uses':useful_reuses,'main_valid_positive_continuations':positive,'main_omitted_FI_continuations':negative,'new_control_observed':positive>=2 and negative>=2 and useful_reuses>=2,'predeclared_tradeoff_met':loss<=2 and reduction>=25,'functional_gain_gate_provisionally_met':positive>=2 and negative>=2 and useful_reuses>=2 and loss<=2 and reduction>=25,'other_adoption_gates_not_asserted':['causal controls','conservation','post-reopening use','Native replay','public interface/full adoption'],'sealed_criterion':{'path':str(prototype),'sha256':sha(prototype)},'actual_differing_outcomes':differences,'scope':'Fixed Native-output transduction is preparation. Cached RAW and certificate are external resources. Fewer fresh FI calls are not demonstrated energy/tick savings. No superior true-contingency claim from this contrast.'}
 with a.output.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({k:value[k]for k in('main_attributed','inherited_attributed','main_FI','inherited_FI','useful_delivery_loss','FI_reduction_percent','functional_gain_gate_provisionally_met')}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);main(ap.parse_args())
