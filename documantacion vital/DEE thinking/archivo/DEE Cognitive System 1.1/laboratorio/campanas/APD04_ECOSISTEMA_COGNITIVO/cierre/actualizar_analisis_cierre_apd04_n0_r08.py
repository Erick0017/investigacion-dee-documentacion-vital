"""Actualiza sólo borradores N0 con los primarios cerrados de la reserva temprana."""
import argparse,hashlib,json
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();r=a.root
    lab=r/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO';c=lab/'cierre';out=c/'BORRADOR_CIERRE_CIENTIFICO_N0_R08';assert not out.exists();out.mkdir()
    comp=lab/'controles_diseno/EVIDENCIA_RESERVA_TEMPRANA_CERRADA_N0_R08'
    early=json.loads((comp/'RECALCULO_CIENTIFICO.json').read_bytes());e=early['cases'][0]
    assert e['completed_work']==14 and e['planned_work_opportunities']==43 and not e['actual_clean_STOP']
    report=(c/'INFORME_CIENTIFICO_RESULTADOS_CONSOLIDADO_R07.md').read_text(encoding='utf8')
    intro='''## 6.1 Reserva temprana: experiencia conservada, acceso fallido y futuro incierto\n\nAPD04_PERSISTENCIA_TEMPRANA_RESERVA_R01 fue una bifurcación completa desde T639374, con vista persistente P0 instalada temprano: no T0, reparación de los brazos post10 ni fusión de futuros. De43 oportunidades previstas se enviaron15, se archivaron14 y quedó una pendiente;28 no se enviaron. Las14 terminadas produjeron7 INSPECT,2 WAIT,1 USE y4 NULL:10 acciones formadas,11 oportunidades elegibles,ganancia antigua2 ycalidad nueva2;ninguna de las dos WAIT relevantes fue útil. Sólo se presentaron fuentes externas0..6, no20 fuentes simultáneas ni20 inspecciones nativas.\n\nLa única USE recibió la forma solicitada clasifica y comparó mediante Native el dato de caché27/v0 frente a la referencia adquirida20; emitió positivo. El objeto externo actual era14/v1, dato que no se presentó a esa comparación. La clasificación era aritméticamente coherente con27, pero obsoleta e irrelevante para el objetivo actual; no hubo ganancia de la tarea. No es generalización a14 ni prueba de error aritmético. El sensor del selector sólo entrega tag+goal, no ID de fuente, vigencia/versionado de caché o magnitud;20 fuentes comparten dos tags. Ese límite preparado restringe las situaciones físicamente distinguibles y no autoriza atribuir todo fallo a incapacidad atencional general.\n\nSe comprometieron243 IDs Native nuevos:169 aplicados y74 rechazados por ocupación. De42 señales sensoriales,30 se admitieron y12 se rechazaron. En work10 se admitieron3/3 sensoriales, pero se rechazaron seis entradas finales de clear/failure; en work11..14 se rechazaron17/17 entradas por oportunidad, incluidas las tres sensoriales, y hubo NULL. Se conserva la actividad no comprometida como desconocida, no cero.\n\nEl cierre instrumental duró4624,535226 segundos y terminó exit1, Job sin procesos activos y STOP no confirmado: no acredita completar el programa integrado de60 minutos. Último commit T664324, snapshotSHA `14d450f7495c5a9041ec706b7a3e55a335de9885c1e81a24aa657bddab886bbe`,ocupación297588,max_s_reg4524. Quedó `apd04_early_persistent_r01_event_017` pendiente y no hay par FULL actual que capture ese futuro. El RAW estable de T658070 a T664324 no demuestra pérdida universal de memoria; tampoco se demostró recuperación Native. No se promueve esta rama ni se limpia su cola. El recálculo portátil del cierre tiene108 verificaciones sin discrepancias y fue byte-idéntico desde una copia temporal ajena al proyecto.\n\nFuente: `controles_diseno/EVIDENCIA_RESERVA_TEMPRANA_CERRADA_N0_R08`, manifiesto `13162984aab77c09a879eeb44b6bbc33149eac52288872cc4dfeaef214df5f31`, y su QA externa.\n\n'''
    report=report.replace('## 7 Acceso consecutivo del descendiente diagnóstico',intro+'## 7 Acceso consecutivo del descendiente diagnóstico')
    report=report[:report.index('## 9 Incorporación y estado de cierre')]+'''## 9 Incorporación y estado operativo\n\nEl mismo gestor dispone de los comandos literales ecosistema-iniciar, ecosistema-vivir, ecosistema-cambio, ensenar-ecosistema y palabra-ecosistema, además de las operaciones previas. Se incorporaron contratos, guía, catálogo, genealogía, overlay NSM sin upgrades y continuidad del corte seleccionado. Son transporte literal y aparato preparado; no un intérprete de idioma libre ni una política aprendida general. La palabra solicitada y la herramienta emitida se registran por separado: old_work_gain obtenido por otra herramienta no acredita el significado pedido.\n\nLa autoridad de Source es `entregas/SELLO_DISTRIBUCION_APD04_R01.json`,SHA `663382aef356d230bfaee5ebcad9068868391e83c763e76db080d010ad90989d`:279 miembros, tres actores físicos congelados,semilla completa T654959 sin consultas al sellar,propietario cerrado y ningún pendiente de transporte. Esto no declara vacía la agenda nativa. ACTIVO sigue protegido; las ramas adversas no se promueven. El patch previo no define los bytes finales: inicialmente2/5 miembros coincidieron byte a byte y3/5 sólo por CRLF(normalizados/JSON iguales); después Root hizo cambios descriptivos explícitos y el sello identifica los finales. Véase INCORPORACIONES.md.\n\nEl Manual real DCS11-MM-001 edición1.18 tiene158521 bytes ySHA `c0c1d75011d181f4d8c81555dcc5997bcc60643e2ce09dbe20889692a1110d98`. Conserva813 nodos y cambia cuatro partes OOXML; la edición1.17 se preservó. Se intentó renderizar y faltó soffice.exe: cero páginas verificadas visualmente. No se afirma validación visual.\n\nEl CAS conserva evidencia positiva y negativa, entradas port+channel, revisiones ejecutadas y recálculos exactos sin motor/WHL ni todos los snapshots. Las extracciones RAW/clocks no sustituyen SQLite,interfaces,agenda,cola y progreso de una vida completa. Las copias finales de Source/Word llevan mapa de origen yhash;27 miembros heredados de core no se duplican y quedan identificados por el sello. Es análisis, no respaldo operativo.\n\nLa prueba del ZIP Full exacto y su continuación corresponden a un ledger externo posterior. No se certifican desde el sello Source ni desde estos borradores. La selección permanece DRAFT_NOT_APPROVED hasta autorización y evidencia final; la ciencia Native principal cerró sin convertir sus futuros inciertos en vidas continuables.\n'''
    report=report.replace('Pendientes de cierre:','Alcance de cierre:')
    rp=out/'INFORME_CIENTIFICO_RESULTADOS.md'
    with rp.open('x',encoding='utf8',newline='\n') as f:f.write(report)
    x=json.loads((c/'BORRADOR_INTEGRACION_FINAL_N0_R07_NORMALIZADO/RESULTADOS_FINAL.json').read_bytes())
    x['native_work_closed']=False;x['full_status']='Exact Full proof pending; no success inferred from the selected Source seal.'
    x['attempts'].append({'id':'EARLY_PERSISTENT_RESERVE_R08','life':e['life'],'role':'FORK','status':'PRESERVED_UNCOMMITTED_FUTURE',
      'scope':'Complete fork from T639374, prepared early persistent view;14 archived work/43 planned,15submitted,1uncertain future,28not sent. Instrumental closure is not completed integrated60minute protocol.',
      'initial_tick':639374,'final_committed_tick':664324,'requested':43,'submitted':15,'responded':14,'admitted':None,'correct':None,'incorrect':None,'abstained':4,'rejected':None,
      'source_ids':['CLOSED_CAS'],'denominator_scope':'Work opportunities are not Native inputs:243committed IDs=169applied+74rejected_occupied;42sensorials=30applied+12reject. Pending future unknown,notzero.'})
    life={'id':e['life'],'parent':{'life':'APD04_MAIN','tick':639374,'snapshot_sha256':'771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8'},'N':67,'tick':664324,
      'snapshot_sha256':'14d450f7495c5a9041ec706b7a3e55a335de9885c1e81a24aa657bddab886bbe',
      'status':'PRESERVED_UNCOMMITTED_FUTURE_NOT_NORMAL_CONTINUABLE','available':[],
      'not_currently_proven':['Current inherited24 access','Native recovery after density','General learned attention/P2/R2','All20sources inspected'],
      'continuation':{'scope':'Last committed snapshot only; no final FULL/cleanSTOP. Do not replay/clear unresolved request or certify ordinary continuation.', 'pending_ID':'apd04_early_persistent_r01_event_017'}}
    x['lives'].append(life)
    for l in x['lives']:
        if l['id']=='APD04_SEMILLA_COLABORADOR_R01':
            l['not_currently_proven']=['Arbitrary access order, current generalWAIT policy, long integrated attention, or semantic24concepts. Full exact verification is external and still pending here.']
    x['claims'].append({'id':'EARLY_RESERVE_INPUT_COLLAPSE','text':'The prepared early persistent view did not complete the integrated program; admission collapsed in the committed prefix while historical caches could remain stale.',
      'level':'HECHO_COMPUTACIONAL','life':e['life'],'scope':'14/43work archived;243Native IDs169applied74rejected;uniqueUSEcomparedcache27notactual14;STOPnotconfirmed.',
      'source_ids':['CLOSED_CAS'],'limits':['Uncommitted future unknown, not zero.','No proof of global content destruction or native recovery.','Sensor provides onlytag+goal; absence of freshness information limits distinct situations.'],
      'localizers':['laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/controles_diseno/EVIDENCIA_RESERVA_TEMPRANA_CERRADA_N0_R08/RECALCULO_CIENTIFICO.json#/cases/0']})
    x['pending_root_closures']=[{'id':'FULL_EXACT_PROOF','status':'PENDING_ROOT_CLOSED_PRIMARY','numbers':None}]
    x['components'][0].update(source=(c/'CANDIDATO_CAS_FINAL_CIENCIA_N0_R08').relative_to(r).as_posix(),manifest_sha256=sha((c/'CANDIDATO_CAS_FINAL_CIENCIA_N0_R08/MANIFIESTO_CAS.json').read_bytes()))
    reference=c/'REFERENCIA_CAS_FINAL_CIENCIA_N0_R08.json';assert reference.exists()
    for f in x['files']:
        if f['id']=='CAS_REFERENCE': f.update(source=reference.relative_to(r).as_posix(),sha256=sha(reference.read_bytes()))
        if f['id']=='SCIENTIFIC_DRAFT': f.update(source=rp.relative_to(r).as_posix(),sha256=sha(rp.read_bytes()),kind='Closed Native scientific results; Full external proof pending.')
    x['files']=[f for f in x['files'] if f['id']!='MANUAL_DRAFT']
    for id_,name,dest in [('ACTUAL_MANUAL','DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_18_APD04_ECOSISTEMA_SIN_VALIDACION_VISUAL.docx','MANUAL/Manual_Maestro_1_18.docx'),
        ('ACTUAL_INCORPORATIONS',(c/'FUENTES_CIERRE_SOURCE_Y_WORD_N0_R01/INCORPORACIONES.md').relative_to(r).as_posix(),'INCORPORACIONES.md'),
        ('ACTUAL_SOURCE_SEAL','entregas/SELLO_DISTRIBUCION_APD04_R01.json','INCORPORACIONES/SELLO_SOURCE.json')]:
        b=(r/name).read_bytes();x['files'].append({'id':id_,'source':name,'destination':dest,'kind':'Actual closed artifact; not a global scientific PASS.','sha256':sha(b)})
    # Update existing compact JSON tables; preserve all preceding rows and add final branch explicitly.
    for fname in ['CAPACIDADES_POR_VIDA.json','COBERTURA.json','COMPARACION_DE_VIDAS.json','DEMOSTRABILIDAD.json','FUENTES_DE_TABLAS.json']:
        old=next(z for z in x['files'] if z['id']==fname[:-5]);d=json.loads((r/old['source']).read_bytes())
        if fname=='CAPACIDADES_POR_VIDA.json':d['rows'].append({'life':e['life'],'moment':664324,'capability':'Incomplete integrated access under early persistent preparation','level':'HECHO_COMPUTACIONAL','result':{'completed_work':14,'planned':43,'formed':10,'NULL':4,'Native_applied':169,'Native_rejected':74,'old_gain':2,'new_quality':2,'correct_WAIT':0},'limits':['Future uncertain; no current repertoire panel or ordinary continuation certified.'],'scope':'Last committed only; no FULL.','source_id':'CLOSED_CAS'})
        if fname=='COBERTURA.json':d['attempts']=x['attempts']
        if fname=='COMPARACION_DE_VIDAS.json':d['lives']=x['lives']
        if fname=='DEMOSTRABILIDAD.json':d['claims']=x['claims']
        if 'pending' in d:d['pending']=x['pending_root_closures']
        dest=out/fname;dump(dest,d);old.update(source=dest.relative_to(r).as_posix(),sha256=sha(dest.read_bytes()),kind='Closed Native scientific table; Full external proof pending.')
    dump(out/'RESULTADOS_FINAL.json',x)
    print(json.dumps({'selection':str(out/'RESULTADOS_FINAL.json'),'attempts':len(x['attempts']),'lives':len(x['lives']),'Native_ticks':0,'status':x['status']}))
if __name__=='__main__':main()
