from pathlib import Path
import importlib.util,os,hashlib,json
from zipfile import ZipFile
from lxml import etree
W=Path(__file__).resolve().parent.parent
s=importlib.util.spec_from_file_location('reorg',W/'reorganizar_dee.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
source=r.ROOT/'archivo/_edicion/compendio.docx'
target=r.ROOT/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
assert not target.exists()
with ZipFile(source) as z:
    assert z.testzip() is None
    t=etree.fromstring(z.read('word/document.xml'))
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    marks=t.xpath('//w:bookmarkStart',namespaces=ns)
    ids=[m.get('{'+ns['w']+'}id') for m in marks]
    names={m.get('{'+ns['w']+'}name') for m in marks}
    refs=t.xpath('//w:hyperlink/@w:anchor',namespaces=ns)
    assert len(ids)==len(set(ids)) and not set(refs)-names
target.parent.mkdir(parents=True,exist_ok=True)
temporary=target.with_name(target.name+'.reorg_tmp')
temporary.write_bytes(source.read_bytes());os.replace(temporary,target)
assert r.sha(target)==r.sha(source)
life=json.loads((r.ROOT/'DEE Cognitive 2.0/sistema/estado/vidas/DEE20_DEMO_01/VIDA.json').read_text(encoding='utf8'))
assert life['physical']['tick']==697764 and life['snapshot_sha256']=='3ad3e16b772e8ea44a7814c197651d4cb8d841c8739a1950ad2f0e6953884b8f'
directories=sorted(p.name for p in r.ROOT.iterdir() if p.is_dir())
assert directories==sorted(['4.5','DEE Cognitive 2.0','CPC - Experimentos y mecanismos','archivo','casos practicos'])
assert not [p for p in r.ROOT.iterdir() if p.is_file()]
d=r.read()
d['fuentes_compendio']={'fuentes':70,'comprobaciones':{'fuentes_existentes_y_SHA256_coincidentes':70,'miembros_ZIP_citados_con_SHA256_coincidente':13,'primarios_adicionales_con_SHA256_coincidente':7,'faltantes_entre_los_citados':0},'metodo':'Lectura dirigida de fuentes y primarios, sin repetir campañas; 68 fuentes y sus miembros/primarios comprobados por colaborador, dos manuales oficiales abiertos y SHA verificados por root. Índice completo dentro del Word; no es auditoría íntegra de todo el corpus.','indice_externo_adicional':False}
d['comprobaciones'].append({'utc':r.now(),'tipo':'compendio_cientifico','path':str(target.relative_to(r.ROOT)),'SHA256':r.sha(target),'bytes':target.stat().st_size,'familias_editoriales_de_mecanismos':12,'no_son_capacidades_nuevas_ni_vidas_fusionadas':True,'paginas_Word':28,'QA':'Todas las28 páginas inspeccionadas a resolución nativa después de exportación real desde Word; sin recortes, solapamientos o páginas vacías.','pdf_SHA256':r.sha(r.ROOT/'archivo/_edicion/compendio_publicar.pdf'),'bookmarks':len(marks),'enlaces_internos':len(refs),'sin_duplicados_ni_enlaces_colgantes':True,'sin_importacion_del_motor_ni_repeticion_de_experimentos_para_compendio':True})
d['estructura_final']={'carpetas':directories,'archivos_sueltos_en_raiz':0,'objetivo_cuatro_carpetas':'PARCIAL_POR_BLOQUEO_REAL','excepcion':'casos practicos conservada en raíz: WinError5 al renombrar, incluso en reintento fuera del aislamiento. No se alteraron ACL ni propietario.','Cognitive_activo':{'vida':'DEE20_DEMO_01','tick':697764,'snapshot_SHA256':life['snapshot_sha256'],'seleccion_no_modificada':True},'Manual_vigente':'DEE Cognitive 2.0/DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx','compendio':str(target.relative_to(r.ROOT))}
d['cierre_utc']=r.now()
d['pendientes_concretos']=['Trasladar casos practicos a archivo sólo cuando Windows permita el renombrado coherente; no forzar ni copiar parcialmente. El compendio y el manual citan su ubicación real actual.']
d['politica_reversion']='No devolver copias evolucionadas a la vida original. Para revertir rutas de software, usar bytes originales y movimientos inversos registrados sólo sin escritor activo y sin colisión de destinos. El Manual original exacto queda preservado. Los snapshots, bases, colas y genealogías no se fusionan.'
r.write(d)
print('COMPENDIO',target,flush=True)
print('SHA256',r.sha(target),'bytes',target.stat().st_size,flush=True)
print('Raíz final:',directories,flush=True)
print('Vida original:',life['life_id'],'T'+str(life['physical']['tick']),flush=True)
