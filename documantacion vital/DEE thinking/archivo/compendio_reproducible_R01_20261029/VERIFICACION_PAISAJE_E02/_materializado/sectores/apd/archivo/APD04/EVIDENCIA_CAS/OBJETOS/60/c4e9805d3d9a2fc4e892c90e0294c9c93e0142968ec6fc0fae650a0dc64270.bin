"""Wrapper stdlib del dossier Full cerrado: no Runtime/Native ni nuevas experiencias."""
import argparse,importlib.util,json
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument('--dossier',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert not a.out.exists()
    script=a.dossier/'CODIGO/exportar_full_exacto_compacto_n0_r01.py';s=importlib.util.spec_from_file_location('archived_exact_full_recalculation',script);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    result=m.recalculate(a.dossier)
    with a.out.open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
if __name__=='__main__':main()
