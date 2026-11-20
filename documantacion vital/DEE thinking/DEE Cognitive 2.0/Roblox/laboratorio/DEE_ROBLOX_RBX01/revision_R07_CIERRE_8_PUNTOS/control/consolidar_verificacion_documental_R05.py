"""Consolidate the actual passive selector output; no experiment code imports."""
from pathlib import Path
import datetime
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
def read(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8-sig'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
check=read('control/VERIFICACION_SELECTOR_R05_PASIVA.json')
assert check['status']=='CLOSED_SOURCE_SELECTION_CHECKED' and check['verify_only'] is True
assert check['selected_files']==301 and check['Native_calls']==0
assert check['DB_opened'] is False and check['ZIP_created'] is False
assert sum(g['status']=='CLOSED_SOURCE_VERIFIED_NOT_EXPERIMENTALLY_REPRODUCED'for g in check['groups'])==7

readme_path=ROOT/'control/LEER_PRIMERO_V3_TENTATIVO_R01.txt'
readme_path.write_text('''DEE–ROBLOX V3 / R07 — EXPEDIENTE TENTATIVO R05
No es la entrega final ni un respaldo Native ejecutable. No se creó ZIP.

MAIN6 CERRADO
MAIN conserva N67/T1000571, con padre R06/PAR28 T991187 y seis oportunidades
29–34. Fueron 9384 ticks nuevos y 21 operaciones únicas. Eligió ASK/EXIT_1 seis
veces, sin override, y alternó entre 2 y 3. Tres contactos usaron luma positiva
heredada: 8+3=11. No hubo enseñanza, lectura de nara, recurso o entrega nuevos.
Stock final: 152. Los acumulados 3/3 son antiguos. P02 no cumple salida sostenida:
ninguna de las últimas tres posiciones quedó fuera de {2,3}.

CIERRES ADMINISTRATIVOS R06
La lease R06 se aplicó con cero ticks a los seis roles y cambió sólo el testigo
de alcance. CTRL1/PILOT conservaron sus importaciones0 por archivos. Se mantuvo
la proyección N/T/RAW/clocks, junto con política, pending, failure y uncertain.
La recuperación posterior fue separada y sólo afectó a LOAD1/2/3: uncertain
True→False, con los demás campos literales y el fallo original conservado.
El ledger archivó tres rechazos Q2 de cero ticks; consumed siguió en 10452 y
la reserva en 3740 por vida. No hubo reset ni repetición de Q1. El permiso externo
se corrigió de 164 a 163 por la consulta real que ya se había ejecutado.
Ventana aplicada: inicio 16nov15:07UTC; lastnew 17nov08:00UTC; hard 17nov09:07UTC.

REFERENCIAS E5
PROGRAMMED cerró 18/18: dos recursos nuevos, una entrega y ocho enteros correctos
para sus opcodes. En el prefijo común de seis logró 1/1, frente a MAIN 0/0.
Se conservan los dos denominadores. El programa usa estrategia, asociaciones y
aritmética Python preparadas; las ayudas e historias no equivalen a las de Native.
No se establece un ranking general de capacidad o eficiencia.
El rechazo36 fue por falta de prerrequisitos. En41 cambió el signo esperado sobre
la tupla 9/2/1 retenida: el B10 anterior era aritméticamente correcto. Archive43
permitió al programa formar A7/B8 y el contacto46 aceptó8. El segundo recurso no
se entregó dentro del horizonte. No se adquirió la tupla 7/3/2.

CONVENTIONAL_AI fue rechazado antes de abrir World o política: 3333148672 B de RAM
disponibles frente al mínimo 3758096384 B. Hubo cero oportunidades e inferencias;
no son 18 fallos del modelo. El daemon R05 cerró. La infraestructura R06 siguiente
está preparada por archivos, sin resultado incorporado. Root reinició una
herramienta NodeJS antigua, no DEE; no se atribuye un efecto RAM medido.

P07 EN CURSO: SIN FUENTES VIVAS CONGELADAS
La etapa inicial cerró con tres Q1 reales de 356 ticks cada una, T991543 y cero
episodios completos. Q2 fue rechazado antes de pulsos por el permiso no descontado.
El solapamiento común fue 280,405 s de llamadas de pared, incluidos host/checkpoint;
no prueba simultaneidad de instrucciones CPU. Tras la recuperación, Root informó
continuación activa con 2/3 episodios por vida, T994315.
El aviso preliminar de A2 es 8/4/8: LOAD2 usó luma negativa, 6−2=4, tras experience
admitted. LOAD1/3 tuvieron NativePartialAdmission en lesson1. No fusionar LOAD2
con MAIN ni afirmar independencia causal perfecta o cierre 3×3.

P01 SIGUE ABIERTO
Se conservan GDI blanco y CaptureService NoDeviceSupport. La nueva activación
CUA de Main retornó éxito sin inputs/capturas; el probe expuso cliente 1280×648.
DDA_R02 falló por ancho impar1279 en el encoder y dejó cero bytes: se excluye el
MP4 vacío y se conservan stderr/metadatos. R03 corrige ROI par/clamp, sin resultado
validado en este corte. No hay video final válido de tres actuaciones.

P04 / P06 / P08
P04 conserva descriptor PUNTO34_R06 de 5831 miembros, copias críticas parciales
y raíz local completa. No acredita immutable_all_members, rollback autónomo
completo ni uso material posterior útil de MAIN tras reapertura.
P06: 19,4693% frente al umbral20%; cero ticks y testigos iguales. Caché no instalada.
El negativo R01 está incluido completo porque la receta de recursos lo necesita.
P08 incluye conector XML real, mapa y controladores preparados. El editor piloto
cerró con SHA de escena igual y cero Native allí. Falta el episodio real en otro
mapa y la validación externa. No se contactó a desarrolladores.

LECTURA Y REPRODUCCIÓN DOCUMENTAL
1. analisis/INFORME_CIERRE8_R07.md y protocolos prospectivos.
2. MAIN6: analisis/RECALCULO_MAIN6_R01 y sus primarios exactos.
3. E5: analisis/E5_MAIN6_PROGRAMMED18_RECALCULO_R01 y primarios completos.
4. control/RECETA_PORTABLE_E5_R05.json, desde una extracción limpia.
5. RECURSOS_MAIN6_R01 y RECURSOS_MAIN6_Y_P06_R01, con sus recetas existentes.
6. LEASE_R06_TX y RECUPERACION_LOAD_R06_TX: planes previos y resultados.

Plan: control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R05.json, finalized:false.
Registro: control/FUENTES_CERRADAS_EFECTIVAS_R07.json. El selector sólo verifica
archivos explícitos, pins y afirmaciones de cierre. No abre SQLite ni ejecuta DEE,
Studio o modelos. Source absoluto exacto y archive relativo seguro sostienen los
aliases portables. Usar RECALCULO_CIERRE8_R07_R02.py con --package-root y la receta
R05. cerrar_y_recalcular_E5_R06.py es un instrumento local de cierre con checks de
rutas/existencia; no es el punto de entrada portable.

PENDIENTES ANTES DE ENTREGAR
Cierres de MAIN posterior34, CTRL, LOAD3×3, IA y piloto; ámbito P04; revisión de
nuevos bytes y privacidad; protección de los once críticos; freeze de Root;
ZIP Deflate real <=15000000 B; extracción limpia y recálculo documental.
La revisión R03 cubrió 146 miembros: cero candidatos textuales y cinco binarios
sin revisión visual. No se repitió ni certifica los nuevos miembros R05.
Principal PI10, ACTIVO, Manual1.40, v27 y Thinking4.5 permanecen protegidos. No se
duplica otro Manual, pesos, SQLite ni estados Native completos.
''',encoding='utf-8')

path=ROOT/'control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R05.json'
raw=path.read_bytes();plan=json.loads(raw)
plan['closed_source_assembly']=dict(schema='DEE.R07.ClosedSourceSelection.R01',
 utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),groups=check['groups'],
 file_only=True,Native_calls=0,DB_opened=False,ZIP_created=False,
 scientific_or_operational_approval=False,portable_verification=False,
 plan_before_sha256=sha(raw),registry_sha256=sha((ROOT/'control/FUENTES_CERRADAS_EFECTIVAS_R07.json').read_bytes()),
 selector_sha256=sha((ROOT/'control/ensamblar_fuentes_cerradas_v3.py').read_bytes()),
 actual_verify_only_report='control/VERIFICACION_SELECTOR_R05_PASIVA.json',actual_exit_code=0)
for row in plan['files']:
 if Path(row['source'])==readme_path:
  b=readme_path.read_bytes();row.update(bytes=len(b),sha256=sha(b))
for row in plan['recalculations']:
 if row.get('script')=='control/ensamblar_fuentes_cerradas_v3.py':
  row['status']='11previousfixturesnotrerun;actualR05verify_onlyexit0;7closedgroupsand5pending;noZIP'
plan['selected_raw_bytes_at_listing_not_freeze']=sum(r['bytes']for r in plan['files'])
write(path,plan)
cont_path=ROOT/'control/CONTINUIDAD_PAQUETE_PASIVO_R05.json'
cont=json.loads(cont_path.read_text(encoding='utf-8'))
cont['raw_bytes']=plan['selected_raw_bytes_at_listing_not_freeze']
cont['selector_verification']=dict(path='control/VERIFICACION_SELECTOR_R05_PASIVA.json',actual_exit_code=0,
 selected_files=301,closed_groups=7,pending_groups=5,scope='Only explicit paths/pins/closure assertions; no new experiment or recalculation.')
cont['readme_after_final_copyedit_sha256']=sha(readme_path.read_bytes())
cont['final_freeze_still_required']=True
write(cont_path,cont)
print(json.dumps(dict(members=301,raw_bytes=plan['selected_raw_bytes_at_listing_not_freeze'],
 closed_groups=7,pending_groups=5,selector_actual_exit_code=0,finalized=False,ZIP_created=False,
 final_hash_issued=False,portable_clean_extraction_pending=True),ensure_ascii=False))
