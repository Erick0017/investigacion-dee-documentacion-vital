"""Add actual administrative correction and family status before DOCX authoring."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[1];old=P/'documentos/HECHOS_HITO1_EDICION_1_37_PI09.json';out=P/'documentos/HECHOS_HITO1_EDICION_1_37_PI09_R02.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not out.exists();f=json.loads(old.read_text('utf8'));f['editorial_source_facts']={'path':str(old),'sha256':sha(old)}
names=('CARGA_PREPARADA_PI09_APLICADA_R01.json','CARGA_PREPARADA_PI09_APLICADA_R02.json','PRESERVACION_INTERRUPCION_TRANSPORTE_PI09_R03.json','CONCILIACION_LOCK_PRODUCTO_PI09_R04.json','RP_FAMILIA_INCORPORADA_PI09_R04.json')
for name in names:
 p=P/'control'/name;f['evidence'].append({'path':str(p),'sha256':sha(p)})
f['manual_sections'][8]['paragraphs'].append('La reapertura previa a seleccionar detectó dos defectos administrativos: el transporte confundía ACTIVO con la vida cargada y el primer guard de PREPARED rechazaba controles de pausa y cierre. Se preservaron los intentos. El proceso9308 terminó; Win32 comprobó su ausencia y se copió conjuntamente SQLite/WAL/SHM con hashes originales estables. La corrección R02 validó el payload completo de los cuatro controles y de las tres sesiones de estado. La única petición pendiente se completó por su mismo identificador, sin reenviarla ni purgar la cola. Se conciliaron exclusivamente el lock muerto preservado y sus recibos. La reapertura posterior cerró con igualdad Native y cero ticks: los fallos no se atribuyen a la cognición ni a destrucción del paisaje.')
f['manual_sections'][8]['sources'].append('control/CARGA_PREPARADA_PI09_APLICADA_R01.json y R02; control/PRESERVACION_INTERRUPCION_TRANSPORTE_PI09_R03.json; control/CONCILIACION_LOCK_PRODUCTO_PI09_R04.json; control/REAPERTURA_PRODUCTO_PI09.json')
f['manual_sections'][6]['paragraphs'][1]+=' La receta pi09_consulta_native12_familia_desde_C_R04 ya quedó instalada con335 archivos de código y el mismo prefijo completo compartido. Admite exclusivamente IDs diagnósticos ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_RPF_ seguidos de1..10 letras mayúsculas o dígitos, destino nuevo e identidad no utilizada. Sus requisitos se comprobaron por la CLI sin importar DEE; su primera repetición material sigue pendiente en este corte editorial. La receta R03 y su ejecución real no se reescribieron.'
f['manual_sections'][6]['sources'].append('control/RP_FAMILIA_INCORPORADA_PI09_R04.json; reproducibilidad/recetas/pi09_consulta_native12_familia_desde_C_R04.json')
f['front']['control_table']['Base principal']+=' Suplementos administrativos R01/R02 y recibos rechazados preservados; ninguna alteración de v27 o del cuerpo científico R02.'
f['description']+=' Incluye conciliación de transporte PREPARED y registro de receta familiar R04 aún sin repetición material.'
out.write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'facts':str(out),'sha256':sha(out),'DOCX_authored':False,'Native_executed':False}))
