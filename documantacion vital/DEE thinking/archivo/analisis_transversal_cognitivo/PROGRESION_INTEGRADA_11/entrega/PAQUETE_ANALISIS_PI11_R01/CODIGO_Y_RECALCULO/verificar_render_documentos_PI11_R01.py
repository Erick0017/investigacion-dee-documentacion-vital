"""Bounded canonical renderer attempt on the two staged full DOCX. No desktop Office."""
from pathlib import Path
from datetime import datetime,timezone
import os,json,hashlib,subprocess,sys
P=Path(__file__).resolve().parents[1]
BASE=Path(r'C:\Users\Erik\.cache\codex-runtimes\codex-primary-runtime\dependencies')
PY=BASE/'python/python.exe'
RENDER=Path(r'C:\Users\Erik\.codex\plugins\cache\openai-primary-runtime\documents\26.1104.22356\skills\documents\render_docx.py')
assert Path(sys.executable).resolve()==PY.resolve()
proof=json.loads((P/'documentos/ESTRUCTURA_EDICION_1_40_PI11_R01.json').read_text('utf8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=[]
env=dict(os.environ);env['PATH']=os.pathsep.join(str(BASE/x) for x in ('bin/override','bin/fallback'))
for i,row in enumerate(proof['rows']):
    f=Path(row['output']['path']);assert sha(f)==row['output']['sha256']
    out=P/'documentos'/('RENDER_1_40_'+str(i));assert not out.exists()
    cmd=[str(PY),'-I','-B','-X','utf8',str(RENDER),str(f),'--output_dir',str(out)]
    try:
        r=subprocess.run(cmd,env=env,cwd=P,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=60)
        status={'command':cmd,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
    except subprocess.TimeoutExpired as e:
        status={'command':cmd,'exit_code':None,'timeout_seconds':60,'stdout':str(e.stdout),'stderr':str(e.stderr)}
    pages=list(out.glob('page-*.png')) if out.exists() else []
    rows.append({'path':str(f),'sha256':sha(f),'bytes':f.stat().st_size,'render':status,'PNG_pages':len(pages),'visual_review_performed':False})
blocked=any(v['render']['exit_code']!=0 or v['PNG_pages']==0 for v in rows)
v={'schema':'DEE.PI11.actual_DOCX_render_attempt.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),
 'status':'render_blocked_explicit_limitation' if blocked else 'rendered_pending_Root_review',
 'documents':rows,'limitation':'El runtime disponible no proporciona LibreOffice soffice.exe en sus binarios empaquetados; el renderizador canónico falló y no generó páginas. Se verificó estructura XML/CRC y preservación literal, no legibilidad visual.' if blocked else '',
 'runtime_PATH_limited_to_bundle':env['PATH'],'desktop_Office_or_user_LibreOffice_used':False,'Native_imported':False,'authoring_marker_run_once_by_Root':True}
out=P/'documentos/VERIFICACION_VISUAL_1_40_PI11_R01.json';assert not out.exists();out.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'proof':str(out),'status':v['status'],'render_codes':[r['render']['exit_code'] for r in rows],'pages':[r['PNG_pages'] for r in rows]},ensure_ascii=False))

