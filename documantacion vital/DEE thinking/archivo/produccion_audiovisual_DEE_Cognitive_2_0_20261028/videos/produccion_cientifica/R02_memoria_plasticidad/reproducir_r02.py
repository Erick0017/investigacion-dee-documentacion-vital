"""Entrada de reproducción audiovisual local; no ejecuta el motor DEE.

Uso: Python 3.12 -X utf8 -B reproducir_r02.py plan|previas|render|musica|
     mezcla|verificar|muestras|secuencia|voz
Los originales y las exportaciones existentes nunca se sobrescriben.
"""
from pathlib import Path
import argparse,subprocess,sys,tempfile,os
W=Path(__file__).resolve().parent;PROD=W.parent
def alias_render():
    alias=Path(tempfile.gettempdir())/'DEE_R02_RENDER_PROD'
    if alias.exists():
        assert alias.is_junction() and alias.resolve()==PROD.resolve(),'Alias ajeno; no se cambia.'
        return
    # Sólo crea una unión, sin borrar/mover el origen ni cambiar permisos.
    quote=lambda p:"'"+str(p).replace("'","''")+"'"
    cmd='New-Item -ItemType Junction -Path '+quote(alias)+' -Target '+quote(PROD)+' -ErrorAction Stop | Out-Null'
    subprocess.run(['powershell.exe','-NoProfile','-Command',cmd],check=True)
    assert alias.is_junction() and alias.resolve()==PROD.resolve()
def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('fase',choices=['plan','previas','render','musica','mezcla','verificar','muestras','secuencia','voz']);a.add_argument('--ids',nargs='*');n=a.parse_args()
    if n.fase in ['previas','render']:alias_render()
    if n.fase=='voz':args=['sintetizar_voz_r02.py','--all']
    elif n.fase in ['verificar','muestras','secuencia']:args=['verificar_r02.py',{'verificar':'technical','muestras':'samples','secuencia':'sequence'}[n.fase]]
    else:args=['pelicula_r02.py',{'previas':'preview','musica':'music','mezcla':'mux'}.get(n.fase,n.fase)]
    if n.ids:
        assert n.fase in ['previas','render','voz'];args+=['--ids',*n.ids]
    subprocess.run([sys.executable,'-X','utf8','-B',str(W/args[0]),*args[1:]],check=True,cwd=W)
if __name__=='__main__':main()
