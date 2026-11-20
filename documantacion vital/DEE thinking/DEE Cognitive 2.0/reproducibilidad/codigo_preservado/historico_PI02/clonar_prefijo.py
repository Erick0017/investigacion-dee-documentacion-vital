"""Branch only an explicit frozen campaign paired prefix, never recreateT0."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parent.parent;R=P.parent.parent.parent;S=P/'estados/candidato/sistema'
p=argparse.ArgumentParser();p.add_argument('--vida',required=True);p.add_argument('--descriptor',required=True);args=p.parse_args()
if not args.vida.startswith('ECI02_PI02_'):raise ValueError('Only identified PI02 branches')
desc=(P/args.descriptor).resolve(strict=True)
if not desc.is_relative_to((P/'control').resolve()):raise ValueError('Descriptor must be an existing campaign control record')
proof=P/'control'/('IMPORTACION_'+args.vida+'.json')
if proof.exists()or(S/'estado/vidas'/args.vida).exists():raise ValueError('Never overwrite/reimport a branch')
d=json.loads(desc.read_text(encoding='utf-8'));pair=Path(d['pair']['directory']).resolve(strict=True)
if not pair.is_relative_to(P.resolve()):raise ValueError('Only a preserved complete campaign prefix')
manifest=json.loads((pair/'EXPORTACION_SERVICIO.json').read_text(encoding='utf-8'))
if manifest['life_id']!=d['source_life']or manifest['physical']['tick']!=d['source_tick']or hashlib.sha256((pair/'EXPORTACION_SERVICIO.json').read_bytes()).hexdigest()!=d['pair']['manifest_sha256']:raise ValueError('Frozen prefix identity differs')
sys.path[:0]=[str(S),str(S/'app')]
from app.lives import Store
from app.importacion_emparejada import import_pair
store=Store(S);result=import_pair(store,pair,args.vida)
spec=importlib.util.spec_from_file_location('passive_parser',R/'archivo/analisis_transversal_cognitivo/PROGRESION_INTEGRADA_01/codigo/PROMOVER_PI01.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rec=store.record(args.vida);comp=m.compare_native(m.snapshot_view(pair/'VIDA.deetsnap.gz'),m.snapshot_view(S/rec['snapshot']))
proof.write_text(json.dumps({'schema':'PI02.explicit.frozen.prefix.branch.v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'life':args.vida,'physical_parent':{'life':manifest['life_id'],'tick':manifest['physical']['tick'],'snapshot':manifest['snapshot_sha256']},'source_descriptor':str(desc),'pair':str(pair),'result':result,'comparison':comp,'new_ticks':0},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'life':args.vida,'tick':rec['physical']['tick'],'new_ticks':0}))
