"""Documentary maps only; reads closed published proofs, never an owner/DEE."""
from pathlib import Path
from datetime import datetime, timezone
import csv, hashlib, json

P=Path(__file__).resolve().parents[1]

def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(name):
    p=P/name
    return {'file':name,'bytes':p.stat().st_size,'sha256':sha(p)}
def closed(name):
    p=P/name
    if not p.exists(): return None
    v=read(p)
    if not v.get('closed'): return None
    return v

def main():
    path=P/'mapas/CONTINUIDAD_PI07.json';m=read(path)
    m['cut_utc']=datetime.now(timezone.utc).isoformat()
    m['status']='PARTIAL_CLOSED_EVIDENCE_NEW_CONSERVATION_GATES_PENDING'
    comparison_name=('control/COMPARACION_R03_REAL_NOFAIL_YOKE_Y_CORTES_PI07_R02.json'
                     if(P/'control/COMPARACION_R03_REAL_NOFAIL_YOKE_Y_CORTES_PI07_R02.json').exists()
                     else'control/COMPARACION_R03_REAL_NOFAIL_YOKE_PI07.json')
    comparison=read(P/comparison_name)
    m['R03']['matched_controls']={**ref(comparison_name),
        'comparability_checks_passed':comparison['all_comparability_checks_passed'],
        'arms':{k:{key:v[key]for key in('opportunities','FI_correct','complete','messages_offered',
            'messages_delivered','unique_requested','applied','rejected','Native_ticks')}
            for k,v in comparison['arms'].items()},
        'interpretation':'La contingencia real conserva un mensaje adicional frente al retorno constante nofallo y cinco frente al desacoplado. FI12/12 en los tres. Prefijo compartido, no individuos independientes; dosis admitidas divergen por las propias actuaciones y conflictos.',
        'action_reference_scope':comparison['reference_scope']}
    for key,name in [('restoration','control/PI07_RESTAURACION_12_13_R03.json'),
                     ('after_reopen','control/PI07_POST_REAPERTURA_14_15_R03.json')]:
        v=closed(name)
        if v:
            m['R03'][key]={**ref(name),'before_tick':v['initial_tick'],'after_tick':v['final_tick'],
                'Native_ticks':v['new_ticks'],'complete':sum(not r['actual_failed']for r in comparison['arms'][key]['rows']),
                'opportunities':2,'scope':'Experiencia material de la candidata; restauración incluye un fallo y readaptación, no retención intacta de la contingencia opuesta.' if key=='restoration' else 'Dos usos posteriores al cierre y reapertura, no un panel histórico completo.'}
    for key,name in [('new_access_development','control/PI07_FI_DESARROLLO_R01.json'),
                     ('new_access_conservation','control/PI07_PANEL_ACCESO_R02.json'),
                     ('old_C2C_use','control/PI07_C2C_28_29_R01.json')]:
        v=closed(name)
        if v:
            m['R03'][key]={**ref(name),**{k:v.get(k)for k in('status','criteria_met','before_tick','after_tick',
                'new_Native_ticks','correct','tested','expected_uses','Native_inputs','scientific_stop','error')},
                'scope':'Contrato de acceso FI nuevo y acotado; no reemplaza retrospectivamente el fallo del panel antiguo. Dos datos Native0/sensor0 de desarrollo acreditan retiming P0, no protección adquirida.' if key.startswith('new_access') else 'Uso material del dispositivo heredado, sin resuministro ni reinicio de ordinales.'}
    last=closed('control/PI07_PANEL_ACCESO_R02.json') or closed('control/PI07_FI_DESARROLLO_R01.json')
    if last:
        m['R03']['latest_closed_experimental_cut']={'life_id':last['life_id'],'N':67,'T':last['after_tick'],
            'not_selected_main':True,'scope':'Último corte de este comprobante cerrado; un proceso posterior puede haber continuado. No se infiere su estado de ejecución.'}
    corrected=closed('control/C2C_CONSERVACION_VERIFICADA_PI07_R03.json')
    if corrected:
        m['R03']['old_C2C_use']={**ref('control/C2C_CONSERVACION_VERIFICADA_PI07_R03.json'),
            'original_false_checker_preserved':corrected['original_checker_proof'],
            'actual_functional_success':corrected['material_success'],'opportunities':2,'products':2,
            'Native_inputs':corrected['Native_inputs'],'before_tick':corrected['initial_tick'],
            'after_tick':corrected['final_tick'],'Native_ticks':corrected['actual_Native_ticks'],
            'scope':corrected['correction']}
        m['R03']['latest_closed_experimental_cut']={'life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_CAND_01',
            'N':67,'T':corrected['final_tick'],'not_selected_main':True,
            'scope':'Último comprobante cerrado, no afirmación sobre un owner posterior en curso.'}
    m['R03']['yoked_source']['control_execution_not_implied']=False
    m['R03']['yoked_source']['control_execution_proof']=ref('control/PI07_YOKED12_R03.json')
    m['R03']['new_FI_access_protocol']={**ref('codigo/PROTOCOLO_PI07_ACCESO_FI_R01.json'),
        'old_API_failure_preserved':True,'revised_calendar_and_material_dose_declared':True,
        'scope':'Acceso Native general con la señal física presente, el mismo selector y actuador; referencia aritmética del evaluador sólo después de la función. No respuesta de Python.'}
    m['adoption']['status']='BLOCKED_UNTIL_ALL_ACTUAL_CONSERVATION_AND_INTEGRATION_GATES_CLOSE'
    m['adoption']['old_API_failure_remains']=True
    m['pending']=['Cierre del nuevo panel de acceso y dispositivo C2C, controles restantes y decisión real de Root; no asumir promoción.',
                  'Publicación documental y verificación del ZIP no ejecutadas por este actualizador.']
    final_failure=P/'control/CIERRE_CONJUNTO_MATERIAL_PI07_R01.json'
    if final_failure.exists():
        f=read(final_failure)
        if not f['criteria_met']:
            m['status']='NO_ADOPTION_FINAL_ENVIRONMENT_INTEGRATION_FAILED_PRESERVED'
            m['adoption']['status']='BLOCKED_BY_FINAL_P0_INTEGRATION_AND_CHECKPOINT_FAILURE'
            m['R03']['final_attempt']={**ref('control/CIERRE_CONJUNTO_MATERIAL_PI07_R01.json'),
                'status':f['status'],'closed':f['closed'],'criteria_met':False,
                'initial_tick':f['initial_tick'],'final_tick':f['final_tick'],'new_Native_ticks':f['new_Native_ticks'],
                'no_C2C30_executed':True,'no_R03_16_executed':True,
                'new_environment34_operationally_committed':False,
                'scope':'Fallo técnico de integración P0: protocolo34 excede el máximo32 del cuerpo heredado; posible futuro externo parcial y checkpoint fallido. No es una regresión Native funcional. No restablecer ni reintentar silenciosamente.'}
            m['pending']=['Preservar y localizar el futuro técnico fallido bajo responsabilidad de Root; no nuevos ensayos ni promoción por este cierre.',
                'Cierre documental, incorporación instrumental si Root la ejecuta y verificación del ZIP son operaciones separadas.']
    ledger_path=P/'control/LEDGER_FINAL_GUARDADO_PI07_R01.json'
    if ledger_path.exists():
        ledger=read(ledger_path)
        m['actual_finite_execution']={**ref('control/LEDGER_FINAL_GUARDADO_PI07_R01.json'),
            'Native_ticks_all_branches':ledger['Native_ticks_all_branches'],
            'diagnostic_worlds':ledger['diagnostic_worlds'],'principal_Native_ticks':0,
            'scope':'Ticks de avances Native guardados por vida, no conceptos ni réplicas independientes. No implica cierre coherente del futuro técnico final.'}
    future_path=P/'control/JOB_Y_SNAPSHOT_FALLO_C2C34_PI07_R01.json'
    if future_path.exists():
        m['R03']['preserved_failed_snapshot']={**ref('control/JOB_Y_SNAPSHOT_FALLO_C2C34_PI07_R01.json'),
            'T':866067,'snapshot_sha256':'b4906d817f9ce52093ae1af9bdab6266abbea63b04f0409dba191391ab14bda7',
            'C2C_environment_protocol34_present':True,'extension_ready':False,'extension_uncertain':True,
            'R03_ordinal_preserved':16,
            'scope':'El snapshot guardado sí contiene el futuro34 fallido. No es un supuesto checkpoint30 limpio ni una reapertura validada. Los C2C28/29 precedieron al intento sin avance Native adicional.'}
    native_unchanged=P/'control/COMPARACION_FUTURO_FALLIDO_C2C34_PI07_R01.json'
    if native_unchanged.exists():
        m['R03']['failed_future_Native_comparison']={**ref('control/COMPARACION_FUTURO_FALLIDO_C2C34_PI07_R01.json'),
            'scope':'Comparación pasiva de Root/I4:6/6 campos Native iguales antes/después del intento0tick; historia C2C y R03 conservada. Cambió la configuración/estado externo34 y su KEY incierta. No atribuir el bloqueo técnico a pérdida de contenido Native.'}
    rp3_name=('control/RP_R03_INCORPORADA_PI07_R04.json'
              if(P/'control/RP_R03_INCORPORADA_PI07_R04.json').exists()
              else'control/RP_R03_INCORPORADA_PI07_R02.json')
    rp3=P/rp3_name
    if rp3.exists():
        registration=read(rp3)
        m['R03']['stable_reproduction']={**ref(rp3_name),
            'status':registration['status'],'recipe':registration['recipe'],'capsule':registration['capsule'],
            'prefix':registration['prefix'],'new_frontdoor_CLI_material_replay_executed':False,
            'dependency_closure_status':'ADDITIVE_SOURCE_CLOSURE_PRESERVED_FRONTDOOR_REQUIREMENTS_PENDING' if rp3_name.endswith('R04.json') else'UNDER_ROOT_REVIEW_NO_USABILITY_CLAIM',
            'scope':'Registro administrativo real de receta y cápsula aditiva con dependencias históricas; las versiones incompletas se preservan con advertencia. La utilización por puerta de Cognitive requiere su comprobante de requisitos separado. El referente material original fue ejecutado; no hubo nuevo replay NativeCLI ni adquisición al principal.'}
    documentary_applied=P/'control/CIERRE_DOCUMENTAL_NO_ADOPCION_PI07_R01.json'
    if documentary_applied.exists():
        doc=read(documentary_applied)
        if doc.get('applied') is True:
            m['status']='SCIENCE_CLOSED_NO_MAIN_ADOPTION_INSTRUMENTAL_DOCUMENTATION_APPLIED'
            m['adoption']['status']='NO_ADOPTION_DOCUMENTED_PRINCIPAL_PRESERVED'
            m['documentary_incorporation']={**ref('control/CIERRE_DOCUMENTAL_NO_ADOPCION_PI07_R01.json'),
                'catalogue_ids':doc['catalogue_ids'],'Native_ticks':0,'main_acquisition':False,
                'targets':[r['target']for r in doc['changes']],
                'scope':'Cierre aplicado por Root: registro, continuidad, catálogo y anexo transversal. Dos entradas de instrumentos/procedimiento experimental, sin desplegar despachadores ni adoptar la historia experimental como principal.'}
            m['pending']=['Publicación del Manual1.34 y comprobación del ZIP final son cierres documentales separados; no más Native ni adopción en esta campaña.']
    rp_recalc=P/'control/RP_R03_RECALCULO_ACTUAL_R01/VERIFICACION_RECALCULO_RP.json'
    if rp_recalc.exists():
        verified=read(rp_recalc)
        m['R03']['actual_documentary_recalculation']={**ref('control/RP_R03_RECALCULO_ACTUAL_R01/VERIFICACION_RECALCULO_RP.json'),
            'all_checks_passed':verified['all_checks_passed'],'episodes_recalculated':verified['episodes_recalculated'],
            'new_Native_ticks':0,'fence':verified['fence'],'result_sha256':verified['result_sha256'],
            'scope':'Recálculo real por herramienta Cognitive de tres registros originales intacto/sensor/actuador, sin lecturas externas al paquete ni DEE. No es replay material nuevo.'}
    advisory=P/'control/ADVISORY_RP_PI07_APLICADO_R01.json'
    if advisory.exists():
        m['R03']['reproduction_advisory_applied']={**ref('control/ADVISORY_RP_PI07_APLICADO_R01.json'),
            'Native_ticks':0,'old_incomplete_recipe_material_execution_blocked':True,
            'new_recipe':'pi07_r03_uso_adquirido_post4_R03',
            'new_recipe_requirements_verified_without_Native':True,
            'new_recipe_Native_CLI_replay_executed':False,
            'scope':'Microcambio instrumental aplicado por Root al gestor de reproducción. La receta incompleta se conserva bloqueada; la nueva tiene requisitos comprobados y recálculo, sin nueva reproducción material.'}
        if 'stable_reproduction'in m['R03']:
            m['R03']['stable_reproduction']['dependency_closure_status']='REQUIREMENTS_VERIFIED_NATIVE_MATERIAL_REPLAY_NOT_EXECUTED'
    path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    matrix=P/'mapas/MATRIZ_ANTES_DESPUES.csv'
    rows=list(csv.DictReader(matrix.open(encoding='utf-8-sig',newline='')))
    rows=[r for r in rows if r['familia']not in('Reproducción','Iteración R03','Control R03','Transferencia R03',
          'Cambio y retención R03','Conservación API anterior','Acceso FI nuevo','Conservación C2C','Integración final P0','Incorporación documental')]
    additions=[
      ('Reproducción','Reproducción documental y Native son propiedades diferentes','Cold8: Native completo exacto y dosis1464/1464; igualdad persistente global falló por queue.0 en EP04','RP cold8/EP04/EP08','control/EXPLICACION_TRANSPORTE_EP04_RP_PI07_R01.json','No ampliar el criterio: física reproducida y metadato de transporte discrepante'),
      ('Iteración R03','Política realmente adquirida durante R02; herramienta51 ineficaz','Herramienta perpendicular53/48/56 preparada y calibrada; misma historia A54/B54','P0 R03 T846520','control/RECALCULO_CALIBRACION_R03_PI07_R02.json','Anatomía P0 mejorada; no inventada por el ente'),
      ('Transferencia R03','Reservas prospectivas de cuatro oportunidades','Reserva A4/4, dos pulsos admitidos útiles; FI12/12 en los tres brazos de doce','CAND R03 hasta855901','control/COMPARACION_R03_REAL_NOFAIL_YOKE_PI07.json','Transferencia local a datos, historia y fase de esta familia; sin autonomía general'),
      ('Control R03','Mismo prefijo completo y calendarios; real/NF/yoke+5','Completos11/12,10/12,6/12; mensajes7/8,6/8,2/8 respectivamente','Tres ramas T855901','control/COMPARACION_R03_REAL_NOFAIL_YOKE_PI07.json','Ventaja funcional local de la contingencia real; misma FI, dosis físicas divergentes por acciones reales'),
      ('Cambio y retención R03','Cambio de utilidad de la misma señal física','Costo real8: delta0→−1; cero material10 evita pulso y conserva mensaje11; restore1/2 y reapertura2/2','CAND R03 ordinal16 T859811','control/COMPARACION_R03_REAL_NOFAIL_YOKE_PI07.json','Readaptación localizada; no planificación; la regla contextual mantener/cambiar explica esta traza corta'),
      ('Conservación API anterior','Panel histórico de doce usos','Se detuvo5/6: FI14/3 produjo−1 frente a+1 esperado,176/176;5asociaciones correctas','CAND T856398','control/PI07_PANEL_INTERCALADO_R01.json','Regresión material preservada; no panel12/12 y no borrado de memoria probado'),
      ('Acceso FI nuevo','Protocolo distinto, sellado antes de las consultas','Desarrollo14/3 y2/11:2/2,364/364; nuevo panel12/12,947/947,con FIreservados13/4,2/12,6/6','CAND T864240','control/PI07_PANEL_ACCESO_R02.json','Retiming P0; no borrar el fallo de la API anterior ni llamar a los 12 usos 12 facultades'),
      ('Conservación C2C','Dos ofertas originales28/29, sin reiniciar recursos','Dos productos reales23/17;372/372 outer+FI+MU. R02 contó sóloouter12 y dio falso negativo preservado','CAND T866067','control/C2C_CONSERVACION_VERIFICADA_PI07_R03.json','Error de colección del verificador corregido pasivamente; criterio372 y Native intactos')]
    if final_failure.exists()and not read(final_failure)['criteria_met']:
        additions.append(('Integración final P0','Protocolo preparado34; límite heredado de2..32ofertas','Intento falla al validar/checkpoint;0Native;work30 yEP16 no ejecutados; adopción bloqueada','Futuro técnico preservado T866067','control/CIERRE_CONJUNTO_MATERIAL_PI07_R01.json','No llamar operativo al suministro parcial; principal PI05 protegido'))
    if documentary_applied.exists()and read(documentary_applied).get('applied')is True:
        additions.append(('Incorporación documental','Catálogo125 y principal PI05 protegido','Root añadió2entradas de instrumento/procedimiento experimental y cierre en4JSON; principal sin nuevas experiencias','MAIN T824911; catálogo127','control/CIERRE_DOCUMENTAL_NO_ADOPCION_PI07_R01.json','No promoción ni despliegue de nuevos despachadores; receta R03 material nueva aún no reproducida por CLI'))
    for values in additions: rows.append(dict(zip(rows[0].keys(),values)))
    with matrix.open('w',encoding='utf-8-sig',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    coverage=P/'mapas/FUENTES_Y_COBERTURA.csv'
    old=list(csv.DictReader(coverage.open(encoding='utf-8-sig',newline='')))
    records={r['ruta_relativa']:r for r in old}
    items={
      'codigo/PROTOCOLO_PI07_R03.json':('Lectura completa: contrato sellado; evaluación y controles ejecutados en las condiciones declaradas','PROTOCOLO_EJECUTADO'),
      'control/COMPARACION_R03_REAL_NOFAIL_YOKE_PI07.json':('36 primarios matched12 y seis de restauración/reapertura/sensor; RAW, firmas, recibos y calendarios recalculados','RECALCULO_PASIVO'),
      'control/PI07_PANEL_INTERCALADO_R01.json':('Comprobante completo:5/6 y detención; primarios FI leídos; contraste F1 referido separadamente','RESULTADO_NATIVE_ROOT_LEIDO'),
      'codigo/PROTOCOLO_PI07_ACCESO_FI_R01.json':('Contrato íntegro: nuevo calendario, lector, retorno y límites','PROTOCOLO_EJECUTADO_EN_DESARROLLO'),
      'control/PI07_FI_DESARROLLO_R01.json':('Comprobante completo de dos usos, primarios Native RAW y dosis contrastados','RESULTADO_NATIVE_ROOT_RECALCULADO'),
      'control/PI07_PANEL_ACCESO_R02.json':('Cierre completo12/12,947/947; tres FI nuevos y nueve usos heredados cotejados con RAW y recibos','RESULTADO_NATIVE_ROOT_RECALCULADO'),
      'control/PRUEBA_PORTABLE_PANEL12_NUEVO_R01/RESULTADO.json':('Doce primarios copiados:15checks; tres FI nuevos, nueve testigos de asociación/números reales; no DEE/Native','RECALCULO_DOCUMENTAL_PORTABLE'),
      'control/C2C_CONSERVACION_VERIFICADA_PI07_R03.json':('Dos primarios: primerRAW, aritméticaNative, segundoRAW y dos productos64B;372recibosdedup; falso negativoR02 preservado','RECALCULO_PASIVO_CORRECCION_VERIFICADOR'),
      'control/PRUEBA_PORTABLE_C2C_28_29_R01/RESULTADO.json':('Dos primarios y dosproductos reales copiados:4checks sin DEE/Native','RECALCULO_DOCUMENTAL_PORTABLE'),
      'control/CIERRE_CONJUNTO_MATERIAL_PI07_R01.json':('Comprobante de error íntegro leído:fallo checkpoint,0Native,closedfalse; no resultado funcional final inventado','FALLO_TECNICO_REAL_PRESERVADO'),
      'control/DIAGNOSTICO_INCOMPATIBILIDAD_C2C34_PI07_R01.json':('Cláusula contractual32 y protocolo34 contrastados; orden de escritura/validación leído estáticamente','ANALISIS_ESTATICO_Y_PRIMARIO_REAL'),
      'control/LEDGER_FINAL_GUARDADO_PI07_R01.json':('Ledger real final83178ticks y14vidas, leído como registro; sin ejecutarNative ni sumarlo como conceptos','LEDGER_ROOT_LEIDO'),
      'control/JOB_Y_SNAPSHOT_FALLO_C2C34_PI07_R01.json':('Testigo de Root/I4 referido: snapshotactual contiene protocolo34yKEYuncertain; no confundir con estado30 anterior','AUTOPSIA_AJENA_REFERIDA'),
      'control/COMPARACION_FUTURO_FALLIDO_C2C34_PI07_R01.json':('Comparación pasiva referida:6/6Native iguales y0tick; configuración externa34incierta distinta','RECALCULO_AJENO_REPORTADO'),
      'control/RP_R03_INCORPORADA_PI07_R02.json':('Registro real de receta/cápsulaPRE34; dependencias históricas bajo revisiónRoot; sin nueva ejecuciónNativeCLI','REGISTRO_RP_REAL_USABILIDAD_PENDIENTE'),
      'control/RP_R03_INCORPORADA_PI07_R04.json':('Registro aditivo real de cápsula301archivos conCPC/eventos; receta nueva sin replayNativeCLI; versiones incompletas preservadas','REGISTRO_RP_ROOT_LEIDO_NO_REPLAY_NUEVO'),
      'control/CIERRE_DOCUMENTAL_NO_ADOPCION_PI07_R01.json':('Aplicación documental Root real:4JSON,125→127entradas; principal/protecciones intactos,0Native','ACTUALIZACION_DOCUMENTAL_REAL_NO_ADOPCION'),
      'control/RP_R03_RECALCULO_ACTUAL_R01/VERIFICACION_RECALCULO_RP.json':('Tres primarios recalculados por herramientaCognitive, cerca0lecturasexternas/0DEE, sinreplaymaterial','RECALCULO_DOCUMENTAL_ROOT_VERIFICADO'),
      'control/ADVISORY_RP_PI07_APLICADO_R01.json':('Microdelta real del gestorRP: bloquea recetaR03incompleta; requisitos nueva receta verificados0Native, no nuevo replay','CAMBIO_INSTRUMENTAL_ROOT_REAL'),
      'control/PRUEBA_PORTABLE_FI_ACCESO_DEV2_R01/RESULTADO.json':('Dos primarios copiados a destino independiente; cuatro checks y RAW decode, sin DEE ni Native','RECALCULO_DOCUMENTAL_PORTABLE')}
    for name,(scope,kind)in items.items():
        p=P/name
        if p.exists(): records[name]={'ruta_relativa':name,'bytes':p.stat().st_size,'sha256':sha(p),'cobertura_real':scope,'tipo':kind}
    with coverage.open('w',encoding='utf-8-sig',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(old[0]));w.writeheader();w.writerows(records.values())
    proposal={'schema':'DEE.PI07.catalogue_and_continuity.proposed_close.v1','applied':False,'new_Native_ticks':0,
       'protected_current_main':m['source_main'],
       'available_scientific_result':'Regulación contextual local y reajuste por consecuencias reales demostrados en clon continuo; reservas y contingencia acotadas. Conservación global sigue gate explícito.',
       'if_no_promotion':{'principal':'Conservar literalmente el principal PI05 T824911; preservar candidata completa como vida experimental.',
           'catalogue_scope':'Sólo procedimientos/instrumentos y reproducción experimental realmente preservados y comprobados. No atribuir estas experiencias al principal.',
           'required_actual_proof':'DECISION_NO_ADOPCION_PI07 y comprobante de incorporación documental/instrumental si Root la ejecuta.'},
       'if_promotion':{'precondition':'Todos los gates reales, conservación representativa, suministro futuro, reapertura e integridad completos; CAS del principal vigente.',
           'required_actual_proof':'ADOPCION_PRODUCTO_PI07 COMMITTED y reapertura seleccionada; leer N/T/parent/VIDA/ACTIVO actuales, no rellenarlos por pronóstico.',
           'historical_negative_preserved':'El fallo de la API anterior y la readaptación12 permanecen en historia y alcance aunque una interfaz nueva pase.'},
       'not_an_operational_selector_or_permission':True}
    if documentary_applied.exists()and read(documentary_applied).get('applied')is True:
        proposal['status']='HISTORICAL_PROPOSAL_SUPERSEDED_BY_ACTUAL_DOCUMENTARY_CLOSURE'
        proposal['actual_documentary_closure']=ref('control/CIERRE_DOCUMENTAL_NO_ADOPCION_PI07_R01.json')
        proposal['actual_adopted']=False
    (P/'mapas/CATALOGO_Y_CONTINUIDAD_PROPUESTA_PI07.json').write_text(json.dumps(proposal,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({p.name:sha(p)for p in(path,matrix,coverage)},ensure_ascii=False))

if __name__=='__main__':main()
