"""Stage complete Manual1.28 / Compendium PI02A copies; no publication or DEE imports.

Root must run the document skill's edit marker exactly once before executing
this authoring command, then pass --artifact-marker-completed. This builder
never runs that marker, a renderer, a world owner or an operational command.
"""
from pathlib import Path
from copy import deepcopy
import argparse,datetime,hashlib,json,re,zipfile
from lxml import etree as E
P=Path(__file__).resolve().parent.parent;R=P.parent.parent.parent
C=R/'DEE Cognitive 2.0';D=P/'documentos'
NAME='DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
MAN=C/NAME;COMP=R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
EXPECTED_MAN='dec1fa7f96ddb5d0db541653152d9f4ba0cf741a85260973d1538bdde3651178'
EXPECTED_COMP='90a5c68f6c13c6348d388119c1125ddbbc52db3483d8155cc301ef73274a6ee9'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W='{'+NS['w']+'}';XML='{http://www.w3.org/XML/1998/namespace}'
TITLE='44 PI02 Retornos físicos selección y asistencia'
SECTIONS=[
('44.1 Qué se ejecutó y qué cambió frente a PI01',[
 'PI02 continúa el estado completo de ECI02_PI01_MAIN, N67, T735843. La etapa A se ejecutó en la candidata ECI02_PI02_MAIN y tres controles del mismo prefijo, sin instalar un portador inicial ni reconstruir T0. Cada brazo avanzó 4500 ticks hasta T740343. La principal operativa global sigue siendo PI01 en este corte documental intermedio; este capítulo no realiza una promoción.',
 'La llegada de un portador A o B al origen preparado activa un trabajo mediante un transductor fijo. Se ofreció una sola petición exterior vivir4500 por brazo; no una orden individual actúa ahora para cada trabajo. Se retiraron los pulsos SENSOR y NORMALIZER de oportunidad de PI01. La geometría de recurrencia, el lector, el mapa A a MA y B a FI y la contrapresión del dispositivo siguen preparados.',
 'Los accesos heredados producen el contenido de la acción: MA utiliza la referencia alfa negativa adquirida por esta genealogía y FI128 compara los dos datos públicos. Su respuesta física mueve un actuador sobre un banco externo de archivos de 64 bytes. El anfitrión compara la acción ya emitida con una condición privada de la regla ambiental y devuelve una valencia genérica si hubo fracaso. No entrega la ruta óptima ni modifica directamente el estado de política.'
]),
('44.2 Organización y observación controlada',[
 'Una organización compuesta N67 conserva los mecanismos MA/FI y el portador circulante heredados. Los controles son bifurcaciones físicas identificadas, no recuerdos acumulados de la misma MAIN. Compartir un prefijo no los convierte en réplicas independientes. El entorno de recursos y el puente son asistencia externa; su estado operativo no es una memoria cognitiva accesible al portador.',
 'El lector se fijó en el origen [0,5,20], con firmas activas SEM1 A=(1,0,0) y B=(0,1,0). Estas firmas directas son distintas de las que se leían después del SENSOR en PI01. Se cuenta el flanco de llegada para no convertir una permanencia en múltiples solicitudes. El registrador acompaña cada avance del propietario, incluidos los pasos internos de los accesos MA/FI; no abre un segundo escritor.',
 'Antes de puntuar la nueva conducta, dos copias del mismo estado avanzaron 134 ticks con y sin registro intermedio hasta T735977. El recálculo pasivo de los snapshots encontró RAW, clocks, prefijo causal y metadata no administrativa iguales: 1009 interfaces, cero pendientes y 112829 recibos heredados. Esta igualdad respalda ese instrumento y esa trayectoria, no cualquier observador futuro ni una equivalencia de todos los artefactos externos.',
 'Una calibración posterior de 268 ticks en esas copias transformó A/carga937 a B/carga942 tras una entrada genérica aplicada, mientras la omisión conservó A. No se añadieron SENSOR ni NORMALIZER. Fue una prueba de factibilidad física con valencia impuesta; no demuestra por sí misma utilidad aprendida, iniciativa temporal ni descubrimiento de una interfaz.'
]),
('44.3 Reserva utilidad y controles',[
 'El protocolo congeló doce pares públicos, los cambios de condición ambiental, 4500 ticks por brazo, busy308 y un retorno previsto 268 ticks después de cada solicitud admitida. Fijó mínimo9 recursos en MAIN, ventaja mínima2 frente a omisión y sham, cero recursos con actuación anulada y doce respuestas válidas. El código R02B y sus hashes quedaron identificados antes de observar las reservas.',
 'Cada brazo registró 67 firmas de retorno: 12 trabajos admitidos, 48 descartes por busy y 7 firmas después de agotar el banco. Las doce respuestas de cada brazo fueron válidas. Los descartes son un límite P0 del dispositivo, no decisiones aprendidas de abstención. La tabla conserva solicitudes y admisiones; no convierte rechazos en respuestas ni recibos antiguos en experiencias nuevas.'
]),
('44.4 Qué sostiene la causalidad y qué limita el resultado',[
 'MAIN empezó usando MA. Tras el fracaso del episodio3 se aplicó la primera valencia en T737142; la llegada siguiente admitida, T737210, utilizó FI. OMIT conservó la ruta anterior. El primer aporte sham se admitió en la misma fase fuera de la ruta y también conservó MA. La diferencia de selección precedió a las entradas nuevas de FI, que no pueden explicar retrospectivamente esa primera elección.',
 'FI produjo una respuesta negativa útil en el episodio8, por lo que la ruta B no significa siempre positivo ni existe una ruta universalmente correcta. Tras el fracaso9, la segunda consecuencia cambió de nuevo la selección y los dos trabajos siguientes utilizaron MA con utilidad. Anular el actuador dejó que se formasen decisiones y respuestas, pero impidió liberar recursos.',
 'El brazo sham solicitó cinco aportes de valencia y sólo uno se aplicó; cuatro fueron rechazados por ocupación. Es un límite del control repetido de dosis. El primer aporte admitido y la primera divergencia son el contraste interpretable; no se afirma que toda la ventaja final se haya demostrado con igual exposición material total. Después de divergir la ruta, FI y MA también consumen cantidades distintas de entradas.',
 'Como referencias externas separadas se calcularon WSLS, siempreA, siempreB y alternancia fija, con la misma información y oportunidades. Obtuvieron respectivamente 10/12, 7/12, 6/12 y 7/12. La secuencia observada de MAIN coincide con WSLS en este dominio. Estas referencias no controlaron DEE. El resultado no demuestra una política más compleja que la alternancia condicional preparada ni superioridad general.'
]),
('44.5 Qué es nativo qué se adquirió y qué permanece asistido',[
 'El portador y sus encuentros producen la dirección física; la consecuencia efectivamente vivida modifica la selección posterior. Los contenidos MA y las emisiones FI proceden de la evolución del mismo mundo. La novedad utilizable de etapa A es un inicio material por recurrencia sin los dos pulsos individuales de oportunidad, con selección binaria revisada por consecuencias y efecto externo verificado.',
 'La recurrencia de 67 ticks, las ventanas, el filtro de flanco, busy308, el mapa MA/FI y las reglas de retorno son preparación P0. No se observó adquisición de cuándo actuar, exploración abierta, selección espontánea de objetivos o descubrimiento de una interfaz desconocida. El anfitrión aún conecta una firma A/B con un acceso específico. Las etapas de regulación, advertencia y anticipación no se acreditan por este ensayo.',
 'Cero pulsos SENSOR/NORMALIZER de oportunidad no equivale a cero entradas sensoriales o consultas materiales. MAIN utilizó seis accesos MA de siete entradas y seis FI de 176, más dos valencias: 1100 entradas nuevas aplicadas. Las respuestas procedieron de lectores fijados; NULL se mantiene distinto de cero. Un calendario automático de Python tampoco se contabiliza como aprendizaje del tiempo.',
 'La densificación ECI02 C no acreditó dolor ni asfixia; el portador temprano R04 también aparecía sin consulta. Los cierres CORE, Ingeniería06 y OBP mantienen sus límites de preparación, redundancia, contexto y causalidad. PI02 reutiliza esos antecedentes sin sumarlos como aprendizajes del principal. Una analogía aversiva necesitaría una definición funcional y sus controles; no se infiere sufrimiento de congestión o valencia.'
]),
('44.6 Conservación continuación y decisiones pendientes',[
 'Durante la tarea MAIN utilizó consecutivamente MA y FI sin reenseñar el contenido heredado. Sin embargo, esta edición intermedia aún no dispone de un panel nuevo completo de asociaciones y aritmética después de T740343 ni de la prueba final de nueva función tras guardar y reabrir PI02. El panel PI01 de 12/12 corresponde a T735466 y no se atribuye retrospectivamente al final de PI02.',
 'La candidata de etapa A no se adopta mediante este documento. El principal global conserva ID ECI02_PI01_MAIN, N67, T735843, COMMITTED. La candidata ECI02_PI02_MAIN se documenta en T740343 como corte A; si su ficha registra una continuación posterior legítima, ésta prevalece y no se restaura el corte antiguo. B/C deben acumularse en esa misma genealogía para atribuirles integración.',
 'El banco A contiene doce trabajos y ya está agotado. Vivir más ticks no garantiza nuevos recursos; no se debe reiniciar el entorno ni reimportar la semilla para aparentar continuidad. La continuación exige el snapshot y el conjunto emparejado: interfaces, agenda, cola SQLite, recibos, outbox, artefactos y progreso. Las reservas de los controles se conservan como otras historias.',
 'Al cerrar cada propietario se registraron recursos de CPU/RAM con bajo coste. Los picos working-set observados fueron de 289665024 a 292024320 bytes, bajo un límite Job de 536870912 bytes, con cierres de código0. Son intervalos de aproximadamente75–90 segundos. No verifican ni descartan un fallo Mac de80–90 minutos, una fuga universal ni la conveniencia general de reiniciar cada45 minutos. La RAM del anfitrión no se presenta como memoria cognitiva.'
]),
('44.7 Uso del corte experimental y evidencia',[
 'Para el principal protegido se mantiene ABRIR_DEE_COGNITIVE.bat y la selección PI01. Para la candidata se utiliza el gestor de la copia de laboratorio, no el gestor importado desde el producto estable con código antiguo. Desde DEE thinking/DEE Cognitive 2.0, los siguientes comandos PowerShell definen la ruta de trabajo y abren un único propietario pausado. No se han de ejecutar si ya hay un propietario vivo de esa vida.',
 ('code','$pi02System = "../archivo/analisis_transversal_cognitivo/PROGRESION_INTEGRADA_02/estados/candidato/sistema"'),
 ('code','& "./motor/python313/python.exe" -I -B -X utf8 "$pi02System/gestionar.py" --system-root $pi02System mente-unificada-iniciar --vida ECI02_PI02_MAIN --backend mente_unificada --eci01 --pausado --intervalo 60 --guardar-cada 3600 --max-segundos 7200'),
 'Desde otra terminal, con la misma variable, mente-unificada-estado, mente-unificada-guardar y mente-unificada-detener administran el propietario existente por su cola. Una petición literal eci01-pi02-estado es una vista del auditor, no un recuerdo ni actuación del ente. Usar IDs únicos; ante una operación incierta, consultar el mismo ID y no enviarla otra vez con otro nombre.',
 ('code','& "./motor/python313/python.exe" -I -B -X utf8 "$pi02System/gestionar.py" --system-root $pi02System mente-unificada-estado --vida ECI02_PI02_MAIN'),
 'No usar --nueva, no ejecutar el modo iniciar del entorno sobre una vida ya admitida, no reemplazar un futuro por otro favorable y no promover desde esta ficha. Las verificaciones finales de conservación y reapertura corresponden a la continuación completa y al protocolo de adopción, no a que este comando aparezca en el Manual.',
 'Las fuentes precisas están en archivo/analisis_transversal_cognitivo/PROGRESION_INTEGRADA_02. El protocolo está en control/PROTOCOLO_RESERVA_R02A.json; la revisión exacta ejecutada, en codigo/revisiones/R02B_RESERVA_CONGELADA; los cuatro primarios terminales, en ensayos/PI02_R02A_*_VIVIR.json. El registro lecturas/CONTRASTES/RESULTADO_CIENTIFICO_R02A.json separa ciencia y adopción. RECALCULAR_PI02.py permite verificar RAW, recibos únicos, recursos y referencias con Python estándar, sin motor.',
 'La síntesis AFIRMACIONES_Y_FUENTES.json conserva lectura nueva dirigida y cobertura completa previa reutilizada. El núcleo de evidencia exportado incluye las ocho capturas R01/R02A y dos snapshots diagnósticos para el contraste del observador; no es respaldo operativo completo de la candidata. El ZIP final y sus límites sólo se certifican en el testimonio exterior del contenedor efectivamente verificado.'
])]
RESUME=[
 ('Principal: ECI02_PI01_MAIN', 'Principal operativo: ECI02_PI01_MAIN, N67, T735843, COMMITTED. La candidata experimental ECI02_PI02_MAIN se documenta en el corte A N67, T740343, aún sin adopción. Conservan su genealogía; no se mezclan recuerdos de controles.'),
 ('Abra ABRIR_DEE_COGNITIVE.bat', 'Para el principal use el lanzador y la vida existente, inicialmente pausada. Para la candidata, el capítulo44 da el gestor del laboratorio PI02 con --system-root. No use --nueva ni copie estados sobre una continuación que haya avanzado.'),
 ('T727225 queda protegido', 'PI02A obtuvo10/12 recursos frente7/12 sin valencia,7/12 con sham y0/12 con actuación anulada. La cadencia y el mapa MA/FI siguen preparados. El panel final nuevo y la adopción siguen pendientes en este corte intermedio.'),
 ('El producto conserva aplicación', 'Se requiere snapshot completo, interfaces, agenda, SQLite, recibos, artefactos y progreso. PI01 permanece protegido; la candidata continúa en la copia PI02. El ZIP de análisis no es respaldo operativo. Consulte capítulos43–44 para ayuda, fuentes y límites.')]
COMPENDIUM=[
 'Etapa A ejecutada el8de noviembre de2026. Desde el estado completo PI01 N67,T735843 se continuó una candidata y tres controles de prefijo compartido durante4500ticks por brazo hastaT740343. La candidata ECI02_PI02_MAIN registró67firmas de retorno,12trabajos admitidos,48descartes busy y7retornos tras agotar el banco. MA y FI participaron en el mismo futuro. La principal global aún es PI01 en este corte; esta adición no realiza promoción.',
 'Resultados de reserva:MAIN10/12 recursos,OMIT7/12,SHAM7/12 y actuaciónanulada0/12. Se verificaron archivos reales64bytes y doce respuestas físicas válidas por brazo. MAIN aplicó1100/1100 entradas nuevas(6MA×7,6FI×176,2valencias);OMIT84/84;SHAM85/89 con4rechazos;NULLED1110/1110. Los pulsos de oportunidad SENSOR/NORMALIZER de PI01 fueron0, no las consultas materiales heredadas.',
 'La valencia ligada al fracaso modifica la selección posterior; el primer aporte sham se admite fuera de la ruta y no produce la misma transición. El sham repetido está limitado:5valencias solicitadas,1aplicada y4rechazadas porocupación. No es control total de dosis perfectamente igualada. Las referencias externas separadas dieronWSLS10/12,siempreA7/12,siempreB6/12 yalternancia7/12; MAIN coincide conWSLS en estos casos.',
 'El logro es una reducción acotada de asistencia por oportunidad con solicitudes activadas por retornos físicos. Recurrencia,busy,filtro de flanco,mapaMA/FI,lectores y regla ambiental siguen preparados. No se demostró timing aprendido, exploración abierta, interfaz desconocida adquirida, anticipación, regulación general ni dolor. La conservación completa y reapertura final PI02 están pendientes en esta etapa intermedia.',
 'Fuentes: archivo/analisis_transversal_cognitivo/PROGRESION_INTEGRADA_02/control/PROTOCOLO_RESERVA_R02A.json; codigo/revisiones/R02B_RESERVA_CONGELADA; ensayos/PI02_R02A_*_VIVIR.json; lecturas/CONTRASTES/RESULTADO_CIENTIFICO_R02A.json y código RECALCULAR_PI02.py. Las lecturas nuevas dirigidas conservan las correcciones sobre ECI02C,R04,CORE,Ingeniería06 y cierresOBP, sin sumar recuerdos de otras genealogías.'
]
def sha(data):return hashlib.sha256(data).hexdigest()
def text(p):return ''.join(t.text or''for t in p.iter(W+'t'))
def style(p):
    value=p.find('w:pPr/w:pStyle',NS);return value.get(W+'val','')if value is not None else''
def h1(p):return style(p).lower()in('heading1','ttulo1','titulo1','title1')
def nice(value):
    """Space authored prose only; never touch historical XML, paths, IDs or CLI."""
    protected=[]
    def hold(m):protected.append(m.group());return '\ue000'+str(len(protected)-1)+'\ue001'
    value=re.sub(r'\b[0-9a-f]{64}\b|\S+\.(?:json|docx|md|py|bat|ps1|exe|sqlite3|gz)\b|--?[A-Za-z][A-Za-z0-9_-]*|\b[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]*\b',hold,value)
    value=re.sub(r'(?<=[a-záéíóúñ])(?=\d)|(?<=\d)(?=[a-záéíóúñ]{2,})',' ',value)
    value=re.sub(r'\b(MAIN|OMIT|SHAM|NULLED|WSLS)(?=\d)',r'\1 ',value)
    value=re.sub(r'([,;])(?=\S)',r'\1 ',value)
    value=value.replace('etapaA','etapa A').replace('corteA','corte A').replace('panelPI01','panel PI01').replace('mapaMA/FI','mapa MA/FI').replace('PI01T735843','PI01 T735843').replace('reaperturaPI02','reapertura PI02')
    return re.sub('\ue000([0-9]+)\ue001',lambda m:protected[int(m[1])],value)
def settext(p,value,verbatim=False):
    pp=p.find(W+'pPr');rp=next((deepcopy(r.find(W+'rPr'))for r in p.iter(W+'r')if r.find(W+'rPr')is not None),None)
    for child in list(p):
        if child is not pp and child.tag not in(W+'bookmarkStart',W+'bookmarkEnd'):p.remove(child)
    r=E.SubElement(p,W+'r')
    if rp is not None:r.append(rp)
    t=E.SubElement(r,W+'t');t.set(XML+'space','preserve');t.text=value if verbatim else nice(value)
def para(template,value,code=False):
    p=deepcopy(template)
    for child in list(p):
        if child.tag!=W+'pPr':p.remove(child)
    settext(p,value,verbatim=code)
    r=p.find(W+'r');rp=r.find(W+'rPr')
    if rp is None:rp=E.SubElement(r,W+'rPr');r.remove(rp);r.insert(0,rp)
    color=rp.find(W+'color')
    if color is None:color=E.SubElement(rp,W+'color')
    color.attrib.clear();color.set(W+'val','000000')
    if code:
        fonts=rp.find(W+'rFonts')
        if fonts is None:fonts=E.SubElement(rp,W+'rFonts')
        fonts.set(W+'ascii','Consolas');fonts.set(W+'hAnsi','Consolas')
        size=rp.find(W+'sz')
        if size is None:size=E.SubElement(rp,W+'sz')
        size.set(W+'val','20')
    return p
def insert_bookmark(root,p,name):
    value=max([int(x.get(W+'id'))for x in root.iter(W+'bookmarkStart')]+[20000])+1
    start=E.Element(W+'bookmarkStart');start.set(W+'id',str(value));start.set(W+'name',name);p.insert(1,start)
    end=E.SubElement(p,W+'bookmarkEnd');end.set(W+'id',str(value))
def index_entry(template,label,anchor):
    p=para(template,'');link=E.SubElement(p,W+'hyperlink');link.set(W+'anchor',anchor);r=E.SubElement(link,W+'r');t=E.SubElement(r,W+'t');t.text=label;return p
def table(template):
    rows=[['Brazo','Recursos','Entradas solicitadas / aplicadas','Valencia solicitada / aplicada'],['MAIN','10 / 12','1100 / 1100','2 / 2'],['OMIT','7 / 12','84 / 84','0 / 0'],['SHAM','7 / 12','89 / 85','5 / 1'],['NULLED','0 / 12','1110 / 1110','12 / 12']]
    widths=[1600,1200,3000,2200];tbl=E.Element(W+'tbl');pr=E.SubElement(tbl,W+'tblPr');w=E.SubElement(pr,W+'tblW');w.set(W+'w',str(sum(widths)));w.set(W+'type','dxa');j=E.SubElement(pr,W+'jc');j.set(W+'val','center');layout=E.SubElement(pr,W+'tblLayout');layout.set(W+'type','fixed')
    borders=E.SubElement(pr,W+'tblBorders')
    for side in('top','left','bottom','right','insideH','insideV'):
        b=E.SubElement(borders,W+side);b.set(W+'val','single');b.set(W+'sz','4');b.set(W+'color','D9D9D9')
    margins=E.SubElement(pr,W+'tblCellMar')
    for side in('top','bottom','left','right'):
        m=E.SubElement(margins,W+side);m.set(W+'w','100');m.set(W+'type','dxa')
    grid=E.SubElement(tbl,W+'tblGrid')
    for width in widths:E.SubElement(grid,W+'gridCol').set(W+'w',str(width))
    for index,values in enumerate(rows):
        row=E.SubElement(tbl,W+'tr');trpr=E.SubElement(row,W+'trPr');E.SubElement(trpr,W+'cantSplit')
        if index==0:E.SubElement(trpr,W+'tblHeader')
        for column,value in enumerate(values):
            tc=E.SubElement(row,W+'tc');tcpr=E.SubElement(tc,W+'tcPr');cw=E.SubElement(tcpr,W+'tcW');cw.set(W+'w',str(widths[column]));cw.set(W+'type','dxa');E.SubElement(tcpr,W+'vAlign').set(W+'val','center');shd=E.SubElement(tcpr,W+'shd');shd.set(W+'fill','E6EEF4'if index==0 else('FFFFFF'if index%2 else'F6F8FA'))
            p=para(template,value);pp=p.find(W+'pPr')
            if pp is None:pp=E.Element(W+'pPr');p.insert(0,pp)
            for k in('pageBreakBefore','keepNext'):
                for x in pp.findall(W+k):pp.remove(x)
            E.SubElement(pp,W+'jc').set(W+'val','left'if column==0 else'center');spacing=pp.find(W+'spacing')
            if spacing is None:spacing=E.SubElement(pp,W+'spacing')
            spacing.set(W+'before','40');spacing.set(W+'after','40')
            rp=p.find('w:r/w:rPr',NS)
            if rp is None:rp=E.SubElement(p.find(W+'r'),W+'rPr')
            size=rp.find(W+'sz')
            if size is None:size=E.SubElement(rp,W+'sz')
            size.set(W+'val','20')
            if index==0:E.SubElement(rp,W+'b')
            tc.append(p)
    return tbl
def fields(data):
    root=E.fromstring(data);return [x.text for x in root.iter(W+'instrText')],[dict(x.attrib)for x in root.iter(W+'fldChar')]
def xml(root):return E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
def package(source,target,edits):
    if target.exists():raise ValueError('Preserve prior staged candidate; choose another staging directory')
    target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(source)as old,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED)as new:
        before={}
        for item in old.infolist():
            data=old.read(item.filename);before[item.filename]=sha(data);new.writestr(item,edits.get(item.filename,data))
    with zipfile.ZipFile(target)as z:
        if z.testzip()is not None:raise ValueError('Invalid DOCX ZIP')
        after={name:sha(z.read(name))for name in z.namelist()}
    if set(before)!=set(after):raise ValueError('Unexpected OOXML member-set change')
    changed=[name for name in before if before[name]!=after[name]]
    if not set(changed)<=set(edits):raise ValueError('Unexpected OOXML rewrite')
    return {'source':str(source),'source_sha256':sha(source.read_bytes()),'output':str(target),'bytes':target.stat().st_size,'sha256':sha(target.read_bytes()),'changed_parts':changed,'unchanged_parts':len(before)-len(changed),'member_set_preserved':True}
def preserve(source,folder):
    target=folder/source.name;target.parent.mkdir(parents=True,exist_ok=True);data=source.read_bytes()
    if target.exists()and target.read_bytes()!=data:raise ValueError('Prior preservation copy differs')
    if not target.exists():target.write_bytes(data)
    return {'path':str(target),'bytes':len(data),'sha256':sha(data)}
def main(args):
    if not args.artifact_marker_completed:raise ValueError('Root must complete document edit marker once before authoring')
    if sha(MAN.read_bytes())!=EXPECTED_MAN or sha(COMP.read_bytes())!=EXPECTED_COMP:raise ValueError('Current source changed; reconcile before creating1.28')
    active=json.loads((C/'sistema/estado/ACTIVO.json').read_text(encoding='utf-8-sig'))
    if active['life_id']!='ECI02_PI01_MAIN'or active['tick']!=735843:raise ValueError('Operational principal advanced; do not publish an obsolete continuation description')
    result=json.loads((P/'lecturas/CONTRASTES/recalculo_R02A/RECALCULO_PI02.json').read_text(encoding='utf-8'))
    if result['identity_or_structure_errors']or any(x['inconsistencies']for x in result['R02A']):raise ValueError('Unresolved scientific evidence inconsistency')
    if {x['arm']:x['resources']for x in result['R02A']}!={'real':10,'omit':7,'sham':7,'nulled':0}:raise ValueError('StageA results differ from authored claims')
    staged=args.staging or D/'staging_A_R01'
    if not staged.resolve().is_relative_to(D.resolve()):raise ValueError('Staging must stay under this campaign documentos')
    backups={'Manual':preserve(MAN,D/'respaldo_1_27'),'Compendium':preserve(COMP,D/'respaldo_1_27')}
    with zipfile.ZipFile(MAN)as z:
        root=E.fromstring(z.read('word/document.xml'));body=root.find(W+'body');old=list(body);before={id(e):E.tostring(e)for e in old};allowed=set()
        chapter43=next(p for p in body if p.tag==W+'p'and text(p).startswith('43 Progresión integrada')and h1(p));h2=next(p for p in body if p.tag==W+'p'and text(p).startswith('43.1 '));ordinary=next(p for p in list(body)[list(body).index(chapter43)+2:]if p.tag==W+'p'and len(text(p))>180 and not h1(p)and not text(p).startswith('43.'))
        original_appendix=next(p for p in body if p.tag==W+'p'and text(p)=='Apéndice A. Inventario histórico de las 73 entradas'and h1(p))
        chapter43_elements=old[old.index(chapter43):old.index(original_appendix)]
        for prefix,value in RESUME:
            slots=[p for p in body if p.tag==W+'p'and text(p).startswith(prefix)]
            if len(slots)!=1:raise ValueError('Ambiguous resume slot:'+prefix)
            settext(slots[0],value);allowed.add(id(slots[0]))
        for p in body:
            if p.tag!=W+'p':continue
            t=text(p);value=None
            if t.startswith('DEE thinking 4.5.0 |'):value=t.replace('Edición documental 1.27','Edición documental 1.28')
            elif t.startswith('Edición documental 1.27.'):value='Edición documental 1.28. PI02 etapaA reduce los pulsos de oportunidad: retornos físicos inician trabajos y las consecuencias modifican la selección. MAIN obtuvo10/12 recursos frente7/12 sin valencia,7/12 con sham y0/12 con actuación anulada. La cadencia y el mapa MA/FI siguen preparados. La principal global es PI01T735843; la candidata PI02 se documenta al corteA T740343, sin adopción ni panel final nuevo en esta edición intermedia.'
            elif t.startswith('Los capítulos 1–42 y los apéndices'):value='Los capítulos1–43 y los apéndices conservan sus hechos e identidades históricas. El capítulo44 incorpora los resultados científicos de PI02 etapaA, con asistencia, controles, rechazos y pendientes explícitos. No atribuye los futuros de los controles ni resultados de otras genealogías a la principal.'
            elif 'Su edición vigente 1.27'in t:value=t.replace('Su edición vigente 1.27','Su edición vigente 1.28')
            elif t.startswith('Para retomar, lea el punto inicial'):value='Para retomar, lea el punto inicial y el capítulo44. La principal operativa sigue siendo ECI02_PI01_MAIN,N67,T735843. La candidata ECI02_PI02_MAIN se documenta en el corteA T740343; una continuación posterior acreditada prevalece. El panelPI01 completo fueT735466. PI02 requiere conservación y reapertura finales antes de una adopción, sin copiar recuerdos de controles ni reiniciar el banco agotado.'
            if value is not None:settext(p,value);allowed.add(id(p))
        control=next(t for t in body.findall(W+'tbl')if any(text(row.findall(W+'tc')[0])=='Documento'for row in t.findall(W+'tr')if row.findall(W+'tc')));allowed.add(id(control))
        values={'Documento':'DCS11-MM-001 / Edición documental1.28 / PI02 etapaA / 8 NOV2026','Corte de liberación registrado':'Principal operativo COMMITTED:ECI02_PI01_MAIN,N67,T735843. Candidata experimental:ECI02_PI02_MAIN,corteA T740343. Esta edición no adoptaPI02 ni acredita un panel completo posterior.','Base principal':'Mismo Manual rector y nombre1_21 por compatibilidad. La edición1.27literal y el Compendio anterior quedan preservados en el respaldo documentalPI02 con hashes. El capítulo43 se conserva como historia.','Estado de esta edición':'PI02A:10/12 recursos frente7/12OMIT,7/12SHAM y0/12NULLED. Disparo por retorno y selección local; cadencia,busy ymapaP0. SHAM tiene4rechazos. Conservación yreaperturaPI02finales pendientes.'}
        found=set()
        for row in control.findall(W+'tr'):
            cells=row.findall(W+'tc')
            if len(cells)>=2 and text(cells[0])in values:
                key=text(cells[0]);settext(cells[1].find(W+'p'),values[key]);found.add(key)
        if found!=set(values):raise ValueError('Document-control slots changed')
        appendix=next(p for p in body if p.tag==W+'p'and text(p)=='Apéndice A. Inventario histórico de las 73 entradas'and h1(p))
        chapter44=para(chapter43,TITLE);insert_bookmark(root,chapter44,'PI02_ETAPA_A');appendix.addprevious(chapter44)
        for title,paragraphs in SECTIONS:
            appendix.addprevious(para(h2,title))
            for value in paragraphs:
                if isinstance(value,tuple):appendix.addprevious(para(ordinary,value[1],code=True))
                else:appendix.addprevious(para(ordinary,value))
            if title.startswith('44.3 '):appendix.addprevious(table(ordinary));appendix.addprevious(para(ordinary,'SHAM conserva cuatro rechazos por ocupación; los demás brazos no tuvieron rechazos nuevos. La regla de utilidad se aplica después de la lectura física, no alimenta al decodificador.'))
        index=next(p for p in body if p.tag==W+'p'and text(p).startswith('43 Progresión integrada')and not h1(p));index.addnext(index_entry(index,TITLE,'PI02_ETAPA_A'))
        protected=[]
        for e in old:
            if id(e)not in allowed:
                if e.getparent()is not body or E.tostring(e)!=before[id(e)]:raise ValueError('Unapproved historical body rewrite')
                protected.append(id(e))
        if any(E.tostring(e)!=before[id(e)]for e in chapter43_elements):raise ValueError('Historical chapter43 must remain literal')
        edits={'word/document.xml':xml(root)}
        for name in z.namelist():
            if not re.fullmatch(r'word/(header|footer)\d+\.xml',name):continue
            data=z.read(name);x=E.fromstring(data);changed=False
            for t in x.iter(W+'t'):
                if t.text:
                    new=t.text.replace('ED. 1.27','ED. 1.28').replace('Ed. documental 1.27','Ed. documental 1.28').replace('Progresión PI01','PI02 etapa A');changed=changed or new!=t.text;t.text=new
            candidate=xml(x)
            if fields(data)!=fields(candidate):raise ValueError('Header/footer fields changed')
            if changed:edits[name]=candidate
        settings=E.fromstring(z.read('word/settings.xml'));update=settings.find(W+'updateFields')
        if update is None:update=E.SubElement(settings,W+'updateFields')
        update.set(W+'val','true');edits['word/settings.xml']=xml(settings)
        core=E.fromstring(z.read('docProps/core.xml'));CP='{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}';DC='{http://purl.org/dc/elements/1.1/}';DT='{http://purl.org/dc/terms/}'
        for tag,value in [(DC+'title','DEE Cognitive2.0 Manual Maestro Edición1.28 PI02 etapaA'),(CP+'revision','28'),(DT+'modified',datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'))]:
            child=core.find(tag)
            if child is None:child=E.SubElement(core,tag)
            child.text=value
        edits['docProps/core.xml']=xml(core)
    manual=package(MAN,staged/NAME,edits);manual.update(internal_edition='1.28',source_body_elements=len(old),protected_body_elements_exact=len(protected),editorial_body_elements_changed=len(allowed),chapter43_preserved=True,publication_status='STAGED_ONLY_NOT_CURRENT_MASTER')
    with zipfile.ZipFile(COMP)as z:
        root=E.fromstring(z.read('word/document.xml'));body=root.find(W+'body');old=list(body);before={id(e):E.tostring(e)for e in old};ps=[p for p in body if p.tag==W+'p'];heading=next(p for p in ps if h1(p));ordinary=next(p for p in ps if len(text(p))>180 and not h1(p));sec=body.find(W+'sectPr');new=[]
        title=para(heading,'Actualización PI02 etapa A y selección por retornos físicos');insert_bookmark(root,title,'PI02_A_COMPENDIO');new.append(title)
        new.extend(para(ordinary,value)for value in COMPENDIUM)
        for e in new:
            if sec is not None:sec.addprevious(e)
            else:body.append(e)
        index=next(p for p in ps if text(p).startswith('Actualización PI01')and not h1(p))
        entry=index_entry(index,'Actualización PI02 etapa A y corte experimental T740343','PI02_A_COMPENDIO');index.addnext(entry)
        for e in old:
            if e.getparent()is not body or E.tostring(e)!=before[id(e)]:raise ValueError('Compendium history changed')
        comp=package(COMP,staged/COMP.name,{'word/document.xml':xml(root)});comp.update(source_body_elements=len(old),protected_body_elements_exact=len(old),new_body_elements=len(new)+1,publication_status='STAGED_ONLY_NOT_CURRENT_COMPENDIUM')
    if sha(MAN.read_bytes())!=EXPECTED_MAN or sha(COMP.read_bytes())!=EXPECTED_COMP:raise ValueError('Original source modified during staging')
    report={'schema':'PI02.stageA.editorial-staging.v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'Manual':manual,'Compendium':comp,'literal_prior_documents':backups,'principal_global_unchanged':'ECI02_PI01_MAIN N67T735843 COMMITTED','candidate_cut_documented':'ECI02_PI02_MAIN N67T740343,stageA,not adopted by this document','new_native_ticks':0,'engine_imports':0,'originals_modified':False,'marker':'Root explicitly declared the documents skill edit marker completed before this command','rendering_and_visual_QA':'PENDING; no pagecount or visual approval claimed','scope':'Intermediate stageA edition. Subsequent legitimate candidate continuations require another affected-section update, no rollback.'}
    path=D/'ACTUALIZACION_DOCUMENTAL_PI02_ETAPA_A.json'
    if path.exists():raise ValueError('Prior editorial proof protected; stage with another revision/report name')
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--artifact-marker-completed',action='store_true');parser.add_argument('--staging',type=Path);args=parser.parse_args();main(args)
