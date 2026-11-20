"""RP stdlib adapter over the preserved actual Native12 recalc."""
from pathlib import Path
import argparse,importlib.util,json
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args()
 root=a.root.resolve(strict=True);out=a.out_dir.resolve()
 if out.exists()or out==root or root.is_relative_to(out)or out.is_relative_to(root):raise ValueError('El recálculo exige un directorio nuevo fuera del material estable')
 spec=importlib.util.spec_from_file_location('PI09_preserved_recalculation',root/'RECALCULAR_CONSULTA_PI09_R01.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.calculate(root)
 if result.get('integrity_passed')is not True or result.get('completed_opportunities')!=12:raise ValueError('El recálculo conservado no verifica los doce primarios')
 out.mkdir(parents=False);(out/'RESULTADO_RECALCULO.json').write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n','utf8')
 print(json.dumps({'integrity_passed':True,'completed_opportunities':12,'Native_executed':False,'DEE_imports':0}))
if __name__=='__main__':main()
