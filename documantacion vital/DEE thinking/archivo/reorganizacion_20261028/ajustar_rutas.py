from pathlib import Path
import json,sys,shutil,hashlib
import reorganizar_dee as R
ROOT=R.ROOT;APP=ROOT/'DEE Cognitive 2.0'
archive=ROOT/'archivo/produccion_audiovisual_DEE_Cognitive_2_0_20261028/videos'
assert APP.is_dir() and not archive.exists()
p=APP/'aplicacion/inicio.py';s=p.read_text(encoding='utf8')
s=s.replace("video=ROOT/'videos/DEE_Cognitive_2_0_Presentacion.mp4'","video=(ROOT/project['public_presentation']).resolve()")
s=s.replace('for path in (video,python,app):','for path in (python,app):')
s=s.replace("'root':str(ROOT),'video':str(video),'manual':str(manual),'life_id':card['life_id'],","'root':str(ROOT),'video':str(video),'video_available':video.is_file(),'manual':str(manual),'life_id':card['life_id'],")
s=s.replace("path=video if action=='presentacion' else manual\n            try:","path=video if action=='presentacion' else manual\n            if not path.is_file():\n                print('El archivo solicitado no está disponible: '+str(path),file=sys.stderr)\n                return 2\n            try:")
compile(s,str(p),'exec');R.preserve_edit(p,s.encode('utf8'),'El video archivado sólo se verifica al solicitar presentación; no es dependencia del sistema ni del manual.')
p=APP/'PROYECTO.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
assert d['selected_life']=='DEE20_DEMO_01'
d['preserved_source']='../archivo/DEE Cognitive System 1.1'
d['public_presentation']='../archivo/produccion_audiovisual_DEE_Cognitive_2_0_20261028/videos/DEE_Cognitive_2_0_Presentacion_Cientifica_Profesional_1080p.mp4'
R.preserve_edit(p,(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf8'),'Localizadores explícitos de procedencia y audiovisual archivados; selección y versión conservadas.')
p=APP/'sistema/iniciar_sistema.ps1';s=p.read_text(encoding='utf-8-sig')
s=s.replace("$localPython = Join-Path $PSScriptRoot '.entorno\\Scripts\\python.exe'","$localPython = Join-Path $PSScriptRoot '..\\motor\\python313\\python.exe'\n    if (-not (Test-Path -LiteralPath $localPython)) { $localPython = Join-Path $PSScriptRoot '.entorno\\Scripts\\python.exe' }")
s=s.replace("if (-not $Comandos -or $Comandos.Count -eq 0) { $Comandos = @('estado') }","if (-not $Comandos -or $Comandos.Count -eq 0) {\n    $project = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot '..\\PROYECTO.json') | ConvertFrom-Json\n    $Comandos = @('estado','--vida',[string]$project.selected_life)\n}")
R.preserve_edit(p,s.encode('utf8'),'Lanzador de mantenimiento usa intérprete local y selección real; no crea ACTIVO ni otra vida.')
relative=Path('sistema/estado/fuentes_emparejadas/APD04_SEMILLA_COLABORADOR_R01_T654959_COMPLETO_N0_R01')
src=ROOT/'DEE Cognitive System 1.1'/relative;dst=APP/relative
assert src.is_dir() and not dst.exists()
manifest=json.loads((src/'EXPORTACION_SERVICIO.json').read_text(encoding='utf8'))
assert R.sha(src/'EXPORTACION_SERVICIO.json')=='0658ca4404f1d676cb9d496f2c1d4f5fbdfee98188a5c717db68e760088f9b2c'
shutil.copytree(src,dst)
for item in manifest['members']:
    f=(dst/item['file']).resolve();assert f.is_relative_to(dst.resolve())
    assert f.is_file() and f.stat().st_size==item['bytes'] and R.sha(f)==item['sha256'],item['file']
log=R.read();log['comprobaciones'].append({'utc':R.now(),'type':'copied_complete_preexisting_parent_unit','source':str(src.relative_to(ROOT)),'destination':str(dst.relative_to(ROOT)),'members_verified':len(manifest['members']),'bytes':sum(x['bytes'] for x in manifest['members']),'manifest_sha256':R.sha(dst/'EXPORTACION_SERVICIO.json'),'selected_life_unchanged':True,'not_a_new_acquisition':True,'reason':'El contrato CLI ya exigía este par; se incorpora entero sin fusionarlo con la vida seleccionada.'});R.write(log)
(ROOT/'CPC - Experimentos y mecanismos').mkdir(exist_ok=True)
print('AJUSTES_Y_PAR_COMPLETO',len(manifest['members']),flush=True)
