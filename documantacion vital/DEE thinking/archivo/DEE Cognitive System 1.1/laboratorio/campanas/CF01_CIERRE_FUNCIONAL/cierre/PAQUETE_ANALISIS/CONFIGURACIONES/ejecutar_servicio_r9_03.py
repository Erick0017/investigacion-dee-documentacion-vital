"""Three frozen prospective sequences, same continuous life per arm."""
from pathlib import Path
import argparse,json,subprocess,sys
HERE=Path(__file__).resolve().parent
def main():
    p=argparse.ArgumentParser();p.add_argument('--vida',required=True);p.add_argument('--anular',action='store_true');p.add_argument('--desde',type=int,default=1);p.add_argument('--hasta',type=int,default=3);args=p.parse_args()
    protocol=json.loads((HERE/'PROTOCOLO_SERVICIO_RESERVAS_R9_03.json').read_text(encoding='utf-8'))
    for seq in protocol['new_sequences'][args.desde-1:args.hasta]:
        pairs=','.join(':'.join(map(str,p))for p in seq['pairs'])
        argv=[sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--caso','SERVICIO_'+args.vida+'_'+seq['id'],'--','cf01-servicio','--vida',args.vida,'--mediciones='+pairs,'--referencia-entorno','7']
        if args.anular:argv.extend(['--actuador','nulled'])
        r=subprocess.run(argv,check=False)
        if r.returncode:raise SystemExit(r.returncode)
    return 0
if __name__=='__main__':raise SystemExit(main())
