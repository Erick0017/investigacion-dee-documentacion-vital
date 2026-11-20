"""FS-only complete PAR28 export and independent R07 descendants. No Native load.

Root may prepare copies. import0 is a separate explicit operation. Original R06,
its exhausted epoch, DB, snapshots, resources and code are never modified.
"""
from pathlib import Path,PurePosixPath
import argparse,ast,hashlib,json,os,re,shutil,sqlite3,stat,time
ROOT=Path(__file__).resolve().parents[1];PRODUCT=ROOT.parents[2]
PAIR=ROOT.parent/'revision_R06_INTEGRAL_V2/evidencia/PAR28'
PAIR_SHA='c4638b02ea660f2e32d13c015637e817a28d471e96c3bee0284918f1d55cf2c2'
SOURCE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V2_MAIN'
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_'
SNAPSHOT='b3163197548980355c45c6ffd57d2785b3a5e75cf71d8de3afb6b6ffdd4722d1'
WORLD='48544f655382bdf97b4930200158e35371d878c29d17c1ce918077aa27cf6930'
START=1794841620;LAST=1794859200;END=1794863220
BUNDLE=('rbx07_native_v3.py','rbx07_identity_v3.py','rbx07_funciones_v3.py')
CAPS={'main':24,'control':6,'load':3,'pilot':3}
_checked_directories=set()
def need(v,why):
    if not v:raise ValueError(why)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def new(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def relative(name):
    p=PurePosixPath(name)
    need(isinstance(name,str)and '\\'not in name and ':'not in name and not p.is_absolute()and p.parts and not any(x in('.','..')for x in p.parts),'SAFE_RELATIVE_MEMBER')
    return p
def safe(path):
    p=Path(path).absolute()
    for q in(p,*p.parents):
        if q!=p and q in _checked_directories:continue
        if q.exists()or q.is_symlink():
            s=q.lstat();need(not stat.S_ISLNK(s.st_mode)and not getattr(s,'st_file_attributes',0)&1024,'NO_LINK_REPARSE')
            if stat.S_ISDIR(s.st_mode):_checked_directories.add(q)
    return p
def recheck_directories():
    for p in _checked_directories:
        s=p.lstat();need(stat.S_ISDIR(s.st_mode)and not getattr(s,'st_file_attributes',0)&1024,'DIRECTORY_REPARSE_CHANGED')
def source_record():
    index=PAIR/'PAREJA_INTEGRAL_V2.json';need(sha(index)==PAIR_SHA,'EXACT_FROZEN_PAR28_MANIFEST')
    record=read(index);b=record['boundary'];need(b['life_id']==SOURCE and b['native_tick']==991187 and b['completed_opportunities']==28 and b['next_opportunity']==29,'EXACT_CLOSED_PAR28')
    need(b['last_owner_close']['exit_code']==0 and b['last_owner_close']['final_status']['running']is False,'SOURCE_WRITER_CLOSED')
    rows={x['file']:x for x in record['members']}
    need(len(rows)==len(record['members']),'NO_DUPLICATE_SOURCE_MEMBERS')
    for name in rows:relative(name)
    return record,rows
def copy_checked(src,dst,expected):
    safe(src);safe(dst);need(src.is_file()and src.stat().st_size==expected['bytes'],'SOURCE_FILE_SIZE')
    dst.parent.mkdir(parents=True,exist_ok=True);need(not dst.exists(),'FRESH_DESTINATION_FILE')
    before=src.stat();h=hashlib.sha256()
    with src.open('rb')as i,dst.open('xb')as o:
        for block in iter(lambda:i.read(1048576),b''):h.update(block);o.write(block)
    after=src.stat();need((before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)and h.hexdigest()==expected['sha256']and sha(dst)==expected['sha256'],'SOURCE_OR_COPY_CHANGED')
def shared_export():
    record,rows=source_record();base=ROOT/'persistencia/PREFIJO_PAR28_COMPLETO'
    if base.exists():
        manifest=read(base/'EXPORTACION_SERVICIO.json');need(manifest['snapshot_sha256']==SNAPSHOT and manifest['source_PAR28_manifest_sha256']==PAIR_SHA,'EXACT_EXISTING_SHARED_PREFIX')
        return base,manifest
    base.mkdir(parents=True);system='native_root/sistema/'
    card_rel=system+'estado/vidas/'+SOURCE+'/VIDA.json';card=read(PAIR/card_rel)
    need(sha(PAIR/card_rel)==rows[card_rel]['sha256']and card['snapshot_sha256']==SNAPSHOT,'SOURCE_CARD')
    service=system+'estado/servicios_persistentes/'+SOURCE+'/'
    worker=system+'estado/servicios_locales/'+SOURCE+'/'
    sources=[(system+card['snapshot'],'VIDA.deetsnap.gz')]
    for name,row in rows.items():
        if name.startswith(worker):sources.append((name,'artefactos_trabajador/'+name[len(worker):]))
        elif name.startswith(service):
            suffix=name[len(service):]
            need(suffix!='IMPORTACION_EN_CURSO.json','NO_UNRESOLVED_IMPORT')
            if suffix in('cola.sqlite3-wal','cola.sqlite3-journal'):need(row['bytes']==0,'NO_LIVE_WAL_OR_JOURNAL')
            sources.append((name,suffix))
    members=[]
    for src,rel in sources:
        copy_checked(PAIR/src,base/relative(rel),rows[src]);members.append({'file':rel,'bytes':rows[src]['bytes'],'sha256':rows[src]['sha256']})
    empty=[]
    for directory in record['native_directories']:
        name='native_root/'+directory
        if name.startswith(worker):rel='artefactos_trabajador/'+name[len(worker):]
        elif name.startswith(service):rel=name[len(service):]
        else:continue
        if rel:
            target=base/relative(rel);target.mkdir(parents=True,exist_ok=True)
            if not any(target.iterdir()):empty.append(rel)
    db=base/'cola.sqlite3';con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        need(con.execute('PRAGMA quick_check').fetchone()[0]=='ok','COPIED_CLOSED_QUEUE_INTEGRITY')
        need(con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]==0,'COPIED_QUEUE_NO_AMBIGUOUS_FUTURE')
    finally:con.close()
    manifest={'schema':'DEE.persistent_service.paired_export.v1','life_id':SOURCE,'profile':'fisica_directa','backend':'mente_unificada',
        'native_snapshot':'VIDA.deetsnap.gz','snapshot_sha256':SNAPSHOT,'physical':card['physical'],'members':members,'queue_journal_required':True,
        'source_record':{'life_id':SOURCE,'world_id':SOURCE,'parent':card.get('parent')},'empty_directories_preserved':empty,
        'source_PAR28_manifest_sha256':PAIR_SHA,'source_PAR28_path':str(PAIR),'new_Native_ticks':0,
        'scope':'Current complete closed service export; all worker artifacts and service files retained, original historical PREFIX_DEV4 not redundantly copied. Official runtime/code separately preserved.'}
    new(base/'EXPORTACION_SERVICIO.json',manifest)
    recheck_directories()
    return base,manifest
def prepare(a):
    need(START<=time.time()<LAST,'NEW_PROSPECTIVE_WINDOW_ONLY')
    if a.shared_only:
        p,m=shared_export();return{'prefix':str(p),'members':len(m['members']),'bytes':sum(x['bytes']for x in m['members']),'Native_imports':0}
    need(a.role in CAPS and a.life and a.destination and a.freeze and a.freeze_sha256,'EXPLICIT_PREPARATION_CONTRACT')
    suffix=a.life.removeprefix(PREFIX);need(a.life.startswith(PREFIX)and re.fullmatch(r'MAIN|CTRL[0-9]?|LOAD[123]|PILOT',suffix),'NEW_R07_ID')
    role='main'if suffix=='MAIN'else'control'if suffix.startswith('CTRL')else'load'if suffix.startswith('LOAD')else'pilot'
    need(role==a.role,'ROLE_ID_MISMATCH')
    dest=safe(a.destination);need(dest.parent.resolve()==ROOT/'native'and not dest.exists(),'FRESH_DIRECT_NATIVE_DESTINATION')
    freeze=safe(a.freeze);need(sha(freeze)==a.freeze_sha256,'FROZEN_CODE_HASH');pins=read(freeze)
    need(pins['sealed']is True and pins['native_start_epoch']==START and pins['last_new_episode_epoch']==LAST and pins['native_cutoff_epoch']==END,'SEALED_PROSPECTIVE_SCOPE')
    for name in BUNDLE:need(pins['native_sources_sha256'][name]==sha(ROOT/'native/bundle'/name),'FROZEN_BUNDLE')
    parent,manifest=shared_export();record,rows=source_record();dest.mkdir(parents=True);system=dest/'sistema';system.mkdir()
    for name,row in rows.items():
        prefix='native_root/sistema/'
        if not name.startswith(prefix):continue
        rel=name[len(prefix):]
        if rel.startswith('estado/')or '__pycache__'in PurePosixPath(rel).parts or rel.endswith(('.pyc','.pyo')):continue
        copy_checked(PAIR/name,system/relative(rel),row)
    for folder in('estado/checkpoints','estado/locks'):(system/folder).mkdir(parents=True,exist_ok=True)
    for name in BUNDLE:shutil.copyfile(ROOT/'native/bundle'/name,system/'capacidades'/name)
    changed={}
    for rel in('app/mundo_genesis_apd05.py','app/cola_local.py'):
        p=system/rel;old=sha(p);text=p.read_text('utf-8-sig')
        need('rbx06_native_integral'in text,'KNOWN_R06_APPLICATION_INTEGRATION')
        text=text.replace('rbx06_native_integral','rbx07_native_v3').replace('rbx06_identity_integral','rbx07_identity_v3');ast.parse(text);p.write_text(text,encoding='utf-8');changed[rel]={'before':old,'after':sha(p)}
    transport=system/'capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json';v=read(transport);v['life_id']=a.life;v['role']='rbx01';transport.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    registry=system/'capacidades/PI10_PLUGINS_R01.json';v=read(registry);v['files_sha256'][transport.name]=sha(transport);registry.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    scope={'schema':'DEE.RBX01.fixed_native_scope.INTEGRAL.V3.R01','sealed':True,'life_id':a.life,'role':a.role,'source_life_id':SOURCE,'source_tick':991187,
        'source_snapshot_sha256':SNAPSHOT,'source_pair_manifest_sha256':sha(parent/'EXPORTACION_SERVICIO.json'),'source_PAR28_manifest_sha256':PAIR_SHA,
        'code_scope_manifest_sha256':a.freeze_sha256,'sources_sha256':{n:sha(system/'capacidades'/n)for n in BUNDLE},'sensor_codec':'products_v1',
        'q2_sensor_codec':'price_tag_v1','q2_sensor_arm':a.sensor_arm,'parent_completed_opportunities':28,'parent_native_cycles':24,'parent_last_sequence':56,
        'max_cycles':CAPS[a.role],'max_ticks_per_cycle':4096,'max_total_ticks':CAPS[a.role]*4096,'max_raw_support':10000,'monitor_tick_block':16,'max_permission_stock':200,
        'native_start_utc_epoch':START,'last_new_cycle_utc_epoch':LAST,'native_cutoff_utc_epoch':END,'feedback_arm':'real','teacher_mode':a.teacher_mode,
        'input_codec':{'Q1':'unchanged products_v1','Q2':'one legal datum pulse rawPrice0..2+3*fixed localTag0..5; constant_tag2 control; omission staysNone'},
        'new_offer_not_R06_counter_reset':True,'promotion':False,'raw_clocks_banks_edited':False,'threads':1}
    new(system/'capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json',scope)
    service=ROOT/'native/servicio_eventos_v3.py';shutil.copyfile(service,system/'app'/service.name)
    host={'schema':'DEE.RBX01.INTEGRAL.V3.host_scope.v1','sealed':True,'system':str(system),'life':a.life,'event_driven':True,'single_initial_resume':True,
        'native_cutoff_utc_epoch':END,'immutable_source_cache':True,'host_sources_sha256':{n:sha(system/'app'/n)for n in(service.name,'cache_fuentes_C02.py')},
        'inherited_sources_sha256':{n:sha(system/'app'/n)for n in('servicio_persistente.py','mundo_genesis_apd05.py','cola_local.py','lives.py','process_control.py')},'new_native_ticks_when_idle':0,'threads':1}
    new(system/'app/HOST_INTEGRAL_V3.json',host)
    shutil.copyfile(PAIR/'WORLD_CHECKPOINT.json',dest/'WORLD_PADRE_PAR28.json')
    need(sha(dest/'WORLD_PADRE_PAR28.json')==WORLD,'LITERAL_PARENT_WORLD')
    card_rel='native_root/sistema/estado/vidas/'+SOURCE+'/VIDA.json';shutil.copyfile(PAIR/card_rel,dest/'VIDA_PADRE_PAR28.json')
    context={'schema':'DEE.RBX07.official_import_context.V3.R01','product':str(PRODUCT),'system':str(system),'life':a.life,'prefix':str(parent),
        'prefix_manifest_sha256':sha(parent/'EXPORTACION_SERVICIO.json'),'source_life_id':SOURCE,'source_tick':991187,'source_snapshot_sha256':SNAPSHOT,
        'source_world':str(dest/'WORLD_PADRE_PAR28.json'),'source_world_sha256':WORLD,'source_record':str(dest/'VIDA_PADRE_PAR28.json'),
        'source_code_directory':str(PAIR/'native_root/sistema'),'tool_sources':[{'file':n,'sha256':sha(PRODUCT/'reproducibilidad'/n)}for n in('importar_diagnostico.py','observador_pasivo.py')]}
    new(dest/'CONTEXTO_EJECUCION.json',context)
    proof={'schema':'DEE.RBX07.prepare_closed_PAR28.R01','life':a.life,'parent':SOURCE,'parent_tick':991187,'parent_global_completed':28,
        'R06_cycles24_retained':True,'new_R07_supply':CAPS[a.role],'first_new_sequence_must_exceed':56,'complete_shared_prefix':str(parent),
        'prefix_manifest_sha256':context['prefix_manifest_sha256'],'source_members':len(manifest['members']),'source_bytes':sum(x['bytes']for x in manifest['members']),
        'new_Native_ticks':0,'Native_imported':False,'owner_opened':False,'source_originals_modified':False,'application_changes':changed}
    new(dest/'PREPARACION_PAR28_V3.json',proof);return proof
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--shared-only',action='store_true');p.add_argument('--destination',type=Path);p.add_argument('--life');p.add_argument('--role',choices=CAPS)
    p.add_argument('--freeze',type=Path);p.add_argument('--freeze-sha256');p.add_argument('--sensor-arm',choices=('local_tag','constant_tag2'),default='local_tag');p.add_argument('--teacher-mode',choices=('paired','desync','omitted'),default='paired')
    print(json.dumps(prepare(p.parse_args()),ensure_ascii=False,indent=2))
