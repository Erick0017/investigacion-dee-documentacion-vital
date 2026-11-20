"""One bounded actual render attempt on staged complete documents; no Word COM."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, subprocess, sys
P=Path(__file__).resolve().parents[1]
RENDER=Path(r'C:\Users\Erik\.codex\plugins\cache\openai-primary-runtime\documents\26.1104.22356\skills\documents\render_docx.py')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main(a):
    stage=a.staging.resolve(strict=True)
    if not stage.is_relative_to((P/'documentos').resolve()): raise ValueError('Only actual PI08 staging')
    v=json.loads((stage/'VALIDACION_ESTRUCTURAL_PI08_B_1_36.json').read_text('utf-8'))
    rows=[]
    for i,d in enumerate(v['documents']):
        src=Path(d['output'])
        if sha(src)!=d['output_sha256']: raise ValueError('Staged bytes changed')
        out=stage/('render_'+str(i+1))
        cmd=[sys.executable,'-I','-B','-X','utf8',str(RENDER),str(src),'--output_dir',str(out),'--emit_pdf','--verbose']
        start=datetime.now(timezone.utc).isoformat()
        try:
            r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90)
            row={'command':cmd,'started_utc':start,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
        except subprocess.TimeoutExpired as e:
            row={'command':cmd,'started_utc':start,'timeout_seconds':90,'error':str(e)}
        row['PNG_count']=len(list(out.glob('page-*.png'))) if out.exists() else 0
        row['PDF_count']=len(list(out.glob('*.pdf'))) if out.exists() else 0
        rows.append(row)
        # Same renderer/dependency: a missing soffice is decisive for both.
        if 'soffice.exe was not found on PATH' in row.get('stderr',''): break
    obj={'schema':'DEE.PI08.final_document.actual_render_attempt.v1','at_utc':datetime.now(timezone.utc).isoformat(),
         'attempted':True,'visual_validation':False,'actual_attempts':rows,
         'limitation':'No visual page validation is claimed. '+('LibreOffice soffice.exe was not found on PATH; the same missing renderer prevents both documents.' if any('soffice.exe was not found on PATH' in r.get('stderr','') for r in rows) else 'Rendering output requires visual review before any approval.'),
         'Native_ticks':0,'foreign_Word_instances_opened_or_closed':False}
    out=P/'documentos/INTENTO_RENDER_CIERRE_1_36.json'
    with out.open('x',encoding='utf-8') as f: json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(out),'sha256':sha(out),'visual_validation':False,'attempts':len(rows)}))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--staging',type=Path,required=True);main(a.parse_args())
