"""Technical packaging test, not final delivery or a new scientific document."""
from pathlib import Path
import argparse,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;P=H.parent;THINK=P.parents[2]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directorio',type=Path,required=True);args=ap.parse_args();base=args.directorio.absolute();assert not base.exists();base.mkdir()
    fixtures=base/'fixtures';fixtures.mkdir()
    values={'00_LEER_PRIMERO.txt':'PRUEBA TECNICA. No entrega final, no nueva experiencia. Copias documentales literales y Cal5 existente.\n',
      'INFORME_PRUEBA.md':'# Prueba del empaquetador\nValidación de formato y recálculo archivado. No constituye el informe científico final ni un nuevo manual.\n',
      'CONTINUIDAD_PRUEBA.json':json.dumps({'schema':'DEE.PI10.package_test_only','Native_executed':False,'actual_principal_not_changed':True})+'\n',
      'MATRIZ_PRUEBA.csv':'tipo,valor,unidad\nprueba,1,registro_sintetico\n','COBERTURA_PRUEBA.md':'Sólo prueba del empaquetador y lectura de Cal5 ya registrada. No Native.\n'}
    for name,text in values.items():(fixtures/name).write_text(text,'utf8')
    manual=THINK/'DEE Cognitive 2.0/DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
    comp=THINK/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
    assert manual.is_file()and comp.is_file()
    roles={'00_LEER_PRIMERO.txt':'readme','INFORME_PRUEBA.md':'scientific_report','CONTINUIDAD_PRUEBA.json':'continuity','MATRIZ_PRUEBA.csv':'capabilities_csv','COBERTURA_PRUEBA.md':'coverage'}
    files=[{'source':str(fixtures/name),'member':name,'role':role}for name,role in roles.items()]
    files.extend([{'source':str(manual),'member':'02_MANUAL/MANUAL_LITERAL_ACTUAL_AL_TEST.docx','role':'manual'},
      {'source':str(comp),'member':'02_MANUAL/COMPENDIO_LITERAL_ACTUAL_AL_TEST.docx','role':'compendium'},
      {'source':str(H/'recalcular_primarios_PI10_R03.py'),'member':'CODIGO/recalcular_primarios_PI10_R03.py','role':'analysis_code'}])
    cfg={'schema':'DEE.PI10.exact_analysis_selection.R01','facts_finalized':True,'scope':'Pure technical test only, not a final campaign seal',
      'files':files,'closed_primary_bundles':[{'source':str(P/'fuentes/CAL5_R02_CERRADA_PORTABLE_R01'),'member':'EVIDENCIA/CAL5'}],
      'pure_recalculations':[{'script':'CODIGO/recalcular_primarios_PI10_R03.py','args':['--indice','EVIDENCIA/CAL5/INDEX.json','--salida','05_CONTROL/RECALCULO_EXTRAIDO.json'],
        'output':'05_CONTROL/RECALCULO_EXTRAIDO.json','schema':'DEE.PI10.independent_RAW_recalc.R03'}]}
    (base/'SELECCION_DE_PRUEBA.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n','utf8')
    sp=importlib.util.spec_from_file_location('pack',H/'empaquetar_analisis_PI10_R01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
    proof=m.build(cfg,base/'trabajo_nuevo',base/'SOLO_PRUEBA_TECNICA_NO_ENTREGA.zip')
    result={'schema':'DEE.PI10.pure_packaging_contract_test.R01','Native_executed':False,'DEE_imported':False,'final_delivery':False,
      'full_existing_manual_and_compendium_literal_copies':True,'actual_archived_Cal5_recalc_in_clean_extraction':True,'verification':proof}
    out=base/'PRUEBA_EMPAQUETADO_PURO.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps({'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'zip_bytes':proof['bytes'],'Native_executed':False}))
if __name__=='__main__':main()
