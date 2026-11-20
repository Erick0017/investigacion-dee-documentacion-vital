"""Finite CLI contract checks; rejected arguments never create a world."""
import argparse,json,subprocess,sys,tempfile
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();root=Path(a.root).resolve();empty=Path(tempfile.mkdtemp(prefix='cpc3_cli_contract_'));rows=[]
    combinations=[['continuidad','--perfil','politica'],['comparacion','--perfil','politica'],['politica','--abierto'],['seleccion','--snapshot','unused.deetsnap'],['continuidad','--zip','unused.zip']]
    for i,args in enumerate(combinations):
        output=empty/str(i);cmd=[sys.executable,'-I','-B',str(root/'ejecutar.py'),*args,'--output',str(output)]
        r=subprocess.run(cmd,cwd=empty,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=15)
        assert r.returncode==2 and not output.exists(),(cmd,r.returncode,r.stderr)
        rows.append({'arguments':args,'exit_code':r.returncode,'output_not_created':not output.exists(),'stderr':r.stderr})
    out=root/'resultados/CLI_CONTRACT_CHECK.json';out.write_text(json.dumps({'technical_assertions':True,'cases':rows,'scope':'Parser only; these rejected configurations are not physical experiments'},indent=2),encoding='utf-8');print(json.dumps({'cases':len(rows),'technical_assertions':True}))
if __name__=='__main__':main()
