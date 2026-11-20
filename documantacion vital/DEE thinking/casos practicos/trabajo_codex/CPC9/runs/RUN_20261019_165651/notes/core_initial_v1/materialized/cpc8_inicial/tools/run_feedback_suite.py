"""Freeze contrasts before execution. Each native worker is supervised separately."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENV=Path(sys.argv[1]);BASE=Path(sys.executable)
code=ROOT/'src/regulacion/native_feedback.py'
cases=[
 ('REG_V1_H11',-1,'intact','Q',0,67,'opposite world direction'),
 ('REG_V1_C11',1,'omit_actuator','P',0,67,'zero-load contact actuator omitted'),
 ('REG_V1_C12',-1,'omit_actuator','Q',0,67,'zero-load contact actuator omitted'),
 ('REG_V1_S11',1,'sham_actuator','P',0,67,'same actuator inventory moved off path'),
 ('REG_V1_D11',1,'cut_feedback','P',0,67,'consequence return interrupted off path'),
 ('REG_V1_D12',-1,'cut_feedback','Q',0,67,'consequence return interrupted off path'),
 ('REG_V1_X11',1,'intact','Q',0,67,'regulation has opportunity cost for other requested delivery'),
 ('REG_V1_X12',-1,'intact','P',0,67,'regulation has opportunity cost for other requested delivery'),
 ('REG_V1_R11',1,'intact','P',17,131,'reserved larger geometry, declared new preparation'),
 ('REG_V1_R12',-1,'intact','Q',17,131,'reserved larger geometry, opposite medium'),
]
folder=ROOT/'configuraciones/regulacion';folder.mkdir(parents=True,exist_ok=True)
frozen={'schema':'CPC8.native-consequence-regulation.v1','frozen_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
        'discovery':'REG_PILOT_P; not confirmatory independent evidence','preparation_sha256':hashlib.sha256(code.read_bytes()).hexdigest(),
        'criterion':'Only exact useful load3 +X at delivery receiver tick15. P/Q evaluator requests are never supplied to world. All routes and adverse outcomes retained.',
        'prediction':'Native medium+ should retainP; medium- should switchQ. Removing probe contact/return should affect policy and delivery. Offpath sham is not assumed inert before measurement.',
        'cases':[dict(zip(('case_id','medium','mode','context','translation','N','purpose'),row)) for row in cases]}
(folder/'V1_FROZEN.json').write_text(json.dumps(frozen,ensure_ascii=False,indent=2),encoding='utf-8')
results=[]
for ident,m,mode,context,translation,n,purpose in cases:
    command=[str(BASE),'-I','-B',str(ROOT/'tools/supervisor.py'),'--name',ident.lower(),'--timeout','180','--',str(ENV),'-I','-B',str(ROOT/'src/regulacion/run_feedback.py'),'--case',ident,'--medium',str(m),'--mode',mode,'--context',context,'--translation',str(translation),'--N',str(n)]
    completed=subprocess.run(command,timeout=260)
    row={'case_id':ident,'supervisor_exit':completed.returncode}
    path=ROOT/'resultados/regulacion'/ident/'RESULT.json'
    if path.exists():row['measurement']=json.loads(path.read_text(encoding='utf-8'))
    results.append(row)
    (folder/'V1_EXECUTION_INDEX.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(ident,completed.returncode,flush=True)
