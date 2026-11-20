"""Root-only D code/config CAS; default prepares a reviewable proposal.

No Native/DEE/Owner/SQLite, snapshot, card or metadata entry is opened. Before
official imports, only F1's fresh prepared code trees may receive the overlay.
For Discovery or imported trees, Root's narrow fresh process proof is mandatory.
The actual D/WSLS seals must already have been written/copied by Root.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ast,copy,hashlib,json,os,re
P=Path(__file__).resolve().parents[1];H=P/'codigo';PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_';ROLES={'real':'DISCOVERY','none':'STAGE3_NONE','yoked':'STAGE3_YOKE','reproduction':'DREPRO','reference':'D_WSLS'};MANIFEST='SISTEMA_CODIGO_PI09.json'
PINNED={'pi09_consulta_selectiva_R02.py':'3b81573f4dc0d9401db2210f3b23694e1f1f4a4d820d7654bcbd1e1b42b2dfbf','pi09_entorno_persistente_D_R02.py':'c9938b50fbdf68d94954eaf341abae025faa307e4c8d24d23862c7b78bf085f8','PROTOCOLO_PI09_D_R02.json':'7d99060711544aebaf8882b8246cd0e09ac36ca77374d32e7dd29080188ea897'}
PINNED['pi09_lote_FI8_R01.py']='ecbf6cf65bdfce0359ed840bd803e5775e494bc10d8b50716bfd4124cfd12d96'
COMMON=['pi09_transporte_D_R02.py','pi09_antecedente_R02_readonly_D_R01.py','pi09_FI8_D_alias_R01.py','pi09_dispatcher_D_R02.py','pi09_entorno_persistente_D_R02.py','PROTOCOLO_PI09_D_R02.json','SELLO_PI09_D_R02.json','pi09_lote_FI8_R01.py']
def need(ok,why):
    if not ok:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def encoded(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def sha(data):return hashlib.sha256(data).hexdigest()
def digest(p):return sha(Path(p).read_bytes())
def plain(p):
    for q in(p,*p.parents):need(not q.exists()or not(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024),'No linked code/config paths')
def process(file,system,life,expected_physical):
    v=read(file);need(v.get('schema')=='DEE.PI09.scoped_code_patch_process_proof.R01'and v.get('safe_to_patch')is True and v.get('no_live_affected_writers')is True and Path(v['system']).resolve()==system and v['life_id']==life,'Exact Root narrow process proof; not a claim about other worlds')
    age=(datetime.now(timezone.utc)-datetime.fromisoformat(v['recorded_utc'])).total_seconds();need(0<=age<=min(600,v.get('reuse_limit_seconds',0)),'Refresh expired process witness')
    observed=v.get('evidence',{}).get('physical',{});need({k:observed.get(k)for k in('N','tick','RAW_sha256','clocks_sha256')}==expected_physical,'Root closed-process proof must describe the exact sealed pre-D physical source; no state opened here')
    return {'path':str(Path(file).resolve()),'sha256':digest(file),'age_seconds':age}
def structural_new(system,prep,ctx):
    need(prep.get('schema')=='DEE.PI09.D.base_prepared_no_Native.R01'and prep.get('Native_executed')is False and ctx.get('D_adapter_required_before_owner')is True,'Only F1 official fresh D prepared code may use preimport mode')
    need(not(system/'estado/vidas'/ctx['life']).exists()and not(system/'estado/servicios_persistentes'/ctx['life']).exists(),'Preimport mode refuses a Native/persistent future; no reading or overwriting it')
def seal_inputs(role):
    file=H/'SELLO_PI09_D_R02.json'
    if not file.is_file():return None
    seal=read(file);need(seal['schema']=='DEE.PI09.persistent_environment.D.source_seal.R02'and seal['protocol_sha256']==PINNED['PROTOCOLO_PI09_D_R02.json']and seal['source_parent_R02_ordinal']==12,'Root actual D seal required')
    need(seal['first_milestone_committed']is True and re.fullmatch('[0-9a-f]{64}',seal['first_milestone_adoption_sha256']),'Actual committed hito1 SHA')
    adoption=P/'control/ADOPCION_PRODUCTO_PI09.json';a=read(adoption);need(digest(adoption)==seal['first_milestone_adoption_sha256']and a['phase']=='COMMITTED','Actual immutable adoption receipt, not future approval')
    need(set(seal['source_prefix']['physical'])=={'N','tick','RAW_sha256','clocks_sha256'}and seal['source_prefix']['physical']['N']==67 and seal['source_prefix']['physical']['tick']==seal['source_prefix']['tick'],'Exact four-field physical source; extra metrics separate')
    for name,pin in PINNED.items():need(digest(H/name)==pin,'Scientific source pin changed: '+name)
    for name,pin in seal['files_sha256'].items():need(Path(name).name==name and digest(H/name)==pin,'Actual D sealed dependency changed: '+name)
    if role=='reference':need((H/'SELLO_PI09_D_WSLS_R01.json').is_file(),'Root independent optional WSLS seal must exist; no automatic authorization')
    return seal
def prepare(system,role,tag,preimport):
    system=system.resolve(strict=True);need(role in ROLES and system.name=='sistema'and system.parent.parent==(P/'estados').resolve(),'Discrete isolated PI09 systems only');plain(system);life=PREFIX+ROLES[role]+'_01'
    need(not(system/'estado/ACTIVO.json').exists(),'This installer never touches selected product');seal=seal_inputs(role)
    if seal is None:return {'status':'WAIT','reason':'Root actual SELLO_PI09_D_R02.json is not present; no target/config read or proposal written','Native_executed':False}
    root=system.parent;mf=root/MANIFEST;context=root/'CONTEXTO_EJECUCION.json';prepfile=root/'PREPARACION_PI09.json';ctx=read(context);prep=read(prepfile)
    need(ctx['life']==life and Path(ctx['system']).resolve()==system and prep['context_sha256']==digest(context),'Exact actual context/preparation identity')
    if role!='real':need(ctx['prefix_manifest_sha256']==seal['source_prefix']['manifest_sha256'],'New copies must name the same actual complete post-panel D source, not C/post12')
    if preimport:structural_new(system,prep,ctx)
    manifest=read(mf);rows={}
    for item in manifest['files']:
        name=item['file'];need(name not in rows and not name.startswith(('estado/','runtime/','motor/'))and not Path(name).is_absolute()and '..'not in Path(name).parts,'Relative code/config closure only')
        f=system/name;plain(f);need(f.is_file()and f.stat().st_size==item['bytes']and digest(f)==item['sha256'],'Current code/config differs from declared closure: '+name);rows[name]=dict(item)
    need(digest(system/'capacidades/pi09_consulta_selectiva_R02.py')==PINNED['pi09_consulta_selectiva_R02.py'],'Never alter acquired scientific R02')
    oldscopefile=system/'capacidades/PI09_TRANSPORTE_HEREDADO_R02.json';oldscope=read(oldscopefile);need(oldscope['life_id']==life,'F1 exact ancestry identity binding must precede overlay')
    oldscope['D_adapter_status']='RESOLVED_CODE_ONLY_R02_NO_METADATA_OR_NATIVE_CHANGE';oldscope['D_source_manifest_sha256']=seal['source_prefix']['manifest_sha256']
    dscope={'schema':'DEE.PI09.D.exact_readonly_transport_scope.R02','life_id':life,'role':role,'parent_R02_ordinal':12,'old_R02_metadata_and_stocks_untouched':True,'source_D_manifest_sha256':seal['source_prefix']['manifest_sha256'],'source_D_tick':seal['source_prefix']['tick'],'scientific_R02_sha256':PINNED['pi09_consulta_selectiva_R02.py'],'C_B_only_STATE_and_dependencies':True,'R02_only_STATE_and_dependencies':True,'selected_permission':'Only canonical real Discovery with exact D COMMITTED contract; all control/replay/reference selected use denied'}
    additions={name:(H/name).read_bytes()for name in COMMON}
    if role=='reference':
        for name in('pi09_referencia_contextual_D_WSLS_R01.py','PROTOCOLO_PI09_D_WSLS_R01.json','SELLO_PI09_D_WSLS_R01.json'):additions[name]=(H/name).read_bytes()
    additions['PI09_TRANSPORTE_HEREDADO_R02.json']=encoded(oldscope);additions['PI09_TRANSPORTE_D_R02.json']=encoded(dscope)
    for name,data in additions.items():
        if name.endswith('.py'):ast.parse(data.decode('utf-8-sig'))
    base_registry=read(system/'capacidades/PI09_PLUGINS_R02.json');need(base_registry['schema']=='DEE.PI09.fixed_plugins_source_registry.R01','Existing explicit plugin registry required')
    registry=copy.deepcopy(base_registry);registry['schema']='DEE.PI09.D.fixed_plugins_source_registry.R02'
    registry['plugins']=[{'pi09_consulta_selectiva_R02':'pi09_antecedente_R02_readonly_D_R01','pi09_lote_FI8_R01':'pi09_FI8_D_alias_R01'}.get(n,n)for n in registry['plugins']]
    need('pi09_antecedente_R02_readonly_D_R01'in registry['plugins'],'R02 ancestry must have readonly route')
    if 'pi09_FI8_D_alias_R01'not in registry['plugins']:registry['plugins'].append('pi09_FI8_D_alias_R01')
    registry['plugins'].append('pi09_referencia_contextual_D_WSLS_R01'if role=='reference'else'pi09_entorno_persistente_D_R02')
    registry['files_sha256'].update({name:sha(data)for name,data in additions.items()});additions['PI09_PLUGINS_D_R02.json']=encoded(registry)
    changes=[(system/'capacidades'/name,data)for name,data in additions.items()]
    for name in('app/mundo_genesis_apd05.py','app/cola_local.py'):
        source=(system/name).read_text('utf-8-sig');need('pi09_dispatcher_D_R02'not in source,'Already patched D code is preserved; no automatic reapplication');changed=source.replace('pi09_dispatcher_R02','pi09_dispatcher_D_R02')
        need(changed!=source,'Exact old PI09 dispatch hook required')
        if name.endswith('mundo_genesis_apd05.py'):
            need('pi09_transporte_heredado_R02'in changed,'Exact ancestry transport hook required');changed=changed.replace('pi09_transporte_heredado_R02','pi09_transporte_D_R02')
        ast.parse(changed);changes.append((system/name,changed.encode('utf8')))
    for target,data in changes:
        rel=target.relative_to(system).as_posix();rows[rel]={'file':rel,'bytes':len(data),'sha256':sha(data)}
    prior=digest(mf);manifest.update(schema='DEE.PI09.D.current_code_closure.R02',files=[rows[k]for k in sorted(rows)],previous_literal_manifest_sha256=prior,D_permissions_resolved=True,scientific_R02_literal_unchanged=True,source_D_seal_sha256=digest(H/'SELLO_PI09_D_R02.json'),Native_executed_by_code_overlay=False)
    mbytes=encoded(manifest);ctx['current_code_manifest']={'file':MANIFEST,'sha256':sha(mbytes)};ctx.setdefault('code_only_preparations',[]).append({'kind':'D_R02_EXACT_READONLY_AND_DISPATCH','manifest_sha256':sha(mbytes),'old_scientific_bodies_literal':True,'no_Native_or_metadata_edit':True});ctx['D_adapter_required_before_owner']=False
    cbytes=encoded(ctx);prep['context_sha256']=sha(cbytes);prep['current_code_manifest_sha256']=sha(mbytes);prep['D_permissions_resolved']=True;prep['D_native_import_or_admission_claimed']=False;changes.extend([(mf,mbytes),(context,cbytes),(prepfile,encoded(prep))])
    need(re.fullmatch('[A-Za-z0-9_]{1,64}',tag),'Fresh short tag');dest=H/('D_OVERLAY_'+tag);need(not dest.exists(),'Fresh staged proposal');dest.mkdir()
    plan={'schema':'DEE.PI09.D.code_only_CAS_installation_plan.R02','role':role,'system':str(system),'life_id':life,'tag':tag,'preimport_code_only':preimport,'source_D_seal_sha256':digest(H/'SELLO_PI09_D_R02.json'),'plan_builder_sha256':digest(__file__),'Native_executed':False,'SQLite_or_world_read':False,'changes':[]}
    for i,(target,data)in enumerate(changes):
        proposal=dest/('%03d_PROPUESTO'%i);proposal.write_bytes(data);before=target.read_bytes()if target.exists()else None
        if before is not None:(dest/('%03d_ORIGINAL_LITERAL'%i)).write_bytes(before)
        plan['changes'].append({'target':str(target),'before_sha256':None if before is None else sha(before),'source':str(proposal),'after_sha256':sha(data),'bytes':len(data)})
    file=dest/'PLAN.json';file.write_bytes(encoded(plan));return {'plan':str(file),'sha256':digest(file),'Native_executed':False,'installed':False,'D_permissions_resolved_in_proposal_only':True,'targets':len(changes)}
def apply(planfile,processfile):
    plan=read(planfile);need(plan['schema']=='DEE.PI09.D.code_only_CAS_installation_plan.R02'and plan['plan_builder_sha256']==digest(__file__),'Exact plan/builder');system=Path(plan['system']).resolve(strict=True);life=plan['life_id'];role=plan['role'];need(system.name=='sistema'and system.parent.parent==(P/'estados').resolve()and life==PREFIX+ROLES[role]+'_01','Discrete exact D target');seal_inputs(role);need(plan['source_D_seal_sha256']==digest(H/'SELLO_PI09_D_R02.json'),'Root source seal changed')
    if plan['preimport_code_only']:structural_new(system,read(system.parent/'PREPARACION_PI09.json'),read(system.parent/'CONTEXTO_EJECUCION.json'));witness={'scope':'Fresh F1 code tree before official Native import; no Native future exists','process_proof_not_claimed':True}
    else:need(processfile is not None,'Fresh exact Root narrow process witness required after import');witness=process(processfile,system,life,read(H/'SELLO_PI09_D_R02.json')['source_prefix']['physical'])
    need(not(system/'estado/ACTIVO.json').exists(),'Never selected/product');proof=P/'control'/('D_OVERLAY_'+plan['tag']+'_APLICADA.json');need(not proof.exists(),'Existing application preserved')
    explicit_capabilities={*(COMMON),'PI09_TRANSPORTE_HEREDADO_R02.json','PI09_TRANSPORTE_D_R02.json','PI09_PLUGINS_D_R02.json','pi09_referencia_contextual_D_WSLS_R01.py','PROTOCOLO_PI09_D_WSLS_R01.json','SELLO_PI09_D_WSLS_R01.json'}
    allowed={system/'capacidades'/n for n in explicit_capabilities}|{system/'app/mundo_genesis_apd05.py',system/'app/cola_local.py',system.parent/MANIFEST,system.parent/'CONTEXTO_EJECUCION.json',system.parent/'PREPARACION_PI09.json'}
    for row in plan['changes']:
        target=Path(row['target']);plain(target);source=Path(row['source']);need(target in allowed and source.resolve().is_relative_to(H.resolve())and digest(source)==row['after_sha256'],'Explicit code/config target and proposal only');need((digest(target)if target.exists()else None)==row['before_sha256'],'CAS changed: '+str(target));need(not target.with_name(target.name+'.D_OVERLAY_TMP').exists(),'Prior partial overlay retained')
    for row in plan['changes']:
        target=Path(row['target']);temp=target.with_name(target.name+'.D_OVERLAY_TMP')
        with temp.open('xb')as f:f.write(Path(row['source']).read_bytes());f.flush();os.fsync(f.fileno())
        os.replace(temp,target)
    result={'schema':'DEE.PI09.D.code_only_CAS_installation.applied.R02','applied':True,'role':role,'system':str(system),'life_id':life,'plan':{'path':str(Path(planfile).resolve()),'sha256':digest(planfile)},'closed_process_or_fresh_preimport_witness':witness,'Native_executed':False,'SQLite_snapshot_card_or_metadata_opened':False,'D_preparation_or_FI8_admission_executed':False,'R02_scientific_source_literal_unchanged':digest(system/'capacidades/pi09_consulta_selectiva_R02.py')==PINNED['pi09_consulta_selectiva_R02.py'],'D_permissions_resolved':True,'current_code_manifest':{'path':str(system.parent/MANIFEST),'sha256':digest(system.parent/MANIFEST)},'context_sha256':digest(system.parent/'CONTEXTO_EJECUCION.json'),'literal_backups':str(Path(planfile).parent),'changes':plan['changes']}
    with proof.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    return {'proof':str(proof),'sha256':digest(proof),'applied':True,'Native_executed':False,'current_code_manifest_sha256':result['current_code_manifest']['sha256']}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--sistema',type=Path);ap.add_argument('--rol',choices=tuple(ROLES));ap.add_argument('--tag');ap.add_argument('--preimport',action='store_true');ap.add_argument('--plan',type=Path);ap.add_argument('--procesos',type=Path);ap.add_argument('--aplicar',action='store_true');a=ap.parse_args()
    if a.aplicar:need(a.plan is not None,'Explicit reviewed plan');result=apply(a.plan,a.procesos)
    else:need(a.sistema is not None and a.rol is not None and a.tag is not None,'Explicit discrete system/role/fresh tag');result=prepare(a.sistema,a.rol,a.tag,a.preimport)
    print(json.dumps(result,ensure_ascii=False))
