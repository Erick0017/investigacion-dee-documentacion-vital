"""Serialize authored claim/evidence links and negative-case access indexes.

This is an auditor tool, not a participant or an automatic semantic verdict.
"""
from pathlib import Path
from collections import Counter
import argparse,json,sys,shutil
sys.path.insert(0,str(Path(__file__).resolve().parent))
from codec import Reader,canonical
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--calc',type=Path,required=True);p.add_argument('--historical-contrast',type=Path,required=True);a=p.parse_args();root=a.package;r=Reader(root/'EVIDENCIA_PRIMARIA_ESENCIAL');by={}
    for d in r.index['documents']:
        for o in d['origins']:
            if o.get('archive')=='CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip':by[o['member'][5:]]=d['id']
    def evidence(name,pointer=''):
        k=by[name];row=r.lookup[k];o=next(o for o in row['origins']if o.get('member')=='CPC9/'+name)
        return{'id':k,'original_member':o['member'],'original_sha256':o['sha256'],'canonical_sha256':row['canonical_sha256'],'pointer':pointer,'decode':'python CONFIGURACIONES_Y_REPRODUCCION/codec.py --id '+k+' --out NUEVO.json'}
    # These readings are authored judgments, never generated from a global PASS.
    specs=[
      ('C01','Continuidad física y operativa registrada de E1','Una vida N67 preparada desdeT0; interfaces vacías añadidas1220/1907; ningún trasplante declarado.',
       ['resultados/vida_integral/EI_D01/MEDICIONES.json','resultados/continuacion/E1_MAIN_884_1220/MEDICIONES.json','front_relations/resultados/E1_MAIN_1220_1371/MEDICIONES.json','front_relations/resultados/E1_MAIN_1371_1639/MEDICIONES.json','front_relations/resultados/E1_MAIN_1639_1907/MEDICIONES.json','resultados/continuacion/E1_MAIN_K65_1907_2353/MEDICIONES.json','resultados/continuacion/E1_MAIN_TAIL_2353_2493/MEDICIONES.json'],
       'Las seis fronteras tienen el mismoRAW/clocks/tick y el SHA del padre guardado correcto;1573recibos únicos.','No demuestra identidad cognitiva humana ni estabilidad indefinida; son352frames registrados, no observación completa de cada sitio en cada tick.'),
      ('C02','Acceso a65formas en E1 y deterioro posterior','Misma vida; bloques8+8+16+33 y lectores de cadencia67 preparados.',
       ['resultados/continuacion/E1_MAIN_K65_1907_2353/MEDICIONES.json','resultados/continuacion/E1_CF_K65_NO_EVENT/MEDICIONES.json','resultados/continuacion/E1_CF_K65_UNPAIRED/MEDICIONES.json'],
       '60/65primeras respuestas agregadas; barridos escalonados57/65,53/65,4/65. Se conservan753consultas de MAIN/control.','No son65significados ni65lecturas simultáneas. Fallo de lectura no prueba borrado de cada relación.'),
      ('C03','Composición física sensible a ambas contribuciones y dirección','Dos llegadas reales de26y30 en la vecindad205; diagnóstico sólo sobre copias.',
       ['resultados/auditoria/COMPOSICION_E1/MEDICIONES.json','resultados/vida_integral/EI_D01/MEDICIONES.json','resultados/vida_integral/EI_C03_NO_ORDER_A/MEDICIONES.json'],
       'Formación56(1,1,1)en206 y uso63(1,0,1)en210. Retirar cualquiera o borrarX/Z a igual carga elimina esa consecuencia; sham conserva884.','No acredita gramática productiva, deíxis o conservación general de referentes/roles.'),
      ('C04','Comparación con referencia adquirida y revisión54→67','Operador/gradiente preparados; nueva experiencia aporta13 y el control lo envía fuera de ruta.',
       ['resultados/continuacion/E1_MAIN_884_1220/MEDICIONES.json','resultados/continuacion/E1_CF_OFFPATH_884_1220/MEDICIONES.json'],
       'Cuatro objetos nuevos producen−X,+X,−X,+X; control−X,−X,−X,+X. La primera respuesta941aún utiliza54;67llega posteriormente al hub.','No se aprendió por experiencia la ley comparativa ni toda la primitivaMÁS. Los pronósticos previos eran del auditor.'),
      ('C05','Operandos antiguos causales durante nuevas adquisiciones','R36/O16 adquiridos y conservados; control al final2283sobre copia de2219.',
       ['resultados/auditoria/MEMORIAS_TARDIAS_2283_R1/MEDICIONES.json','resultados/auditoria/MEMORIAS_TARDIAS_2283/MEDICIONES.json','resultados/continuacion/E1_MAIN_K65_1907_2353/MEDICIONES.json'],
       'Cambiar36a5invierte el resultado;36a16produce portador activo sin dirección; sham reproduceMAIN.','El corte global de referencia desestabiliza más funciones. Cortar el lector admite una entrada antes rechazada: esa fila no certifica el comprobador pasivo previo.'),
      ('C06','Retorno físico E1→B→E1 y asociación posterior','E1tiene respaldo adquirido por exposiciones propias; Bcompara con objeto accesible y la respuesta retorna porv27.',
       ['resultados/retorno/RET_CAUSAL/MEDICIONES.json','resultados/retorno/RET_CAUSAL_MINUS/MEDICIONES.json','resultados/retorno/RET_V3_R31_SOURCE23_OBJECT16/MEDICIONES.json','resultados/retorno/RET_V3_R32_SOURCE23_OBJECT35/MEDICIONES.json','resultados/vida_integral/EI_D01/MEDICIONES.json'],
       'Transporte, recepción, nueva asociación y uso posterior; reservasV3positiva/negativa conservadas.','El corte positivo deja salida negativa residual; el negativo cambia44a32sin borrar su dirección. No prueba lenguaje bidireccional general ni segunda mente completa.'),
      ('C07','Solicitud condicionada por estado recibido','Oportunidad, periodicidad y destinatario preparados; historia local/remota contrastada.',
       ['resultados/consulta/QA_INTEGRAL_CAUSAL/MEDICIONES.json','resultados/consulta/QA_D01_REMOTE_LEARNING/MEDICIONES.json','resultados/consulta/QA_C02_LOCAL_KNOWN/MEDICIONES.json','resultados/consulta/QA_C03_REMOTE_ABSENT/MEDICIONES.json','resultados/consulta/QA_C04_WRONG_CONTENT/MEDICIONES.json'],
       'Cortar el portador recibido impide adquisición137y altera la compuerta210, conservando funciones testigo; sham/restauración concuerdan.','La pregunta reaparece277; no se demostró elección general de qué preguntar, a quién o cuándo terminar.'),
      ('C08','RegulaciónR0/R1 en sus modalidades físicas','Guardas/contraflujos preparados y dirección dependiente del estado adquirido; igual aporte fuera de ruta.',
       ['resultados/vida_integral/EI_D01/MEDICIONES.json','resultados/vida_integral/EI_C05_RCA_OFFPATH/MEDICIONES.json','front_relations/resultados/R0_D01_ONPATH/MEDICIONES.json','front_relations/resultados/R0_C01_OFFPATH/MEDICIONES.json','front_relations/resultados/R0_C02_NONE/MEDICIONES.json'],
       'Cambian acceso y respuesta física dentro de ventanas declaradas; se preservan también mejoras tempranas y fallos tardíos.','No demuestraR2enE1: política reguladora adquirida por consecuencias. Una guarda preparada no es atención aprendida.'),
      ('C09','Contacto y temporalidad con límites de transferencia','Experiencias y señales posteriores; mismas condiciones iniciales en controles pertinentes.',
       ['resultados/vida_integral/EI_D01/MEDICIONES.json','resultados/vida_integral/EI_R31_REVERSED_COMBINATION/MEDICIONES.json','resultados/vida_integral/EI_R32_NEW_COMBINATION/MEDICIONES.json','front_relations/resultados/E1_MAIN_1371_1639/MEDICIONES.json','front_relations/resultados/EI_R31_WORD_DIAGNOSTIC/MEDICIONES.json'],
       'Funciones temporales/decontacto finitas y composición; reservas positivas y adversas permanecen.','La reservaBA3deMAINfalla por encuentro/ocupación; una preparación nueva exitosa no es generalización semántica de E1.'),
      ('C10','Memoria conservada frente a lector o fase ineficaz','Conteo y lectores previos en una misma historia, sin reenseñanza oculta atribuida.',
       ['resultados/continuacion/E1_MAIN_884_1220/MEDICIONES.json','front_relations/resultados/E1_MAIN_1220_1371/MEDICIONES.json','front_relations/resultados/E1_NEW_ORDER_DIAGNOSTIC/MEDICIONES.json','front_relations/resultados/EI_R31_WORD_DIAGNOSTIC/MEDICIONES.json'],
       'Se separan fallos de fase/ocupación de la presencia de soportes y recuperaciones posteriores1287/1354.','No toda recuperación alternativa equivale a acceso ordinario renovable, ni todoRAWpersistente es conocimiento utilizable.'),
      ('C11','Ocupación masiva y nacimiento local de semantic7','Copia diagnóstica2219→2353, pre/postMoore27y controlsham/corte.',
       ['resultados/auditoria/CRECIMIENTO_OCUPACION/MEDICIONES.json','resultados/auditoria/OCUPACION_Y_RESTAURACION/MEDICIONES.json','resultados/continuacion/E1_CF_K65_UNPAIRED/MEDICIONES.json','resultados/continuacion/E1_CF_K65_NO_EVENT/MEDICIONES.json'],
       'RAW/clocks completos de13estados permiten recontar298024/300763sitios ocupados enMAIN2353,297334ennoemparejado y348sinevento. El corte evita un nacimiento local pero no la expansión global.','No demuestra límite universal de65ni causa única de la onda. semantic7es un campo físico, no siete significados.'),
      ('C12','Continuación final y rechazos','MAIN2353→2493 y control sin los intentos nuevos.',
       ['resultados/continuacion/E1_MAIN_TAIL_2353_2493/MEDICIONES.json','resultados/continuacion/E1_TAIL_NO_NEW/MEDICIONES.json','resultados/auditoria/OCUPACION_Y_RESTAURACION/MEDICIONES.json'],
       '177/178peticiones finales rechazadas; cuatro intentos de revisión no aplicados. La rama sin esos intentos coincide físicamente.','No contar los intentos como aprendizaje. RAWestable2493→2498conclocksdistintos no es punto fijo completo ni continuidad funcional ilimitada.'),
      ('C13','YO/TÚ y regulaciónR2 no demostrados enE1','Se preservan trazas auxiliares de origen de acción y el inventario de65.',
       ['revision/NSM65_EVIDENCIAS.json','front_semantics/revision/NSM65_PLAN_CPC9.json'],
       'Hay prerrequisitos físicos investigados, pero no ligamiento deíctico aprendido con intercambio de roles ni selección reguladoraR2enE1.','Ausencia de demostración no es refutación universal; tampoco debe borrar realizaciones auxiliares o históricas con otro dominio.'),
      ('C14','Las34familias históricas y16filas pendientes','Núcleo con fuentes, controles y reproducción registrada antes de esta auditoría; se incluyen originales y salidas de esa recuperación.',
       [],'Se preservan las34actas y datos originales/frescos; el contraste genérico recalcula1071huellas coincidentes en124pares de23familias. Las16filasDmantienen testigos documentales.','No hubo34reproducciones físicas nuevas aquí. Los demás formatos requieren lectores específicos incluidos/referenciados; no se promueven por unPASS.'),
      ('C15','CoberturaNSM65 y alcance de niveles','Catálogo oficial con65identidades y dimensiones originales A–J separadas de juicios nuevos.',
       ['revision/NSM65_EVIDENCIAS.json','genealogia/NSM65_CATALOGO_4_5.json'],
       'Se recontó60E0/4E2/1E3como clasificación original episódica. Cinco funciones candidatas finitas;14entradas con funciones/prerrequisitos ejecutados.','No acredita65conceptos ni cinco significados humanos completos; E3deMÁSes uso de referencia adquirida en operador preparado.'),
    ]
    calc=json.loads((a.calc/'CALCULOS_RECALCULADOS.json').read_bytes())
    claims=[]
    for cid,title,initial,names,yes,no in specs:
        ev=[evidence(n)for n in names]
        if cid=='C14':
            ids=set()
            for family in calc['historical_families']:
                ids.update(family['original_primary_ids_identified'])
                for k in family['completed_replay_documents']:
                    if any(o.get('member','').endswith(('MEASUREMENTS.json','RESULTADOS.json','PRIMARY_TRANSITIONS.json','OBSERVED.json'))for o in r.lookup[k]['origins']):ids.add(k)
            for k in sorted(ids):
                d=r.lookup[k];o=d['origins'][0];ev.append({'id':k,'original_member':o.get('logical_path',o.get('member')),'original_sha256':o['sha256'],'canonical_sha256':d['canonical_sha256'],'pointer':'','scope':d['role']})
        claims.append({'id':cid,'title':title,'initial_conditions':initial,'measured_function_or_change':yes,'does_not_demonstrate':no,'evidence':ev,'interpretation_status':'Authored bounded audit reading; not automatic global verdict'})
    controls=[];negative=[]
    for row in r.index['documents']:
        if row['role']!='CPC9_PRIMARY':continue
        d=r.get(row['id']);origin=next(o for o in row['origins']if o.get('archive')=='CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip');name=origin['member'];c=d.get('case_id',Path(name).parent.name)
        if any(s in str(c).upper()for s in('C0','CUT','SHAM','NO_','UNPAIR','OFFPATH','REVERSE','DIAGNOSTIC','CAUSAL','RESERV','_R3','_H0'))or'rows'in d:
            controls.append({'document':row['id'],'case':c,'original_member':name,'original_sha256':origin['sha256'],'status':d.get('status'),'configuration':d.get('configuration',d.get('config')),'conditions':[x.get('condition')for x in d.get('rows',[])if isinstance(x,dict)],'scope':'Index only; outcome must be read from physical observations, not inferred from the case name.'})
        if d.get('status')not in('MEASURED','EXECUTED'):
            negative.append({'document':row['id'],'case':c,'status':d.get('status'),'original_member':name,'original_sha256':origin['sha256'],'interpretation':'Unclosed/technical/predicted status, not a validated negative scientific finding.'})
    put(root/'AFIRMACIONES_Y_EVIDENCIAS.json',{'scope':'Author-reviewed functional claims and their original primary locators. Data/metrics/interpretations separate.','claims':claims})
    put(root/'CONTROLES_CAUSALES/INDICE_CONTROLES.json',{'records':controls,'selection_is_not_success_only':True,'all281_primary_containers_preserved':True})
    put(root/'RESULTADOS_NEGATIVOS/INTENTOS_NO_CERRADOS_Y_TECNICOS.json',{'records':negative,'scientific_negatives_are_in_claims_and_complete_primaries':True})
    put(root/'CONTROLES_CAUSALES/CONTRASTE_HISTORICO_RECALCULADO.json',json.loads(a.historical_contrast.read_bytes()))
    put(root/'CONTROLES_CAUSALES/COMPOSICION_Y_CORTE.json',calc['composition']);put(root/'CONTROLES_CAUSALES/CONSULTA_Y_REGULACION.json',{'query':calc['query_causal'],'R1':calc['regulation_R1'],'R2_E1':'NOT_DEMONSTRATED'})
    put(root/'EVIDENCIA_PRIMARIA_ESENCIAL/34_FAMILIAS_Y_FUENTES.json',calc['historical_families'])
    put(root/'RESULTADOS_NEGATIVOS/CONSULTAS_65_Y_CONTROLES.json',json.loads((a.calc/'CONSULTAS_65_COMPLETAS.json').read_bytes()))
    put(root/'EVIDENCIA_PRIMARIA_ESENCIAL/CALCULOS_RECALCULADOS.json',calc)
    # Direct small reading route: actual selected observations across all7phases,
    # with complete source containers still reconstructible from the codec.
    put(root/'EVIDENCIA_PRIMARIA_ESENCIAL/LECTURAS_E1_ACCESO_DIRECTO.json',json.loads((a.calc/'TRAYECTORIA_DATOS.json').read_bytes()))
    put(root/'EVIDENCIA_PRIMARIA_ESENCIAL/CONTINUIDAD_FISICA_RECALCULADA.json',calc['continuity'])
    print(json.dumps({'status':'PASS','authored_claims':len(claims),'controls_indexed':len(controls),'nonclosed_or_technical':len(negative),'engine_imported':False}))
if __name__=='__main__':main()
