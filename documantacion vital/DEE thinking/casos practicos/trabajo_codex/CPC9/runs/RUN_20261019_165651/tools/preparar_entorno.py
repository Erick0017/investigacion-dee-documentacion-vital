"""Offline installation of the included, immutable CPython3.13 Windows wheel.

No network access, package updates, historical paths or source edits are used.
The virtual environment is an installation output and must not be redistributed.
"""
from __future__ import annotations
import argparse,hashlib,json,os,struct,subprocess,sys,venv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WHEEL=ROOT/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
WHEEL_SHA='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
PYD_SHA='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
KERNEL_SHA='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
CHECK='''import hashlib,json,sys,dee_thinking as d
from pathlib import Path
from dee_thinking import _native
p=Path(_native.__file__).resolve()
print(json.dumps({'python':sys.executable,'version':d.__version__,'module':str(Path(d.__file__).resolve()),'native':str(p),'native_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'build_info':d.build_info()}))
'''

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description='Instala4.5oficial offline sin tocar versiones previas')
    p.add_argument('--dest',type=Path,default=ROOT/'.runtime_cpc9');a=p.parse_args()
    if sys.version_info[:2]!=(3,13) or struct.calcsize('P')!=8 or os.name!='nt':
        raise SystemExit('Use py -3.13 x64 Windows. No se instala ni descarga un intérprete automáticamente.')
    if not WHEEL.is_file() or sha(WHEEL)!=WHEEL_SHA:raise SystemExit('WHL ausente o SHA diferente; no se prepara el entorno')
    dest=a.dest.resolve();python=dest/'Scripts/python.exe';created=False
    if dest.exists():
        if not python.is_file():raise SystemExit('Destino existente que no es venv válido. Se conserva; elija otro --dest.')
        check=subprocess.run([str(python),'-I','-B','-c',CHECK],capture_output=True,text=True,timeout=60)
        if check.returncode:raise SystemExit('El venv existente no contiene el instrumento esperado. Se conserva sin modificar. Use otro --dest.')
    else:
        venv.EnvBuilder(with_pip=True,clear=False).create(dest);created=True
        install=subprocess.run([str(python),'-I','-m','pip','install','--no-index','--no-deps','--disable-pip-version-check',str(WHEEL)],capture_output=True,text=True,timeout=180)
        if install.returncode:
            (dest/'INSTALL_ERROR.txt').write_text(install.stdout+'\n'+install.stderr,encoding='utf-8')
            raise SystemExit('Instalación offline fallida; no se elimina el entorno parcial. Véase INSTALL_ERROR.txt.')
        check=subprocess.run([str(python),'-I','-B','-c',CHECK],capture_output=True,text=True,timeout=60)
        if check.returncode:raise SystemExit('Importación limpia falló: '+check.stderr)
    identity=json.loads(check.stdout)
    if identity['version']!='4.5.0' or identity['native_sha256']!=PYD_SHA or identity['build_info'].get('kernel_source_sha256')!=KERNEL_SHA:
        raise SystemExit('Identidad importada inesperada; no se anuncia una instalación válida.')
    report={'status':'VERIFIED_OFFLINE_INSTALLATION','new_environment':created,'wheel_sha256':WHEEL_SHA,'wheel':str(WHEEL),
            'identity':identity,'network_used':False,'historical_dependencies':False,
            'run_example':[str(python),'-I','-B',str(ROOT/'ejecutar.py'),'demo','--out',str(ROOT/'runs/demo_nueva')],
            'scope':'Identidad e importación; las regresiones físicas se documentan por separado. Este venv no forma parte de la entrega.'}
    (dest/'INSTALLATION_CPC9.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
