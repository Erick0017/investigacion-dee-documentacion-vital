"""Read-only retrospective transport/process autopsy; no Native or replay."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):
            h.update(b)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def write(path,value):
    raw=(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf8')
    with Path(path).open('xb')as f:
        f.write(gzip.compress(raw,mtime=0)if Path(path).suffix=='.gz'else raw)


def raw_fields(value):
    n=int(value)
    if not 0<=n<2**64:
        raise ValueError('RAW must remain exactuint64.')
    return {'state':n&0xffffffff,'semantic':(n>>60)&15,'s_reg':(n>>32)&65535,
            'direction':[((n>>k)&15)-(16 if((n>>k)&15)>=8 else 0)for k in(48,52,56)]}


def current_choice(reader):
    expected={(15+2*x,17,15+2*z):(x,z)for x in(-1,0,1)for z in(0,-1)}
    obs=reader['observations']
    if len(obs)!=6 or{tuple(o['site'])for o in obs}!=set(expected):
        raise ValueError('The archived fixed six-gate reader differs. Do not substitute another reader.')
    candidates=[]
    for o in obs:
        f=raw_fields(o['raw'])
        x,z=expected[tuple(o['site'])]
        if f['state'] and f['semantic']==1 and f['direction']==[x,1,z]:
            candidates.append(x)
    return candidates[0]if len(candidates)==1 else None


def recalculate(export):
    rows=export['requests']
    byid={r['id']:r for r in rows}
    lesson=json.loads(byid['apd04main_prologue_r01_criterion_lesson_A']['result'])['result']['rows'][0]
    frames=lesson['frames']
    first,last=frames[0]['references'],frames[-1]['references']
    def difference(refs):
        if[tuple(r['site'])for r in refs]!=[(14,14,15),(16,14,15)]:
            raise ValueError('The archived fixed reference pair differs.')
        decoded=[raw_fields(r['raw'])for r in refs]
        if any(d['s_reg']!=r['s_reg']for d,r in zip(decoded,refs)):
            raise ValueError('Stored field and exact RAW disagree.')
        return decoded[1]['s_reg']-decoded[0]['s_reg']
    before,after=difference(first),difference(last)
    criterion=json.loads(byid['apd04main_prologue_r01_criterion_19']['payload'])['situaciones'][0]['criterio']
    actual=json.loads(byid['apd04main_prologue_r01_first_new_criterion']['result'])['result']['rows'][0]['rows']
    cases=[]
    for trial in actual:
        native=trial['native_trial']
        value=native['raw_sensor_value']
        choice=current_choice(native['reader'])
        expected=(value>criterion)-(value<criterion)
        cases.append({'value':value,'RAW_decoded_choice':choice,'criterion_environment':criterion,
                      'correct_for_declared_new_criterion':choice==expected,
                      'auditor_expected_not_supplied_to_actor':expected,'read_tick':native['read_tick']})
    planned=export['plan']['events']
    calendar=[]
    for event in planned:
        row=byid.get(event['request_id'])
        calendar.append({'at_seconds':event['at_seconds'],'request_id':event['request_id'],
                         'database_status':None if row is None else row['status'],
                         'submitted_in_archived_SQLite':row is not None,
                         'completed':row is not None and row['status']=='completed'})
    return {'lesson_reference_before':before,'lesson_reference_after':after,'environment_criterion':criterion,
            'lesson_kind':lesson['kind'],'teacher_side':lesson['side_declared_by_teacher'],
            'lesson_receipt':lesson['request']['receipt'],'new_criterion_cases':cases,
            'declared_criterion_correct':sum(r['correct_for_declared_new_criterion']for r in cases),
            'declared_criterion_cases':len(cases),'calendar':calendar,
            'planned_events':len(calendar),'submitted_events':sum(r['submitted_in_archived_SQLite']for r in calendar),
            'completed_events':sum(r['completed']for r in calendar),
            'not_submitted_at500_or_later':all(not r['submitted_in_archived_SQLite']for r in calendar if r['at_seconds']>=500),
            'new_native_ticks':0,'new_owners':0,'replay':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path)
    p.add_argument('--out',type=Path)
    p.add_argument('--recalcular',type=Path)
    p.add_argument('--salida',type=Path)
    a=p.parse_args()
    if a.recalcular:
        export=json.loads(gzip.decompress(a.recalcular.read_bytes()))
        result=recalculate(export)
        write(a.salida,result)
        print(json.dumps(result,ensure_ascii=False))
        return
    root=a.root.resolve(strict=True)
    system=root/'sistema'
    ev=root/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
    attempt=ev/'MAIN_CONTENIDO_Y_CARGA_R01'
    out=a.out.resolve()
    if out.exists():
        raise FileExistsError('Preserve every autopsy edition.')
    journal=system/'estado/servicios_persistentes/APD04_MAIN/cola.sqlite3'
    card_path=system/'estado/vidas/APD04_MAIN/VIDA.json'
    marker_path=card_path.with_name('FUTURO_INTERRUMPIDO.json')
    protected=[journal,card_path,marker_path,system/'estado/ACTIVO.json']
    for suffix in('-wal','-shm'):
        q=journal.with_name(journal.name+suffix)
        if q.exists():
            protected.append(q)
    before={str(q):sha(q)for q in protected}
    with sqlite3.connect(journal.as_uri()+'?mode=ro',uri=True)as con:
        con.row_factory=sqlite3.Row
        schemas={name:[dict(r)for r in con.execute('PRAGMA table_info('+name+')')]for name in('requests','meta')}
        first=con.execute("SELECT MIN(seq) FROM requests WHERE id LIKE 'apd04main_prologue_r01_%'").fetchone()[0]
        rows=[dict(r)for r in con.execute('SELECT * FROM requests WHERE seq>=? ORDER BY seq',(first,))]
        meta={r['key']:r['value']for r in con.execute('SELECT key,value FROM meta')}
        last=[dict(r)for r in con.execute("SELECT seq,id,status,finished_utc FROM requests WHERE status='completed' ORDER BY seq DESC LIMIT 5")]
    if before!={str(q):sha(q)for q in protected}:
        raise ValueError('Read-only sources changed while observed; do not assert one fixed causal cut.')
    for row in rows:
        payload=json.dumps(json.loads(row['payload']),sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)
        if hashlib.sha256(payload.encode('utf8')).hexdigest()!=row['payload_sha']:
            raise ValueError('Archived request payload identity differs: '+row['id'])
    command=read(attempt/'ANTES_DEL_PROCESO.json')['command']
    plan_path=Path(command[command.index('--plan')+1])
    plan=read(plan_path)
    if sha(plan_path)!=read(attempt/'ANTES_DEL_PROCESO.json')['plan_sha256']:
        raise ValueError('Original frozen literal plan changed.')
    export={'schema':'APD04.main_prologue.read_only_SQLite_primary_extraction.v1',
            'query':'SELECT * FROM requests WHERE seq >= first_prologue_seq ORDER BY seq',
            'connection_mode':'mode=ro','journal':str(journal),'journal_sha256':before[str(journal)],
            'schemas':schemas,'requests':rows,'meta':meta,'last_completed':last,'plan':plan,
            'plan_sha256':sha(plan_path),'snapshot_record':read(card_path),'marker':read(marker_path)}
    result=recalculate(export)
    driver=read(attempt/'TRAYECTORIA/RESULTADO.json')
    wrapper=read(attempt/'RESULTADO_SUPERVISION.json')
    pending=[{'id':r['id'],'seq':r['seq'],'status':r['status'],'operation':json.loads(r['payload']).get('operacion')}for r in rows if r['status']in('queued','processing','uncertain')]
    result.update({'driver_error':driver['error'],'driver_stop':driver['stop'],'driver_wall_seconds':driver['driver_wall_seconds'],
                   'native_job_at_driver_exit':driver['final_native_job'],'wrapper_final':wrapper,
                   'pending_transport':pending,'last_committed_tick':export['snapshot_record']['physical']['tick'],
                   'uncommitted_future_possible':export['marker']['uncommitted_native_future_possible'],
                   'normal_continuation_blocked_by_marker':True,
                   'scope':'Transport/host supervision failure with unfinished operation and uncommitted Native future. Not evidence of a cognitive crash, destruction of all memory, P2/R2 or a universal physical limit.'})
    out.mkdir(parents=True)
    write(out/'EXTRACCION_SQLITE_PRIMARIA.json.gz',export)
    write(out/'RECALCULO_N0.json',result)
    originals=[]
    members=[attempt/'ANTES_DEL_PROCESO.json',attempt/'RESULTADO_SUPERVISION.json',attempt/'MUESTRAS_TOTALES_CLASS8.jsonl',
             attempt/'TRAYECTORIA/RESULTADO.json',attempt/'TRAYECTORIA/EVENTOS.jsonl',plan_path,card_path,marker_path]
    for index,path in enumerate(members):
        value=path.read_bytes()
        target=out/(str(index).zfill(2)+'_'+path.name+'.gz')
        with target.open('xb')as f:
            f.write(gzip.compress(value,mtime=0))
        assert gzip.decompress(target.read_bytes())==value
        originals.append({'source':str(path),'source_sha256':sha(path),'source_bytes':len(value),
                          'export':target.name,'export_sha256':sha(target),'compression':'lossless original bytes gzip, not JSON reserialization'})
    shutil.copyfile(__file__,out/Path(__file__).name)
    write(out/'INDICE_PRIMARIOS_Y_LIMITES.json',{'originals':originals,'protected_before':before,
          'protected_after':{str(q):sha(q)for q in protected},'journal_full_remains_local':str(journal),
          'snapshot_full_remains_local':str(system/export['snapshot_record']['snapshot']),
          'same_id_not_requeued':True,'no_main_or_fork_owner_started':True,'new_ticks':0,
          'omitted':'Full SQLite, snapshots, worker artifacts and unrelated historical transport rows stay local. Extraction includes all prologue requests plus later queued controls and complete selected result strings.'})
    explanation=(
        '# Autopsia de supervisión de MAIN\n\n'
        f"Se enviaron {result['submitted_events']} de {result['planned_events']} acontecimientos del plan; {result['completed_events']} constan completados. La petición del desplazamiento390 quedó procesándose. Ningún acontecimiento previsto desde500 se envió; no se evalúan como fallos cognitivos.\n\n"
        f"La experiencia explícita A cambió la diferencia de registros, recalculada desde RAW, de {result['lesson_reference_before']} a {result['lesson_reference_after']}. El entorno se cambió a criterio{result['environment_criterion']}. Para valores20 y18 las salidas fueron negativas: {result['declared_criterion_correct']}/{result['declared_criterion_cases']} cumplen ese criterio ambiental. La enseñanza no ajustó la referencia a19 y no demuestra P2. No se corrigen retrospectivamente estos resultados.\n\n"
        'El driver agotó la espera de la misma petición; STOP no quedó confirmado. Su Job nativo todavía tenía dos procesos activos y consumo CPU registrado al salir. El cierre externo registra después cero procesos. No hay evidencia para llamar a esto un crash cognitivo ni para afirmar la finalización del trabajo pendiente.\n\n'
        'El último snapshot comprometido es T658938. El marcador conserva la posibilidad de futuro nativo no comprometido y bloquea la continuación normal. No se borra el marcador, no se limpian colas, no se repite la petición y no se avanza MAIN. APD04_CONTINUABLE_R01 es una bifurcación explícita desde el par completo T639374, no la reparación de ese futuro.\n\n'
        'El recálculo portable utiliza EXTRACCION_SQLITE_PRIMARIA.json.gz y este script con --recalcular y --salida. Es análisis archivado, no reproducción nativa. Las cadenas SQLite payload/result se preservan completas; sus registros originales y hashes se localizan en el índice.\n')
    with(out/'AUTOPSIA_SUPERVISION_MAIN.md').open('x',encoding='utf8',newline='\n')as f:
        f.write(explanation)
    print(json.dumps({k:result[k]for k in('planned_events','submitted_events','completed_events','not_submitted_at500_or_later','lesson_reference_before','lesson_reference_after','environment_criterion','declared_criterion_correct','declared_criterion_cases','last_committed_tick','new_native_ticks')},ensure_ascii=False))


if __name__=='__main__':
    main()
