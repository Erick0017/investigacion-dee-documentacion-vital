"""Referencias compactas y prosa de cierre ya acreditadas; no sello ni ensayo."""
import argparse,hashlib,json
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n') as f:json.dump(d,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();r=a.root;lab=r/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO';c=lab/'cierre'
    old=c/'BORRADOR_CIERRE_CIENTIFICO_N0_R08';out=c/'BORRADOR_CIERRE_CIENTIFICO_N0_R09';assert not out.exists();out.mkdir()
    x=json.loads((old/'RESULTADOS_FINAL.json').read_bytes())
    rp=out/'INFORME_CIENTIFICO_RESULTADOS.md';report=(old/'INFORME_CIENTIFICO_RESULTADOS.md').read_text(encoding='utf8')
    report=report.replace('Estado: resultados cerrados de la campaña, preparados para su integración final. La reserva temprana, el Full exacto y el Word permanecen pendientes de sus cierres acreditados; este documento no los certifica. No se han sumado recuerdos de ramas divergentes.',
      'Estado: ciencia Native cerrada, con resultados positivos, negativos y futuros inciertos preservados. Reserva temprana, Source y edición Word están documentados por sus primarios de cierre; sólo la prueba del Full exacto y la aprobación del análisis siguen pendientes. No se han sumado recuerdos de ramas divergentes.')
    with rp.open('x',encoding='utf8',newline='\n') as f:f.write(report)
    cas=c/'CANDIDATO_CAS_FINAL_CIENCIA_COMPACTO_N0_R09';ref=c/'REFERENCIA_CAS_FINAL_CIENCIA_COMPACTO_N0_R09.json';assert ref.exists()
    x['components'][0].update(source=cas.relative_to(r).as_posix(),manifest_sha256=sha((cas/'MANIFIESTO_CAS.json').read_bytes()))
    for f in x['files']:
        if f['id']=='CAS_REFERENCE':f.update(source=ref.relative_to(r).as_posix(),sha256=sha(ref.read_bytes()))
        if f['id']=='SCIENTIFIC_DRAFT':f.update(source=rp.relative_to(r).as_posix(),sha256=sha(rp.read_bytes()))
        if f['id'].startswith('LOGISTICS_PATCH'):
            f['kind']='Historical proposal retained as original evidence; final installed bytes are independently sealed, not inferred byte-identical to this proposal.'
            f['destination']=f['destination'].replace('MODIFICACIONES_PROPUESTAS/','PREINCORPORACION/')
    changes='''# Cambios del Manual Maestro\n\nDocumento lógico: DCS11-MM-001. Se conservó la edición1.17 y se editó el Word real a1.18, no sólo un addendum. Archivo local: DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_18_APD04_ECOSISTEMA_SIN_VALIDACION_VISUAL.docx. SHA-256 c0c1d75011d181f4d8c81555dcc5997bcc60643e2ce09dbe20889692a1110d98;158521bytes.\n\nSe añadieron capítulo35 y resultados APD04; se actualizaron frente, índice y referencias de edición/continuidad pertinentes, preservando813 nodos históricos y el original. La comprobación estructural registró cuatro partes OOXML cambiadas; no se revelaron reglas ni código interno del kernel. Se distinguen las18 formas finitas(16heredadas+2nuevas),6 contextos MA, asociación de señal, intervención P0, selección local P1 y ausencia de una prueba general P2/R2. Se conservan adversos, pendientes y límites de sensores.\n\nSe intentó el renderizador disponible. Falló por FileNotFoundError de soffice.exe y se produjeron0 páginas: no hay validación visual de esta edición. La limitación figura en el propio nombre y en evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/VERIFICACION_MANUAL_EDICION_1_18_R01.json,SHA55013114225497d248fae908015551cf68dcc4dda17f74a012839c8c46156b2e. La prueba del ZIP Full se registra externamente después de sellar, no se anticipa en Word ni se modifica su hash para añadir un PASS posterior.\n'''
    mp=out/'CAMBIOS_MANUAL.md'
    with mp.open('x',encoding='utf8',newline='\n') as f:f.write(changes)
    for id_,src,dest in [('MANUAL_CHANGES',mp,'CAMBIOS_MANUAL.md'),
      ('ACTUAL_MANUAL_VERIFICATION',r/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/VERIFICACION_MANUAL_EDICION_1_18_R01.json','MANUAL/VERIFICACION_ESTRUCTURAL_Y_RENDER.json'),
      ('EXPLICIT_SOURCE_COPY_OMISSIONS',cas/'OMISIONES_SOURCE_REDUNDANTE.json','INDICE/OMISIONES_SOURCE_REDUNDANTE.json'),
      ('ACTUAL_CONTINUITY',r/'CONTINUIDAD_APD04_ECOSISTEMA_COGNITIVO.json','CONTINUIDAD_APD04_ECOSISTEMA_COGNITIVO.json'),
      ('ACTUAL_RESUMPTION',r/'REANUDACION.json','REANUDACION.json')]:
        b=src.read_bytes();x['files'].append({'id':id_,'source':src.relative_to(r).as_posix(),'destination':dest,'kind':'Actual closed local artifact, no additional Native actions.','sha256':sha(b)})
    x['omissions'].append({'locator':(c/'FUENTES_CIERRE_SOURCE_Y_WORD_N0_R01').relative_to(r).as_posix(),
      'reason':'235 copied Source aliases inherited from older work are excluded from compact CAS, along with27original core members not copied initially. Every omitted final path/bytes/hash remains indexed against the exact279-memberSource seal. Word itself is exported directly, not lost.',
      'scientific_consequence':'No APD04 primary, unique negative, executed revision or archived recalculation input is excluded by this compacting step.'})
    x['attempts'].append({'id':'ACTUAL_WORD_EDIT_R01','life':None,'role':'EDITORIAL','status':'CLOSED_RESULT',
      'scope':'Real Word1.18edited,813historicalnodespreserved;renderattemptFileNotFoundsoffice.exe,0pagesvisualQA. No Native work.',
      'source_ids':['ACTUAL_MANUAL','ACTUAL_MANUAL_VERIFICATION','MANUAL_CHANGES']})
    x['attempts'].append({'id':'ACTUAL_SOURCE_CLOSURE_R01','life':'APD04_SEMILLA_COLABORADOR_R01','role':'N0_INSTRUMENT','status':'CLOSED_RESULT',
      'scope':'Selected completeSource closed, no Native ticks/source-lifequeries;ACTIVOprotected;FullverificationnotcertifiedbySourceclosure.',
      'source_ids':['ACTUAL_SOURCE_SEAL','ACTUAL_INCORPORATIONS']})
    x['claims'].append({'id':'ACTUAL_INCORPORATION','text':'APD04mechanisms/seed became selectable through the existing platform and realWord1.18,withboundedattribution andunmodifiedfrozenactors.',
      'level':'HECHO_COMPUTACIONAL','life':'APD04_SEMILLA_COLABORADOR_R01','scope':'Sourceclosure279members,completepair654959,zeroNativeticksintheseal;notFullproof.',
      'source_ids':['ACTUAL_SOURCE_SEAL','ACTUAL_INCORPORATIONS','ACTUAL_MANUAL_VERIFICATION'],
      'limits':['No global default promotion, no merging divergent histories.','VisualWordQAunavailable.','Full exact archive proof remains external/pending.']})
    dump(out/'RESULTADOS_FINAL.json',x)
    print(json.dumps({'selection':str(out/'RESULTADOS_FINAL.json'),'attempts':len(x['attempts']),'lives':len(x['lives']),'claims':len(x['claims']),'native_work_closed':x['native_work_closed'],'status':x['status']}))
if __name__=='__main__':main()
