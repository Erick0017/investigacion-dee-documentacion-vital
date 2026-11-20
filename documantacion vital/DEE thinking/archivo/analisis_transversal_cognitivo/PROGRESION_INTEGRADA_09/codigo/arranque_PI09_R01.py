"""Read-only identity and finite new PI09 budget; no DEE import."""
from pathlib import Path
import datetime as dt, hashlib, json, shutil, sqlite3
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema'
TASK=Path(r'C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\977C71AF-6B48-41DB-9DE4-4A8C2C1F1E80\1-PROMPT_CODEX_DEE_PI09_INTEGRACION_CONSULTA_Y_PLASTICIDAD.txt')
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def info(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def main():
 record=P/'REGISTRO_CAMPANA.json'
 if record.exists():raise FileExistsError('Resume existing PI09 without resetting budget')
 for name in ('control','fuentes','mapas','evidencia','estados','documentos','entrega','ensayos','pares'):(P/name).mkdir(exist_ok=True)
 active=read(S/'estado/ACTIVO.json');life=active['life_id'];cp=S/'estado/vidas'/life/'VIDA.json';card=read(cp);snap=S/card['snapshot']
 if sha(snap)!=card['snapshot_sha256'] or active['snapshot_sha256']!=card['snapshot_sha256']:raise ValueError('Snapshot/card/selection disagree')
 db=S/'estado/servicios_persistentes'/card['world_id']/'cola.sqlite3'
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True)
 try:
  con.execute('BEGIN');row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();owner=None if row is None else json.loads(row[0]);statuses=con.execute('SELECT status,COUNT(*) FROM requests GROUP BY status').fetchall()
 finally:con.close()
 stable=not any(status in ('queued','processing','uncertain') and n for status,n in statuses)
 if not stable or (owner or {}).get('running'):raise ValueError('Live or unresolved main transport; preserve and inspect')
 critical=[S/'estado/ACTIVO.json',cp,snap,C/'PROYECTO.json',C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json',S/'estado/genesis/SELECCION_PERSONAL.json',S/'capacidades/CATALOGO_CAPACIDADES.json',C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx',P.parents[2]/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx',S/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl',C/'motor/python313/site-packages/dee_thinking/_native.cp313-win_amd64.pyd',P.parents[2]/'4.5/DEE_thinking_4_5_0/source/src/kernel_v27.cpp']
 now=dt.datetime.now(dt.timezone(dt.timedelta(hours=-6)))
 v={'schema':'DEE.PI09.campaign.R01','campaign':'PROGRESION_INTEGRADA_09','started_local':now.isoformat(),'budget_fixed_once':True,
 'budget':{'hard_stop_local':(now+dt.timedelta(hours=5,minutes=40)).isoformat(),'new_experimental_uses_cutoff_local':(now+dt.timedelta(hours=4,minutes=30)).isoformat(),'Native_ticks_all_branches':220000,'diagnostic_worlds_all_new':12,'additional_logical_bytes_including_delivery':16000000000,'closure_storage_reserved_bytes':1000000000,'owned_Native_job_memory_bytes':536870912,'Native_threads':1,'writers_per_world':1,'global_anchors':120,'global_delta_frames':2400,'final_ZIP_bytes':15000000},
 'source_main':{'selection':active,'life_id':life,'profile':card['profile'],'physical':card['physical'],'parent':card.get('parent'),'snapshot':info(snap),'card':info(cp)},
 'owner_at_inspection':{'cached':owner,'cache_not_instantaneous_observation':True,'queue_status_counts':statuses,'no_unresolved_transport_rows':stable,'auxiliaries':{x:Path(str(db)+x).stat().st_size if Path(str(db)+x).exists()else None for x in ('-wal','-shm')},'life_lock_exists':(S/'estado/locks'/(card['world_id']+'.lock')).exists()},
 'protected_before':{str(p):info(p)for p in critical},'disk_D_free_bytes_at_start':shutil.disk_usage(P).free,
 'priority':'Preserve A; intact B/C descendant; causal information/use tests; adopt bounded gain; only then further exploration.',
 'budget_rationale':'At most twelve full worlds, total220000Native ticks including confirmations and reopen/adoption; C PI08 complete opportunities observed~1564ticks. Reserve~70minutes for documentation/cleanZIP. No whole-corpus inventory. Safety unchanged512MiB one Native owner.',
 'phase':'DIRECTED_PREFLIGHT','Native_ticks_added_by_registration':0,'DEE_imports':0}
 record.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8');(P/'ENCARGO_PI09.txt').write_bytes(TASK.read_bytes())
 print(json.dumps({'record':str(record),'main':life,'N':card['physical']['N'],'T':card['physical']['tick'],'owner_running':(owner or {}).get('running'),'transport_stable':stable,'deadline':v['budget']['hard_stop_local'],'Native_ticks':0},ensure_ascii=False))
if __name__=='__main__':main()
