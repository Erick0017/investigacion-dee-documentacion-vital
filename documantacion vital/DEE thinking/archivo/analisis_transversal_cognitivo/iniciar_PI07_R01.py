"""Establish one PI07 campaign and its fixed resources; no DEE imports/ticks."""
from pathlib import Path
import datetime, hashlib, json, shutil, sqlite3

A = Path(__file__).resolve().parent
R = A.parents[1]
C = R/'DEE Cognitive 2.0'
S = C/'sistema'
P = A/'PROGRESION_INTEGRADA_07'
PROMPT = Path(r'C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\01B8A4CD-29B0-47B2-95B9-0526C92A703C\1-PROMPT_CODEX_DEE_PI07_REGULACION_ADQUIRIDA_Y_DESCUBRIMIENTO.txt')

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if P.exists(): raise FileExistsError('PI07 exists; resume its actual ledger instead of restarting')
    active = read(S/'estado/ACTIVO.json'); life = active['life_id']
    card = read(S/'estado/vidas'/life/'VIDA.json')
    assert life == 'ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
    assert card['physical']['tick'] == active['tick'] == 824911
    assert card['snapshot_sha256'] == active['snapshot_sha256'] == 'af74c8f47e43ed3b2395a338a23a6cbd42f105ec2cff4daac15b7a4d45e90832'
    assert sha(S/card['snapshot']) == card['snapshot_sha256']
    db = S/'estado/servicios_persistentes'/life/'cola.sqlite3'
    assert not any(Path(str(db)+ext).exists() for ext in ('-wal','-shm','-journal'))
    con = sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        meta = dict(con.execute('select key,value from meta'))
        owner = json.loads(meta.get('owner','{}'))
    finally: con.close()
    assert owner.get('running',False) is False
    initial = datetime.datetime.fromisoformat('2026-11-10T07:58:52-06:00')
    fixed = [S/'estado/ACTIVO.json',S/'estado/vidas'/life/'VIDA.json',S/card['snapshot'],
             C/'PROYECTO.json',C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json',
             C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx',
             R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx']
    for sub in ('codigo','control','fuentes','mapas','ensayos','estados','documentos','entrega'):
        (P/sub).mkdir(parents=True,exist_ok=False)
    shutil.copyfile(PROMPT,P/'ENCARGO_PI07.txt')
    data = {'schema':'DEE.PI07.campaign.v1','campaign':'PROGRESION_INTEGRADA_07',
        'started_local':initial.isoformat(),'science_cutoff_local':(initial+datetime.timedelta(hours=4,minutes=10)).isoformat(),
        'hard_stop_local':(initial+datetime.timedelta(hours=5,minutes=30)).isoformat(),
        'budget_fixed_once':True,'budget':{'Native_ticks_all_branches':100000,
            'new_logical_bytes':5500000000,'diagnostic_worlds':14,
            'Native_owner_job_memory_bytes':536870912,'Native_threads':1,'writers_per_world':1,
            'global_anchors':100,'global_delta_frames':2000,'final_ZIP_bytes':15000000},
        'reserved_for_controls_reproduction_conservation':{'worlds':4,'Native_ticks':35000,'logical_bytes':1600000000},
        'source_main':active,'current_card_physical':card['physical'],'owner_journal_at_read':owner,
        'protected_before':{str(p):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in fixed},
        'manual_initial_internal_edition':'1.33','principal_Native_ticks':0,'new_Native_ticks_closed':0,
        'phase':'DIRECTED_REVIEW_AND_FIXED_INTERFACE_FEASIBILITY',
        'system_process_inventory_limit':'Global WMI process read returned access denied; no absence of all processes is claimed. Main-specific closed owner journal, no SQLite auxiliaries and frozen complete pair are used.',
        'disk_D_free_observed_bytes':shutil.disk_usage(C).free,
        'assistance_boundary':'Fixed generic sensor/codec/actuator and environmental opportunities allowed; no threat-dependent repair dispatch, correct answer injection, clock/memory edit, T0 reset or control-history feed to the participant.',
        'creation_Native_ticks':0}
    (P/'REGISTRO_CAMPANA.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    shutil.copyfile(Path(__file__),P/'codigo/iniciar_PI07_R01_exacto.py')
    print(json.dumps({'campaign':str(P),'record':str(P/'REGISTRO_CAMPANA.json'),'Native_ticks':0,
        'owner_pid_recorded':owner.get('pid'),'owner_running':owner.get('running'),'disk_free':data['disk_D_free_observed_bytes']},ensure_ascii=False))

if __name__ == '__main__': main()
