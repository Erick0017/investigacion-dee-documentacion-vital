"""Compact exact evidence export; no Native engine import or simulated ticks."""
from pathlib import Path
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
import shutil
import sqlite3

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
S=ROOT/'sistema'
OUT=HERE/'EXPORT_GUI_ESENCIAL_N0_R01'


def sha(data): return hashlib.sha256(data).hexdigest()
def encoded(value): return (json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
def put(name,value):
    data=encoded(value);p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(gzip.compress(data,compresslevel=9,mtime=0) if p.suffix=='.gz' else data)
    return p


def main():
    if OUT.exists(): raise FileExistsError('No overwrite of a sealed export.')
    OUT.mkdir()
    spec=importlib.util.spec_from_file_location('forensic_n0_export',S/'capacidades/observador_causal_retrospectivo_01.py')
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    sources=[]
    def copy(path,relative):
        path=Path(path);data=path.read_bytes();target=OUT/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        sources.append({'source':str(path.relative_to(ROOT)),'sha256':sha(data),'bytes':len(data),'export':relative})
    for name in ['PLAN_GUI_WALK_R01.json','SELECCION_GUI_WALK_R01.json','PLAN_OBSERVADOR_ON_OFF_R01.json',
        'PRUEBA_ATOMIC_REPLACE_N0_R02.json','VERIFICACION_CORTE_GUI_R02_N0_R01.json','RESULTADO_OBSERVADOR_ON_OFF_N0_R01.json']:
        copy(HERE/name,'CALCULOS/'+name)
    # First-process primary request results, including the explicit revision.
    for path in sorted((HERE/'WALK_R01_EJECUTADO').glob('*.json')):
        if path.name.startswith(('04_','05_','06_')):
            outer=json.loads(path.read_bytes());request=outer['job']['result']['request'];body=json.loads(request['result'])
            put('PRIMARIOS_GUI/'+path.name+'.gz',{'source_file':path.name,'source_sha256':sha(path.read_bytes()),
                'transport':{k:v for k,v in request.items() if k!='result'},'native_outbox_result':body})
    copy(HERE/'WALK_R01_EJECUTADO/02_IGUALDAD_RECHAZO_INTERFAZ.json','NEGATIVOS/02_IGUALDAD_RECHAZO_INTERFAZ.json')
    copy(HERE/'WALK_R01_EJECUTADO/ERROR_VISOR_R01.json','NEGATIVOS/ERROR_VISOR_R01.json')
    # All interface events remain exact and losslessly compressed, not only wins.
    for folder in ('WALK_R01_EJECUTADO','WALK_R02_CONTINUACION','WALK_R04_PENDIENTE_CONTINUADO','WALK_R05_IDS_ORIGINALES'):
        path=HERE/folder/'EVENTOS_DRIVER.jsonl'
        data=path.read_bytes();target=OUT/'EVENTOS'/ (folder+'.jsonl.gz');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(gzip.compress(data,compresslevel=9,mtime=0))
        sources.append({'source':str(path.relative_to(ROOT)),'sha256':sha(data),'bytes':len(data),'export':str(target.relative_to(OUT)),'encoding':'gzip_exact_original_bytes'})
    final=HERE/'WALK_R05_IDS_ORIGINALES/CIERRE_IDS_ORIGINALES_R05.json'
    state=json.loads(final.read_bytes())
    put('CONTINUIDAD_GUI_FINAL.json.gz',state)
    # Preserve every decisive instrument traceback byte available.
    for session in sorted((S/'estado/entrada_sencilla/vidas/APD05_GUI_WALK_R01').glob('sesion_*')):
        error=session/'OWNER_STDERR.txt'
        if error.is_file() and error.stat().st_size:copy(error,'NEGATIVOS/'+session.name+'_OWNER_STDERR.txt')
    for condition in ('ON','OFF'):
        life='APD05_GUI_OBS_'+condition+'_R01';card=json.loads((S/'estado/vidas'/life/'VIDA.json').read_bytes())
        snapshot=reader.Snapshot(S/card['snapshot']);common=Counter(snapshot.clocks).most_common(1)[0][0]
        arrays={'schema':'GENESIS.lossless_RAW_clock_extract.R01','N':snapshot.N,'tick':str(snapshot.tick),
            'RAW_sha256':sha(reader.pbytes(snapshot.raw)),'clocks_sha256':sha(reader.pbytes(snapshot.clocks)),
            'raw_default':'0','clock_default':str(common),'rows':[[i,str(v),str(snapshot.clocks[i])]for i,v in enumerate(snapshot.raw)if v],
            'clock_exceptions':[[i,str(v)]for i,v in enumerate(snapshot.clocks)if v!=common]}
        native={'N':snapshot.N,'tick':snapshot.tick,'paused':snapshot.paused,'phase':snapshot.phase,
            'next_event_id':snapshot.next_event_id,'next_sequence':snapshot.next_sequence,'channels':snapshot.channels,
            'pending':snapshot.pending,'receipts':snapshot.receipts}
        put('OBSERVADOR/'+condition+'_RAW_CLOCK.json.gz',arrays)
        put('OBSERVADOR/'+condition+'_AGENDA_RECIBOS.json.gz',native)
        source_path=S/card['snapshot']
        sources.append({'source':str(source_path.relative_to(ROOT)),'sha256':sha(source_path.read_bytes()),'bytes':source_path.stat().st_size,
            'export':['OBSERVADOR/'+condition+'_RAW_CLOCK.json.gz','OBSERVADOR/'+condition+'_AGENDA_RECIBOS.json.gz'],
            'omitted':'Complete snapshot metadata, queues and worker artifacts remain local; these extracts are not a restorable mind.'})
    qpath=S/'estado/servicios_persistentes/APD05_GUI_WALK_R01/cola.sqlite3'
    con=sqlite3.connect('file:'+qpath.as_posix()+'?mode=ro',uri=True);con.row_factory=sqlite3.Row
    pending=dict(con.execute('select * from requests where id=?',('apd05_gui_walk_pending_r01',)).fetchone())
    con.close()
    log=(S/'estado/entrada_sencilla/vidas/APD05_GUI_WALK_R01/SESIONES.jsonl').read_text(encoding='utf8').splitlines()
    events=[json.loads(s)for s in log if s]
    matched=[r for r in events if r.get('id')=='apd05_gui_walk_pending_r01']
    put('CONTINUIDAD_ID_UNICO.json',{'queue_row':pending,'transport_events':matched,
        'material_submissions':sum(r['event']=='literal_material_submission'for r in matched),
        'scope':'One write-ahead submission; subsequent result polls do not re-PUT the task.'})
    # Executed revisions stay separate. Do not replace R01/R02 errors with R05.
    for folder in ['WALK_R01_EJECUTADO/FUENTES_EJECUTADAS','WALK_R02_CONTINUACION/FUENTES_EJECUTADAS_R02',
        'R03_N0_NO_NATIVE_FUENTES','WALK_R04_PENDIENTE_CONTINUADO/FUENTES_EJECUTADAS_R04']:
        for path in sorted((HERE/folder).glob('*')):
            if path.is_file():copy(path,'FUENTES_EJECUTADAS/'+folder.replace('/','__')+'/'+path.name)
    for name in ['recalcular_walk_n0.py','recalcular_observador_on_off_n0.py','exportar_gui_esencial_n0_r01.py',
        'ejecutar_walk_gui_r01.py','continuar_walk_gui_r02.py','continuar_pendiente_r04.py','continuar_ids_ya_encolados_r05.py',
        'ejecutar_observador_fijo_r01_ON_EJECUTADO.py','ejecutar_observador_fijo_r01.py','probar_atomic_replace_n0_r01.py','probar_atomic_replace_n0_r02.py']:
        copy(HERE/name,'CODIGO/'+name)
    copy(S/'capacidades/observador_causal_retrospectivo_01.py','CODIGO/observador_causal_retrospectivo_01.py')
    put('INDICE_ORIGINALES_Y_OMISIONES.json',{'schema':'GENESIS.GUI_essential_source_index.R01','sources':sources,
        'not_a_complete_or_restorable_operational_backup':True,
        'omissions':['Official engine/WHL/PYD','All complete snapshots and SQLite journals','Repeated cumulative API status copies except decisive endpoint/witnesses','Unrelated historical campaigns'],
        'physical_or_actor_files_modified_by_export':False,'native_ticks':0})
    files=[]
    for path in sorted(OUT.rglob('*')):
        if path.is_file():files.append({'file':str(path.relative_to(OUT)).replace('\\','/'),'bytes':path.stat().st_size,'sha256':sha(path.read_bytes())})
    put('MANIFIESTO.json',{'files':files,'native_ticks':0,'expanded_bytes_in_export_files':sum(r['bytes']for r in files)})
    print(json.dumps({'folder':str(OUT),'files':len(files)+1,'bytes':sum(r['bytes']for r in files)},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
