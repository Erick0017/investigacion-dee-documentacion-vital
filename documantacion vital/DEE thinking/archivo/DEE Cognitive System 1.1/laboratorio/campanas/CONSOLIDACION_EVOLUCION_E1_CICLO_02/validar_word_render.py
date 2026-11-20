"""One bounded visual-render attempt on the exact updated Word. No simulation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
L=Path(__file__).resolve().parent;R=L.parents[2];E=R/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
doc=R/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_6_CICLO02_SIN_VALIDACION_VISUAL.docx'
script=Path('C:/Users/Erik/.codex/plugins/cache/openai-primary-runtime/documents/26.1011.51657/skills/documents/render_docx.py')
target=Path('D:/GENESIS AI/GENESIS 5.0/simulador de universo ab-initio/dee_libreria/VERSION_27/tests/_c02_render_20261022')
command=[sys.executable,str(script),str(doc),'--output_dir',str(target),'--emit_pdf','--verbose']
try:
    p=subprocess.run(command,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=45)
    code=p.returncode;stdout=p.stdout;stderr=p.stderr;error=None
except subprocess.TimeoutExpired as ex:
    code=None;stdout=str(ex.stdout or'');stderr=str(ex.stderr or'');error='Bounded45s timeout; no claim of visual validation'
images=list(target.glob('*.png'))if target.exists()else[]
out={'utc':datetime.now(timezone.utc).isoformat(),'word':str(doc),'sha256':hashlib.sha256(doc.read_bytes()).hexdigest(),'command':command,'returncode':code,
     'stdout':stdout,'stderr':stderr,'error':error,'page_images':len(images),'visual_validation':'RENDERED_REQUIRES_PAGE_QA'if code==0 and images else'BLOCKED_NO_VISUAL_VALIDATION',
     'structural_check':'ZIP/XML and footer fields checked separately; not substituted for page QA','native_ticks':0,'software_version_unchanged':'1.1.0'}
(E/'VALIDACION_VISUAL_WORD.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
