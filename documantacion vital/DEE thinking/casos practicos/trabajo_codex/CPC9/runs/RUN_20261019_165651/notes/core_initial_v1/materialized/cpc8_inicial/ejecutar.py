"""Single CPC8 public entry. Research workers and auditor remain separate."""
import argparse,runpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser(description='CPC8 privado: ejecución física y revisión')
 p.add_argument('modo',choices=('interactivo','eventos','verificar-datos','referencias','regresion'))
 p.add_argument('archivo',nargs='?');p.add_argument('--salida');a=p.parse_args()
 if a.modo=='verificar-datos':
  # Auditor only, never imported by the participant.
  runpy.run_path(str(ROOT/'tools/verificar_datos.py'),run_name='__main__');return
 if a.modo in('referencias','regresion'):
  if not a.salida:p.error('Esta reproducción requiere --salida en una carpeta nueva')
  destination=Path(a.salida).resolve()
  if a.modo=='regresion':
   sys.argv=['regress_base45.py','--out',str(destination)]
   runpy.run_path(str(ROOT/'tools/regress_base45.py'),run_name='__main__');return
  destination.mkdir(parents=True,exist_ok=False)
  for script,subfolder in(('reproducir_cp01_cp02.py','cp01_cp02'),('reproducir_sem01.py','sem01')):
   sys.argv=[script,'--out',str(destination/subfolder)]
   runpy.run_path(str(ROOT/'base_validada'/script),run_name='__main__')
  return
 args=[str(ROOT/'app/consola.py')]
 if a.modo=='eventos':
  if not a.archivo:p.error('eventos requiere un archivo JSON')
  args+=['--eventos',a.archivo]
 if a.salida:args+=['--salida',a.salida]
 sys.argv=args;runpy.run_path(args[0],run_name='__main__')
if __name__=='__main__':main()
