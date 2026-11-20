"""Edit the existing logical manual, preserving its scientific history. No DEE imports."""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
from zipfile import ZipFile
from lxml import etree as E

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).parent
NAME = 'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_12_MENTE_ACUMULATIVA_SIN_VALIDACION_VISUAL.docx'
OLD = 'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_11_R1_ENTE02_SIN_VALIDACION_VISUAL.docx'
BASE_SHA = 'c85d33bc3c637e4e8f804f2d9332f1078f11ed9f5f4085479a3e0a7548ea9d33'

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def txt(p): return ''.join(n.text or '' for n in p.iter(W+'t'))
def sty(p):
    n=p.find(f'{W}pPr/{W}pStyle')
    return n.get(W+'val','') if n is not None else ''
def put(p, value):
    if list(p.iter(W+'instrText')): raise ValueError('Refuse replacement of a field paragraph')
    r=p.find(W+'r'); pr=deepcopy(r.find(W+'rPr')) if r is not None and r.find(W+'rPr') is not None else None
    for n in list(p):
        if n.tag!=W+'pPr': p.remove(n)
    r=E.SubElement(p,W+'r')
    if pr is not None: r.append(pr)
    for i,line in enumerate(value.split('\n')):
        if i: E.SubElement(r,W+'br')
        n=E.SubElement(r,W+'t'); n.set('{http://www.w3.org/XML/1998/namespace}space','preserve'); n.text=line
def para(style,value):
    p=E.Element(W+'p');pr=E.SubElement(p,W+'pPr');E.SubElement(pr,W+'pStyle').set(W+'val',style);put(p,value);return p

ADDITIONS = {
'1. Qué es 1.1 y qué hace más sencillo': [
 ('Heading2','Desarrollo acumulativo de una línea principal'),
 ('Normal','El desarrollo mantiene una línea principal identificada y una referencia protegida. La organización principal recibe experiencias, usa su estado y continúa mientras aprende. Sus componentes pueden cambiar cuando una alternativa mejora la función; una preparación nueva o un cambio de N conserva su identidad de nueva vida. La elección externa de una candidata se documenta como ingeniería y no como aprendizaje del participante.'),
 ('Normal','El ciclo permanente consiste en formular una hipótesis material, probarla en una copia, contrastar la función nueva y los usos anteriores afectados e incorporar el resultado útil en su dominio. Se permite práctica intercalada y aprendizaje gradual. No se exige acierto a la primera ni validación de toda la biblioteca para conservar una mejora local.'),
 ('Normal','La acumulación se comprueba por el primer uso de relaciones anteriores después de incorporar otra experiencia, antes de que el retorno pueda reenseñarlas. Las consultas, decisiones, herramientas y combinaciones deben interactuar mediante la organización declarada. Un gestor que elige por fuera la respuesta correcta no acredita selección propia.'),
 ('Normal','Los capítulos 20 a 28 conservan sus cortes científicos. ENTE02 deja EO02_MAIN T169383 como continuación operativa y R10 T40353 como otra vida; no demuestra que una sola organización conserve dos políticas contextuales. La campaña MENTE_ACUMULATIVA parte de esa limitación sin convertir sus objetivos en capacidades ya disponibles.')],
'13. Lo heredado, lo mejorado y lo todavía separado': [
 ('Heading2','Capacidad utilizable y conocimiento de una vida'),
 ('Normal','Cada incorporación distingue mecanismo del sistema, adquisición de la vida, uso actual comprobado y asistencia. Una función causalmente demostrada puede utilizarse de inmediato dentro de su contrato; no necesita probar inteligencia general. Si permanece en un perfil complementario se conserva ejecutable y se explica la incompatibilidad concreta, sin sumarla a la mente principal.'),
 ('Normal','Adoptar un clon como continuación seleccionada conserva su snapshot completo, padre y futuros alternativos. Aplicar el mismo procedimiento en otra vida requiere experiencias propias y comprobación de uso. No se mezclan snapshots ni se trasplantan recuerdos mediante etiquetas. Las ganancias se registran junto a pérdidas y funciones todavía necesarias.')],
'14. Qué muestran las verificaciones y qué no': [
 ('Heading2','Retención y evaluación del uso'),
 ('Normal','Una prueba breve pertinente compara la función nueva con un control que pueda cambiar su interpretación y con las funciones anteriores afectadas. El primer regreso a una relación anterior mide retención; las respuestas después de un retorno docente se registran aparte como readquisición. Cambios documentales no requieren repetir física. Un cambio compartido de sensor, lector o protocolo amplía sólo la regresión pertinente.'),
 ('Normal','Las reservas fijan entradas accesibles, recursos, lector, criterio, horizonte y asistencia antes de evaluarlas, sin congelar la plasticidad que se pretende estudiar. Los fallos se conservan. Un mecanismo inesperado puede incorporarse después de un contraste nuevo, sin forzarlo a ocupar el soporte previsto ni cambiar retrospectivamente la métrica.')],
'15. Laboratorio, evolución y promoción de ramas': [
 ('Heading2','Incorporación proporcional durante el desarrollo'),
 ('Normal','Una mejora local con evidencia causal pertinente se incorpora durante la misma ejecución, con vida, corte, asistencia, forma de uso y limitaciones. El registro utiliza el contrato instalado de promoción o selección, no una autoridad documental nueva. La promoción de una continuación no exige que domine todas las capacidades históricas; sí exige declarar pérdidas y proteger funciones esenciales del objetivo.'),
 ('Normal','El estado seleccionado es uno realmente alcanzado. No se importa a MAIN un futuro favorable de otra rama. Si un candidato ofrece una especialización valiosa pero incompatible, permanece como alternativa utilizable. La arquitectura puede simplificarse, recomponerse o distribuirse según resultados funcionales; el número de regiones y canales no decide por sí solo la calidad de la organización.')],
'17. Lenguaje español: objetivo y estado del programa': [
 ('Heading2','Uso situado de señales y herramientas'),
 ('Normal','El modo científico principal utiliza señales y vocabulario acotado ligados a actos y relaciones accesibles. Un codec fijo puede transportar símbolos o unidades; no conserva memoria, elige estrategia ni calcula la respuesta atribuida a DEE. Las asociaciones de significado se enseñan por experiencias y se contrastan con enseñanza desacoplada, referentes nuevos y combinaciones.'),
 ('Normal','Seleccionar una herramienta local puede ser una acción propia comprobable. Comprimir o calcular un hash pertenece al algoritmo de esa herramienta, no acredita que el ente conozca criptografía. La consecuencia procede del trabajo realmente ejecutado y puede volver por el canal fijo; nunca se escribe desde Python la próxima respuesta o la memoria correcta. No se atribuyen nuevas primitivas NSM65 por disponer de estos servicios.')],
'18. Memoria de proyecto y relevo entre conversaciones': [
 ('Heading2','Continuación seleccionada y límites del relevo'),
 ('Normal','La ficha de continuidad existente debe identificar por separado la referencia protegida y la línea principal seleccionada, con su último estado completo, padre, operación finalizada y capacidades actuales. Se usa el registro instalado; no se crea otra base paralela. Las colas, interfaces, entorno y progreso pendientes necesarios para continuar son estado operativo, no telemetría descartable.'),
 ('Normal','La sesión de uso presenta otra secuencia de situaciones sin editar código, conserva la misma vida, guarda y continúa en un proceso nuevo. La prueba de distribución verifica además que la copia no lea el código o estados del proyecto original. Los diarios de investigación y el manual nunca alimentan las respuestas del participante.')],
'19. Actualización del manual y control de versiones': [
 ('Heading2','Una autoridad documental y un cierre finito'),
 ('Normal','DCS11-MM-001 es el único Manual Maestro lógico. La edición vigente se identifica en la raíz de DEE Cognitive System 1.1 y en cognitive sistem; las ediciones previas permanecen recuperables en el archivo histórico. La metodología se integra en los capítulos de operación y desarrollo, no en un manifiesto independiente. El cierre corrige los estados, comandos y alcances realmente afectados.'),
 ('Normal','La investigación mantiene el presupuesto autorizado y reserva su tramo final para prueba integrada, incorporación y entrega. No se prolonga una serie improductiva suponiendo que más ticks resolverán el problema. El cierre entrega un estado realmente continuable cuando existe, el alcance ejecutado y sus límites; no exige un resultado positivo por decreto.'),
 ('Normal','Tras un corte operativo sin escritores activos se ejecuta el actualizador existente de cognitive sistem. Se conservan trabajo_personal, modificaciones y vidas del colaborador; se copian completos los estados seleccionados y el entorno pendiente. El ZIP se comprueba desde otra extracción. La prueba en otra carpeta de la misma computadora no se presenta como ejecución en otro equipo.')],
}

def edit_initial():
    source=ROOT/OLD
    if digest(source)!=BASE_SHA: raise AssertionError('Source identity changed')
    output=ROOT/NAME
    if output.exists(): raise FileExistsError(output)
    with ZipFile(source) as z:
        infos=z.infolist(); old={x.filename:z.read(x.filename) for x in infos}
    members=dict(old); doc=E.fromstring(members['word/document.xml']); body=doc.find(W+'body');changes=[]
    replacements={
      'DEE CognitiveSystem 1.1':'DEE Cognitive System 1.1',
      'Manual maestro de uso, memoriay continuidad de la investigación':'Manual maestro de uso memoria y continuidad de la investigación',
      'DCS11-MM-001 / Edición documental 1.11':'DCS11-MM-001 / Edición documental 1.12',
      'Edición 1.10 ENTE01 preservada; continuación y resultados ejecutados de ENTE_DEE_EVOLUCION_02.':'Edición 1.11 R1 ENTE02 preservada; metodología acumulativa incorporada a los capítulos vigentes. El último corte científico cerrado sigue siendo ENTE02.',
    }
    for p in list(doc.iter(W+'p')):
        before=txt(p); after=replacements.get(before)
        if before.startswith('DEE thinking 4.5.0  |') and 'Edición documental 1.11' in before:
            after='DEE thinking 4.5.0  |  DEE Cognitive System 1.1.0\nEdición documental 1.12  |  DCS11-MM-001'
        elif before.startswith('Corte documental ENTE02 del'):
            after='Edición 1.12 con metodología acumulativa integrada\nÚltimo corte científico cerrado ENTE02 del 24 de octubre de 2026 UTC\nReferencia protegida E1_SOCIAL_11 T3154\nContinuación operativa EO02_MAIN T169383\nAlternativa independiente EO02_SENSORIAL_R10_T0 T40353'
        elif before.startswith('La edición original se basó en el resumen funcional'):
            after='Este Manual Maestro conserva la genealogía desde el resumen funcional y los cortes de Español Funcional, Paisaje Causal, Acceso Adaptativo, Retrospectiva, Hábitat, Integración Situada, Ciclo02, MI01, MI02, CF01, ENTE01 y ENTE02. Los capítulos 20 a 28 describen los resultados de sus vidas y fechas, no un estado universalmente actual. Los estados completos, contratos y fichas vigentes prevalecen sobre las descripciones históricas. La edición 1.12 integra la metodología permanente de desarrollo acumulativo en los capítulos 1, 13 a 15 y 17 a 19. No añade aprendizajes por el solo cambio editorial.'
        elif before.startswith('El software permanece en la capa Cognitive 1.1.0'):
            after='El software permanece en la capa Cognitive 1.1.0; DEE thinking 4.5.0 y Universe v27 siguen congelados. La edición documental vigente es 1.12. El cambio editorial no fusiona vidas ni convierte objetivos de MENTE_ACUMULATIVA en resultados adquiridos.'
        elif before.startswith('La matriz de 1.1 contiene 73 entradas.'):
            after=before.replace('La matriz de 1.1 contiene','En el corte original de consolidación, la matriz de 1.1 contenía').replace('El recuento de sus valores da','El recuento histórico de sus valores dio')
        elif before.startswith('El corte 1.1 no acreditó primitivas nuevas:'):
            after=before.replace('El corte 1.1','El corte original de consolidación 1.1')
        elif before.startswith('NSM65 se conserva como mapa de preguntas'):
            after=before.replace('El corte 1.1 no acreditó','El corte original de consolidación 1.1 no acreditó')+' ENTE02 tampoco acreditó primitivas nuevas; esos máximos históricos no sustituyen el panel actual de cada vida.'
        elif before.startswith('La ficha siguiente es un formato documental propuesto'):
            after='Las fichas de continuidad de campañas posteriores ya registran estados y localizadores. El esquema siguiente sirve como comprobación de los campos necesarios, no obliga a abrir otro archivo ni implica que cada campo se actualice automáticamente por el gestor:'
        elif before.startswith('Las ediciones 1.5 a 1.9 incorporaron Integración Situada'):
            after=before+' La edición 1.12 concreta desarrollo acumulativo, anatomía flexible, retención en el primer uso e incorporación proporcional inmediata en los capítulos vigentes. El cierre de la nueva ejecución actualizará este mismo Word sólo con resultados comprobados.'
        if after is not None and after!=before:
            put(p,after);changes.append({'old':before,'new':after})
    for heading, additions in ADDITIONS.items():
        nodes=list(body);at=next(i for i,p in enumerate(nodes) if p.tag==W+'p' and sty(p)=='Heading1' and txt(p)==heading)
        end=next((i for i in range(at+1,len(nodes)) if nodes[i].tag==W+'p' and sty(nodes[i])=='Heading1'),len(nodes))
        pos=end
        for i in range(at+1,end):
            if nodes[i].tag==W+'p' and sty(nodes[i])=='Source':pos=i;break
        for j,(s,value) in enumerate(additions):body.insert(pos+j,para(s,value))
    members['word/document.xml']=E.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True)
    for name in ('word/header1.xml','word/footer1.xml'):
        tree=E.fromstring(members[name])
        for n in tree.iter(W+'t'):
            if n.text:n.text=n.text.replace('DOCUMENTAL 1.11','DOCUMENTAL 1.12').replace('documental 1.11','documental 1.12')
        members[name]=E.tostring(tree,xml_declaration=True,encoding='UTF-8',standalone=True)
    core=E.fromstring(members['docProps/core.xml'])
    for n in core:
        if n.tag.endswith('}title'):n.text='DEE Cognitive System 1.1 Manual Maestro Edicion 1.12 Mente Acumulativa'
        if n.tag.endswith('}modified'):n.text=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    members['docProps/core.xml']=E.tostring(core,xml_declaration=True,encoding='UTF-8',standalone=True)
    with ZipFile(output,'w') as z:
        for info in infos:z.writestr(info,members[info.filename])
    archive=ROOT/'documentos'/'historico_manuales';archive.mkdir(parents=True,exist_ok=True)
    moved=[]
    for p in sorted(ROOT.glob('DEE_Cognitive_System_1_1_Manual_Maestro*.docx')):
        if p==output:continue
        target=archive/p.name;sha=digest(p)
        if target.exists():
            if digest(target)!=sha:raise FileExistsError(target)
            raise FileExistsError('Duplicate archive already exists; manual review needed before removing root copy: '+str(p))
        shutil.move(str(p),str(target))
        if digest(target)!=sha:raise AssertionError('Archive changed')
        moved.append({'source':str(p),'archive':str(target),'sha256':sha})
    proof={'schema':'MENTE_ACUMULATIVA.manual.edit.v1','stage':'METODOLOGIA_INCORPORADA_INICIO','native_ticks':0,'source':str(archive/OLD),'source_sha256':BASE_SHA,'output':str(output),'sha256':digest(output),'bytes':output.stat().st_size,'changes':changes,'inserted_sections':list(ADDITIONS),'archived_previous_editions':moved,'visual_validation':'REQUIRES_AUTHORIZED_RENDER'}
    (HERE/'EDICION_INICIAL_1_12.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:proof[k] for k in ('stage','output','sha256','bytes','native_ticks')},ensure_ascii=True))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--inicio',action='store_true');args=ap.parse_args()
    if not args.inicio:raise ValueError('Explicit --inicio required')
    edit_initial()
