from pathlib import Path
import argparse,importlib.util,json
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args();root=a.root.resolve(strict=True);out=a.out_dir.resolve()
 if out.exists()or out==root or root.is_relative_to(out)or out.is_relative_to(root):raise ValueError('El recálculo requiere destino nuevo externo al material')
 s=importlib.util.spec_from_file_location('D6_preserved_recalc',root/'RECALCULAR_D_PI09_R03.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);value=m.calculate(root)
 if value.get('integrity_passed')is not True or not any(g['arm']=='real'and g['evaluation_completed']==6 for g in value['groups']):raise ValueError('Los seis primarios D reales no están verificados')
 out.mkdir();(out/'RESULTADO_RECALCULO.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'integrity_passed':True,'Native_executed':False,'DEE_imports':0}))
if __name__=='__main__':main()
