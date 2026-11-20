"""Root-only closed diagnostic code/supply-scope extension; no Native call.

Default PLAN reads only. --aplicar writes an explicit new wrapper/config and
code-closure revision to one closed unselected PI11 system, preserving prior
registry, manifest and contexts. Actual eight-offer admission is a separate
owner operation. No product, selected state, snapshot or SQLite is written.
"""
from pathlib import Path
import argparse,ast,hashlib,importlib.util,json,os,shutil
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema'
KEYS=('DEE.Cognitive.PI09.explicit_FI_eight_offer_lot.R01','DEE.Cognitive.PI07.regulated_FI_access.R01','DEE.Cognitive.PI07.regulation.environment.R03')
def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,p):
    sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def regular(p):
    for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No linked extension path')
def write_new(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def replace(p,v):
    tmp=p.with_name(p.name+'.PI11_FI8_WRITING');write_new(tmp,v);os.replace(tmp,p)
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--system',type=Path,required=True);ap.add_argument('--life',required=True);ap.add_argument('--closed-proof',type=Path,required=True);ap.add_argument('--closed-proof-sha256',required=True);ap.add_argument('--prospective-decision',type=Path,required=True);ap.add_argument('--prospective-decision-sha256',required=True);ap.add_argument('--aplicar',action='store_true');a=ap.parse_args()
    system=a.system.resolve(strict=True);regular(system)
    need(system.name=='sistema'and system.parent.parent==(P/'estados').resolve()and not(system/'estado/ACTIVO.json').exists(),'Only explicit unselected PI11 diagnostic system')
    proof_file=a.closed_proof.resolve(strict=True);prospective=a.prospective_decision.resolve(strict=True)
    need(proof_file.is_relative_to(P.resolve())and prospective.is_relative_to(P.resolve())and sha(proof_file)==a.closed_proof_sha256 and sha(prospective)==a.prospective_decision_sha256,'Exact actual closed/prospective local proofs')
    proof=read(proof_file);decision=read(prospective)
    need(proof.get('life_id')==a.life and proof.get('closed')is True and proof.get('error')is None,'Actual coherent closed source owner required')
    need(decision.get('schema')=='DEE.PI11.prospective_FI8_external_supply.R01'and decision.get('life_id')==a.life and decision.get('new_offers')==8 and decision.get('old_counters_not_reset')is True and decision.get('not_learning')is True and decision.get('authorized_before_first_use')is True,'Explicit prospective architectural supply decision')
    cardfile=system/'estado/vidas'/a.life/'VIDA.json';card=read(cardfile);snapshot=system/card['snapshot'];need(card['life_id']==a.life and card['physical']['tick']==proof['final_tick']and sha(snapshot)==card['snapshot_sha256'],'Current actual reached stable source cut')
    parser_file=C/'reproducibilidad/observador_pasivo.py';need(sha(parser_file)=='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873','Exact passive parser')
    view=load('PI11_FI8_scope_parser',parser_file).snapshot_view(snapshot);e=view['metadata'];need(KEYS[0]in e and all(k in e for k in KEYS),'All exact old histories present')
    need('DEE.Cognitive.PI11.explicit_FI_eight_offer_lot.R01'not in e,'New lot already admitted; never replace code/reset its scope')
    old={k:json.loads(e[k])for k in KEYS}
    need(all(not v.get('pending')and not v.get('uncertain')for v in old.values()),'No incomplete antecedents')
    need(all(v['ordinal']==len(v['rows'])and 0<=v['ordinal']<=8 for k,v in old.items()if k!=KEYS[2]),'Closed finite old FI counters')
    scope={'schema':'DEE.PI11.explicit_FI8_supply_scope.R01','life_id':a.life,'offers':8,'Native_admission_ticks':0,'Native_admission_inputs':0,'old_metadata_sha256':{k:hashlib.sha256(e[k].encode('utf8')).hexdigest()for k in KEYS},'admit_not_before_tick':card['physical']['tick'],'same_frozen_body_sha256':'cefe1174debca3650fffeba22f1f1c2d03420211993734e319b9e47684c5db46','physical_banks_reset':False,'not_learning':True,'prospective_decision_sha256':sha(prospective)}
    registryfile=system/'capacidades/PI11_PLUGINS_R01.json';registry=read(registryfile);need(registry.get('schema')=='DEE.PI11.fixed_plugins.R01'and 'pi11_lote_FI8_R01'not in registry['plugins'],'Fresh fixed plugin only')
    for name,digest in registry['files_sha256'].items():need(sha(system/'capacidades'/name)==digest,'Current registry changed: '+name)
    manifestfile=system.parent/'SISTEMA_CODIGO_PI11.json';contextfile=system.parent/'CONTEXTO_EJECUCION.json';prepfile=system.parent/'PREPARACION_PI11.json';mf=read(manifestfile);ctx=read(contextfile);prep=read(prepfile)
    need(ctx['life']==a.life and ctx['source_code_manifest_sha256']==sha(manifestfile),'Exact original closure/context')
    for row in mf['files']:need(sha(system/row['file'])==row['sha256'],'Current code changed: '+row['file'])
    source=H/'pi11_lote_FI8_R01.py';ast.parse(source.read_bytes());targets=[system/'capacidades/pi11_lote_FI8_R01.py',system/'capacidades/PI11_FI8_SUMINISTRO_R01.json']
    need(all(not f.exists()for f in targets),'Existing extension/partial installation preserved')
    result={'schema':'DEE.PI11.explicit_FI8_closed_code_extension.R01','life_id':a.life,'source_tick':card['physical']['tick'],'new_external_offers_when_later_admitted':8,'actual_offers_admitted_now':0,'Native_imported':False,'new_Native_ticks':0,'old_ordinals':{k:v.get('ordinal')for k,v in old.items()},'scope':scope,'source':{'path':str(source),'sha256':sha(source)},'prospective_decision':{'path':str(prospective),'sha256':sha(prospective)},'only_diagnostic_code_and_scope_changes':True}
    if not a.aplicar:print(json.dumps({**result,'mode':'PLAN_ONLY','writes':0},ensure_ascii=False,indent=2));return
    closed=load('PI11_FI8_closed_guard',H/'comprobar_proceso_PI11_R01.py').inspect('PI11_closed_before_explicit_FI8_code_extension',system,a.life);need(closed.get('no_live_affected_writer')is True,'Actual scoped writer/queue must be closed')
    before={str(p):sha(p)for p in(cardfile,snapshot)};backup=system.parent/'EXTENSION_FI8_R01_ANTES';need(not backup.exists(),'Prior extension attempt preserved');backup.mkdir()
    for f in(registryfile,manifestfile,contextfile,prepfile):shutil.copyfile(f,backup/f.name)
    shutil.copyfile(source,targets[0]);write_new(targets[1],scope)
    registry['plugins'].append('pi11_lote_FI8_R01')
    for f in targets:registry['files_sha256'][f.name]=sha(f)
    replace(registryfile,registry)
    files={r['file']:dict(r)for r in mf['files']}
    for f in(*targets,registryfile):files[f.relative_to(system).as_posix()]={'file':f.relative_to(system).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}
    mf['files']=[files[n]for n in sorted(files)];mf['PI11_FI8_extension_prospective_decision_sha256']=sha(prospective);replace(manifestfile,mf)
    ctx['source_code_manifest_sha256']=sha(manifestfile);replace(contextfile,ctx);prep.update(context_sha256=sha(contextfile),final_code_manifest_sha256=sha(manifestfile));replace(prepfile,prep)
    need(before=={p:sha(Path(p))for p in before},'Closed Native/card changed during pure code extension')
    result.update(applied=True,backup=str(backup),code_manifest_sha256=sha(manifestfile),closed_guard=closed,Native_snapshot_card_unchanged=True)
    output=P/'control'/('EXTENSION_FI8_'+system.parent.name+'_R01.json');write_new(output,result);print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
