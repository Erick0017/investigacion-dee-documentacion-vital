"""Explicit final package closure; copies nothing and executes no discovered code."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=R/'DEE Cognitive 2.0'
def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def source(p,target=None):
    p=Path(p).resolve(strict=True);r={'source':str(p),'sha256':sha(p)}
    if target:r['target']=target
    return r
n=read(P/'fuentes/HECHOS_CIERRE_NATIVE_PI11_R01.json')
assert n['native_running'] is False and n['principal_adopted'] is False and n['replay']['overall_exact'] is True
files=[];targets=set()
def add(p,t):
    if t in targets:raise ValueError('Repeated explicit target '+t)
    targets.add(t);files.append(source(p,t))
maps=P/'entrega/MAPAS_CIERRE_PI11_R01'
for file in maps.iterdir():
    if file.name=='OMISIONES_LOCALIZADAS_PI11.json':continue
    add(file,file.name if file.name=='00_LEER_PRIMERO.txt' else '03_MAPAS/'+file.name)
for file in sorted((P/'fuentes').glob('*.json')):
    if file.name in {'HECHOS_INFORME_PI11_Root_R01.json','HECHOS_INFORME_PI11_Root_R02.json','ARRAYS_AUTOPSIA_COMPACTOS_PI11_R01.json'}:continue
    add(file,'04_EVIDENCIAS/SINTESIS_Y_HALLAZGOS/'+file.name)
add(P/'fuentes/CUERPO_HISTORICO_PARA_INFORME_PI11_R01.txt','04_EVIDENCIAS/FUENTES/CUERPO_HISTORICO_PARA_INFORME_PI11_R01.txt')
for file in sorted((P/'control').glob('*.json')):
    if '.INTENT.' in file.name or file.name.startswith('PUNTO_ROOT') or 'ANTES_CIERRE' in file.name:continue
    add(file,'05_CONTROL/CIERRES_Y_GUARDAS/'+file.name)
for folder,names in [
 ('control/INSTALACION_REPRODUCCION_PI11_R01',['REGISTRO_COMPLETADO.json']),
 ('control/RECONCILIACION_ARRANQUE_NONE_0T_PI11_R01',['RESULTADO.json']),
 ('control/SINCRONIZACION_PUBLICACION_DOCUMENTAL_PI11_R01',['SINCRONIZACION.json']),
 ('documentos',['PUBLICACION_EDICION_1_40_PI11_R01.json','ESTRUCTURA_EDICION_1_40_PI11_R01.json','VERIFICACION_VISUAL_1_40_PI11_R01.json','HECHOS_REALES_1_40.json']),
 ('documentos/base_1_39',['FUENTES_ORIGINALES_1_39_PI11_R01.json'])]:
    for name in names:add(P/folder/name,'05_CONTROL/'+folder.replace('/','_')+'/'+name)
# Complete scored and failed transport primaries, never just edited excerpts.
for file in sorted((P/'ensayos').glob('PI11_MAIN01_PANEL12_OWNER_R01_*.json')):
    add(file,'04_EVIDENCIAS/PANEL/'+file.name)
for file in sorted((P/'ensayos').glob('PI11_MAIN01_POST4_OWNER_R01_*.json')):
    add(file,'04_EVIDENCIAS/POSTERIOR_Y_PARO/'+file.name)
for name in ('RESULTADO_REPRODUCCION.json','GUARDIA_DRIVER_FAMILIA_PI11_R02.json','ENSAYOS.jsonl'):
    add(P/'estados/REPLAYRP01'/name,'04_EVIDENCIAS/REPRODUCCION/'+name)
for parent in ('MAIN01','HEREDADO01'):
    root=P/'fuentes/PRIMARIOS_CERRADOS_R01'/parent
    add(root/'CIERRE_DOCUMENTAL.json','05_CONTROL/EXPORTACIONES/'+parent+'_CIERRE_DOCUMENTAL.json')
for parent in ('PRIMARIOS_CERRADOS_YOKE16_R02','PRIMARIOS_CERRADOS_RP16_R02'):
    add(P/'fuentes'/parent/'CIERRE_DOCUMENTAL.json','05_CONTROL/EXPORTACIONES/'+parent+'_CIERRE_DOCUMENTAL.json')
# Selected exact installed delta / recipe / verification: not the whole engine.
for name in ('reproducir.py','pi11_vinculo_reproduccion_R02.py','pi11_guardia_reproduccion_R02.py','observador_pasivo.py'):
    p=C/'reproducibilidad'/name;assert p.is_file(),str(p)
    add(p,'CODIGO_Y_RECALCULO/INCORPORADO/'+name)
rid='pi11_habitat16_familia_desde_REAL2_R02'
add(C/'reproducibilidad/recetas'/(rid+'.json'),'03_MAPAS/RECETA_PI11_R02.json')
add(C/'reproducibilidad/verificaciones'/rid/'VERIFICACION_NATIVE16_PI11_R02_R01.json','04_EVIDENCIAS/REPRODUCCION/VERIFICACION_REGISTRADA.json')
add(C/'reproducibilidad/codigo_preservado/PI11_HABITAT16_FAMILIA_R02/MANIFIESTO_CODIGO.json','03_MAPAS/MANIFIESTO_CAPSULA_R02.json') if (C/'reproducibilidad/codigo_preservado/PI11_HABITAT16_FAMILIA_R02/MANIFIESTO_CODIGO.json').exists() else None
for rel,target in [
 ('PROYECTO.json','03_MAPAS/PROYECTO_ACTUAL.json'),
 ('CONTINUIDAD_DEE_COGNITIVE_2_0.json','03_MAPAS/CONTINUIDAD_PRODUCTO_ACTUAL.json'),
 ('sistema/estado/ACTIVO.json','03_MAPAS/ACTIVO_ACTUAL.json'),
 ('sistema/estado/vidas/'+n['selected']['life_id']+'/VIDA.json','03_MAPAS/VIDA_PRINCIPAL_ACTUAL.json'),
 ('sistema/contratos/PI10_USO_OPERATIVO_R01.json','03_MAPAS/CONTRATO_PRINCIPAL_PI10.json')]:add(C/rel,target)
for label,folder in [('MAIN','RECALCULO_MAIN16_R01'),('HEREDADO','RECALCULO_HEREDADO16_R01'),('YOKE','RECALCULO_YOKE16_R02'),('REPLAY','RECALCULO_RP16_R02')]:
    for file in (P/'fuentes'/folder).iterdir():
        if file.is_file(): add(file,'04_EVIDENCIAS/RECALCULOS_ARCHIVADOS/'+label+'/'+file.name)
roots=[
 ('MAIN','PRIMARIOS_CERRADOS_R01/MAIN01'),
 ('HEREDADO','PRIMARIOS_CERRADOS_R01/HEREDADO01'),
 ('YOKE','PRIMARIOS_CERRADOS_YOKE16_R02'),
 ('REPLAY','PRIMARIOS_CERRADOS_RP16_R02')]
primaries=[]
for role,rel in roots:
    root=P/'fuentes'/rel;closure=read(root/'CIERRE_DOCUMENTAL.json')
    primaries.append({'role':role,'life_id':closure['life_id'],'source':str(root),'expected_ordinals':list(range(16)),'closure_evidence':str(root/'CIERRE_DOCUMENTAL.json')})
v={'schema':'DEE.PI11.closed_delivery_selection.R02','closed_for_packaging':True,'closed_for_documentary_read':True,
 'closure_evidence':[source(P/'fuentes/HECHOS_CIERRE_NATIVE_PI11_R01.json'),source(P/'documentos/PUBLICACION_EDICION_1_40_PI11_R01.json')],
 'cut_utc':datetime.now(timezone(timedelta(hours=-6))).isoformat(),
 'documents':{'report':source(P/'INFORME_CIENTIFICO.md'),'manual':source(C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'),'compendium':source(R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx')},
 'omissions':source(maps/'OMISIONES_LOCALIZADAS_PI11.json','03_MAPAS/OMISIONES_LOCALIZADAS_PI11.json'),
 'array_evidence':source(P/'fuentes/ARRAYS_AUTOPSIA_COMPACTOS_PI11_R01.json','04_EVIDENCIAS/ARRAYS_AUTOPSIA_COMPACTOS_PI11_R01.json'),
 'files':files,'primary_roots':primaries,
 'replay':{'comparison':source(P/'fuentes/COMPARACION_REPLAY_PUBLICO_PI11_R02_R01.json'),'criterion':source(P/'control/CRITERIO_PROSPECTIVO_REPLAY_EXACTO_PI11_R02.json'),'main_role':'MAIN','replay_role':'REPLAY','expected_overall':True}}
out=P/'entrega/CIERRE_ENTREGA_PI11_Root_R02.json';assert not out.exists()
out.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'closure':str(out),'sha256':sha(out),'explicit_files':len(files),'primary_roles':len(primaries),'Native_imported':False}))

