"""New boundary use and full external prepare/verify across processes."""
from pathlib import Path
import json,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def op(case,args):subprocess.run([sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--caso',case,*args],cwd=ROOT,check=True)
def main():
    dest=HERE/'PROTOCOLO_CONTINUACION_FINAL.json'
    if dest.exists():raise FileExistsError('No repeated final test')
    dest.write_text(json.dumps({'revision':'EO02.current_reacquired_reference.and_complete_external_state.1','frozen_monotonic':time.monotonic(),'parent_actual_life':'EO02_MAIN after27D, no rollback','reference_environment':14,'border_probe':[24,38],'meaning':'First new boundary use after two errors/readquisition, never intact contextual retention','prepare':[20,34],'verify_next_process':[23,37],'fixed_context_codec':'append0and actual phase0/1; no previousworker or target','criterion':'Boundary native+ useful; actual prepare file then other-worker verification across independent processes; if adverse, preserve it without repair'},indent=2)+'\n',encoding='utf8')
    op('36_MAIN_BORDE_READQUIRIDO',['evolucion-servicio','--vida','EO02_MAIN','--dominio','puertas','--observaciones','[[24,38]]','--referencia-entorno','14','--reiniciar-entorno'])
    op('37_MAIN_C_PREPARAR',['evolucion-servicio','--vida','EO02_MAIN','--dominio','transaccion','--observaciones','[[20,34]]','--referencia-entorno','14','--reiniciar-entorno','--fase-visible'])
    op('38_MAIN_C_OTRO_PROCESO',['evolucion-servicio','--vida','EO02_MAIN','--dominio','transaccion','--observaciones','[[23,37]]','--referencia-entorno','14','--fase-visible'])
if __name__=='__main__':main()
