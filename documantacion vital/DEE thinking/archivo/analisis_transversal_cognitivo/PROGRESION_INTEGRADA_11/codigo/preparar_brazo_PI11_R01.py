"""Prepare a declared isolated control/replay code closure, never start Native.

The frozen protocol and independent feedback generator are set before outcomes
are examined. This helper only prepares files. Import and material execution
require separate Root commands with actual hashes.
"""
from pathlib import Path
import argparse,hashlib,json,random,shutil,subprocess,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';PY=C/'motor/python313/python.exe'
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_'
PIN='649ce851ea75489c417496e4ca541e6df7c075399081bda160cd871a61b937b1'
PAIR_SHA='f80c72145dc5b20e1c0c066d0bab9755183eea6e7c7ef89c8ce33b8339788d19'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(a):
 assert Path(sys.executable).resolve()==PY.resolve()
 source=H/'PROTOCOLO_PI11_EVALUACION_R01.json';assert sha(source)==PIN
 assert a.slug in('HEREDADO01','NONE01','YOKE01','REPLAY01')
 scope={'schema':'DEE.PI11.fixed_experiment_scope.R01','life_id':PREFIX+a.slug,'protocol_sha256':PIN,'role':'reproduction'if a.slug=='REPLAY01'else'evaluation','return_arm':a.arm,'continuation':a.continuation}
 if a.arm=='yoked':
  rng=random.Random(2026111191);values=[False,True]*12;rng.shuffle(values);scope.update(yoked_values=values,yoked_seed_auditor_only=2026111191)
 file=H/('PI11_EXPERIMENTO_'+a.slug+'_R01.json')
 with file.open('x',encoding='utf8')as f:json.dump(scope,f,ensure_ascii=False,indent=2);f.write('\n')
 shutil.copyfile(source,H/'PROTOCOLO_PI11_R01.json');shutil.copyfile(file,H/'PI11_EXPERIMENTO_R01.json')
 command=[str(PY),'-I','-B','-X','utf8',str(H/'pi11_clonar_R01.py'),'--slug',a.slug,'--vida',scope['life_id'],'--rol',a.role,'--prefijo',str(P/'pares/PRINCIPAL_REAL2_T947395'),'--manifest-sha256',PAIR_SHA,'--actor',str(H/'pi11_actor_R01.py')]
 for name in('PROTOCOLO_PI11_R01.json','PI11_EXPERIMENTO_R01.json','pi11_habitat_persistente_R01.py'):command+=['--dependencia',str(H/name)]
 command+=['--preparar']
 result=subprocess.run(command,cwd=P,check=True)
 assert result.returncode==0
 print(json.dumps({'prepared':a.slug,'Native':0,'scope_sha256':sha(file)}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--slug',required=True);ap.add_argument('--arm',choices=['real','nonfailure','yoked'],required=True);ap.add_argument('--continuation',choices=['native','fixed'],required=True);ap.add_argument('--role',choices=['real','none','yoked','reproduction'],required=True);main(ap.parse_args())
