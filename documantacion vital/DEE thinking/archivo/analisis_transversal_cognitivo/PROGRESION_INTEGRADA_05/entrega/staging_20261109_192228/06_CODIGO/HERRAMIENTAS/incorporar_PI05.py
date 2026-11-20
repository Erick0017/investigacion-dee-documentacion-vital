"""Reasoned complete-state PI05 incorporation through existing Cognitive contracts.

Default is read-only dry-run. --prepare deploys only explicitly approved
Cognitive Python files and imports the final full pair under the explicit PI05 product identity, preserving the source identity in provenance,
without promotion. Root then reopens/closes that product life at zero ticks and
writes the reopening witness. --adopt uses Store.promote and synchronizes the
existing product selectors/catalog/contracts. No phase is executed at import.

No fixed final PI05 tick is assumed; DECISION_FINAL_PI05.json defines the exact
source cut, approved bytes, empirical gates, assistance and allowed losses.
"""
from pathlib import Path,PurePosixPath
import argparse,ast,datetime,hashlib,importlib.util,json,os,shutil,sqlite3,struct,sys

P=Path(__file__).resolve().parent.parent;R=P.parent.parent.parent
C=R/'DEE Cognitive 2.0';S=C/'sistema';CS=P/'estados/candidato/sistema';RP=C/'reproducibilidad'
LIFE='ECI02_PI03_REPRO_PI04_PI05_MAIN_01';SOURCE_LIFE='ECI02_PI03_REPRO_PI04_PI05_GUARD_01';PARENT='ECI02_PI03_MAIN';PARENT_T=775355
PARENT_SHA='5581d3785bf7d7194b5bdb545827aab55f0659d8b3f2c00301425d89616cf07b'
WHEEL_SHA='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
PYD_SHA='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
GATEWAY_SHA='1dad8e7f63303b8584f31a165c9f517141e6c80830b43699adee9e59833fc2f5'
CONTROL=P/'control';BACKUP=CONTROL/'INCORPORACION_RESPALDO_PI05'
PREPARED=CONTROL/'PREPARACION_PRODUCTO_PI05.json'
COMMITTED=CONTROL/'ADOPCION_PRODUCTO_PI05.json'
NATIVE_COMMITTED=CONTROL/'PROMOCION_NATIVE_COMMITTED_PI05.json'
STAGE=CONTROL/'INCORPORACION_EN_CURSO_PI05.json'
CONFIG=CONTROL/'DECISION_FINAL_PI05.json'
INCORPORATOR_ANTECEDENT={'file':'PROGRESION_INTEGRADA_03/codigo/incorporar_PI03.py','sha256':'99ec6af2e63c5565885d2df01500cc70e7058e7ce4042c76fca67ab188806ffa'}
PARSER=R/'archivo/analisis_transversal_cognitivo/PROGRESION_INTEGRADA_01/codigo/PROMOVER_PI01.py'

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def info(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def write(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);temporary=p.with_name(p.name+'.pi05.tmp')
    if temporary.exists():raise FileExistsError('Prior temporary write preserved; inspect:'+str(temporary))
    with temporary.open('x',encoding='utf-8')as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temporary,p)
def safe_relative(value):
    if not isinstance(value,str)or not value or '\\'in value or ':'in value:raise ValueError('Portable relative path required')
    path=PurePosixPath(value)
    if path.is_absolute()or any(x in ('.','..')for x in path.parts):raise ValueError('Unsafe relative path:'+value)
    return path
def checked(path,root,must_exist=True):
    path=Path(path).resolve(strict=must_exist);root=Path(root).resolve(strict=True)
    if not path.is_relative_to(root):raise ValueError('Path outside declared root:'+str(path))
    for part in (path,*path.parents):
        if part==root.parent:break
        if part.exists()and(part.is_symlink()or getattr(part.stat(),'st_file_attributes',0)&1024):raise ValueError('Reparse/link not admitted:'+str(part))
    return path
def copy_new(source,target):
    source=Path(source);target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        if sha(source)!=sha(target):raise FileExistsError('Different preserved bytes:'+str(target))
        return
    with source.open('rb')as a,target.open('xb')as b:shutil.copyfileobj(a,b)
    if sha(source)!=sha(target):raise ValueError('Copy identity mismatch')
def passive_parser():
    spec=importlib.util.spec_from_file_location('pi01_passive_incorporation_parser',PARSER)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def load_decision(path):
    d=read(path)
    required=('approved_for_adoption','life_id','desired_cut','pair','approved_code_files','gates','scope','gains','losses','uncertainties','assistance','evidence','regression_coverage','process_proof','catalog_entry','new_contract','stable_pair_relative_to_product','source_life_id','product_cas_baselines','genealogy_proof')
    if any(key not in d for key in required):raise ValueError('Incomplete final decision; required:'+','.join(required))
    if d['approved_for_adoption']is not True or d['life_id']!=LIFE or d['source_life_id']!=SOURCE_LIFE:raise ValueError('Explicit reasoned approval must identify the actual PI05 MAIN life')
    cut=d['desired_cut']
    if cut.get('N')!=67 or type(cut.get('tick'))is not int or cut['tick']<=PARENT_T or not isinstance(cut.get('snapshot_sha256'),str):raise ValueError('Exact later N67 source cut is required; no guessed final tick')
    for name in ('functional_gain','conservation','reserved_comparisons','combined_function_and_reopening','phase_order_controls','source_reopening','new_function_at_final_cut','decisive_recipe_replay'):
        gate=d['gates'].get(name)
        if not isinstance(gate,dict)or gate.get('satisfied')is not True or not gate.get('criterion')or not gate.get('result')or not gate.get('evidence'):
            raise ValueError('Reasoned satisfied empirical gate required:'+name)
    # Evidence gates refer to already performed experiments; no benchmark or
    # protocol is executed again by this integration helper.
    refs=[item for gate in d['gates'].values()if isinstance(gate,dict)for item in gate.get('evidence',[])]
    refs+=d['evidence']
    for item in refs:
        if not isinstance(item,dict)or not{'path','sha256'}<=set(item):raise ValueError('Evidence descriptors need path and exact SHA-256')
        evidence=checked(item['path'],P)
        if not evidence.is_file()or sha(evidence)!=item['sha256']:raise ValueError('Empirical evidence changed:'+str(evidence))
    return d
def protect_parent(require_selected=True):
    card=read(S/'estado/vidas'/PARENT/'VIDA.json')
    if card['physical']['N']!=67 or card['physical']['tick']!=PARENT_T or card['snapshot_sha256']!=PARENT_SHA or sha(S/card['snapshot'])!=PARENT_SHA:
        raise ValueError('Product principal advanced/changed; reconcile from the new cut, never overwrite it')
    if require_selected:
        if read(S/'estado/ACTIVO.json')['life_id']!=PARENT or read(C/'PROYECTO.json')['selected_life']!=PARENT:
            raise ValueError('Selection changed concurrently; do not promote an outdated candidate')
    return card
def no_writers(decision,include_target=False):
    proof_path=checked(decision['process_proof'],P);proof=read(proof_path)
    stamp=proof.get('recorded_utc');stamp=datetime.datetime.fromisoformat(stamp.replace('Z','+00:00'))if isinstance(stamp,str)else None
    if stamp is None or stamp.tzinfo is None:raise ValueError('Fresh affected-writer proof needs zoned recorded_utc')
    age=(datetime.datetime.now(datetime.timezone.utc)-stamp.astimezone(datetime.timezone.utc)).total_seconds()
    if not 0<=age<=600 or proof.get('no_live_affected_writers')is not True or not proof.get('scope')or not proof.get('evidence'):
        raise ValueError('Fresh explicit no-live-writer proof required; cached running:false alone is insufficient')
    if not{LIFE,SOURCE_LIFE,PARENT}<=set(proof.get('affected_life_ids',[])):raise ValueError('Process proof omits an affected source/target/parent identity')
    targets=[(S,PARENT),(CS,SOURCE_LIFE)]+([(S,LIFE)]if include_target else[])
    owners=[]
    for system,life in targets:
        cardfile=system/'estado/vidas'/life/'VIDA.json'
        if not cardfile.exists():continue
        card=read(cardfile)
        for marker in (system/'estado/locks'/(card['world_id']+'.lock'),cardfile.parent/'FUTURO_INTERRUMPIDO.json',system/'estado/servicios_persistentes'/life/'IMPORTACION_EN_CURSO.json'):
            if marker.exists():raise ValueError('Active lock or interrupted operation preserved:'+str(marker))
        db=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
        if db.exists():
            wal=db.with_name(db.name+'-wal')
            if wal.exists()and wal.stat().st_size:raise ValueError('Nonempty WAL requires live consistency diagnosis; do not copy or assume closed:'+str(db))
            con=sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)
            try:
                row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();owner=None if row is None else json.loads(row[0])
                pending=con.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain')").fetchall()
            finally:con.close()
            if owner and owner.get('running')is True:raise ValueError('Published owner still running; reconcile with exact process before proceeding')
            if pending:raise ValueError('Current operational queue is not closed/conciliated:'+repr(pending))
            owners.append({'system':str(system),'life_id':life,'cached_owner':owner,'pending_transport':pending,'scope':'Historical cache corroborated by fresh process proof and no locks; not an instantaneous world observation'})
    return {'at':now(),'process_proof':info(proof_path),'proof_age_seconds':age,'owner_caches':owners,'world_locks_found':0,'scope':proof['scope']}
def frozen_engine():
    paths=[(S/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl',WHEEL_SHA),(C/'motor/python313/site-packages/dee_thinking/_native.cp313-win_amd64.pyd',PYD_SHA)]
    result=[]
    for path,expected in paths:
        if sha(path)!=expected:raise ValueError('Frozen engine identity differs:'+str(path))
        result.append(info(path))
    return result
def require_official_python():
    expected=(C/'motor/python313/python.exe').resolve(strict=True)
    if sys.implementation.name!='cpython'or sys.version_info[:2]!=(3,13)or struct.calcsize('P')!=8 or Path(sys.executable).resolve()!=expected:
        raise RuntimeError('Native phases require the existing official motor/python313/python.exe. Wrong interpreter rejected before any product write.')
def source_state(d,parser):
    cardfile=CS/'estado/vidas'/SOURCE_LIFE/'VIDA.json';card=read(cardfile);cut=d['desired_cut']
    if card['physical']['N']!=cut['N']or card['physical']['tick']!=cut['tick']or card['snapshot_sha256']!=cut['snapshot_sha256']or sha(CS/card['snapshot'])!=cut['snapshot_sha256']:
        raise ValueError('Candidate advanced/changed since the final decision; do not import an older future')
    genealogy=validate_genealogy(d,card)
    supplied_pair=Path(d['pair']['directory']).absolute()
    if supplied_pair.is_relative_to(P):
        pair=checked(supplied_pair,P)
    else:
        pair=checked(supplied_pair,RP/'materiales')
        direct=d.get('direct_preservation')
        if direct is not None:
            if not isinstance(direct,dict)or not {'path','sha256'}<=set(direct):raise ValueError('Exact direct-RP preservation witness required')
            proof_path=checked(direct['path'],RP/'materiales')
            if sha(proof_path)!=direct['sha256']:raise ValueError('Direct preservation proof changed')
            proof=read(proof_path)
            expected=(RP/'materiales'/('PI03_PI05_FINAL_GUARD_T'+str(cut['tick']))).resolve()
            if pair!=expected or proof.get('schema')!='DEE.PI05.direct_stable_closed_paired_preservation.R03' or proof.get('direct_stable_RP_export')is not True or proof.get('source_files_all_unchanged')is not True or proof.get('Native_executed')is not False or proof.get('new_ticks')!=0:raise ValueError('Only exact completed direct stable final-guard export admitted')
            if Path(proof['destination']).resolve()!=pair or Path(proof['source_system']).resolve()!=CS.resolve()or proof.get('life_id')!=SOURCE_LIFE or proof.get('source_tick')!=cut['tick']or proof.get('snapshot_sha256')!=cut['snapshot_sha256']or proof.get('manifest_sha256')!=d['pair']['manifest_sha256']:raise ValueError('Direct stable pair witness does not match final source')
        else:
            # Historical fallback: a verified closed export may be relocated,
            # never copied again by this helper or confused with an old cut.
            relocation=d.get('pair_relocation')
            if not isinstance(relocation,dict)or not{'path','sha256'}<=set(relocation):raise ValueError('Stable RP source needs direct_preservation or explicit verified relocation')
            relocation_path=checked(relocation['path'],P)
            if sha(relocation_path)!=relocation['sha256']:raise ValueError('Relocation proof changed')
            proof=read(relocation_path)
            if proof.get('schema')!='DEE.PI05.closed_pair_relocation.v1'or proof.get('completed')is not True or proof.get('applied')is not True:raise ValueError('Paired export relocation is not complete')
            if Path(proof['destination']).resolve()!=pair or proof.get('life_id')!=SOURCE_LIFE or proof.get('tick')!=cut['tick']or proof.get('manifest_sha256')!=d['pair']['manifest_sha256']:raise ValueError('Relocation map does not identify this exact final pair')
            origin=Path(proof['source']).absolute();allowed_origin=CS/'estado/servicios_persistentes'/SOURCE_LIFE/'exportaciones'
            if origin.parent!=allowed_origin or origin.exists()or proof.get('original_path_absent')is not True:raise ValueError('Relocation must preserve the exact closed historical export origin')
    manifest=pair/'EXPORTACION_SERVICIO.json';m=read(manifest)
    if sha(manifest)!=d['pair']['manifest_sha256']or m.get('life_id')!=SOURCE_LIFE or m.get('queue_journal_required')is not True:
        raise ValueError('Final complete paired export does not match the decision')
    for key in ('N','tick','RAW_sha256','clocks_sha256'):
        if m['physical'][key]!=card['physical'][key]:raise ValueError('Final pair is not the selected source physical cut')
    exported=parser.snapshot_view(pair/'VIDA.deetsnap.gz');current=parser.snapshot_view(CS/card['snapshot'])
    comparison=parser.compare_native(exported,current,allow_service=True)
    return card,pair,m,exported,comparison
def approved_code(d):
    if not isinstance(d['approved_code_files'],list)or not d['approved_code_files']:raise ValueError('A nonempty approved changed-code list is required')
    items=[];seen=set()
    for item in d['approved_code_files']:
        rel=safe_relative(item['file']);name=rel.as_posix()
        protocol_jsons={'capacidades/'+n for n in ('PROTOCOLO_PI04_C2_R01.json','PROTOCOLO_PI04_C2B_R01.json','PROTOCOLO_PI04_C2C_R01.json','PROTOCOLO_PI05_TRANSITO_R01.json','PROTOCOLO_PI05_GUARDIA_R01.json','PROTOCOLO_PI05_C2C_EXTENSION_R01.json','PROTOCOLO_PI05_C2C_30_R01.json')}
        python_allowed=rel.suffix=='.py'and rel.parts[0]in ('app','capacidades')
        if name=='gestionar.py':raise ValueError('Keep newer tested product gateway; S5 historical gateway must never be deployed')
        protocol_allowed=name in protocol_jsons and rel.suffix=='.json'
        if name in seen or not(python_allowed or protocol_allowed):
            raise ValueError('Only approved Cognitive Python files or the seven exact PI04/PI05 protocol JSONs are admitted:'+name)
        seen.add(name);src=checked(CS/rel,CS);target=checked(S/rel,S,must_exist=False)
        if sha(src)!=item['sha256']:raise ValueError('Approved source code/protocol bytes changed:'+name)
        if python_allowed:ast.parse(src.read_text(encoding='utf-8-sig'))
        else:
            document=read(src)
            if not isinstance(document,dict):raise ValueError('A literal protocol JSON object is required:'+name)
        before=item.get('product_before_sha256')
        if target.exists():
            if before is None or sha(target)!=before:raise ValueError('Product code changed from the approved baseline:'+name)
        elif before is not None:raise ValueError('An expected prior product file is absent:'+name)
        items.append({'file':name,'source':str(src),'target':str(target),'sha256':item['sha256'],'product_before_sha256':before})
    return items
def stable_pair(d):
    # Reuse an ALREADY-preserved full pair under the product reproducibility
    # store. Never create another distribution copy under estado/pares_iniciales.
    rel=safe_relative(d['stable_pair_relative_to_product'])
    path=checked(C/rel,C);root=checked(RP/'materiales',C)
    supplied=Path(d['pair']['directory']).resolve(strict=True)
    if supplied.is_relative_to(root)and path!=supplied:raise ValueError('Direct stable pair is reused at the exact same destination; no second pair copy')
    if not path.is_dir()or path==root or not path.is_relative_to(root):
        raise ValueError('Stable full pair must already exist strictly under product reproducibilidad')
    manifest_path=checked(path/'EXPORTACION_SERVICIO.json',path);manifest=read(manifest_path)
    if sha(manifest_path)!=d['pair']['manifest_sha256']or manifest.get('life_id')!=SOURCE_LIFE or manifest.get('queue_journal_required')is not True:
        raise ValueError('Stable pair manifest differs from the final closed source export')
    if manifest['physical']['N']!=d['desired_cut']['N']or manifest['physical']['tick']!=d['desired_cut']['tick']:
        raise ValueError('Stable pair is not the exact reasoned final cut')
    seen=set();members=[]
    for item in manifest['members']:
        relative=safe_relative(item['file']);name=relative.as_posix()
        if name in seen:raise ValueError('Duplicate stable pair member:'+name)
        seen.add(name);member=checked(path/relative,path)
        if not member.is_file()or member.stat().st_size!=item['bytes']or sha(member)!=item['sha256']:
            raise ValueError('Stable complete pair member missing/changed:'+name)
        members.append({'file':name,'bytes':item['bytes'],'sha256':item['sha256']})
    native_name=safe_relative(manifest['native_snapshot']).as_posix()
    if native_name not in seen or sha(path/native_name)!=manifest['snapshot_sha256']:
        raise ValueError('Stable pair Native snapshot identity is not substantiated by its manifest')
    return path,{'path_relative_to_product':rel.as_posix(),'manifest':info(manifest_path),
                 'members_checked':len(members),'member_bytes':sum(x['bytes']for x in members),
                 'distribution_copy_created':False,'scope':'Already stable full export reused; import still creates the necessary operational life through its existing contract.'}

def existing_catalog_id(d):
    entry=d['catalog_entry']
    if not isinstance(entry,dict)or not isinstance(entry.get('id'),str)or not entry['id'].startswith('PI05'):
        raise ValueError('A bounded PI05 catalog entry with explicit ID is required')
    return entry['id']
def check_json_plans(d):
    contract=d['new_contract'];rel=safe_relative(contract['file'])
    if rel.as_posix()!='contratos/PI05_C2C_USO_PRINCIPAL_01.json'or 'document'not in contract:raise ValueError('Exact PI05 selected-life permission contract required')
    doc=contract['document']
    if not isinstance(doc,dict)or doc.get('schema')!='DEE.PI05.C2C.exact_adopted_permission.v1'or doc.get('life_id')!=LIFE or doc.get('profile')!='fisica_directa'or doc.get('requires_environment30')is not True or doc.get('allowed_modes')!=['eci01-pi04-c2c-oportunidad','eci01-pi04-c2c-estado']:raise ValueError('Bounded exact-life two-mode permission plan required')
    if 'adoption_decision_sha256'in doc:raise ValueError('Permission decision hash is added only after real Native COMMITTED; do not create a circular final-decision hash')
    target=S/rel;before=contract.get('product_before_sha256')
    if target.exists()and(before is None or sha(target)!=before):raise ValueError('New PI05 contract would overwrite unexpected prior bytes')
    for item in d.get('affected_contract_updates',[]):
        rel=safe_relative(item['file'])
        if rel.parts[0]!='contratos'or rel.suffix!='.json'or not isinstance(item.get('updates'),dict):raise ValueError('Bounded affected contract update required')
        if sha(S/rel)!=item['product_before_sha256']:raise ValueError('Affected contract changed before adoption')
    existing_catalog_id(d)

C2C_KEY='DEE.Cognitive.PI04.C2C.coordination.R01'
ORIGIN_C2C_LIFE='ECI02_PI03_REPRO_PI04_MAIN_02'
CAS_REQUIRED={'PROYECTO.json','CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/ACTIVO.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json'}

def check_selector_CAS(d,allow_native_commit=False):
    items=d['product_cas_baselines']
    if not isinstance(items,list)or {x.get('file')for x in items}!=CAS_REQUIRED or len(items)!=len(CAS_REQUIRED):raise ValueError('Exact six product selector/continuity/catalog CAS baselines required')
    checks=[]
    for item in items:
        rel=safe_relative(item['file']);path=checked(C/rel,C)
        if allow_native_commit and rel.as_posix()=='sistema/estado/ACTIVO.json':
            active=read(path)
            if active.get('life_id')!=LIFE:raise ValueError('Committed active selector is not exact PI05 target')
        elif sha(path)!=item['sha256']:
            raise ValueError('Concurrent product selector/document changed; preserve and reconcile before adoption: '+rel.as_posix())
        checks.append(info(path))
    return checks

def validate_genealogy(d,card):
    item=d['genealogy_proof']
    if not isinstance(item,dict)or not {'path','sha256'}<=set(item):raise ValueError('Explicit preserved genealogy witness required')
    path=checked(item['path'],P)
    if sha(path)!=item['sha256']:raise ValueError('Genealogy witness changed')
    g=read(path)
    if g.get('schema')!='DEE.PI05.continuous_candidate_genealogy.v1' or g.get('source_life_id')!=SOURCE_LIFE or g.get('continuous_acquisitions_not_merged')is not True:raise ValueError('Exact continuous candidate provenance required')
    if g.get('physical_parent')!={'life_id':PARENT,'tick':PARENT_T,'snapshot_sha256':PARENT_SHA}:raise ValueError('Genealogy physical parent is not the protected selected PI03 cut')
    if g.get('source_final_cut')!={'N':card['physical']['N'],'tick':card['physical']['tick'],'snapshot_sha256':card['snapshot_sha256']}:raise ValueError('Genealogy witness does not identify the exact final source')
    if not isinstance(g.get('chain'),list)or not g['chain']:raise ValueError('Preserved full-prefix ancestry chain is missing')
    for x in g['chain']:
        q=Path(x['path']).resolve(strict=True)
        if not(q.is_relative_to(P.resolve())or q.is_relative_to(RP.resolve()))or not q.is_file()or sha(q)!=x['sha256']:raise ValueError('Genealogy link unavailable or changed')
    return g

def compare_migration_native(parser,a,b,allow_service=False):
    # Only ONE identity leaf may change in C2C; no whole capability exclusion.
    old=a['metadata'].get(C2C_KEY);new=b['metadata'].get(C2C_KEY)
    if old is None or new is None:raise ValueError('C2C acquired state missing during migration')
    x=json.loads(old);y=json.loads(new)
    if x.get('life_id')!=ORIGIN_C2C_LIFE or y.get('life_id')!=LIFE:raise ValueError('Administrative source/target identity mismatch')
    restored=dict(y,life_id=ORIGIN_C2C_LIFE)
    if restored!=x:raise ValueError('C2C content changed beyond its single administrative life_id leaf')
    normalized=dict(b,metadata=dict(b['metadata']));normalized['metadata'][C2C_KEY]=old
    proof=parser.compare_native(a,normalized,allow_service=allow_service)
    proof['C2C_identity_leaf_only']={'key':C2C_KEY,'field':'life_id','old':ORIGIN_C2C_LIFE,'new':LIFE,'all_other_fields_exact':True}
    return proof

def prepare(d,config_path):
    require_official_python()
    if PREPARED.exists():raise FileExistsError('Preparation already witnessed; do not repeat Native import')
    if STAGE.exists():raise FileExistsError('Prior preparation stage preserved; inspect exact progress instead of blind retry')
    if (S/'estado/vidas'/LIFE).exists()or(S/'estado/servicios_persistentes'/LIFE).exists():raise FileExistsError('Product PI05 identity already exists; never overwrite or mix futures')
    protect_parent();check_selector_CAS(d);writers=no_writers(d);engine=frozen_engine();parser=passive_parser()
    source,pair,manifest,exported,source_comparison=source_state(d,parser);code=approved_code(d);check_json_plans(d)
    localpair,stable_pair_proof=stable_pair(d)
    if any(item.get('id')==existing_catalog_id(d)for item in read(S/'capacidades/CATALOGO_CAPACIDADES.json')['entries']):raise ValueError('PI05 catalog ID already exists')
    backups=['PROYECTO.json','CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/ACTIVO.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json']
    backups+=['sistema/'+item['file']for item in code if item['product_before_sha256']is not None]
    backups+=['sistema/'+item['file']for item in d.get('affected_contract_updates',[])]
    if (S/d['new_contract']['file']).exists():backups.append('sistema/'+d['new_contract']['file'])
    for relative in dict.fromkeys(backups):copy_new(C/relative,BACKUP/relative)
    stage={'schema':'PI05.incorporation.stage.v1','phase':'PREPARING','at':now(),'decision':info(config_path),'source_cut':d['desired_cut'],'approved_code':code,'steps':[]}
    write(STAGE,stage)
    for item in code:
        target=Path(item['target']);target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_name(target.name+'.pi05_deploy_tmp')
        with Path(item['source']).open('rb')as a,tmp.open('xb')as b:shutil.copyfileobj(a,b)
        if sha(tmp)!=item['sha256']:raise ValueError('Code deployment copy differs')
        os.replace(tmp,target);stage['steps'].append({'copied':item['file'],'sha256':item['sha256']});write(STAGE,stage)
    # Source remains closed; the already-stable full pair is verified and
    # reused without a second copy under estado/pares_iniciales (storage budget).
    stage['steps'].append({'stable_pair_reused':stable_pair_proof});write(STAGE,stage)
    no_writers(d);protect_parent();check_selector_CAS(d)
    sys.path[:0]=[str(S),str(S/'app')]
    from app.lives import Store
    from app.importacion_emparejada import import_pair
    store=Store(S);(store.state/'checkpoints').mkdir(parents=True,exist_ok=True)
    imported=import_pair(store,localpair,LIFE)
    identity_adapter=checked(S/'app/pi05_identidad_c2c.py',S)
    approved_adapter=[x for x in code if x['file']=='app/pi05_identidad_c2c.py']
    if len(approved_adapter)!=1 or sha(identity_adapter)!=approved_adapter[0]['sha256']:raise ValueError('Exact approved C2C identity adapter required')
    from app.pi05_identidad_c2c import rebind_imported_C2C_identity
    identity_rebinding=rebind_imported_C2C_identity(store,LIFE,SOURCE_LIFE)
    if not isinstance(identity_rebinding,dict)or identity_rebinding.get('new_ticks')!=0 or identity_rebinding.get('source_life_id')!=SOURCE_LIFE or identity_rebinding.get('target_life_id')!=LIFE or identity_rebinding.get('metadata_old_life_id')!=ORIGIN_C2C_LIFE or identity_rebinding.get('metadata_new_life_id')!=LIFE:raise ValueError('Administrative identity adapter proof is incomplete')
    rec=store.record(LIFE);imported_view=parser.snapshot_view(S/rec['snapshot']);comparison=compare_migration_native(parser,exported,imported_view)
    provenance=store.life_dir(LIFE)/'PROCEDENCIA_PI05_PRODUCTO'
    copy_new(CS/'estado/vidas'/SOURCE_LIFE/'VIDA.json',provenance/'VIDA_FUENTE.json')
    copy_new(CS/'estado/vidas'/SOURCE_LIFE/'HISTORIA.jsonl',provenance/'HISTORIA_FUENTE.jsonl')
    migration={'schema':'PI05.explicit_identity_complete_migration.v1','life_id':LIFE,'source_life_id':SOURCE_LIFE,'source_system':str(CS),'target_system':str(S),'source_tick':d['desired_cut']['tick'],
               'physical_parent':{'life_id':PARENT,'tick':PARENT_T,'snapshot_sha256':PARENT_SHA},'source_original_parent':source.get('parent'),'source_documented_genealogy':read(checked(d['genealogy_proof']['path'],P)),
               'transport_import_parent':rec.get('parent'),'source_record_snapshot_sha256':source['snapshot_sha256'],'exported_transport_snapshot_sha256':manifest['snapshot_sha256'],'imported_snapshot_sha256':rec['snapshot_sha256'],
               'paired_manifest_sha256':sha(localpair/'EXPORTACION_SERVICIO.json'),'comparison':comparison,'administrative_identity_rebinding':identity_rebinding,'same_actual_history_not_memory_merge':True,'new_ticks':0,'at':now()}
    rec['PI05_migration']=migration;rec['PI05_provenance']={'physical_parent_life':PARENT,'physical_parent_tick':PARENT_T,'physical_parent_snapshot_sha256':PARENT_SHA,'source_life_id':SOURCE_LIFE,'genealogy_proof':d['genealogy_proof'],'no_memory_merge':True};write(store.life_dir(LIFE)/'VIDA.json',rec);write(provenance/'MIGRACION.json',migration)
    artifact_checks=0
    for item in manifest['members']:
        name=item['file']
        if name.startswith('artefactos_trabajador/'):target=S/'estado/servicios_locales'/LIFE/Path(name).relative_to('artefactos_trabajador')
        elif name.startswith('resultados/'):target=S/'estado/servicios_persistentes'/LIFE/name
        else:continue
        if sha(target)!=item['sha256']:raise ValueError('Operational artifact/outbox copy differs:'+name)
        artifact_checks+=1
    protect_parent();no_writers(d);check_selector_CAS(d)
    receipt={'schema':'PI05.prepared_product.v1','phase':'PREPARED_NOT_PROMOTED','at':now(),'life_id':LIFE,'decision':info(config_path),'desired_cut':d['desired_cut'],'source_snapshot':info(CS/source['snapshot']),'source_to_export':source_comparison,'stable_pair_reused':stable_pair_proof,'import_result':imported,'migration':migration,'deployed_code':code,'worker_and_outbox_files_verified':artifact_checks,'engine_preserved':engine,'writer_check':writers,'new_ticks':0,'next':'Root performs one affected product reopening at0ticks, validates PI05 operational/environment state, exact transport reconciliation and closes the owner, then supplies the reopening witness for --adopt. No repeated scientific suite.'}
    write(PREPARED,receipt);stage.update(phase='PREPARED_NOT_PROMOTED',completed_at=now(),preparation_proof=str(PREPARED));write(STAGE,stage)
    return receipt
def apply_contracts(d,rec):
    decision_id=d.get('decision_id','PI05_ADOPCION_OPERATIVA_01')
    committed=native_commit_from_journal(decision_id,rec['snapshot_sha256'])
    promotion_decision=CONTROL/'DECISION_PROMOCION_PRODUCTO_PI05.json'
    if committed is None or not promotion_decision.is_file()or read(S/'estado/ACTIVO.json').get('life_id')!=LIFE:raise ValueError('Permission contract may be published only after actual matching Native COMMITTED')
    item=d['new_contract'];path=S/safe_relative(item['file']);document=dict(item['document'])
    document['status']='COMMITTED';document['adoption_decision_sha256']=sha(promotion_decision)
    document['actual_native_commit_witness']=committed
    document['PI05_current_operational_cut']={'life_id':LIFE,'physical':rec['physical'],'snapshot_sha256':rec['snapshot_sha256'],'source_physical_parent':{'life_id':PARENT,'tick':PARENT_T}}
    planned_hash=hashlib.sha256((json.dumps(document,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8')).hexdigest()
    if path.exists()and sha(path)not in (item.get('product_before_sha256'),planned_hash):raise ValueError('PI05 contract changed after preparation; preserve concurrent edit')
    write(path,document);results=[info(path)]
    for item in d.get('affected_contract_updates',[]):
        path=S/safe_relative(item['file']);baseline=BACKUP/'sistema'/item['file']
        if sha(baseline)!=item['product_before_sha256']:raise ValueError('Preserved affected contract baseline differs')
        old=read(baseline)
        # The exact previous file is already backed up. Preserve the overwritten
        # fields inside the current contract too, without rewriting its history.
        old.setdefault('PI05_prior_affected_fields',{})
        for key,value in item['updates'].items():
            if key in old and key not in old['PI05_prior_affected_fields']:old['PI05_prior_affected_fields'][key]=old[key]
            old[key]=value
        old['PI05_current_operational_cut']={'life_id':LIFE,'tick':rec['physical']['tick'],'snapshot_sha256':rec['snapshot_sha256']}
        planned_hash=hashlib.sha256((json.dumps(old,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8')).hexdigest()
        if sha(path)not in (item['product_before_sha256'],planned_hash):raise ValueError('Affected contract changed concurrently; do not overwrite it')
        write(path,old);results.append(info(path))
    return results
def native_commit_from_journal(decision_id,snapshot_hash):
    journal=S/'estado/PROMOCIONES.jsonl'
    if not journal.exists():return None
    for line in reversed(journal.read_text(encoding='utf-8').splitlines()):
        row=json.loads(line)
        if row.get('phase')=='COMMITTED'and row.get('decision_id')==decision_id and row.get('life_id')==LIFE and row.get('snapshot_sha256')==snapshot_hash:return row
    return None
def adopt(d,config_path,reopening_path):
    require_official_python()
    if COMMITTED.exists():raise FileExistsError('PI05 adoption already witnessed; reuse it, do not promote again')
    prepared=read(PREPARED)
    if prepared['decision']['sha256']!=sha(config_path):raise ValueError('Final decision changed after preparation')
    proof=read(reopening_path)
    required=('life_id','new_ticks','physical_unchanged','pending_reconciled','operational_state_valid','owner_closed','snapshot_sha256')
    if any(key not in proof for key in required)or proof['life_id']!=LIFE or proof['new_ticks']!=0 or any(proof[key]is not True for key in ('physical_unchanged','pending_reconciled','operational_state_valid','owner_closed')):
        raise ValueError('Explicit product reopening0tick witness is incomplete; no functional experiments repeated by this script')
    protect_parent(require_selected=False);writers=no_writers(d,include_target=True);engine=frozen_engine();parser=passive_parser()
    source,pair,manifest,exported,source_comparison=source_state(d,parser)
    localpair,stable_pair_proof=stable_pair(d)
    target_card=read(S/'estado/vidas'/LIFE/'VIDA.json')
    if target_card['physical']['tick']!=d['desired_cut']['tick']or target_card['snapshot_sha256']!=proof['snapshot_sha256']:
        raise ValueError('Product life changed after its reopening witness; do not adopt another cut silently')
    current_view=parser.snapshot_view(S/target_card['snapshot']);comparison=compare_migration_native(parser,exported,current_view,allow_service=True)
    for item in prepared['deployed_code']:
        if sha(S/item['file'])!=item['sha256']or sha(CS/item['file'])!=item['sha256']:raise ValueError('Approved code changed after product preparation')
    decision_id=d.get('decision_id','PI05_ADOPCION_OPERATIVA_01')
    decision_path=CONTROL/'DECISION_PROMOCION_PRODUCTO_PI05.json'
    reasoned={key:d[key]for key in ('scope','gains','losses','uncertainties','evidence','regression_coverage')}
    reasoned.update(decision_id=decision_id,route='COMPATIBLE',life_id=LIFE,snapshot_sha256=target_card['snapshot_sha256'],source_decision=info(config_path),reopening_proof=info(reopening_path),lineage=target_card.get('PI05_migration'),at=now())
    # Resume metadata after a proven COMMITTED journal entry, never rerun the
    # Native promotion if a connection broke between it and JSON synchronization.
    committed_row=native_commit_from_journal(decision_id,target_card['snapshot_sha256'])
    active=read(S/'estado/ACTIVO.json')
    if committed_row:
        check_selector_CAS(d,allow_native_commit=True)
        if active['life_id']!=LIFE or active['snapshot_sha256']!=target_card['snapshot_sha256']:raise ValueError('Promotion journal/active pointer disagree; preserve and diagnose')
        result={'reused_existing_COMMITTED_journal':committed_row,'Native_promotion_not_repeated':True}
    else:
        protect_parent();check_selector_CAS(d);write(decision_path,reasoned)
        sys.path[:0]=[str(S),str(S/'app')]
        from app.lives import Store
        result=Store(S).promote(LIFE,decision_path)
        committed_row=native_commit_from_journal(decision_id,target_card['snapshot_sha256'])
        if committed_row is None:raise ValueError('Native promotion did not leave COMMITTED; no selector synchronization asserted')
    write(NATIVE_COMMITTED,{'schema':'PI05.native_promotion_witness.v1','at':now(),'journal_entry':committed_row,'result':result,'new_ticks':0})
    # No selected Owner/adapter is opened between Native COMMITTED and this
    # exact permission publication. Preparation never writes a live contract.
    contracts=apply_contracts(d,target_card)
    project=read(C/'PROYECTO.json');personal=read(S/'estado/genesis/SELECCION_PERSONAL.json');config=read(C/'aplicacion/GENESIS/SELECCION_CANDIDATA.json');cont=read(C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json');catalog=read(S/'capacidades/CATALOGO_CAPACIDADES.json')
    prior={'selected_life':project.get('selected_life'),'latest_saved_tick':project.get('latest_saved_tick'),'parent':project.get('parent'),'operational_adoption':project.get('operational_adoption')}
    available=list(dict.fromkeys([LIFE,*project.get('current_available_lives',[])]))
    project.setdefault('prior_selection_PI05',prior)
    project.update(selected_life=LIFE,latest_saved_tick=target_card['physical']['tick'],parent=target_card.get('parent'),current_available_lives=available,operational_adoption={'decision_id':decision_id,'scope':d['scope'],'physical_cut':target_card['physical'],'full_pair_local':localpair.relative_to(C).as_posix(),'previous_principal_preserved':True})
    project['physical_parent']={'life_id':PARENT,'tick':PARENT_T,'snapshot_sha256':PARENT_SHA}
    project['genealogy_scope']='physical_parent identifies the PI03 physical-history predecessor. parent remains the actual final-cut import container required by persistence; no memories were merged from control branches.'
    personal.update(life_id=LIFE,world_id=target_card['world_id'],first_selected_utc=now(),explicit_operational_adoption=decision_id)
    config.update(source_alias=LIFE,source_life=LIFE,source_tick=target_card['physical']['tick'],source_snapshot_sha256=manifest['snapshot_sha256'],paired_export_manifest_sha256=sha(localpair/'EXPORTACION_SERVICIO.json'),source_paired_export_manifest=(localpair/'EXPORTACION_SERVICIO.json').relative_to(C).as_posix(),current_operational_snapshot_sha256=target_card['snapshot_sha256'],explicit_operational_adoption=decision_id,selection_scope='Opens the existing adopted PI05 continuation. The final complete pair is a transport seed, never a replacement over a later future.')
    cont.setdefault('prior_cut_PI05',{key:cont.get(key)for key in ('life_id','world_id','physical_cut','parent','latest_snapshot','identity_card','operational_directories','selected_seed','proof')})
    cont.update(updated_utc=now(),life_id=LIFE,world_id=target_card['world_id'],profile=target_card['profile'],physical_cut=target_card['physical'],parent=target_card.get('parent'),latest_snapshot={'path_relative_to_product':'sistema/'+target_card['snapshot'],'sha256':target_card['snapshot_sha256']},identity_card={'path_relative_to_product':'sistema/estado/vidas/'+LIFE+'/VIDA.json','sha256':sha(S/'estado/vidas'/LIFE/'VIDA.json')},personal_selection=personal,current_available_lives=available,selected_seed=config,PI05_migration=target_card.get('PI05_migration'),operational_directories=['sistema/estado/'+name+'/'+LIFE for name in ('vidas','servicios_persistentes','servicios_locales')]+[localpair.relative_to(C).as_posix()],proof={'promotion_decision':str(decision_path),'product_reopening':str(reopening_path),'evidence_is_provenance_not_actor_input':True},new_ticks_for_this_selection=0)
    cont['physical_parent']={'life_id':PARENT,'tick':PARENT_T,'snapshot_sha256':PARENT_SHA}
    cont['genealogy_scope']=project['genealogy_scope']
    entry=dict(d['catalog_entry']);entry.update(implementation=[item['file']for item in prepared['deployed_code']],validated_lives=[{'life_id':LIFE,'physical':target_card['physical'],'snapshot_sha256':target_card['snapshot_sha256']}],contract=d['new_contract']['file'],assistance=d['assistance'],limits=d.get('limits',d['uncertainties']),source_decision=str(config_path),final_reopening_proof=str(reopening_path))
    matches=[item for item in catalog['entries']if item.get('id')==entry['id']]
    if matches and matches[0].get('source_decision')!=str(config_path):raise ValueError('A different PI05 catalog entry already exists')
    catalog['entries']=[entry,*[item for item in catalog['entries']if item.get('id')!=entry['id']]]
    # Exact prior originals are preserved in BACKUP. Existing manual descriptor
    # is intentionally left truthful until root actually publishes its new Word.
    for path,value in ((C/'PROYECTO.json',project),(S/'estado/genesis/SELECCION_PERSONAL.json',personal),(C/'aplicacion/GENESIS/SELECCION_CANDIDATA.json',config),(C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json',cont),(S/'capacidades/CATALOGO_CAPACIDADES.json',catalog)):write(path,value)
    protect_parent(require_selected=False)
    receipt={'schema':'PI05.adopted_product.v1','at':now(),'life_id':LIFE,'phase':'COMMITTED','record':target_card,'active':read(S/'estado/ACTIVO.json'),'selected_by_project':read(C/'PROYECTO.json')['selected_life'],'selected_by_personal':read(S/'estado/genesis/SELECCION_PERSONAL.json')['life_id'],'source_vs_export':source_comparison,'export_vs_reopened_product':comparison,'stable_pair_reused':stable_pair_proof,'Native_promotion':result,'reopening_proof':info(reopening_path),'contracts':contracts,'engine_preserved':engine,'writer_check':writers,'physical_parent_protected':{'life_id':PARENT,'tick':PARENT_T,'snapshot_sha256':PARENT_SHA},'new_ticks_for_migration_and_promotion':0,'reversal':'Use existing Store.promote/select on the preserved PI03 life with a reasoned decision and preserved selectors. No deletion, memory fusion or rewind of PI05.'}
    write(COMMITTED,receipt);stage=read(STAGE);stage.update(phase='COMMITTED',adopted_at=now(),proof=str(COMMITTED));write(STAGE,stage)
    return receipt
def main():
    parser=argparse.ArgumentParser(description=__doc__);phase=parser.add_mutually_exclusive_group();phase.add_argument('--prepare',action='store_true');phase.add_argument('--adopt',action='store_true');phase.add_argument('--dry-run',action='store_true')
    parser.add_argument('--decision',type=Path,default=CONFIG);parser.add_argument('--reopening-proof',type=Path,default=CONTROL/'REAPERTURA_PRODUCTO_PI05.json');args=parser.parse_args()
    if not(args.prepare or args.adopt):
        result={'mode':'READ_ONLY_NO_NATIVE_IMPORT_NO_WRITES','decision_path':str(args.decision),'decision_exists':args.decision.is_file(),'prepared':PREPARED.exists(),'adopted':COMMITTED.exists(),'source_system':str(CS),'target_system':str(S),'parent_protected':{'life_id':PARENT,'tick':PARENT_T,'snapshot_sha256':PARENT_SHA},'source_life_id':SOURCE_LIFE,'administrative_C2C_identity_source':ORIGIN_C2C_LIFE,'final_PI05_tick':'Read from the future DECISION_FINAL_PI05.json; never fixed here.','sequence':['Freeze reasoned final decision and fresh affected-writer proof','--prepare exact code and complete pair; default principal remains PI03','Root affected product reopening at0ticks and clean close','--adopt exact current product checkpoint, then update Word truthfully']}
        if args.decision.is_file():result['decision_sha256']=sha(args.decision)
        print(json.dumps(result,ensure_ascii=False,indent=2));return
    decision=load_decision(args.decision)
    result=prepare(decision,args.decision)if args.prepare else adopt(decision,args.decision,args.reopening_proof)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
