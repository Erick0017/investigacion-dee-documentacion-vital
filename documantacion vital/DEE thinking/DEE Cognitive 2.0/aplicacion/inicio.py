"""Menú de entrega. Ver la presentación o el manual nunca importa el motor."""
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent

def targets():
    project=json.loads((ROOT/'PROYECTO.json').read_text(encoding='utf-8-sig'))
    manual=(ROOT/project['manual_current']).resolve()
    if not manual.is_relative_to(ROOT) or not manual.is_file():
        raise FileNotFoundError('Falta el Manual Maestro vigente dentro de esta carpeta.')
    video=(ROOT/project['public_presentation']).resolve()
    python=ROOT/'motor/python313/python.exe'
    app=ROOT/'aplicacion/GENESIS/genesis.py'
    for path in (python,app):
        if not path.is_file():raise FileNotFoundError('Falta un archivo de la entrega completa: '+str(path.relative_to(ROOT)))
    return project,manual,video,python,app

def available_lives(project):
    """Read existing identity cards only; never import/create a world."""
    preferred=project.get('selected_life')
    declared=project.get('current_available_lives')
    if declared is None:
        declared=[preferred,*project.get('extensions_ECI02',{}).get('selectable_lives',[])]
    if not isinstance(declared,list):raise ValueError('current_available_lives debe ser una lista explícita.')
    candidates=[preferred,*declared]
    seen=set();valid=[];unavailable=[]
    directory=(ROOT/'sistema/estado/vidas').resolve()
    for item in candidates:
        life=item.get('life_id') if isinstance(item,dict) else item
        if not isinstance(life,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,95}',life):
            unavailable.append({'life_id':str(life),'reason':'Identidad literal inválida; no se crea una vida.'});continue
        if life in seen:continue
        seen.add(life)
        try:
            path=(directory/life/'VIDA.json').resolve(strict=True)
            if not path.is_relative_to(directory):raise ValueError('La ficha escapa de estado/vidas.')
            card=json.loads(path.read_text(encoding='utf-8-sig'))
            if card['life_id']!=life:raise ValueError('La identidad de la ficha no coincide.')
            snapshot=(ROOT/'sistema'/card['snapshot']).resolve(strict=True)
            if not snapshot.is_relative_to((ROOT/'sistema/estado').resolve())or not snapshot.is_file():raise ValueError('El snapshot no es un archivo del estado operativo.')
            tick=card['physical']['tick'];n=card['physical']['N']
            if type(tick)is not int or tick<0 or type(n)is not int or n<1:raise ValueError('Corte físico inválido.')
            valid.append({'life_id':life,'world_id':card['world_id'],'profile':card['profile'],'tick':tick,'N':n,
                          'principal':life==preferred,'snapshot_sha256':card['snapshot_sha256'],
                          'scope':'Principal vigente'if life==preferred else 'Alternativa explícita; no cambia la principal'})
        except (OSError,ValueError,KeyError)as error:
            unavailable.append({'life_id':life,'reason':str(error),'no_automatic_reconstruction':True})
    return valid,unavailable

def launch_existing(project,life,python,app):
    lives,_=available_lives(project)
    if not any(row['life_id']==life for row in lives):raise ValueError('Vida no disponible; no se importa ni reconstruye otra.')
    args=['--vida',life]
    if life==project.get('selected_life'):args+=['--puerto','8884']
    else:args+=['--diagnostico','--puerto','8886'if life=='ECI02_ACCESO_REVISADO_MINUS'else'8885']
    return subprocess.run([str(python),'-I','-B','-X','utf8',str(app),*args],cwd=ROOT).returncode

def main():
    p=argparse.ArgumentParser(description='DEE Cognitive 2.0 · entrada única')
    g=p.add_mutually_exclusive_group()
    g.add_argument('--presentacion',action='store_true')
    g.add_argument('--manual',action='store_true')
    g.add_argument('--sistema',action='store_true')
    g.add_argument('--comprobar-menu',action='store_true')
    g.add_argument('--listar-vidas',action='store_true',help='Enumera fichas existentes sin importar el motor ni avanzar ticks.')
    a,extra=p.parse_known_args()
    project,manual,video,python,app=targets()
    if a.listar_vidas:
        if extra:p.error('--listar-vidas no admite argumentos de ejecución.')
        lives,unavailable=available_lives(project)
        print(json.dumps({'selected_life':project['selected_life'],'lives':lives,'unavailable':unavailable,
                          'native_imported':False,'new_ticks':0},ensure_ascii=False))
        return 0
    if a.comprobar_menu:
        card=json.loads((ROOT/'sistema/estado/vidas'/project['selected_life']/'VIDA.json').read_text(encoding='utf-8-sig'))
        lives,unavailable=available_lives(project)
        print(json.dumps({'menu':['VER PRESENTACION','ABRIR DEE COGNITIVE','CONSULTAR MANUAL','ELEGIR VIDA DISPONIBLE'],
            'root':str(ROOT),'video':str(video),'video_available':video.is_file(),'manual':str(manual),'life_id':card['life_id'],
            'tick':card['physical']['tick'],'available_lives':lives,'unavailable_lives':unavailable,'native_imported':False,'new_ticks':0},ensure_ascii=False))
        return 0
    action='sistema' if a.sistema or extra else 'presentacion' if a.presentacion else 'manual' if a.manual else None
    while True:
        if action is None:
            print('\nDEE COGNITIVE 2.0\n\n1  VER PRESENTACION\n2  ABRIR DEE COGNITIVE\n3  CONSULTAR MANUAL\n4  ELEGIR VIDA DISPONIBLE\n0  SALIR\n')
            answer=input('Elija una opcion: ').strip()
            if answer=='0':return 0
            action={'1':'presentacion','2':'sistema','3':'manual','4':'vidas'}.get(answer)
            if action is None:continue
        if action=='vidas':
            lives,unavailable=available_lives(project)
            for item in unavailable:print('No disponible: '+item['life_id']+' — '+item['reason'])
            if not lives:raise ValueError('No hay vidas operativas disponibles; no se crea otra.')
            for index,item in enumerate(lives,1):
                print(str(index)+'  '+item['life_id']+' · T'+str(item['tick'])+' · '+item['scope'])
            choice=input('Elija una vida (0 para volver): ').strip()
            if choice=='0':action=None;continue
            if not choice.isdecimal()or not 1<=int(choice)<=len(lives):
                print('Selección inválida; no se abrió ninguna vida.');action=None;continue
            return launch_existing(project,lives[int(choice)-1]['life_id'],python,app)
        elif action in ('presentacion','manual'):
            path=video if action=='presentacion' else manual
            if not path.is_file():
                print('El archivo solicitado no está disponible: '+str(path),file=sys.stderr)
                return 2
            try:os.startfile(str(path),'open')
            except OSError as error:
                print('No se pudo abrir el archivo con la aplicacion de Windows: '+str(error),file=sys.stderr)
                print('Para el video use un reproductor MP4 H.264/AAC. Para el manual use Word o un lector DOCX compatible.',file=sys.stderr)
                return 2
            if a.presentacion or a.manual:return 0
            action=None
        else:
            args=list(extra)
            if '--vida' not in args and '--nueva' not in args:args=['--vida',project['selected_life'],*args]
            return subprocess.run([str(python),'-I','-B','-X','utf8',str(app),*args],cwd=ROOT).returncode

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,KeyError) as error:
        print('Entrega incompleta o estado no disponible: '+str(error),file=sys.stderr)
        raise SystemExit(2)
