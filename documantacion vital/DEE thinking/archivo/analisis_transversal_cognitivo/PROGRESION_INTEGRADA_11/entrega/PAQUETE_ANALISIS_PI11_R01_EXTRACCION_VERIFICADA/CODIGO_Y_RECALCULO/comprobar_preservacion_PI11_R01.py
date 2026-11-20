"""Hash only seven named frozen originals; no engine import or source write."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(a):
 ref=P.with_name('PROGRESION_INTEGRADA_10')/'fuentes/PRESERVACION_CRITICOS_CIERRE_PI10_R02.json'
 rows=[{'role':r['role'],'path':r['absolute_path'],'expected_sha256':r['sha256']}for r in read(ref)['files']]
 pair=P/'pares/PRINCIPAL_REAL2_T947395';proof=read(P/'pares/PRINCIPAL_REAL2_T947395_PRESERVACION.json')
 for path,digest in proof.get('protected_hashes_before',{}).items():
  if Path(path).name!='ACTIVO.json':rows.append({'role':'protected_PI10_parent','path':path,'expected_sha256':digest})
 # The literal source card preserved by the paired contract supplies its hash.
 card=S/'estado/vidas/ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01/VIDA.json'
 original=pair/'procedencia/VIDA_ORIGINAL.json';snap=S/read(original)['snapshot']
 rows.extend([{'role':'protected_PI10_card','path':str(card),'expected_sha256':sha(original)},
 {'role':'protected_PI10_snapshot','path':str(snap),'expected_sha256':'fd7372b7f2adc9040866fab8adfaca0d79e0bd18e997c0abc0651fe4fa3c23dc'}])
 unique={r['path']:r for r in rows};result=[]
 for row in unique.values():
  p=Path(row['path']);actual=sha(p);result.append({**row,'bytes':p.stat().st_size,'sha256':actual,'same':actual==row['expected_sha256']})
 value={'schema':'DEE.PI11.selected_frozen_original_preservation.R01','at_utc':datetime.now(timezone.utc).isoformat(),'Native_imported':False,'Native_ticks':0,'files':result,'all_selected_unchanged':all(r['same']for r in result),'scope':'Only named parent cards/checkpoints and official binaries/kernel. ACTIVO/manual/code may change only through separately documented validated adoption/publication; no claim of whole-project immutability.'}
 with a.output.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'all_selected_unchanged':value['all_selected_unchanged'],'files':len(result),'proof':str(a.output),'Native':0}))
 if not value['all_selected_unchanged']:raise SystemExit(1)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);main(ap.parse_args())
