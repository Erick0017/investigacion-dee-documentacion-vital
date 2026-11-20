"""Edición documental local sobre1.6; no importa motor ni avanza ticks."""
import hashlib,json,re,zipfile
from pathlib import Path
from datetime import datetime,timezone
from docx import Document
from docx.shared import RGBColor
from lxml import etree

L=Path(__file__).resolve().parent;R=L.parents[2];E=R/'evidencia/campanas/MENTE_DEE_INTEGRAL_MI01'
src=R/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_6_CICLO02_SIN_VALIDACION_VISUAL.docx'
dst=R/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_7_MI01_SIN_VALIDACION_VISUAL.docx'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original=sha(src);assert original=='8d15cff57b3fb4309877ca335fff6a41c07753776bb0230256694e0c3fcec502'
assert not dst.exists(),'No sobrescribir una revisión ya producida'
d=Document(src)
# La edición1.6 había situado el capítulo23 dentro del índice. Mover sus bytes XML,
# incluidas tablas si las hubiera, sin reescribir la evidencia histórica.
start=next(p for p in d.paragraphs if p.style.name=='Heading 1' and p.text.startswith('23 '))
end=next(p for p in d.paragraphs if p.style.name=='TOCline' and p.text.startswith('Apéndice A'))
anchor=next(p for p in d.paragraphs if p.style.name=='Heading 1' and p.text.startswith('Apéndice A'))
nodes=[];n=start._p
while n is not end._p:
    nodes.append(n);n=n.getnext();assert n is not None
for n in nodes:anchor._p.addprevious(n)
toc23=next(p for p in d.paragraphs if p.style.name=='TOCline' and p.text.startswith('23 '))
tocend=next(p for p in d.paragraphs if p.style.name=='TOCline' and p.text.startswith('Apéndice A'))
tocend.insert_paragraph_before('24 Mente DEE Integral MI01 Desarrollo y evaluación fijada',style='TOCline')
for p in d.paragraphs:
    if 'Edición documental 1.6  |' in p.text:p.text=p.text.replace('Edición documental 1.6','Edición documental 1.7')
    if p.text.startswith('Corte documental actualizado:'):
        p.text='Corte documental actualizado: 22 de octubre de 2026\nPredeterminado protegido: E1_SOCIAL_11, T3154\nInvestigación MI01: E1_MI01_MAIN, T28169; futuro adverso conservado'
    if p.text.startswith('Corte actual de E1_CICLO02_MAIN:'):
        p.text=p.text.replace('Corte actual de','Corte histórico de Ciclo02 de',1)
    if p.text.startswith('La edición original se basó en el resumen funcional'):
        p.add_run(' El capítulo23 conserva Ciclo02 y el capítulo24 incorpora MI01. Los cortes antiguos son históricos; el estado actual de investigación y sus limitaciones se identifican en24 y en la ficha de continuidad vigente.')
table=d.tables[0]
updates={'Documento':'DCS11-MM-001 / Edición documental 1.7','Corte de liberación registrado':'22/10/2026; corte físico MI01 T28169; emisión documental posterior sin nuevos ticks','Base principal':'Edición1.6 preservada; resultados y continuidad de MENTE_DEE_INTEGRAL_MI01','Estado de esta edición':'Word actualizado y estructura comprobada. Validación visual no acreditada; consulte el comprobante editorial.'}
for row in table.rows:
    if row.cells[0].text in updates:row.cells[1].text=updates[row.cells[0].text]
for s in d.sections:
    for area in(s.header,s.footer):
        for p in area.paragraphs:
            for run in p.runs:
                if '1.6' in run.text:run.text=run.text.replace('1.6','1.7')
for name in('Title','Subtitle','Heading 1','Heading 2','Heading 3'):
    st=d.styles[name];st.font.color.rgb=RGBColor(0,0,0)
    if name=='Title':st.font.underline=False
sections=[
('Heading 1','24 Mente DEE Integral MI01 Desarrollo y evaluación fijada'),
('Normal','Conclusión del candidato: capacidades adaptativas especializadas sin integración suficiente. Una sola vida utilizó funciones distintas durante la construcción, pero la configuración fijada no sostuvo el acceso ni actuaciones útiles durante las tres secuencias finales. Esta conclusión no demuestra una imposibilidad general de v27 y no elimina los avances acotados.'),
('Heading 2','Identidad y estado actual'),
('Normal','El padre se fijó antes de evaluar: E1_CICLO02_SEPARACION_TRIPLE_01 T21711, N67. E1_MI01_MAIN es una bifurcación exacta y llegó a T28169, con cero entradas pendientes y su entorno externo persistido. El predeterminado E1_SOCIAL_11 T3154 y el padre permanecieron intactos. No hubo promoción, mezcla de memorias ni sustitución del futuro adverso.'),
('Normal','Se ensayó una organización compuesta y acoplada en un mismo Runtime: soportes adquiridos, selección material, rutas de consulta y participante B. El puente a Pendulum pertenece al instrumento y no es comunicación cerrada v27. Durante la construcción se preparó otro soporte de selección y nuevas rutas mediante entradas legales. Esa anatomía es ingeniería externa; los cambios posteriores de contenido proceden de las experiencias declaradas.'),
('Heading 2','Capacidades utilizadas e incorporadas'),
('Normal','La construcción conservó tres códigos anteriores y utilizó un código nuevo de signo positivo adquirido por interacción con B. Los cuatro estuvieron accesibles después de cuatro usos externos hasta T24190 y después de otras experiencias hasta T24525. Esos cortes contienen su propia agenda, incluido material pendiente; no equivalen al estado final ni a sesenta y cinco significados.'),
('Normal','Una acción fallida produjo material que inició físicamente una solicitud a B dentro de oportunidades preparadas. Omitir o cortar el producto posterior eliminó esa solicitud en controles pertinentes. La iniciativa local es nativa; el circuito, sus ocasiones y suministros siguen preparados. No acredita una política general de búsqueda aprendida ni regulación R2.'),
('Normal','Se incorporó acceso genérico al propio contenido positivo: en T24752 una interacción con recursos no específicos reutilizó el código145 sin aportar de nuevo el docente ni la respuesta privada. El inicio sigue siendo asistido y la historia negativa no mostró la misma recuperación. El número145 es un código físico, no la recuperación del valor privado original ni comprensión del acontecimiento presente.'),
('Normal','Contacto, orden de acontecimientos y una transformación conjunta se utilizaron consecutivamente en MAIN. Los controles de componentes omitidos y orden invertido delimitaron el efecto. La composición es preparada y de consumo finito; no demuestra gramática española productiva. Una consulta material también pudo enseñar, por lo que no se cuenta toda segunda respuesta como retención.'),
('Normal','El gestor existente admite mi01-estado, mi01-experiencia, mi01-continuar, mi01-retorno, mi01-reusar, mi01-vivir y mi01-externo. Son capacidades del sistema dentro de sus contratos. No transfieren automáticamente los conocimientos entre vidas ni convierten cada receta disponible en habilidad de MAIN.'),
('Heading 2','Evaluación fijada y actuación externa'),
('Normal','La preparación, lectores, codec, oportunidades y utilidad se sellaron antes de las tres reservas. La vida continuó sin reparaciones: nueve oportunidades nativas y cuarenta y siete pasos de Pendulum. Hubo una acción material positiva, perjudicial en su contexto, cero contactos útiles, una solicitud nativa por fallo y una respuesta válida de B, pero ninguna utilización final de esa respuesta por el selector. El actuador externo ejecutó una acción no neutral; los otros cuarenta y seis pasos aplicaron el cero obligatorio del puente, no una decisión aprendida de esperar.'),
('Normal','La suma de recompensa externa fue -271.31210209120714. El control de actuador anulado obtuvo -267.76039764518566 desde el mismo prefijo ambiental. Son trayectorias emparejadas, no una estimación general de competencia. El control produjo una diferencia física final de un sitio, con contenido87 frente a92: la acción afectó el entorno y el retorno sensorial afectó DEE, pero no se demostró aprendizaje de una política de control útil.'),
('Normal','De804 solicitudes únicas después de la preparación fijada,173 se aplicaron,613 fueron rechazadas por ocupación y18 por conflicto. Se conservan los rechazos y sus denominadores. La omisión o el retardo del retorno externo no se confunden con reiniciar E1. La interfaz sólo conserva las variables declaradas y su transducción fija; no dispone de un controlador inteligente externo.'),
('Heading 2','Pérdida de acceso y diagnóstico causal acotado'),
('Normal','El primer bloqueo local ocurrió con ocupación global baja. Una respuesta150 se combinó con una contribución188 y cambió de ruta y contenido. Una intervención física preparada y su sham demostraron que era posible rescatar ese tramo, pero no la utilización final. Después apareció otro encuentro que conservó amplitud150 y perdió la dirección requerida. Los recursos del giro habían sido admitidos: admitir una entrada no garantiza que llegue con forma funcional. No se atribuye una procedencia única a toda contribución ni se identifica amplitud conservada con significado conservado.'),
('Normal','El final de MAIN tenía297240 sitios ocupados de300763. Una copia sin entradas recorrió67 intervalos consecutivos con un único RAW y68 configuraciones distintas de clocks. Es estacionariedad RAW finita en ese dominio, no identidad del estado causal completo, muerte, metabolismo ni estabilidad ilimitada. La lectura de los códigos antiguos falló; no se ha probado borrado global de toda su información histórica.'),
('Normal','Las copias de estrés, corte y diagnóstico preservan sus genealogías. Un rescate local posterior a las reservas no se devolvió a MAIN. Los futuros adversos y las variantes especializadas permanecen separados; el ensayo operativo de una especialización produjo un uso motor válido de tres, no una solución sostenida.'),
('Heading 2','Continuar y distinguir los cortes'),
('Normal','Utilice el intérprete exacto ya instalado y el gestor habitual. La ficha CONTINUIDAD_MENTE_DEE_INTEGRAL_MI01.json identifica su ruta, el snapshot completo, hashes, colas, último estado externo y límites. El comando mi01-estado --vida E1_MI01_MAIN informa el estado real. mi01-externo --vida E1_MI01_MAIN --pasos 1 --modo closed --retorno omit --codec-motor native_body_roles --habitat MI01_EVALUACION_FIJADA continúa su futuro adverso sin escoger manualmente una habilidad.'),
('Normal','Los cortes funcionales T24190, T24525 y T24752 son pasados de la misma vida; continuarlos exige una bifurcación nueva explícita con el snapshot exacto. No son reparaciones del presente. Los checkpoints diagnósticos intermedios del puente no se ofrecen como estados operativos completos. El episodio externo MI01 tiene límite200; no se promete una continuación ilimitada ni reinicio implícito del entorno.'),
('Heading 2','Evidencia y límites del cierre'),
('Normal','Fuentes MI01: primarios110–115,193,210–215,220–223,270–283,306–307,314–321,340–348,411–413,440,450–452,460–461,470–490 y495–498; sello previo a reservas; trayectoria original de MAIN; tablas por vida y recálculo portable. El informe y su índice conservan los negativos y distinguen muestras dependientes, reproducción técnica y experiencias nuevas. La comprobación del observador reprodujo exactamente RAW, clocks, interfaces, agenda y recibos.'),
('Normal','No se acreditaron control competente de Pendulum, estrategia general P2/R2, YO/TÚ funcional, aprendizaje de sesenta y cinco primitivas, lenguaje libre ni mente general. El código decisivo de las reservas está sellado y preservado. Existe una laguna de archivo de algunas revisiones tempranas del frontal de comandos, declarada en el índice; no se certifica identidad de bytes de todas esas versiones.'),
('Normal','La edición1.6 y sus fuentes permanecen intactas. Esta edición1.7 corrige el control documental que aún decía1.4, portada, encabezado, pie e índice, traslada el capítulo23 fuera del índice e incorpora24 sin revelar código ni leyes internas del kernel. La comprobación estructural y el intento de render se documentan en CAMBIOS_MANUAL.md. El ZIP de análisis es evidencia compacta, no respaldo autosuficiente de los estados locales.')]
for style,text in sections:
    p=anchor.insert_paragraph_before(text,style=style)
    if style.startswith('Heading'):
        p.paragraph_format.keep_with_next=True
        for run in p.runs:run.font.color.rgb=RGBColor(0,0,0)
    else:p.paragraph_format.widow_control=True
d.core_properties.title='DEE Cognitive System 1.1 Manual maestro de continuidad Edición1.7'
d.core_properties.subject='MI01 Desarrollo y evaluación fijada'
d.core_properties.revision=17
d.save(dst)
assert sha(src)==original
z=zipfile.ZipFile(dst);assert z.testzip() is None
for name in z.namelist():
    if name.endswith('.xml'):etree.fromstring(z.read(name))
dd=Document(dst)
actual=[p.text for p in dd.paragraphs if p.style.name=='Heading 1' and re.match(r'^\d+',p.text)]
numbers=[int(re.match(r'^\d+',t).group())for t in actual]
assert numbers==list(range(1,25)),numbers
assert len([p for p in dd.paragraphs if p.style.name=='TOCline' and p.text.startswith('24 ')])==1
assert all('1.6'not in p.text for s in dd.sections for area in(s.header,s.footer)for p in area.paragraphs)
out={'native_ticks':0,'source':str(src),'source_sha256':original,'original_unchanged':True,'output':str(dst),'output_sha256':sha(dst),'output_bytes':dst.stat().st_size,'actual_chapter_numbers':numbers,'chapter23_moved_out_of_TOC':True,'control_document_version':'1.7','all_XML_parseable':True,'ZIP_CRC_valid':True,'visual_validation':False,'render_attempt_separate':True,'edited_utc':datetime.now(timezone.utc).isoformat()}
(E/'VERIFICACION_WORD_MI01_ESTRUCTURAL.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False,indent=2))
