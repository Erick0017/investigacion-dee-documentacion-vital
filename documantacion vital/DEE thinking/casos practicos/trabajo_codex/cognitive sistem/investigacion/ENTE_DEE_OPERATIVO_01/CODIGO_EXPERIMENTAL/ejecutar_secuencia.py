"""Calendario de experiencias fijadas; el gestor decide físicamente, no este guion."""
from pathlib import Path
import argparse,json,subprocess,sys,time
HERE=Path(__file__).resolve().parent
def main():
    p=argparse.ArgumentParser();p.add_argument('--vida',required=True);p.add_argument('--secuencia',choices=['desarrollo','SOCIAL_RESERVA_1','SOCIAL_RESERVA_2','SOCIAL_RESERVA_3'],required=True);p.add_argument('--prefijo',required=True);p.add_argument('--desde',type=int,default=0);p.add_argument('--hasta',type=int,default=6);a=p.parse_args()
    if not 0<=a.desde<=a.hasta<=6:raise ValueError('Finite predeclared slice0..6')
    plan=json.loads((HERE/'PROTOCOLO_COOPERACION_AMBIENTAL.json').read_bytes())
    if a.secuencia=='desarrollo':
        pairs=[r['public']for r in plan['development']['sequence']];private=[r['B']for r in plan['development']['sequence']]
    else:
        row=next(r for r in plan['reserves']if r['id']==a.secuencia);pairs=row['pairs'];private=row['private']
    for i in range(a.desde,a.hasta):
        pair=pairs[i];args=['ente-servicio','--vida',a.vida,'--mediciones',str(pair[0])+':'+str(pair[1]),'--valvula-social']
        if private[i]is not None:args+=['--privada-B',str(private[i]),'--detalle']
        cmd=[sys.executable,'-I','-B',str(HERE/'ejecutar_operacion.py'),'--caso',a.prefijo+'_'+str(i+1),*args]
        # Never read a verdict to choose a stimulus or an action. Failure only
        # stops the instrument; the reached state is not restored or replaced.
        r=subprocess.run(cmd)
        if r.returncode:return r.returncode
    return 0
if __name__=='__main__':raise SystemExit(main())
