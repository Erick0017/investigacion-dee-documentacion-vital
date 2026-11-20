"""Second and final route repair: freeze first, then measure both histories."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];ENV=Path(sys.argv[1])
cases=[
 ('REG_V2_P21',1,'intact','P',0,67),('REG_V2_H21',-1,'intact','Q',0,67),
 ('REG_V2_C21',1,'omit_actuator','P',0,67),('REG_V2_C22',-1,'omit_actuator','Q',0,67),
 ('REG_V2_D21',1,'cut_feedback','P',0,67),('REG_V2_D22',-1,'cut_feedback','Q',0,67),
 ('REG_V2_S21',1,'cut_negative_return','P',0,67),('REG_V2_S22',-1,'cut_negative_return','Q',0,67),
 ('REG_V2_X21',1,'intact','Q',0,67),('REG_V2_X22',-1,'intact','P',0,67),
 ('REG_V2_R21',1,'intact','P',29,131),('REG_V2_R22',-1,'intact','Q',29,131)]
out=ROOT/'configuraciones/regulacion';out.mkdir(parents=True,exist_ok=True)
config={'schema':'CPC8.regulation.v2','freeze_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
 'preparation_sha256':hashlib.sha256((ROOT/'src/regulacion/native_feedback.py').read_bytes()).hexdigest(),
 'previous_attempts_preserved':['REG_PILOT_P','REG_V1_*','REG_V2_DISCOVERY_NEGATIVE'],
 'change':'Only comparison lane e=+1 physically prepared; previous unused e=-1 devices interfere with negative report. New apparatus, not continuation.',
 'criterion':'Exact useful load3+X delivery@15; current medium+ selectsP, - selectsQ. Evaluation context is NOT a participant input.',
 'controls':'Omit contact actuator; interrupt both consequence returns; interrupt only negative return (sham for medium+, selective cut for medium-). Context opposite measures opportunity cost; no optimality signal is supplied.',
 'predictions':[dict(zip(('case_id','medium','mode','context','translation','N'),q)) for q in cases]}
(out/'V2_FROZEN.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),encoding='utf-8')
results=[]
for ident,m,mode,context,translation,n in cases:
 cmd=[sys.executable,'-I','-B',str(ROOT/'tools/supervisor.py'),'--name',ident.lower(),'--timeout','180','--',str(ENV),'-I','-B',str(ROOT/'src/regulacion/run_feedback.py'),'--case',ident,'--medium',str(m),'--mode',mode,'--context',context,'--translation',str(translation),'--N',str(n),'--single-lane']
 c=subprocess.run(cmd,timeout=260,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 row={'case_id':ident,'supervisor_exit':c.returncode};p=ROOT/'resultados/regulacion'/ident/'RESULT.json'
 if p.exists():row['measurement']=json.loads(p.read_text(encoding='utf-8'))
 results.append(row);(out/'V2_EXECUTION_INDEX.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
 print(ident,c.returncode,flush=True)
