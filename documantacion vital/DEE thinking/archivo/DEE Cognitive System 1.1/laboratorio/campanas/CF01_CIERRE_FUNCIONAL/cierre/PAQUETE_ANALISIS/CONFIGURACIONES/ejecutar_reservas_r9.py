"""Prospectively frozen task sequences, not a host action-selection policy."""
from pathlib import Path
import argparse, json, subprocess, sys
HERE=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--vida',required=True);p.add_argument('--brazo',choices=['intact','omit_return','nulled'],required=True);args=p.parse_args()
    protocol=json.loads((HERE/'PROTOCOLO_RESERVAS_R9_01.json').read_text(encoding='utf-8'))
    for j,seq in enumerate(protocol['sequences']):
        argv=[sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--caso',args.vida+'_'+seq['id'],'--','cf01-tarea','--vida',args.vida,'--oportunidades='+','.join(map(str,seq['jobs'])),'--pasos',str(seq['attempt_horizon'])]
        if j:argv.append('--reiniciar-entorno')
        if args.brazo=='omit_return':argv.extend(['--retorno','omit_return'])
        if args.brazo=='nulled':argv.extend(['--actuador','nulled'])
        r=subprocess.run(argv,check=False)
        if r.returncode:raise SystemExit(r.returncode)
    return 0
if __name__=='__main__':raise SystemExit(main())
