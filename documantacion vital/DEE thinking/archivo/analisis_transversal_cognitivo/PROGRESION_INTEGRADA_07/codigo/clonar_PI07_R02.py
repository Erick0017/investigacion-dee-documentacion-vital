"""Explicit full-pair import plus declared directory schema before first use.

The official import restores Runtime at0ticks; the bounded directory helper
then preserves external empty paths before any Owner/evolution. R01 is kept.
"""
from pathlib import Path
import argparse,importlib.util,json,re,sys
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent.parent
C=P.parents[2]/'DEE Cognitive 2.0'
S=P/'estados/candidato/sistema'
parser=argparse.ArgumentParser();parser.add_argument('--par',required=True);parser.add_argument('--vida',required=True)
a=parser.parse_args()
if not re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_[A-Za-z0-9_]{1,24}',a.vida):raise ValueError('Explicit PI03 descendant ID required')
source=Path(a.par).resolve(strict=True)
sys.path.insert(0,str(P/'codigo'))
from fuentes_completas_PI07_R01 import allowed_pair
if not allowed_pair(source):raise ValueError('Only reviewed complete frozen pair stores accepted')
if(S/'estado/ACTIVO.json').exists():raise ValueError('This isolated system must not select a principal')
if not(S/'gestionar.py').is_file():raise ValueError('Build the reviewed isolated system first')
sys.path[:0]=[str(S),str(S/'app'),str(C/'reproducibilidad')]
from app.lives import Store
from app.importacion_emparejada import import_pair
from observador_pasivo import snapshot_view,compare_native
store=Store(S)
result=import_pair(store,source,a.vida)
sys.path.insert(0,str(P/'codigo'))
from materializar_vacios_PI07_R02 import materialize
directory_proof=P/'control'/('VACIOS_'+a.vida.removeprefix('ECI02_PI03_REPRO_PI04_PI05_PI07_')+'_R02.json')
directories=materialize(a.vida,source,apply=True,output=directory_proof)
r=store.record(a.vida)
comparison=compare_native(snapshot_view(source/'VIDA.deetsnap.gz'),snapshot_view(S/r['snapshot']))
proof={'schema':'DEE.PI07.full_pair_diagnostic_import.R02','result':result,'comparison':comparison,'new_Native_ticks':0,'no_T0':True,'no_selection':True,
 'external_directory_schema':{'proof':str(directory_proof),'declared':directories['declared_directories'],'created':len(directories['created']),
  'critical_files_unchanged':directories['critical_files_unchanged'],'before_first_owned_evolution':True}}
out=P/'control'/('IMPORTACION_'+a.vida+'.json')
with out.open('x',encoding='utf-8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
print(json.dumps({'life':a.vida,'tick':r['physical']['tick'],'proof':str(out)}))
