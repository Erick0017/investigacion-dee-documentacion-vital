"""One bounded packaged-renderer attempt; never edits the DOCX or kernel."""
import subprocess,sys,json,hashlib
from pathlib import Path
L=Path(__file__).resolve().parent;R=L.parents[2];E=R/'evidencia/campanas/MI02_ARQUITECTURA_DISTRIBUIDA'
src=R/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_8_MI02_SIN_VALIDACION_VISUAL.docx'
helper=Path(r'C:\Users\Erik\.codex\plugins\cache\openai-primary-runtime\documents\26.1011.51657\skills\documents\render_docx.py')
root=next(p for p in R.parents if(p/'_dcs11_env_20261020_002458').exists());target=root/'_mi02_render_word_18';target.mkdir(exist_ok=True)
command=[sys.executable,str(helper),str(src),'--output_dir',str(target),'--emit_pdf']
try:
    cp=subprocess.run(command,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=60);result={'command':command,'returncode':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr,'timeout':False}
except subprocess.TimeoutExpired as ex:result={'command':command,'returncode':None,'stdout':str(ex.stdout),'stderr':str(ex.stderr),'timeout':True,'limit_seconds':60}
result.update({'document_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output_directory':str(target),'page_images':[str(p)for p in sorted(target.glob('page-*.png'))],'visual_validation':False,'scope':'A render attempt is not a visual inspection. If no converter is available, structural checks alone do not certify layout.','native_ticks':0})
(E/'VERIFICACION_WORD_MI02_RENDER.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');sys.stdout.reconfigure(encoding='utf8');print(json.dumps(result,ensure_ascii=False,indent=2))
