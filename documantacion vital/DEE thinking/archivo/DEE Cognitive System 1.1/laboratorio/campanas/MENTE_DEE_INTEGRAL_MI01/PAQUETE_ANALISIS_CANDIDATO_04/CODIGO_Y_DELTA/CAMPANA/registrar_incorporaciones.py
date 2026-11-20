"""Preserve exact operational deltas when admitted; no native execution."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
paths=[S/'gestionar.py',S/'capacidades/mente_integral_mi01/__init__.py',S/'contratos/MENTE_DEE_INTEGRAL_MI01.json',S/'capacidades/CATALOGO_CAPACIDADES.json']
records=[]
for p in paths:
    h=sha(p);target=E/'FUENTES_POR_SHA256'/(h+p.suffix)
    if not target.exists():shutil.copy2(p,target)
    records.append({'path':str(p.relative_to(R)),'sha256':h,'exact_bytes':str(target.relative_to(R))})
p=E/('INCORPORACION_'+sys.argv[1]+'.json')
if p.exists():raise FileExistsError(p)
atomic_json(p,{'id':sys.argv[1],'files':records,'native_ticks':0,'meaning':'Operational code availability, not transferred knowledge. MAIN100/103 acquired in its own trajectory.'})
