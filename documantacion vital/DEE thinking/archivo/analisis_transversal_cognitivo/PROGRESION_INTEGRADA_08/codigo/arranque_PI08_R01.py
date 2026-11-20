"""One bounded read-only continuity check and once-only PI08 registration.
No DEE imports, queries, state restoration, source changes or Native ticks.
"""
from pathlib import Path
import datetime,hashlib,json,sqlite3,shutil,ctypes
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema'
TASK=Path(r'C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\E572791C-A536-402C-BB3E-99907C753380\1-PROMPT_CODEX_DEE_PI08_AVANCE_PLASTICIDAD_Y_CONSOLIDACION.txt')
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def info(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def main():
 record=P/'REGISTRO_CAMPANA.json'
 if record.exists():raise FileExistsError('Resume existing PI08; never restart its budget')
 for d in('control','fuentes','mapas','evidencia','estados','documentos','entrega'): (P/d).mkdir(exist_ok=True)
 active=read(S/'estado/ACTIVO.json');life=active['life_id'];cardpath=S/'estado/vidas'/life/'VIDA.json';card=read(cardpath);snapshot=S/card['snapshot']
 if sha(snapshot)!=card['snapshot_sha256']:raise ValueError('Current snapshot identity mismatch; no experiment authorized by this check')
 db=S/'estado/servicios_persistentes'/card['world_id']/'cola.sqlite3'
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True)
 try:
  con.execute('BEGIN');row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();owner=None if row is None else json.loads(row[0]);statuses=con.execute('SELECT status,COUNT(*) FROM requests GROUP BY status').fetchall()
 finally:con.close()
 critical=[S/'estado/ACTIVO.json',cardpath,snapshot,C/'PROYECTO.json',C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json',S/'estado/genesis/SELECCION_PERSONAL.json',S/'capacidades/CATALOGO_CAPACIDADES.json',C/'reproducibilidad/RECURSOS.json',C/'reproducibilidad/reproducir.py',C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx',P.parents[2]/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx']
 zero_pending=not any(status in('queued','processing','uncertain')and n for status,n in statuses)
 aux={x:Path(str(db)+x).stat().st_size if Path(str(db)+x).exists()else None for x in('-wal','-shm')}
 v={'schema':'DEE.PI08.campaign.v1','campaign':'PROGRESION_INTEGRADA_08','started_local':'2026-11-10T14:08:46-06:00','budget_fixed_once':True,
 'budget':{'hard_stop_local':'2026-11-10T19:48:46-06:00','new_experimental_uses_cutoff_local':'2026-11-10T18:38:46-06:00','A_consolidation_target_local':'2026-11-10T16:38:46-06:00','Native_ticks_all_branches':150000,'diagnostic_worlds_all_new':10,'additional_logical_bytes_including_delivery':12000000000,'closure_storage_reserved_bytes':1000000000,'owned_Native_job_memory_bytes':536870912,'Native_threads':1,'writers_per_world':1,'global_anchors':100,'global_delta_frames':2000,'final_ZIP_bytes':15000000},
 'priority':'A1 atomic valid integration and real RP; A2 adopt a useful complete successor before B/C; then successive revision B; C only if feasible.',
 'source_main':{'selection':active,'life_id':life,'profile':card['profile'],'physical':card['physical'],'parent':card.get('parent'),'snapshot':info(snapshot),'card':info(cardpath)},
 'owner_at_inspection':{'cached':owner,'cache_not_instantaneous_observation':True,'queue_status_counts':statuses,'no_unresolved_transport_rows':zero_pending,'auxiliaries':aux,'life_lock_exists':(S/'estado/locks'/(card['world_id']+'.lock')).exists()},
 'protected_before':{str(f):info(f)for f in critical},'disk_D_free_bytes_at_start':shutil.disk_usage(P).free,
 'complete_historical_prefix_preferred':{'alias':'PI07_R03_POST4_T849645','recipe':'pi07_r03_uso_adquirido_post4_R03','manifest':info(C/'reproducibilidad/materiales/PI07_R03_POST4_T849645/EXPORTACION_SERVICIO.json')},
 'PI07_failed_future':'Preserve unchanged. Do not call T866067 operational merely from RAW/clocks. No restore, queue purge, ID resend, merge or silent repair.',
 'budget_accounting':'All new P8 stores, new C/RP materials, adopted state delta, short QA/staging, final ZIP and every verification extraction count. Existing immutable P7/source materials are shared read-only and not re-copied by default.',
 'Native_ticks_added_by_registration':0,'DEE_imports':0,'phase':'REGISTERED_DIRECTED_PREFLIGHT','registered_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 with record.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
 (P/'ENCARGO_PI08.txt').write_bytes(TASK.read_bytes())
 print(json.dumps({'record':str(record),'sha256':sha(record),'main':life,'N':card['physical']['N'],'T':card['physical']['tick'],'snapshot_matches':True,'cached_owner_running':None if owner is None else owner.get('running'),'no_unresolved_rows':zero_pending,'auxiliaries':aux,'Native_ticks':0},ensure_ascii=False))
if __name__=='__main__':main()
