"""Prepare evidence-linked system documentation, never participant decisions."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import argparse,hashlib,json,shutil,time
ROOT=Path(__file__).resolve().parents[4]
SELECTED=['E1_SOCIAL_11','E1_11_ESTABLE','E1_CPC9_1907','E1_CPC9_884','E1_RECONSTRUIDO_11','R65_45_VIVIDO','R65_REVISION_11','R65_N67_VIVIDO','U0_14_VIVIDO']

def read(p):return json.loads(Path(p).read_bytes())
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def text(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(x.strip()+'\n',encoding='utf8')

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);a=p.parse_args();r=a.root;s=r/'sistema';ev=r/'evidencia';calc=read(ev/'informes/CALCULOS_DESDE_PRIMARIOS.json');catalog=read(s/'capacidades/CATALOGO_CAPACIDADES.json')
    records={x:read(s/'estado/vidas'/x/'VIDA.json')for x in SELECTED}
    for value in records.values():value.setdefault('snapshot_sha256',sha(s/value['snapshot']))
    social=records['E1_SOCIAL_11']
    decision={'decision_id':'DCS11_PREF_SOCIAL_R1_3154','route':'COMPATIBLE','life_id':'E1_SOCIAL_11','snapshot_sha256':social['snapshot_sha256'],'scope':'Preferred bounded continuation of CPC9 from completeT1907 throughT1948, social acquisition and transformed-carrier access, thenT3154. No claim of a complete stable mind or K65 integration.','gains':['Four learned social carriers remained functionally readable over eleven later rounds and two further CLI reads.','Reference changed67→78 by actual resource11 and supports less/equal comparisons; previous R36/O16 comparison remains+X.','Full operational snapshot and queues can continue without historical ZIPs.'],'losses':['Initial social use was7/8; only4/8 remain accessible with the admitted mobile reader.','Original A-port repeated access is not retained after transformation.','No complete old18-row count functionality established; one late count reader was informative.'],'uncertainties':['Finite horizon3154, with a new test fork through3221; no unlimited stability.','Opposite/unpaired histories can destabilize the integrated preparation.','No R2 learned utility policy, endogenous source selection or new NSM primitive proved.'],'evidence':['evidencia/telemetria/CONTINUIDAD_FUNCIONAL_R1','evidencia/telemetria/MOVIL_SOCIAL_R1','evidencia/verificaciones/OBSERVADOR_COMPONENTE_CORREGIDO.json','evidencia/verificaciones/VISITA_INTERACTIVA_11'],'regression_coverage':{'old_two':'10/10 plus6/6 follow-up and subsequent common-interface checks; finite actual queries','quantity':'67→78 vs unchanged67 control; later50+5,73+5,82+5 contrasts','old_joint':'Measured plus free/changed paths, not every historical relation','heritage':'34 auxiliary families recovered; these are not34 functions known by this life'},'baseline_retained':'E1_11_ESTABLE T1948 remains unchanged and explicitly selectable','not_promoted':['K65_R1_GUARDS','FUNC_R2_TRANSLATED_Z2','alldenseopposite/unpaired histories','R65_SHAM_11_R2'],'decision_role':'AUDITOR bounded profile preference; not an ENTE choice or automatic PASS'}
    put(s/'contratos/PROMOCION_SOCIAL_R1.json',decision)
    newproofs={'CPC9_E1_ORDER_CONTACT':'evidencia/controles/ONTOGENIA_N67_R1','CPC9_E1_COMPOSITION':'evidencia/controles/ONTOGENIA_N67_R1','CPC9_E1_REFERENCE_REVISION':'evidencia/telemetria/CONTINUIDAD_FUNCIONAL_R1','CPC9_E1_LATE_OPERANDS':'evidencia/telemetria/CONTINUIDAD_FUNCIONAL_R1','CPC9_E1_SOCIAL_RETURN':'evidencia/controles/PUENTE_CAUSAL_R1B/CONTROLES.json','CPC9_E1_QUERY_CONDITIONED':'evidencia/controles/ONTOGENIA_N67_R1','CPC9_E1_K65_ATTEMPT':'evidencia/telemetria/INTERFERENCIA_R1','CPC9_E1_RESTORE':'evidencia/verificaciones/RECUPERACION_ESTADOS_INICIAL.json','CPC9_AUX_K65_N67':'evidencia/telemetria/INTERFERENCIA_R1/K65_R1_PURE','CPC9_OCCUPATION_WAVE':'evidencia/diagnosticos/EXPANSION_MICRO_R1/MICRO_EXPANSION.json'}
    for x in catalog['entries']:
        if x['id']in newproofs:
            x['availability']='REVALIDADA_1_1_CON_DOMINIO_FINITO';x['revalidation_1_1_specific']=newproofs[x['id']]
            if x['id']in('CPC9_E1_ORDER_CONTACT','CPC9_E1_COMPOSITION','CPC9_E1_REFERENCE_REVISION','CPC9_E1_LATE_OPERANDS','CPC9_E1_SOCIAL_RETURN','CPC9_E1_QUERY_CONDITIONED','CPC9_E1_RESTORE'):
                x['integration']='INTEGRADA_CON_LIMITACIONES_EN_RAMA_E1';x['knowledge']='Historical acquired past inherited exactly; new acquisitions/accesses belong to the named continuation only. Currentaccess is not inferred from historicalmaximum.'
        x['preparation_interface']='Declared family constructor/protocol in the included recovered source; not a lookup table of expected responses'
        x['state_effects']='Material teaching/querying can change native state. Passive observations are distinguished. Do not run destructive tests on the preferred life.'
        x['resource_contract']='32*N^3 basic buffers plus native/host structures; exact N and prepared sources in the family configuration; measured process resources where available.'
    additions=[('DCS11_LIFE_STORE','Complete native snapshot, operative queues, atomic pointers and exact forks','All five admitted profiles; no cross-geometry migration','python gestionar.py estado','evidencia/verificaciones/PERFILES_B02/RESULTADOS.json'),('DCS11_SOCIAL_MOBILE','A→B→C physical learning and later transformed-carrier access','N67 socialbridgev1; four accessible forms atT3154; fixed externally initiated reader','python gestionar.py eventos documentacion/ejemplos/visita_1_1.eventos','evidencia/telemetria/MOVIL_SOCIAL_R1'),('DCS11_R65_SEPARATE_PHASE','32+33 same-life acquisition; phase-specific access without reteaching','Official N131 apparatus, acquisition ticks0/134; distinct read windows','python gestionar.py restaurar R65_45_VIVIDO','evidencia/telemetria/REGISTROS_OPERATIVOS/R65_45_VIVIDO/VIDA.json'),('DCS11_REVISION_CONTINUED','Explicit three-port actual teachers update one prior relation','N131, first configured L01 only; private experimental continuation917→1054; offpath control affects L06','python gestionar.py restaurar R65_REVISION_11','evidencia/diagnosticos/REVISION_MICRO_R1/MICRO_REVISION.json'),('DCS11_REPERTOIRE_N67','Independent learned directional repertoire with alternating reader phase','N67,65opaqueforms,10sweeps to2822; newpayload9 reserve2889','python gestionar.py restaurar R65_N67_VIVIDO','evidencia/telemetria/REGISTROS_OPERATIVOS/R65_N67_RESERVA/VIDA.json')]
    for ident,mechanism,domain,command,proof in additions:
        if not any(x['id']==ident for x in catalog['entries']):catalog['entries'].append({'id':ident,'version':'1.1.0','origin':'CONSOLIDACION_1_1','mechanism':mechanism,'domain':domain,'availability':'REVALIDADA_1_1_CON_DOMINIO_FINITO','integration':'INDEPENDENT_PROFILE'if'REPERTOIRE'in ident or'R65'in ident or'REVISION'in ident else'CONTINUITY_OR_CONNECTED_WORLD','knowledge':'See exact learned life and its current query evidence, not library breadth','controls':'Declared matched omission, offpath and sham controls where physically relevant; see proof','limits':domain,'execution_command':command,'evidence':proof,'legacy_families':[],'historical_classification_preserved':'NEW_1_1'})
    put(s/'capacidades/CATALOGO_CAPACIDADES.json',catalog)
    profiles=read(s/'contratos/PERFILES.json')
    for x in profiles['profiles']:
        x['status']='ADMITIDO_EN_DOMINIO_FINITO';x['clean_release_proof']='VERIFICACION_FINAL_EXTERNA.json accompanying the exact sealed archive; no extrapolation from an import check'
        x['current_learned_lives']=[k for k,v in records.items()if v['profile']==x['id']];x['integration_caveat']='Profiles do not automatically share matter, memory, access or learned relations.'
    put(s/'contratos/PERFILES.json',profiles)
    # Byte-exact operative records for engine-free audit. They are not replayed
    # or read by any participant as a source of answers.
    allrecords={p.parent.name:read(p)for p in(s/'estado/vidas').glob('*/VIDA.json')}
    for value in allrecords.values():value.setdefault('snapshot_sha256',sha(s/value['snapshot']))
    for life in allrecords:
        dest=ev/'telemetria/REGISTROS_OPERATIVOS'/life;dest.mkdir(parents=True,exist_ok=True)
        for name in('VIDA.json','HISTORIA.jsonl'):
            src=s/'estado/vidas'/life/name
            if src.exists():shutil.copy2(src,dest/name)
    lives=[]
    for name,d in records.items():
        scope={'E1_SOCIAL_11':'Preferred bounded connected continuation: four mobile social carriers, reference78 and oldtwo R36/O16. Priororder/contact history preserved; current broadsemantic generality notestablished.','E1_11_ESTABLE':'Unchanged continuation branchT1948 with actual oldtwo+X query; no new socialcarriers.','R65_45_VIVIDO':'65 learned directional forms, phase-specific access; notNSM65.','R65_REVISION_11':'Same N131 parent, L01revised and64others accessible in actual reservedwindows; privateexperimentalprotocol.','R65_N67_VIVIDO':'Independent pureN67 65forms, not integratedwithE1.','U0_14_VIVIDO':'Independent officialU0life with14observed directionalassociations; revisedL03 and13others retained.','E1_RECONSTRUIDO_11':'New T0reproduction; entire RAW/clocks at884 equalhistoricalreference; distinct biography.'}.get(name,'Protected complete historical parent, not a newly acquired or currently preferred learner.')
        lives.append({'life_id':name,'profile':d['profile'],'branch':d['branch'],'parent':d.get('parent'),'tick':d['physical']['tick'],'N':d['physical']['N'],'snapshot':d['snapshot'],'snapshot_sha256':d['snapshot_sha256'],'physical':d['physical'],'scope_current_knowledge':scope,'basic_buffers_bytes':32*d['physical']['N']**3,'excludes':'No implication of human meanings, generalmind, unlimitedstability or silently sharedruntime'})
    put(s/'documentacion/ESTADO_ACTUAL_DE_VIDAS.json',{'schema':'DCS1.1.current_lives.v1','preferred_life':'E1_SOCIAL_11','lives':lives,'deep_unselected_lives':'Preserved in working evidence and audit records; not admitted operationally merely because a checkpoint exists.'})
    put(s/'documentacion/RAMAS_Y_GENEALOGIA.json',{'schema':'DCS1.1.lineage.v1','selected':lives,'all_experiment_branches':[{'life_id':k,'branch':v['branch'],'parent':v.get('parent'),'tick':v['physical']['tick'],'snapshot_sha256':v['snapshot_sha256'],'operationally_admitted':k in SELECTED}for k,v in allrecords.items()],'warning':'Exact forks share the past, not independent experimental subjects. A new N or geometry is a new preparation.'})
    pending=[x for x in catalog['entries']if x['availability']=='DOCUMENTAL_PENDIENTE']
    coverage={'schema':'DCS1.1.regression.coverage.v1','heritage_families':calc['heritage'],'profile_validation_history':calc['technical_incidents'],'pending_documentary_rows':[{'id':x['id'],'cause':x['limits'],'scope':x['domain']}for x in pending],'release_levels':{'A':'Identity, exactfullrestore, passiveinertness, representativeaffectednativefunctions','B':'IndependentCLIprocesses, eight+eightacquisition, selectiveupdates, actualinstalledprofiles','C':'Sameprofilepanel after extraction plus separatelyrequested all34auxiliaryfamilies fromincludedcontentstore'},'final_exact_artifact_test':'External verification binds ZIP hashes, commands, pass/failure and actual scope. This internal file does not predeclare that future test succeeded.','not_claimed':['Allhistoricaldocumentaryrows executed','Allcapabilities simultaneouslyinE1','R2regulation','65NSMsemantics','Unlimitedhorizon']}
    put(s/'documentacion/COBERTURA_REGRESION.json',coverage)
    hist=read(ev/'genealogia/NSM65_ANTECEDENTE_CPC9.json');nsm=read(s/'capacidades/NSM65_CATALOGO_OFICIAL.json');assert len(nsm['entries'])==65 and len(hist['rows'])==65
    histby={x['id']:x for x in hist['rows']};nsmrows=[]
    for entry in nsm['entries']:
        h=histby[entry['id']]
        for life in('E1_SOCIAL_11','R65_45_VIVIDO','R65_N67_VIVIDO','U0_14_VIVIDO'):
            integrated=life=='E1_SOCIAL_11';current='SIN_PRUEBA_DE_ADQUISICION_NSM';proof='evidencia/genealogia/NSM65_ANTECEDENTE_CPC9.json'
            if integrated and entry['glosa_inglesa_id']=='MORE':current='COMPARACION_CUANTITATIVA_FINITA_CON_REFERENCIA_ADQUIRIDA78';proof='evidencia/verificaciones/OBSERVADOR_COMPONENTE_CORREGIDO.json'
            elif integrated and entry['glosa_inglesa_id']in('BEFORE','TOUCH'):current='HISTORIA_ADQUIRIDA_Y_RUTAS_COMPUESTAS_PARCIALMENTE_ACCESIBLES;NO_SE_REPRUEBA_SIGNIFICADO_GENERAL_ACTUAL'
            elif integrated and entry['glosa_inglesa_id']=='TWO':current='LECTOR_ANTIGUO_PARCIAL;NO_CARDINALIDAD_GENERAL_ACTUAL'
            elif integrated and entry['glosa_inglesa_id']=='LIKE_AS':current='MAXIMO_HISTORICO_E2;ACCESO_ACTUAL_ESPECIFICO_NO_REVALIDADO'
            nsmrows.append({'vida':life,'id':entry['id'],'forma_es':entry['forma_es'],'grupo':entry['grupo_documental'],'glosa_fuente':entry['glosa_inglesa_id'],'maximo_historico_E1':h['nivel_original_E1_maximo_episodico']if integrated else'NO_ATRIBUIBLE_A_ESTE_PERFIL','estado_actual':current,'adquisicion_nueva_1_1':'NINGUNA_PRIMITIVA_NUEVA_ACREDITADA','pregunta_operacional':h['pregunta_operacional'],'evidencia':proof,'limite':'K65signosnoequivaleaNSM65; máximoepisódiconoimplicaaccesoactual; noextrapolarobservacionesauxiliares','fuente_catalogo':nsm['catalogue_version']})
    heritage_rows=[]
    for x in catalog['entries']:
        heritage_rows.append({k:x.get(k,'')for k in('id','version','origin','mechanism','domain','availability','integration','knowledge','controls','limits','execution_command')})
    put(r/'laboratorio/campanas/CONSOLIDACION_1_1/TABLAS_PARA_EXPORTAR.json',{'MATRIZ_HERENCIA_CPC01_CPC09.csv':heritage_rows,'NSM65_ESTADO_POR_VIDA.csv':nsmrows})
    discoveries={'schema':'DCS1.1.native_observations.v1','findings':[{'id':'DCS_NATIVE_01','mechanism':'Source survival and an empty target receiving its unique directional neighbor can coexist in actual local v27 steps.','evidence':'evidencia/diagnosticos/EXPANSION_MICRO_R1/MICRO_EXPANSION.json','scope':'16localwitnesses;54wholeworldreferenceframesexact. Turnovercanalsoeraseothers. This is not alone a sufficientglobalcause. XNORappearslater, not theuniqueorigin.'},{'id':'DCS_NATIVE_02','mechanism':'A physically acquired sign can remain usable after its carrier is transformed by two social-learning encounters; the original reader can fail while a current relative reader succeeds.','evidence':'evidencia/telemetria/MOVIL_SOCIAL_R1','scope':'Only4/8laterfunctional; sixpassiveYsignatures innoquerycontrol do not demonstrate sixusableknowledgeitems.'},{'id':'DCS_NATIVE_03','mechanism':'Different acquisition phases produce separate access windows.','evidence':'evidencia/telemetria/REGISTROS_OPERATIVOS/R65_45_VIVIDO/VIDA.json','scope':'32+33directionalforms; fixedexternalcadence, notlearnedattention.'},{'id':'DCS_NATIVE_04','mechanism':'Offpath sham teacher can physically act on another nearby form.','evidence':'evidencia/diagnosticos/REVISION_MICRO_R1/MICRO_REVISION.json','scope':'L06collateral;notgloballyinertcontrol.'}],'novelty':'New observations within this campaign, not claims that v27 rules or broadcognitivefunctions were first discovered here.'}
    put(s/'documentacion/DESCUBRIMIENTOS_NATIVOS.json',discoveries)
    text(r/'LEER_PRIMERO.md',"""# DEE Cognitive System 1.1

Sistema privado sobre **DEE thinking4.5.0 / v27 sin cambios**. Abre una vida aprendida, no un universo nuevo silencioso.

La vida preferente es E1_SOCIAL_11, T3154, rama explícita del E1 histórico. Conserva cuatro portadores sociales utilizables, una referencia cuantitativa revisada a78 y acceso al comparador anterior R36/O16. El ejemplo incluido continúa una copia hastaT3221. No afirma65significados ni estabilidad ilimitada.

Perfiles separados: repertorio oficial N131 de65formas con acceso por fase; alternativa N67 con65formas durante diez barridos; U0oficial con14asociaciones comprobadas; física directa vacía. No se suman como conocimientos de E1.

Se ejecutaron34familias heredadas desde el núcleo incluido. Dieciséis filas documentales siguen pendientes de reproducción específica. Los controles adversos, fallos y límites están en la auditoría.

Instalar: `sistema/instalar_sistema.ps1 -Python313 RUTA_A_PYTHON313_X64`. Después `sistema/iniciar_sistema.ps1 estado`, `vidas`, `perfiles` o `interactivo`. Lea GUIA_DE_USO_1_1.md.

Dos ZIP complementarios: SISTEMA contiene el único WHL y estados completos; AUDITORIA_ESENCIAL contiene primarios, controles, recálculos y laboratorio, sin motor. El comprobante externo identifica los ZIP exactos probados. Las partes binarias son menores de16,000,000bytes. No son ZIP independientes.

No modifique ni publique estos archivos privados. Los CPC históricos permanecen intactos.
""")
    guide=r"""# Guía de uso1.1

## Instalación y vida activa

Se requiere Windows x64, CPython3.13x64 y las bibliotecas de ejecución de C++ del sistema. No se distribuye el intérprete ni una toolchain. Ejecute desde la carpeta extraída:

```powershell
.\sistema\instalar_sistema.ps1 -Python313 'C:\\ruta\\python.exe'
.\sistema\iniciar_sistema.ps1 estado
.\sistema\iniciar_sistema.ps1 vidas
.\sistema\iniciar_sistema.ps1 capacidades
.\sistema\iniciar_sistema.ps1 perfiles
```

El inicio normal carga ACTIVO.json y verifica versión, hash del snapshot, RAW/clocks/tick y la identidad documental. Si falta o es incoherente, informa el error. No crea ni rebobina una vida. `activar ID` elige explícitamente otra vida sin alterar su pasado.

## Una interacción nueva con un estado aprendido

```powershell
.\sistema\iniciar_sistema.ps1 eventos .\sistema\documentacion\ejemplos\visita_1_1.eventos
.\sistema\iniciar_sistema.ps1 estado --vida VISITA_11
.\sistema\iniciar_sistema.ps1 restaurar VISITA_11
.\sistema\iniciar_sistema.ps1 interactivo
```

El recorrido crea una bifurcación exacta de E1_SOCIAL_11T3154. Consulta cuatro portadores mediante un lector material preparado; presenta un objeto nuevo82, comprueba82+5>referencia78 y vuelve al antiguo R36/O16. GuardaT3221. El originalT3154 queda intacto. La cadencia, los suministros y la elección del lector son externos y declarados, no iniciativa aprendida. VISITA_11 no debe existir antes de ejecutar el ejemplo; repetirlo con el mismoID produce error, nunca reemplazo.

## Operaciones distintas

`crear NUEVA --perfil fisica_directa --parametros '{"N":11}'` prepara un mundo vacío. `crear ... --perfil cpc9_integral_n67` prepara posibilidades, no asociaciones semánticas. `experiencia ... curriculo_integral` programa experiencias pedagógicas reales; no convierte su programación en invención del ente.

`restaurar ID` sólo carga y verifica; `continuar --vida ID --hasta T` evoluciona; `guardar --vida ID` guarda el mundo completo con colas, interfaces y metadatos. `bifurcar PADRE HIJA --modalidad EXACT_FORK` comparte el pasado hasta ese snapshot. `importar-estado ARCHIVO ID --perfil PERFIL --sha256 HASH` es continuidad importada explícita, no aprendizaje nuevo. `exportar ID --salida NUEVA` exporta un estado completo y su ficha.

`entrada --vida ID PUERTO CARGA T --sonda` introduce materia. `observar --vida ID X Y Z` y `observar-componente --vida ID quantity.center` son lecturas pasivas. Una consulta material puede enseñar, transformar o perder acceso; use copias para pruebas destructivas. Cero activo, silencio, rechazo, ocupación y fuera de dominio no se sustituyen entre sí.

## Repertorios y actualización

R65_45_VIVIDO conserva32formas adquiridasT0 y33T134. Deben consultarse en ventanas separadas: el protocolo común equivocado sólo veía33; sin reenseñar se recuperaron65 enT658/661 yT789/792. R65_REVISION_11 es otra rama: la receta privada de tres puertos revisóL01T917 y conservó64formas enT1051/1054. No amplía silenciosamente la APIoficial4.5 ni demuestra actualización arbitraria. El sham fuera de ruta afectóL06 y se conserva como control imperfecto.

R65_N67_VIVIDO es otra vida, sin el cuerpo integradoCPC9:65/65 durante diez barridos hastaT2822 y reserva con carga9 hastaT2889. U0_14_VIVIDO es el perfil oficialU0, independiente. No existe un puente implícito entre estos Runtime.

## Laboratorio, comparación y promoción

`bifurcar PADRE CANDIDATA --modalidad CANDIDATE`, `comparar PADRE CANDIDATA` y `promover CANDIDATA --decision ARCHIVO.json` están disponibles. La comparación es pasiva y no elige ganador. Promover exige el hash exacto, ganancias, pérdidas, incertidumbres, evidencia y cobertura. Registra PREPARED/COMMITTED y cambia el puntero activo sin volver atrás los individuos. Una nueva geometría oN requiere otra vida desdeT0.

`ensayar --nivel A|B|C --salida DIRECTORIO_NUEVO` ejecuta pruebas en copias. `probar-herencia --familias cpc1,cpc2,... --salida NUEVA --segundos 4200` materializa el núcleo incluido y ejecuta aparatos auxiliares; no enseña al activo. Las34familias están en capacidades/core/FAMILIAS.json. CORE06/07 usan la dependenciaNumPy incluida explícitamente sólo para esos contratos instrumentados.

## Procedencias y límites

ENTE indica campos y emisiones v27; ENTORNO, acontecimientos presentados; INSTRUMENTO, puertos, recibos y observadores; INTERPRETACIÓN, lectura del auditor. No existe chatlibre niLLM que complete respuestas. El gestor selecciona perfiles a petición explícita, nunca porque sabe quién tiene la solución.

Las restricciones de archivos del CLI son una barrera de auditoría Python, no un sandbox de seguridad del sistema operativo. El modo de física directa no añade guardas ni cognición. No hayR2demostrada, YO/TÚfuncional ni65significados. Consulte contratos y evidencia, no una puntuación global.
"""
    text(s/'documentacion/GUIA_DE_USO_1_1.md',guide)
    text(s/'documentacion/ARQUITECTURA_Y_SEPARACION.md',"""# Arquitectura y separación

Motor: el WHLoficial4.5.0, kernel27. La capa1.1 sólo administra preparaciones, protocolos, estados, interfaces y supervisión. No recompila ni modifica el motor. La transición física sigue siendo X(t+1)=F_v27(X(t), entradas admitidas).

sistema/ funciona sin laboratorio/, evidencia/, entregas/ ni CPC históricos. Incluye constructores, contratos y snapshots completos. Las colas pendientes, interfaces, cadencia del lector y progreso operativo se conservan en metadata del mundo, no se eliminan como telemetría. Los registros de experiencia no se consultan como tablas para decidir respuestas.

laboratorio/ conserva variantes y ejecutores nuevos. evidencia/ contiene datos, controles, diagnósticos y auditores. entregas/ nunca es origen de importación. El núcleo de recuperación bajo sistema/capacidades/core sólo se abre en la operación explícita probar-herencia; el CLI ordinario lo bloquea como fuente de respuestas.

Cada vida tieneID, worldID, perfil, padre, rama, snapshot, hash y tick. Una vista regional no crea materia. En los experimentos sociales A/B/C comparten el mismoRuntime; existe un único snapshot autorizado del mundo por checkpoint. Perfiles distintos no se comunican automáticamente. No se implementó puente externo entreRuntime.

Los escritores se excluyen por worldID. Se guardan snapshots nativos comprimidos, sin pickle ni código ejecutable incrustado. La carga verifica hashes y estado exacto, incluye colas y metadata. El diario y puntero deben coincidir; incoherencias interrumpen la carga sin restaurar un pasado favorable.

El autor de experiencias es externo. Un puerto puede estar preparado, un signo quedar adquirido y una respuesta ser nueva: son hechos distintos. El lector móvil es preparado y solicitado por el usuario. Las comparaciones adquiridas y mensajes se realizan mediante encuentros nativos. No hay política externa que lea el target y escriba la respuesta.

La preservación es acumulativa por perfiles.34familias son contratos auxiliares finitos, no34conocimientos simultáneos deE1. Las16filas documentales pendientes conservan su causa. Las referencias originales y sus correcciones permanecen en el registro.
""")
    text(s/'documentacion/DECISIONES_DE_PROMOCION.md',"""# Decisiones de promoción

Se prefiere E1_SOCIAL_11T3154 como continuación utilizable limitada. Se conserva E1_11_ESTABLET1948 sin cambios. La decisión exacta está en contratos/PROMOCION_SOCIAL_R1.json y el registro transaccional estado/PROMOCIONES.jsonl. No se certifica estabilidad general.

La ganancia es comunicación física A→B→C con adquisición posterior y cuatro accesos móviles conservados, junto a revisión cuantitativa y un comparador anterior. La pérdida observada es7/8en el primer uso y4/8tardíos; el antiguo puertoA deja de dar la función y el panel de cantidad anterior no está íntegramente disponible. La dependencia del lector, cadencia y suministros externos permanece.

No se promueven las guardasR0del ensayoK65:37,22y luego0respuestas. Tampoco la traslación+2Z:6/8usos y0accesosA tardíos. El cuerpo integradoK65 reproduce57,53,4y después0; no es un perfil preferente aunque sus finales sigan conservados.

Se admite por ruta arquitectónica separada el repertorioN67vacío con65asociaciones durante diez barridos. No posee las funciones del cuerpoCPC9. La varianteN131con32+33ylectura porfase conserva otro dominio útil. Mantenerlas separadas no declara que sean físicamente imposibles de integrar.

La revisión continuadaN131de1.1 es experimental: tres recursos/puertos, L01configurada, docentes explícitos. La APIoficialrechazó una revisiónT917fuera de su contrato; ese rechazo permanece. El control+10ZtocóL06, por lo que no prueba inocuidad global.
""")
    report="""# Consolidación1.1: resultados y límites

## Hechos computacionales y continuidad

El instrumento oficial fue instalado aisladamente en CPython3.13x64. Se recuperaron snapshots completos deE1T884/T1907/T2493, no sólo arraysRAW/clocks. T2493bloqueado permanece como evidencia y no se eligió por ser el último. E1_11_ESTABLE es una rama deT1907, con consulta nuevaT1948. E1_SOCIAL_11 continúa esa rama hastaT3154; el ejemplo reservado continúa una copia hastaT3221. Otra vida reconstruida desdeT0 reproduce exactamente RAW/clocks/tick deT884, sin confundirse con continuidad importada.

Se ejecutaron34familias de recuperación, cada una con su contrato y controles. Dieciséis filas históricas documentales aún requieren reproducción específica. Las filas comparten mecanismos: no son un conteo de conceptos ni se atribuyen en bloque aE1. La verificación desde el ZIP exacto se consigna externamente, sin autorreferencia del contenedor.

## Deterioro: causalidad acotada

En el cuerpo integrado N67, K65 reproduce57/65,53/65,4/65y después0hastaT2822. La historia desacoplada tampoco protege: el mundo termina densamente ocupado. Igual númeroN67sin el cuerpo anterior conserva65/65durante diez barridos, con65sitios ocupados. Mantener fuentes antiguas en un mundo vacío tampoco produce el colapso; quitar sólo su mantenimiento del cuerpo antiguo no lo resuelve. Por tanto, no se infiere un límite universal de65 ni “demasiados pensamientos”.

Desde el mismo padreT2822sin consultas, una primera lectura tardía consigue61/65. Las consultas repetidas se deterioran. El control sin sonda hastaT3560mantiene326sitios ocupados frente a aproximadamente297mil con sondas. Una sonda no es observación inocua: contribuye causalmente a la expansión en ese contexto. El sham fuera de ruta puede retornar por el toro y no es aislamiento garantizado.

La reconstrucción microscópica coincide con54estadosRAW/clocks históricos. Registra16testigos locales de supervivencia de la fuente junto con recepción en un destino vacío, sin entrada externa próxima. También registra16nacimientosSEM7compatibles con la ramaXNOR; el primero es2291→2292. La ocupación supera600antes, enT2281. Estos mecanismos locales no identifican una causa única de toda la expansión. No se equiparan ocupación, s_reg, energía eléctrica ni muerte del ente.

## Aprendizaje, comunicación y uso

Desde el mismo estadoT1948 se adquirieron ocho correspondencias nuevas. Mensajes v27 producidos porA enseñan aB y su retorno aC; todos compartenRuntime. El primer uso es7/8. Omitir experiencia, asociaciónB o asociaciónC da0/8; cortar ida o retorno da0/8 ysham conserva7/8. En copias diagnósticas, cortar selectivamente una ocupación antigua en el destinoS00 recupera8/8; la copia no devuelve su solución aMAIN.

La fuente cambia físicamente después de las consultas. El lector de los portadores transformados conserva4/8durante once rondas posteriores y nuevas interacciones comunes. Sin esas consultas quedan seis firmasYpasivas, lo que no prueba seis conocimientos utilizables. Se mantienen por separado esos resultados y la pérdida de acceso.

Una adición física11revisa la referencia67→78; el control fuera de ruta queda67. Objetos posteriores50+5,73+5y82+5producen comparaciones menor, igual y mayor. El valor0direccional activo en igualdad no se confunde con silencio. El comparador anteriorR36/O16sigue+X. No se demuestra cardinalidad general ni preservación íntegra de18lectores antiguos.

## Repertorios y actualización

En una vidaN131nueva se adquirieron32formas y luego33. Tres consultas con una ventana común sólo accedían a33. En esa misma vida, sin enseñar otra vez, ventanas separadas recuperan32+33en dos rondas. El fallo era de acceso bajo ese protocolo, no evidencia suficiente de borrado.

La nueva receta privada1.1revisaL01con docentes reales enT917. EnT1051/1054aparecen L01revisada y64no modificadas. El sham de igual dosis produce pérdida enL01yL06: su desplazamiento coincide con otro soporte. Esta limitación del control se documenta, no se transforma enPASSglobal.

La alternativaN67independiente conserva65direcciones durante diez barridos y una reserva de carga9. U0oficial conserva14asociaciones consultables enT539, después de revisarL03. Son otras vidas, no el repertorio semántico deE1.

## Diversidad, consulta y regulación

La repetición desdeT0confirma la historia de orden/contacto y su composición en el aparato finitoCPC9. El orden opuesto cambia emisiones tempranas pero llega densamente ocupado aT884; señales desacopladas también. El control de contacto fuera de ruta permanece distinto y sin ese colapso. No se presenta un resultado técnico completado como un éxito funcional de toda variante.

La oportunidad de consulta, el destinatario y las fases siguen preparados. Hay preguntas condicionadas históricas, no política general aprendida de qué observar o a quién preguntar. Se conservanR0/R1en sus dominios. No se demostróR2seleccionada por consecuencias. YO/TÚfuncional, NOgeneral y productividad lingüística permanecen abiertos.

## NSM65 e interpretación

El catálogo oficial conserva65entradas con preguntas individuales y estado porvida. El máximo episódico histórico deE1era60E0,4E2(TWO,BEFORE,TOUCH,LIKE_AS)y1E3(MORE), todos operacionales y limitados. Esta campaña no acredita otra primitiva nueva ni eleva65correspondencias a65significados. Máximo histórico, función actual y adquisición de otra vida son columnas diferentes. La matriz no sustituye los primarios.

## Información, recursos y límites

Los decoders son fijos y leen campos actuales. No hayLLM, copia de respuestas entreRuntime ni tabla de targets en la decisión. Los auditores posteriores no alimentan al ente. Los controles intervenidos son copias identificadas. Las analogías cognitivas se limitan a funciones observadas, sin conciencia o comprensión humana general.

Se declararon21600segundos, dos trabajadores nativos como máximo,4GiBporJob y cierre dentro del plazo original. Parte inicial deR1carece de RAMrealporproceso; ese hueco no se rellena con la memoria del lanzador. Las medidas posteriores usanJobObjects y recursos reales. 32*N^3es memoria básica de buffers, noRAMtotalni electricidad.

La carpeta completa retiene evidencia profunda. Los ZIPoperativos excluyen cachés regenerables, venvs, toolchain y snapshots densos redundantes. El índice de exclusiones conserva tamaños y hashes; la ausencia en el paquete no equivale a borrado del original. La auditoría no duplica motor ni convierte material privado en publicable.
"""
    text(ev/'informes/INFORME_CIENTIFICO_1_1.md',report)
    text(ev/'informes/HALLAZGOS_Y_LIMITACIONES.md',report)
    text(r/'USO_PRIVADO.md','''# Uso privado

Estos paquetes contienen preparaciones, estados y evidencia confidencial de investigación. No son un exportado seguro para terceros. No publicar ni cargar fuentes, geometrías, estados o manuales en servicios externos. Los avisos y licencias originales se preservan donde fueron recuperados; no se inventa una licencia nueva.

El motor se incluye una sola vez en SISTEMA. El paqueteAUDITORIA no debe interpretarse como completo archivo histórico ni como otra distribución de motor. CPython3.13x64/Windows y bibliotecasC++delSO son dependencias externas explícitas.
''')
    text(s/'documentacion/LEER_PRIMERO.md',(r/'LEER_PRIMERO.md').read_text(encoding='utf8'))
    text(s/'documentacion/USO_PRIVADO.md',(r/'USO_PRIVADO.md').read_text(encoding='utf8'))
    text(ev/'informes/LECTURA_PROVISIONAL.md',report)
    put(ev/'informes/NSM65_COBERTURA.json',{'entries':65,'catalogue_version':nsm['catalogue_version'],'historical_E1_maxima':dict(Counter(x['nivel_original_E1_maximo_episodico']for x in hist['rows'])),'new_primitives_credited_this_cut':0,'all_65_have_individual_questions':all(x['pregunta_operacional']for x in hist['rows']),'per_life_rows':len(nsmrows),'caveat':'No sum across lives; opaque associations are not automatically semantic primitives.'})
    put(ev/'informes/COBERTURA_Y_DECISION.json',{'selected_lives':SELECTED,'promotion':decision,'regression':coverage,'recalculation_source_sha256':sha(ev/'informes/CALCULOS_DESDE_PRIMARIOS.json'),'all_branches_kept_in_working_expedient':True})
    put(r/'PROVENANCE.json',{'project':'DEE Cognitive System1.1','author':'Ivan Erick Tlaltecatl Morales','software_layer':'1.1.0','motor':'Official frozen DEE thinking4.5.0, v27','sources':read(ev/'genealogia/INVENTARIO_INICIAL.json'),'directed_sources':read(ev/'genealogia/LECTURA_DIRIGIDA/FUENTES_ABIERTAS.json'),'history_unchanged':True,'conversations':'No access to ChatGPT conversations claimed. Only opened files and preserved prompts are sources.','unavailable_manuals':'Both requested4.5DOCXmanuals not found in inspected historicalroot/archives; executablecontract and actualtechnicalfiles were used.','private':True})
    budget=read(r/'PROYECTO.json').get('budget',read(r/'REANUDACION.json')['budget']);elapsed=time.perf_counter()-budget['start_monotonic']/budget['monotonic_frequency']
    put(r/'REANUDACION.json',{'status':'CIERRE_Y_VERIFICACION','budget':budget,'elapsed_seconds':elapsed,'completed':'34hereditaryfamilies, completelearnedcontinuation, matchedK65anddosecontrols, socialcausaltests, independentrepertoire, ongoingrevisionandmicroscopicwitnesses','next':'Verify exact sealed ZIPs from clean extraction; do not rerun completed research or resume budget silently','automatic_future_resume_authorized':False})
    print(json.dumps({'selected_lives':len(lives),'catalogue_rows':len(catalog['entries']),'documentary_pending':len(pending),'nsm_rows':len(nsmrows),'elapsed_seconds':elapsed}))
if __name__=='__main__':main()
