from pathlib import Path
import subprocess, sys, json
w=Path(sys.argv[1]); ff=w.parents[6]/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
# Resolve known tools from the tests workspace, without importing or running the renderer.
ff=Path(r'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\_dee20_trabajo\presentacion_clara\herramientas\ffmpeg.exe')
clip=w/'escenas_limpias/s04.mp4'; out=w/'qc/g07_s04_extracted'; out.mkdir(exist_ok=True)
times=[0.5,9.0,11.0,12.5,15.5,17.0,21.0,25.0,28.5,31.0,36.0,44.0,49.0,53.0]
for t in times:
 p=out/f's04_t{t:05.1f}.png'
 subprocess.run([str(ff),'-hide_banner','-loglevel','error','-ss',str(t),'-i',str(clip),'-frames:v','1','-y',str(p)],check=True)
print(json.dumps({'clip':str(clip),'frames':len(times),'times':times,'out':str(out)}))

