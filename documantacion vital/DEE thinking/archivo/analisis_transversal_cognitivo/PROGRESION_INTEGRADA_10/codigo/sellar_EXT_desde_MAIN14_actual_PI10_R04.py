"""Root-only optional EXT seal from actual postCOMMITTED14, no Native.

Default does not read the source. --sellar copies the draft into a new sealed
file without overwriting it. Source, deadlines and budgets are actual and all
events remain prospectively fixed; no response/reader is selected here.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];H=P/'codigo'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def need(ok,msg):
 if not ok:raise ValueError(msg)
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--tick',type=int);ap.add_argument('--snapshot-sha256');ap.add_argument('--compromiso',type=Path);ap.add_argument('--prefijo',type=Path);ap.add_argument('--manifest-sha256');ap.add_argument('--sellar',action='store_true');a=ap.parse_args()
 if not a.sellar:print(json.dumps({'mode':'PLAN_ONLY_NO_SOURCE_READ','requires':['Actually selected COMMITTED Main14 and complete closed exported source','At least720s before unchanged material cutoff','Historical worlds<=11 and Native allowance>=8064','Draft science/calendar/codec remain fixed'],'Native':0}));return
 helper=H/'continuidad_EXT_post_COMMITTED_PI10_R04.py';u=load('PI10_EXT_actual_main14_seal_guard',helper);card,view,commit,protected=u.current(a);old=u.protect_old_D();ledger=u.prospective_time_and_budget();pair,manifest=u.pair(a,card);guard=u.load('PI10_EXT_actual_main14_closed_guard',H/'comprobar_proceso_PI10_R02.py','21d41a1e429f135d100f17826258561dc9f98ca52a465cc2015f30efb5966adb').inspect('PI10_EXT_Main14_before_seal',u.S,u.MAIN);u.need(guard['no_live_affected_writer'],'Actual current parent must be closed before seal');draft=H/'PROTOCOLO_PI10_EXT_R01.json';p=read(draft);need(p['status']=='DRAFT_NOT_AUTHORIZED'and p['Root_execution_authorized']is False,'Preserve original draft, never relabel a previous sealed case');need(p['base_actor_sha256']==sha(u.S/'capacidades/pi10_consulta_adaptativa_R02.py')and p['base_protocol_sha256']==sha(u.S/'capacidades/PROTOCOLO_PI10_R02.json'),'Literal original base body/protocol');out=H/'PROTOCOLO_PI10_EXT_R01_SELLADO_DESDE_MAIN14.json';proof=P/'control/SELLO_EXT_DESDE_MAIN14_ACTUAL_R04.json';need(not out.exists()and not proof.exists(),'Unique prospective seal, never overwrite/reseal after outcomes')
 new=copy.deepcopy(p);new.update(status='SEALED_FOR_DIAGNOSTIC_EXT',Root_execution_authorized=True,Root_hard_aggregate_budgets_checked=True,hard_finish_utc=read(P/'REGISTRO_CAMPANA.json')['budget']['hard_finish_utc'],sealed_utc=datetime.now(timezone.utc).isoformat());new['source_main']={'life_id':u.MAIN,'N':67,'ordinal':14,'snapshot_sha256':card['snapshot_sha256'],'physical':card['physical'],'full_pair_manifest':{'path':str(pair/'EXPORTACION_SERVICIO.json'),'sha256':a.manifest_sha256}};new['committed_proof']={'path':str(commit),'sha256':sha(commit)}
 for field in('ordinals','competitor_ordinals','extra_preview_ordinal','prepared_channel','fixed_external_events','base_actor_sha256','base_protocol_sha256'):need(new[field]==p[field],'Do not adapt prospective science/reader after seeing outcomes')
 with out.open('x',encoding='utf8')as f:json.dump(new,f,ensure_ascii=False,indent=2);f.write('\n')
 need(protected=={k:sha(Path(k))for k in protected}and old=={k:sha(Path(k))for k in old},'Main/originalD changed during pure seal');report={'schema':'DEE.PI10.actual_main14.prospective_EXT_seal.R04','draft':str(draft),'draft_sha256':sha(draft),'sealed':str(out),'sealed_sha256':sha(out),'source_main':new['source_main'],'committed_proof':new['committed_proof'],'source_unchanged':True,'old_D_unchanged':True,'ledger_before':ledger,'closed_source':guard,'Native_imports':0,'Native_ticks':0,'must_install_canonical_filename_without_overwriting_draft':'Clone preparerR04 accepts --protocolo-sellado '+str(out)+'; runtime filename remains PROTOCOLO_PI10_EXT_R01.json inside the new clone only.'}
 with proof.open('x',encoding='utf8')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'sealed':str(out),'sha256':sha(out),'proof':str(proof),'Native':0}))
if __name__=='__main__':main()
