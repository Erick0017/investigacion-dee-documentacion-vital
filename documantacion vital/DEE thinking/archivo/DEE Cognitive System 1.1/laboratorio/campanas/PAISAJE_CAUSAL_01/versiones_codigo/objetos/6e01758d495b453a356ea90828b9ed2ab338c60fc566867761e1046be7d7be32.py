"""Read existing full checkpoints to bracket the older S158 route."""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store,load_adapter
from app.native_tools import observe,physical,digest_file
from app.process_control import protect_current
from instrumentos_pc01 import frame,sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);r=a.system.parent;ef=r/'evidencia/campanas/ESPANOL_FUNCIONAL_01';data={'source_sha256':sha(__file__),'no_evolution':True,'question':'Bracket foreign orbit in existing checkpoints; a phase-matched sample is a candidate, not genealogy through unsampled steps.','samples':[]}
paths=[s.snapshot(s.record('ES01_LEXICAL5_source_guards_strict'))]+sorted((ef/'CONTINUIDAD_SIN_SONDAS_07/D_no_material_queries').glob('*.deetsnap.gz'))+[s.snapshot(s.record('ES01_LONG7_D_no_material_queries'))]
for path in paths:
    x=load_adapter('cpc9_integral_n67',path);t=x.tick;dt=22456-t;q=[(38+dt)%67,(58-dt)%67,(16-dt)%67]
    data['samples'].append({'snapshot':str(path),'sha256':digest_file(path),'tick':t,'predicted_fixed_direction_site':q,'record':observe(x.world,q),'physical':physical(x.world,occupation=True),'frame':frame(x.world)})
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps([{'tick':s['tick'],'site':s['predicted_fixed_direction_site'],'record':s['record']}for s in data['samples']]))
