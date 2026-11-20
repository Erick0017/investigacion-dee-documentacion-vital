"""New literal user-style sequence after explicit research-line selection."""
from pathlib import Path
import json,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
JOBS=[{'contexto':'c3','valores':[31,41],'herramienta':'trabajadores'},
      {'contexto':'c3','valores':[32,43],'herramienta':'puertas'}]
def op(case,args):subprocess.run([sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--caso',case,*args],check=True,cwd=ROOT)
if __name__=='__main__':
    # No --vida argument: the recorded selected continuation must be loaded,
    # never an implicit new world, favorable auxiliary or old parent.
    op('23_ABRIR_PREDETERMINADO',['mente-estado'])
    op('24_SECUENCIA_NUEVA_PREDETERMINADA',['mente-sesion','--situaciones',json.dumps(JOBS,separators=(',',':'))])
    op('25_GUARDAR_PREDETERMINADO',['guardar'])
    op('26_RECARGAR_PREDETERMINADO',['mente-estado'])
