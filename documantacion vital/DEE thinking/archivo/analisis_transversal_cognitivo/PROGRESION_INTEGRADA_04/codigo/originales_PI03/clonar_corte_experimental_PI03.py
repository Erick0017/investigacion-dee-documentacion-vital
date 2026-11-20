"""Explicit import of a full pair to the isolated PI03 system, never selection."""
from pathlib import Path
import argparse,importlib.util,json,re,sys
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent.parent
C=P.parents[2]/'DEE Cognitive 2.0'
S=P/'estados/candidato/sistema'
parser=argparse.ArgumentParser();parser.add_argument('--par',required=True);parser.add_argument('--vida',required=True)
a=parser.parse_args()
if not re.fullmatch(r'ECI02_PI03_[A-Za-z0-9_]{1,48}',a.vida):raise ValueError('Explicit PI03 descendant ID required')
source=Path(a.par).resolve(strict=True)
if not(source.is_relative_to(C/'reproducibilidad/materiales')or source.is_relative_to(P/'estados')):raise ValueError('Only preserved full-pair stores accepted')
if(S/'estado/ACTIVO.json').exists():raise ValueError('This isolated system must not select a principal')
if not(S/'gestionar.py').is_file():raise ValueError('Build the reviewed isolated system first')
sys.path[:0]=[str(S),str(S/'app'),str(C/'reproducibilidad')]
from app.lives import Store
from app.importacion_emparejada import import_pair
from observador_pasivo import snapshot_view,compare_native
store=Store(S)
result=import_pair(store,source,a.vida)
r=store.record(a.vida)
comparison=compare_native(snapshot_view(source/'VIDA.deetsnap.gz'),snapshot_view(S/r['snapshot']))
proof={'schema':'DEE.PI03.full_pair_diagnostic_import.v1','result':result,'comparison':comparison,'new_Native_ticks':0,'no_T0':True,'no_selection':True}
out=P/'control'/('IMPORTACION_'+a.vida+'.json')
with out.open('x',encoding='utf-8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
print(json.dumps({'life':a.vida,'tick':r['physical']['tick'],'proof':str(out)}))
