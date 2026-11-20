"""Recovery note from committed files only, never a world observation."""
from pathlib import Path
from datetime import datetime,timezone
import json,os
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def main():
 active=read(C/'sistema/estado/ACTIVO.json');record=read(P/'REGISTRO_CAMPANA.json');control=P/'control';proofs={}
 for tag in('PI09_NATIVE_R03','PI09_ALWAYS_R03','PI09_NEVER_R03','PI09_YOKE_R03'):
  f=control/(tag+'.json')
  if f.exists():
   d=read(f);proofs[tag]={'life_id':d['life_id'],'closed':d['closed'],'status':d['status'],'T':d['final_tick'],'Native_ticks':d['new_Native_ticks'],'path':str(f)}
 replay=None;f=control/'SUPERVISION_RP_NATIVE12_PI09_R01.json'
 if f.exists():
  d=read(f);replay={k:d.get(k)for k in('status','closed','life_id','destination','pid','finished_utc','actual')};replay['scope']='Supervisor record, not an instantaneous physical observation; RUNNING must not be copied or reopened.'
 v={'schema':'DEE.PI09.recovery_continuity.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),'global_selection_from_file':active,'initial_main':record['source_main'],'closed_consultation_arms':proofs,'RP_replay':replay,'full_source_C':{'path':str(P/'pares/C_HEREDADA_T884835'),'manifest_sha256':'08a8e65deb2071b7653bc0ab95f3d55b8038191a4f585c6803f6d81c16e8182f'},'candidate_post12':{'path':str(P/'pares/NATIVE_POST12_T903603'),'manifest_sha256':'0cce6bcfe366551b52b0ca25c5959bd6e07ed4493221ec26b76af962c13b6553','life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01','N':67,'T':903603,'snapshot_sha256':'be148b940159a48fecc94526656574e0e698860d283f91d7fb424bc1b128d982'},'recovery_rules':['Resume existing sessions and inspect exact closed/uncertain results. Never repeat the control batch or previously used request IDs.','Do not remove active ROOT/RP/owner locks or FUTURO markers based on appearance.','A remains protected until a real COMMITTED adoption; the experiment with greatest tick is not the principal.','Follow closed-cold comparison/registration, then exact prepared PANEL/DISCOVERY import0 and P0 installer/runner. D is conditional and still preparation until actual seal/execution.'],'current_budget':record['budget'],'record':str(P/'REGISTRO_CAMPANA.json'),'single_scientific_report':str(P/'INFORME_CIENTIFICO_PI09.md')}
 path=P/'mapas/CONTINUIDAD_PI09.json';tmp=path.with_name(path.name+'.WRITING')
 with tmp.open('w',encoding='utf8')as stream:json.dump(v,stream,ensure_ascii=False,indent=2);stream.write('\n')
 os.replace(tmp,path);print(json.dumps({'continuity':str(path),'selected':active['life_id'],'RP_status':None if replay is None else replay['status'],'new_Native_ticks':0}))
if __name__=='__main__':main()
