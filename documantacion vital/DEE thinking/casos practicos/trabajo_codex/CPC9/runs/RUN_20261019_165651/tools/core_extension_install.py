"""Copy pre-execution frozen design metadata, never expected solutions into actors."""
from pathlib import Path
import json,shutil
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE'
source=RUN/'notes/core_extension_v2/RECUPERACION_EXTENSION_CONGELADA.json';target=CORE/'configuraciones'/source.name
shutil.copyfile(source,target)
compile((CORE/'reproduccion/worker_extension.py').read_text(encoding='utf8'),'worker_extension.py','exec')
print(json.dumps({'frozen_inputs':str(target)}))
