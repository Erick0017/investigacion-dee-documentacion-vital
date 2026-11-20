"""Sequential bounded coordinator; exactly one owned native worker at a time."""
import argparse,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
IDS=('CTS_R1_C11_NO_FORM','CTS_R1_C12_UNPAIRED_FORM','CTS_R1_C13_NO_QUERY','CTS_R1_C14_SOURCE_NAME_OMITTED','CTS_R1_C15_REG_OFFPATH_CONTACT','CTS_R1_C16_REG_OFFPATH_FREE','CTS_R1_R31_NEW_HISTORY_CONTACT','CTS_R1_R32_NEW_HISTORY_FREE')
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);rows=[];start=time.monotonic()
    for case in IDS:
        folder=ROOT/'resultados/semantica'/case
        if folder.exists():
            rows.append({'case':case,'status':'SKIPPED_EXISTING_NEVER_DUPLICATED'});continue
        argv=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'tools/supervisor.py'),'--name','contact_social_'+case.lower(),'--timeout','600','--',sys.executable,'-I','-B','-X','utf8',str(ROOT/'src/comunicacion/run_contact_social_regulated.py'),'--config',str(ROOT/'configuraciones/semantica/CONTACT_SOCIAL_COUNTERFLOW1_FROZEN.json'),'--case',case,'--out',str(folder)]
        result=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,encoding='utf8',timeout=630)
        rows.append({'case':case,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr});(a.out/'BATCH.json').write_text(json.dumps({'rows':rows,'elapsed_seconds':time.monotonic()-start},ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'cases':len(rows),'returncodes':[x.get('returncode')for x in rows]}))
if __name__=='__main__':main()
