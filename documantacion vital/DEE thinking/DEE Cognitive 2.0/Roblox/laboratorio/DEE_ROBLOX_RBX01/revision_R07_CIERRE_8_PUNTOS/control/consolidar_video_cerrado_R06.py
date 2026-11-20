"""Add exact closed viewer/clip provenance supplied by the passive video owner."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
pins=[
('video/visor_pasivo_npc_R07_R01.client.luau',2757,'7dca2944b7254737793185cb3ec154c355719e8654f715ddfdea730b3d660781'),
('video/visor_pasivo_npc_R07_R02.client.luau',2758,'4f7fc2a01e27511f176e83ac48fc9516e9c2f584ee68e789e68690b81cc4ebb7'),
('control/HANDOFF_CTRL6_R06/09_VIEWER_ACTUAL_RIG_READONLY.json',886,'8da29a20d3c192398a885b5b98958e5b111f93994960575ff93d2bcf8b69116f'),
('video/recorder_eventos_R07_R02.py',12140,'ba8f98732fa64fcfbc70c579de97c0c6e8428f4b2de7e5c98b74bcb954f50226'),
('video/RECORDER_EVENTOS_R07_R02_VERIFICACION_OFFLINE.json',1099,'79224509a2412b897674edb6b6d8c34e31f59fe43b228adbcda669ae36867cd6'),
('video/capturas/CTRL1_SEIS_R06_EVENTOS_R02/PLAN.json',1352,'2d715e3b2512c6fb65a7e98ed95837911b09a406fabeae22333ef966b29639c8'),
('video/capturas/CTRL1_SEIS_R06_EVENTOS_R02/INTENT_01.json',2312,'86cbfcd1fee1af4fbf2725c29c10e58d153519215643dc7a6ceb888b0f35fb68'),
('video/RECORDER_EVENTOS_R07_R03_VERIFICACION_OFFLINE.json',1425,'c40123a9faedefb50bc4cd235ad35434632ae231ff0c90193cbd9c53f5fd9941')]
path=ROOT/'control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R06.json'
plan=json.loads(path.read_text(encoding='utf-8'));assert len(plan['files'])==347 and plan['finalized']is False
names={r['archive'].casefold()for r in plan['files']}
for rel,size,digest in pins:
    source=(ROOT/rel).resolve(strict=True);raw=source.read_bytes()
    assert len(raw)==size and sha(raw)==digest and rel.casefold()not in names
    plan['files'].append(dict(source=str(source),archive=rel,role='code'if rel.endswith(('.py','.luau'))else'protocol',bytes=size,sha256=digest))
    names.add(rel.casefold())
report=ROOT/'analisis/INFORME_CIERRE8_R07.md'
text=report.read_text(encoding='utf-8')
old='''El viewer actúa sólo sobre el cliente/cámara con un offset fijo; se distingue
del motor, lectores y decisión Native. El código del recorder R03 y sus pruebas
offline se transportan como preparación, sin ejecutar otra captura aquí.'''
new='''El clip se generó con recorder R02 y viewer R01. Ambos viewers siguen el
HumanoidRootPart del cuerpo preparado con offset35/28/30 y FOV55, escribiendo
sólo la cámara Client: se distinguen del motor, lectores y decisión Native.
El testigo de lectura acredita viewer R01 activo; viewer R02 cambia sólo
TTL7200→21600. Recorder R03 añade filtros, stop-file entre clips y cierre por
OWNER_CLOSED; sus tres fixtures offline no son captura material. Se transportan
R02 y los preparados R03 sin atribuir a estos últimos la generación del clip.
No se ejecutó otra captura por este curador.'''
assert text.count(old)==1;text=text.replace(old,new,1)
report.write_text(text,encoding='utf-8')
readme=ROOT/'control/LEER_PRIMERO_V3_TENTATIVO_R01.txt'
text=readme.read_text(encoding='utf-8')
old='''El viewer de cliente/cámara y su offset fijo se separan de Native. Se conserva
el código preparado del recorder R03, sin iniciar otra captura en esta curación.'''
new='''El clip usó recorder R02 y viewer R01: offset35/28/30,FOV55, sólo cámara Client.
Viewer R02 sólo amplíaTTL; recorder R03 es preparado y no generó este clip.
Se conservan sus verificaciones offline, sin nueva captura por esta curación.'''
assert text.count(old)==1;readme.write_text(text.replace(old,new,1),encoding='utf-8')
for row in plan['files']:
    if Path(row['source'])in(report,readme):
        raw=Path(row['source']).read_bytes();row.update(bytes=len(raw),sha256=sha(raw))
plan['selected_raw_bytes_at_listing_not_freeze']=sum(r['bytes']for r in plan['files'])
plan['latest_reported_status']['P01_first_original_CTRL_clip']['provenance']=dict(
 recorder='video/recorder_eventos_R07_R02.py',viewer='video/visor_pasivo_npc_R07_R01.client.luau',
 viewer_offset=[35,28,30],viewer_FOV=55,viewer_R02='OnlyTTL7200to21600;prepared',
 recorder_R03='Preparedfilters/stopfile/OWNER_CLOSED;notclipgenerator',
 full_CTRL_journal_and_Native_receipt_crosscheck_pending_control_closure=True)
write(path,plan)
cont_path=ROOT/'control/CONTINUIDAD_PAQUETE_PASIVO_R06.json'
cont=json.loads(cont_path.read_text(encoding='utf-8'))
cont.update(members=len(plan['files']),raw_bytes=plan['selected_raw_bytes_at_listing_not_freeze'])
cont['added_files'] += [rel for rel,_,_ in pins]
cont['video_provenance']=dict(closed_exact_pins_from_passive_video_owner=8,
 actual_R02_recorder_and_R01_viewer_separate_from_R03_prepared=True,
 live_CTRL_EVENTS_not_opened=True,other_clips_not_selected=True)
write(cont_path,cont)
print(json.dumps(dict(members=len(plan['files']),raw_bytes=plan['selected_raw_bytes_at_listing_not_freeze'],
 final_hash_issued=False,finalized=False,ZIP_created=False,video_provenance_added=8),ensure_ascii=False))
