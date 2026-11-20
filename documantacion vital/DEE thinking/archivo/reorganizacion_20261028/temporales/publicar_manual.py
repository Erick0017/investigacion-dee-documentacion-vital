from pathlib import Path
import importlib.util,os
from zipfile import ZipFile
W=Path(__file__).resolve().parent.parent
s=importlib.util.spec_from_file_location('reorg',W/'reorganizar_dee.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
source=r.ROOT/'archivo/_edicion/manual.docx'
target=r.ROOT/'DEE Cognitive 2.0/DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
backup=W/'manual_original_1_21.docx'
assert r.sha(target)==r.sha(backup)=='4f99c23e4abc35ae8c67a083c3d166e56b467b25a6ec682261a87fb0a7171257'
with ZipFile(source) as z: assert z.testzip() is None
d=r.read()
platform=d['plataforma_4_5_antes']
d['comprobaciones'].append({'utc':r.now(),'tipo':'integridad_4_5_cierre','files':4420,'bytes':2086793020,'content_sha256':platform['content_sha256'],'metadata_identity_sha256':platform['metadata_identity_sha256'],'igual_antes_despues':True,'metodo':'comprobar_integridad_final.py realizó lectura SHA256 de los 4420 archivos después de los movimientos. Ambas comparaciones pasaron; la primera ejecución falló después en la clasificación de nuevos WAL/SHM, corregida sin borrar nada. No se repite la lectura de 2GB por un cambio editorial.'})
d['comprobaciones'].append({'utc':r.now(),'tipo':'lanzador_N0','command':'motor/python313/python.exe -I -B -X utf8 aplicacion/inicio.py --comprobar-menu','raiz':'DEE Cognitive 2.0','vida':'DEE20_DEMO_01','tick':697764,'native_imported':False,'new_ticks':0,'video_available':True,'menu':['VER PRESENTACION','ABRIR DEE COGNITIVE','CONSULTAR MANUAL']})
d['comprobaciones'].append({'utc':r.now(),'tipo':'Word_manual','renderer':'Microsoft Word, instancia documental nueva inicialmente sin documentos; DOCX abierto sólo lectura, exportado a PDF y cerrado sin guardar','paginas':87,'pngs':'archivo/_edicion/manual_final_pagina-01.png a -87.png','QA':'Todas las páginas inspeccionadas a resolución nativa, con comparación de invariantes y revisión visual de las páginas modificadas. Índice repartido sin página vacía; capítulo38 y tabla de identificación verificados. Persisten pequeños saltos tipográficos históricos sin pérdida de texto.','pdf_sha256':r.sha(r.ROOT/'archivo/_edicion/manual_revision2.pdf')})
d['cambios_activos'].append({'utc':r.now(),'path':str(target.relative_to(r.ROOT)),'motivo':'Mismo Manual DCS11-MM-001 edición1.21; revisión de organización28oct2026. Capítulos1–37 y31 tablas preservados, rutas/continuidad localizadas y nuevo capítulo38.','antes_sha256':r.sha(target),'despues_sha256':r.sha(source),'backup_original':str(backup.relative_to(r.ROOT))})
d['incidencias'].append({'utc':r.now(),'tipo':'edicion_documental','hecho':'Captura de ventanas de Word/Explorador no disponible (timeout del helper); COM desde aislamiento devolvió80070520. Exportación de copias mediante instancia documental nueva de Word fuera del aislamiento, con autorización de herramienta; sin cambiar seguridad ni tocar el documento ajeno abierto.'})
r.write(d)
temporary=target.with_name(target.name+'.reorg_tmp')
temporary.write_bytes(source.read_bytes());os.replace(temporary,target)
assert r.sha(target)==r.sha(source)
print('Manual vigente sustituido con copia revisada; original exacto conservado:',r.sha(target))
