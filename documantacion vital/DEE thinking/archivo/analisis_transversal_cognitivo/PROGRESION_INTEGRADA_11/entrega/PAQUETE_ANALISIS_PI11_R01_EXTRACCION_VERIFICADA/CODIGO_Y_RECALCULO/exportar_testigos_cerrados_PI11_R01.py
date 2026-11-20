"""Passive export of reached immutable witnesses after an actual owner close."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,shutil
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def main(a):
 proof=read(a.proof);need(proof.get('closed')and proof.get('error')is None,'Actual coherent owner closure required')
 system=a.system.resolve(strict=True);life=proof['life_id'];card=read(system/'estado/vidas'/life/'VIDA.json');need(card['physical']['tick']==proof['final_tick'],'Not the current actual closed cut')
 f=C/'reproducibilidad/observador_pasivo.py';sp=importlib.util.spec_from_file_location('PI11_closed_witness_parser',f);parser=importlib.util.module_from_spec(sp);sp.loader.exec_module(parser)
 snap=system/card['snapshot'];need(sha(snap)==card['snapshot_sha256'],'Current checkpoint/card differs')
 view=parser.snapshot_view(snap);m=json.loads(view['metadata']['DEE.Cognitive.PI11.persistent_habitat.native_continuation.R01'])
 need(not m.get('pending')and not m.get('uncertain')and m['ordinal']==len(m['rows']),'Only complete actual PI11 trajectory')
 folder=system/'estado/servicios_locales'/life/'PI11_HABITAT_ADAPTATIVO_R01'
 need(not a.output.exists(),'New closed-export destination only');a.output.mkdir(parents=True)
 rows=[]
 for row in m['rows']:
  ref=row['witness'];source=folder/ref['file'];need(source.stat().st_size==ref['bytes']and sha(source)==ref['sha256'],'Reached immutable witness changed')
  target=a.output/ref['file'];shutil.copyfile(source,target);need(sha(target)==ref['sha256'],'Copy differs');rows.append({'file':target.name,'bytes':ref['bytes'],'sha256':ref['sha256']})
 closure={'schema':'DEE.PI11.closed_witness_export.R01','closed_for_documentary_read':True,'closure_evidence':{'path':str(a.proof.resolve()),'sha256':sha(a.proof)},'life_id':life,'final_tick':proof['final_tick'],'snapshot_sha256':card['snapshot_sha256'],'at_utc':datetime.now(timezone.utc).isoformat(),'witnesses':rows,'Native_ticks':0,'Native_imported':False,'not_a_full_operational_backup':True}
 with(a.output/'CIERRE_DOCUMENTAL.json').open('x',encoding='utf8')as f:json.dump(closure,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'life_id':life,'witnesses':len(rows),'output':str(a.output),'closure_sha256':sha(a.output/'CIERRE_DOCUMENTAL.json'),'Native':0}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--proof',type=Path,required=True);ap.add_argument('--system',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);main(ap.parse_args())
