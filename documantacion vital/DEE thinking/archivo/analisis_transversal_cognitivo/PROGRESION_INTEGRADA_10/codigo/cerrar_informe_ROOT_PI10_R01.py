"""Root editorial closure from already closed records. No Native imports."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re
P=Path(__file__).resolve().parents[1]
path=P/'INFORME_CIENTIFICO.md'
old=path.read_text('utf-8-sig')
backup=P/'control/INFORME_ANTES_CIERRE_ROOT_PI10_R01.md'
if backup.exists(): raise ValueError('Preserve previous closure; never repeat blindly')
backup.write_bytes(path.read_bytes())
summary='''PI10 incorporó una modificación útil y reproducible de la selección de consulta a una continuación física del principal DEE. La vida adoptada es ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01, N67, perfil fisica_directa. Su adopción quedó COMMITTED en T945831 y un uso material posterior por el gestor público, seguido de guardado y reapertura sin ticks, alcanzó T947395. Quedan cuatro de las dieciocho ofertas nuevas. El padre D T922371 permanece preservado; el enlace inmediato es el prefijo neutral P02 T922377. No se fusionaron aprendizajes de controles.

Se prepararon dos trazas físicas dentro del mismo mundo: Q1 recibe una consecuencia genérica de la tarea y Q2 conserva su referencia heredada. La selección del banco afectado sucede mediante la elegibilidad Native, sin una tabla Python que calcule qué banco corregir. El anfitrión conserva decisiones importantes: inicia oportunidades, fija tiempos e interfaces y ordena Q1, acceso, Q2, comparación y actuador. El dato liberado proviene de un registro técnico externo del RAW muestreado nueve ticks antes; no es memoria Native ni una observación fresca.

En doce oportunidades, la candidata obtuvo nueve usos atribuibles y diez entregas físicas de archivos de 64 bytes, frente a ocho y nueve sin retorno punitivo. Las nueve reservas fijadas previamente fueron 9/9 frente a 7/9 para ambas medidas. La diferencia Q1 cambió de cero a menos uno tras un fallo al consultar, y más tarde volvió a cero tras fallar por no consultar. Cambiaron consultas posteriores y su utilidad. Q2 permaneció en menos uno y la comparación FI fue positiva. Tres preguntas materiales menos no ahorraron ticks ni demostraron ahorro energético; se añadieron treinta y tres soportes preparados.

El corte posterior a una primera elección ya formada impidió la actualización Q1 y produjo un recurso de tres; el sham comparable conservó el cambio y produjo dos de tres. Q2 y FI siguieron estables. Esto acredita un enlace local entre traza, transformación y uso posterior. Sin embargo, el retorno desacoplado produjo once usos atribuibles y doce entregas físicas, con la misma reserva 9/9. Su desplazamiento coincidió con fronteras del currículo. Tampoco se superó a la referencia sencilla mantener/cambiar evaluada offline. No se demostró necesidad exclusiva ni superioridad de la contingencia verdadera.

La adquisición se reprodujo materialmente desde el conjunto neutral completo en un ID diagnóstico nuevo. Coincidieron RAW, clocks, interfaces, agenda, recibos y prefijo Native binario; sólo variaron tres metadatos administrativos y de procedencia admitidos. Se conservaron el NULL frío y los errores originales. La repetición verifica reproducibilidad, no independencia estadística. Después, la candidata conservó doce usos anteriores hasta T943970, incluida la cadena real 6+7→13 y 13−5→8, y realizó otro uso útil tras reabrir.

El primer cliente público falló antes de admitir IDs o avanzar Native. Se confirmó y corrigió una ruta de importación, se preservó el intento y se usó un ID nuevo. La prueba pública corregida fue útil. La variante adversa R01 con RAW direccional mixto también permanece preservada. No se obtuvo iniciativa general, planificación descubierta, protección aprendida ni recuperación ilimitada. La ampliación opcional no se ejecutó; el cierre conserva una capacidad local utilizable, su receta, controles y límites.'''
words=len(summary.split())
if not 400<=words<=600: raise ValueError(('summary word count',words))
begin=old.index('## Síntesis científica')
end=old.index('## Estado y procedencia',begin)
text=old[:begin]+'## Síntesis científica\n\n'+summary+'\n\n'+old[end:]
text=text.replace('**Cierre operativo EN CURSO. Corte científico: 11 de noviembre de 2026.**\nLos resultados cerrados se separan de la incorporación aún pendiente. No se\ninfiere autonomía general ni se sustituye una promoción por un informe.', '**Cierre científico y operativo del 11 de noviembre de 2026.**\nAdopción y uso público comprobados; la publicación documental y su calidad\nvisual se identifican en sus comprobantes propios. No se infiere autonomía general.')
text=text.replace('El Manual Word1.38 y la selección D permanecen intactos en este corte. Los\nconstructores de edición1.39 y adopción están sólo preparados. No se anuncia\nincorporación operativa hasta tener ganancia, conservación, controles,\nreapertura y reproducción fría comprobadas.', 'En este corte histórico de cuatro oportunidades todavía se conservaban el Manual1.38 y la selección D. Los requisitos pendientes entonces se completaron posteriormente; el cierre operativo actual se documenta al final. No se atribuye la adopción a aquel corte intermedio.')
text=text.replace('Aún faltan la ablación selectiva si se\nutiliza, conservación, uso posterior\na reapertura y reproducción fría. Por ello esta ventaja no es una promoción\nni prueba de agencia general.', 'La ablación, conservación, reapertura y reproducción fría se completaron posteriormente y se documentan en sus secciones. La ventaja aislada no constituía por sí sola una promoción ni prueba de agencia general.')
text=text.replace('La aplicación real queda para\ncuando termine y cierre el replay.', 'La aplicación real se realizó después del cierre del replay y antes del panel, con cero ticks y comprobación de preservación de tarjeta, snapshot y SQLite.')
text=text.replace('Ninguno ha alterado el\nproducto, el ente ni los dos Word.', 'Los ensambladores no actúan por sí mismos sobre Native. Root aprobó por separado y ejecutó posteriormente el traslado completo y Store.promote; los recibos reales distinguen preparación y COMMITTED.')
text=text.replace('`codigo/pi10_consulta_adaptativa_R01.py` conserva el actor material sellado.', '`codigo/pi10_consulta_adaptativa_R01.py` conserva la variante inicial; el actor evaluado e incorporado es `pi10_consulta_adaptativa_R02.py`, con hash f7ba09cfea3ea93337ead47368ebbd9baba71b8590787aafe4515e6261cedf06.')
s=text.index('## Evaluación, incorporación y continuación')
e=text.index('## Interrupción material de la variante R01',s)
text=text[:s]+'''## Evaluación, incorporación y continuación

La evaluación, sus controles, adquisición fría, conservación, reapertura y adopción ya se ejecutaron. `control/ADOPCION_PRODUCTO_PI10_R02.json` acredita COMMITTED en T945831 mediante el sucesor completo, con cero ticks por traslado/promoción. Se preservó la identidad REAL2 y sólo se actualizó administrativamente el ID actual de C2C; no se trasladó conocimiento desde otra rama. El borrador R01 y los adoptadores preparados no se confunden con ese recibo real.

`control/PI10_PRODUCTO_EP13_OWNER_R02.json` acredita el uso público posterior: T945831→T947395, 1564 ticks, episodio13 útil, 190/190 entradas admitidas, Q1 consulta positiva, dato real cero, Q2 negativo, FI positivo y archivo64B entregado y atribuible. Guardado, cierre y otra reapertura0 preservaron Native completo y stock14/18. La selección sigue en REAL2; la última prueba completa de doce usos es T943970, no T947395.

''' +text[e:]
text+='''
## Conservación y transporte del resultado real

`control/PI10_REAL2_PANEL_OWNER_R01.json` cerró2831ticks, T941139→943970, sin error: cinco asociaciones luma+, nara−, clasifica−, suma+, alfa−; FI temprano positivo/negativo/cero; suma6+7→13; diferencia con el entero13 realmente formado y operando5→8; alfa− y luma+ posteriores. Fueron12/12, no doce conceptos independientes. La señal denominada suma es distinta de la aritmética preparada. El resultado temprano FIzero0 es material válido; su lector histórico q+6 fue NULL. No se sustituyó un lector tras conocer la respuesta. La extracción pasiva independiente se conserva en `control/METRICAS_ADOPCION_CIENTIFICA_PI10_R04.json` y en el recálculo portátil del panel.

`control/PI10_REAL2_REABRIR_OWNER_R01.json` acredita otra oportunidad útil después del panel y reapertura, hastaT945831: previewZ, Query+, Q2+, FI+,190/190 entradas y64B real. `PI10_REAL2_CERO_OWNER_R01.json` acredita la siguiente apertura/estado/guardar/cierre0 y el checkpoint exacto usado al trasladar. No hubo reenseñanza del contenido del panel ni repetición hasta acertar.

## Incidente del cliente público y corrección ejecutada

El primer cliente R04 terminó antes de admisión: `control/PI10_PRODUCTO_EP13_OWNER_R01.json` conserva STOPPED_PRESERVED, propietario cerrado, cero ticks y registros materiales vacíos. La comprobación SQLite y PID encontró integridad, sin WAL/SHM ni solicitudes pendientes, y los tres IDs originales ausentes. No se reenvió una operación incierta. El diagnóstico puro `DIAGNOSTICO_IMPORT_PUBLICO_PI10_R01.json` reprodujo ModuleNotFoundError de capacidades bajo Python aislado: el cliente añadía app al buscador de módulos, pero no sistema. Agregar esa ruta permitió validar el mismo literal sin importar Native.

Root preservó el mutex literal y comprobó la salida real del supervisor y propietario antes de eliminar únicamente ese mutex. `RECONCILIACION_MUTEX_PUBLICO_R04_ROOT_R01.json` documenta esa operación. `REPARACION_CLIENTE_PUBLICO_PI10_R05/APLICACION.json` conserva copia y CAS del cliente: ad721cbabd9ed50235ac0bb1c69add709d0ab394126ee3a216d0068f1da6bfcd→8bf36a67a2683393a81b2c3120dcd588ea73484739ff59eac0e87398e3ca6d96. Sólo cambió una línea de importación; actor, decoder, bancos y leyes permanecieron iguales. La oportunidad con IDnuevo PI10_PUBLIC_EP13_R05_EP13 fue la verificación útil citada arriba. No se restaura un pasado después del fallo.

Antes del corte original se registró `REASIGNACION_PROSPECTIVA_CIERRE_PUBLICO_PI10_R01.json`: diez minutos del cierre se dedicaron exclusivamente a esta corrección y una oportunidad original13, máximo2016ticks y cero mundos nuevos. El plazo total22:23:44UTC no cambió; el cierre quedó con50minutos. La ampliación EXT siguió sin autorización material y no se ejecutó: se conservan sus borradores como preparados, no como fallos de DEE ni resultados experimentales.

## Uso y recuperación con alcance comprobado

Desde la raíz real de DEE Cognitive2.0, `motor\\python313\\python.exe -I -B -X utf8 sistema\\gestionar.py pi10-estado` lee el checkpoint guardado y no inicia Runtime. El comando público material comprobado es `... sistema\\gestionar.py pi10-usar --id ID_NUEVO --esperar 120`; requiere el propietario existente pausado y cola conciliada. Para iniciarlo, el lanzador existente es `ABRIR_DEE_COGNITIVE.bat --sistema --vida ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01`, seguido de Abrir. Esa ruta GUI se contrastó leyendo su código, no se abrió durante PI10. La prueba material se hizo con el mismo propietario publicado y Job512MiB acotado. Guardar y Detener conservan la vida; no usar --nueva.

La reproducción disponible está en `reproducibilidad/reproducir.py`: listar, verificar requisitos y recalcular registros no avanzan Native. `reproducir pi10_consulta12_familia_desde_P02_R02 --variante real12 --vida ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RPF2_IDNUEVO --destino ABSOLUTO_NUEVO --material` exige un ID diagnóstico nuevo y destino vacío; sólo ese modo ejecuta el motor. El prefijo neutral completo y la cápsula de368archivos se preservan bajo reproducibilidad, compartiendo el motor oficial. La receta no está limitada al ID ya consumido. Restaurar ese prefijo sólo reproduce una historia en clon; no repara ni añade experiencias al principal.

El estado final completo se localiza desde `fuentes/MANIFIESTO_ESTADO_PRINCIPAL_FINAL_PI10_R01.json`:5196archivos/406651401bytes en los tres almacenes y checkpoint/ACTIVO, comprobados en dos pasadas sin copiar406MB ni importar Native. El ZIP es de análisis, no un respaldo operativo de esos almacenes. La preservación crítica comprueba D, WHL, PYD y fuente de kernel, no inmutabilidad de todo el proyecto.

## Lectura científica y frontera alcanzada

Se reutilizaron las fuentes y el código de PI09, las síntesis dirigidas de Thinking/CORE/PI01–PI08 y la metrología local; no se repitió un censo ni la lectura integral de todos los manuales. La cobertura distingue texto/código leído, primarios recalculados y nuevas ejecuciones Native. La física conservó influencias que en R01 ayudaron en una oportunidad y después impidieron el codec; eso no acredita por sí solo memoria funcional específica ni ruido universal.

La incorporación es una selección de consulta adquirida local, con interfaces, oportunidades y secuencia externas. El registro RAW se muestrea en(30,40,30) a q1−1 y se libera a q1+8 sólo con el acceso material previsto; tiene nueve ticks de antigüedad. No es lectura fresca ni memoria nativa del registro técnico. No se demostró iniciativa general, descubrimiento de toda la interfaz, superioridad sobre WSLS, regulación global ni consciencia. La mejora concreta sí quedó físicamente adquirida, reproducida, conservada e integrada a un único principal utilizable.
'''
path.write_text(text,'utf-8')
proof={'schema':'DEE.PI10.Root_report_closure.R01','closed_utc':datetime.now(timezone.utc).isoformat(),'summary_words':words,'report_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'backup_sha256':hashlib.sha256(backup.read_bytes()).hexdigest(),'Native':0,'actual_main':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01','N':67,'T':947395,'actual_public_use_proof':'control/PI10_PRODUCTO_EP13_OWNER_R02.json','document_publication_proof':'documentos/PUBLICACION_EDICION_1_39_PI10_R01.json','document_publication_not_inferred_by_this_script':True}
(P/'control/CIERRE_INFORME_ROOT_PI10_R01.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(proof))
