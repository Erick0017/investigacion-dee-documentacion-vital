"""Update only the current campaign resumption field from actual saved files."""
from pathlib import Path
import argparse,datetime,hashlib,json,os
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main(a):
 source=P/'REGISTRO_CAMPANA.json';r=read(source);active=read(C/'sistema/estado/ACTIVO.json');card=read(C/'sistema/estado/vidas'/active['life_id']/'VIDA.json')
 if active['snapshot_sha256']!=card['snapshot_sha256']:raise ValueError('Saved selection/identity mismatch')
 before={k:r[k]for k in('started_local','budget','source_main')}
 r['reanudacion']={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'actual_selected':active,'actual_saved_record_sha256':hashlib.sha256((C/'sistema/estado/vidas'/active['life_id']/'VIDA.json').read_bytes()).hexdigest(),'actual_parent_as_recorded':card['parent'],'current_step':a.paso,'next_step':a.siguiente,'this_command_Native_inputs_or_ticks':0,'same_initial_budget_not_reset':True}
 tmp=source.with_name(source.name+'.RESUME_WRITING')
 with tmp.open('x',encoding='utf8')as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,source)
 check=read(source)
 assert before=={k:check[k]for k in before}
 print(json.dumps({'principal':active['life_id'],'T':active['tick'],'step':a.paso,'next':a.siguiente,'Native_executed':False},ensure_ascii=False))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--paso',required=True);ap.add_argument('--siguiente',required=True);main(ap.parse_args())
