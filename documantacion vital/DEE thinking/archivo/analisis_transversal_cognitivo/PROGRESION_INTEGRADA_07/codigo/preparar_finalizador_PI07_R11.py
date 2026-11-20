from pathlib import Path
P=Path(__file__).resolve().parent
source=(P/'sellar_desde_extraccion_comprobada_PI07_R09.py').read_text('utf8')
needle="r=root/'r';audit=read(root/'AUDIT.json')"
if source.count(needle)!=1:raise ValueError('Exact previous read-only finalizer expected')
source=source.replace(needle,"r=root/'r2';audit=read(root/'AUDIT_R10.json')").replace('final_analysis.verified.R09','final_analysis.verified.R11')
with(P/'sellar_desde_extraccion_comprobada_PI07_R11.py').open('x',encoding='utf8')as f:f.write(source)
print('ONLY_COMPLETE_FENCE_RESULT_PATH_UPDATED_NO_CRITERION_CHANGE')
