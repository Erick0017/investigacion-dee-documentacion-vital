"""Bounded serial return experiments; subprocesses belong to the supervisor job."""
from pathlib import Path
import json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
cases=[('RET_D02_M',11,18,'paired',False),('RET_C01_NOFORM',31,18,'omitted',False),
       ('RET_C02_UNPAIRED',31,18,'unpaired',False),('RET_C03_NOQUERY',31,18,'paired',True),
       ('RET_R01_SOURCE17_OBJECT9',17,9,'paired',False),('RET_R02_SOURCE17_OBJECT27',17,27,'paired',False),
       ('RET_R03_SOURCE31_OBJECT42',31,42,'paired',False)]
def main():
    results=[];start=time.monotonic()
    for case,value,obj,form,noquery in cases:
        command=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'src/ejecutar_retorno.py'),'--case',case,'--source',str(value),
                 '--first-object',str(obj),'--form',form,'--out',str(ROOT/'resultados/retorno'/case)]
        if noquery:command.append('--no-query')
        done=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=120)
        results.append({'case':case,'command':command,'returncode':done.returncode,'stdout':done.stdout,'stderr':done.stderr})
        out=ROOT/'resultados/retorno/LOTE_V2.json'
        out.write_text(json.dumps({'experiments':results,'elapsed_seconds':time.monotonic()-start},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'case':case,'returncode':done.returncode},ensure_ascii=False),flush=True)
        if done.returncode:raise RuntimeError(case+': '+done.stderr)
if __name__=='__main__':main()
