"""Prepare a bounded R02 product-interface test in a fresh complete clone.

No Native call. Default PLAN writes nothing. The explicit apply phase only
changes that unselected clone's code/admin configs and adds a diagnostic
permission. It never claims COMMITTED/adoption gates or modifies the source
world. The Root supervisor alone opens the new owner and material test.
"""
from pathlib import Path
import argparse,ast,hashlib,importlib.util,json,os,shutil
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0'
SYSTEM='DEE.Cognitive.System.1.1.life.v1';SERVICE='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'
KEY='DEE.Cognitive.PI11.persistent_habitat.native_continuation.R01';OLD='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02';FI8='DEE.Cognitive.PI11.explicit_FI_eight_offer_lot.R01'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,p):
    sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def regular(p):
    for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No reparse diagnostic path')
def write_new(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def replace(p,v):
    temp=p.with_name(p.name+'.PI11_IF_WRITING');write_new(temp,v);os.replace(temp,p)
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--system',type=Path,required=True);ap.add_argument('--life',required=True);ap.add_argument('--scientific-basis',type=Path,required=True);ap.add_argument('--scientific-basis-sha256',required=True);ap.add_argument('--product-code',type=Path,default=H/'PRODUCTO_PREPARADO_R02');ap.add_argument('--aplicar',action='store_true');a=ap.parse_args()
    system=a.system.resolve(strict=True);regular(system);need(system.name=='sistema'and system.parent.parent==(P/'estados').resolve()and not(system/'estado/ACTIVO.json').exists(),'Explicit unselected new PI11 clone only')
    contextfile=system.parent/'CONTEXTO_EJECUCION.json';context=read(contextfile);need(context['life']==a.life,'Exact clone context')
    imported=read(system.parent/'IMPORTACION_PI11.json');official=read(system.parent/'IMPORTACION_DIAGNOSTICA.json')
    need(imported['life_id']==a.life and imported['closed']is True and imported['error']is None and imported['new_Native_ticks']==0 and official['life']==a.life and official['comparison']['physical_equal']and official['comparison']['causal_prefix_equal'],'Actual complete closed zero-tick import before interface preparation')
    cardfile=system/'estado/vidas'/a.life/'VIDA.json';card=read(cardfile);snapshot=system/card['snapshot'];need(card['physical']==official['result']['physical']and card['snapshot_sha256']==official['result']['snapshot_sha256']and sha(snapshot)==card['snapshot_sha256'],'Clone must remain at its actual imported cut')
    basis_file=a.scientific_basis.resolve(strict=True);need(basis_file.is_relative_to(P.resolve())and sha(basis_file)==a.scientific_basis_sha256,'Exact local closed scientific basis')
    basis=read(basis_file);need(basis.get('schema')=='DEE.PI11.closed_scientific_basis_for_interface.R01'and basis.get('not_adoption')is True,'Interface basis does not declare promotion')
    pair=read(Path(context['prefix'])/'EXPORTACION_SERVICIO.json')
    need(basis['source_life_id']==pair['life_id']and basis['source_tick']==pair['physical']['tick']and basis['source_snapshot_sha256']==pair['snapshot_sha256'],'Basis is the actual full cloned source, not another branch')
    ref=basis['source_closed_proof'];proof_file=Path(ref['path']).resolve(strict=True);need(proof_file.is_relative_to(P.resolve())and sha(proof_file)==ref['sha256'],'Exact closed scientific source proof');proof=read(proof_file)
    need(proof.get('life_id')==basis['source_life_id']and proof.get('closed')is True and proof.get('error')is None and proof.get('final_tick')==basis['source_tick'],'Actual closed source Native execution')
    parser_file=C/'reproducibilidad/observador_pasivo.py';need(sha(parser_file)=='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873','Exact passive parser')
    view=load('PI11_interface_frozen_parser',parser_file).snapshot_view(snapshot);meta=view['metadata'];current=json.loads(meta[KEY]);fi8=json.loads(meta[FI8]);service=json.loads(meta[SERVICE]);need(not current.get('pending')and not current.get('uncertain')and fi8['ordinal']<8 and not fi8.get('pending')and not fi8.get('uncertain'),'Closed learned/supplied source with remaining FI access')
    need(type(service.get('material_calls'))is int,'Exact inherited material call counter required for finite interface budget')
    prepared=a.product_code.resolve(strict=True);regular(prepared);need(prepared.parent==H.resolve(),'Prepared R02 code in campaign only');cm=read(prepared/'CODIGO_PREPARADO.json');need(cm.get('schema')=='DEE.PI11.prepared_product_code.R02','R02 diagnostic-safe prepared code')
    for row in cm['files']:need(sha(prepared/row['file'])==row['sha256'],'Prepared product code changed')
    contractfile=system/'contratos/PI11_USO_OPERATIVO_R01.json';markerfile=system/'contratos/PI11_INTERFAZ_DIAGNOSTICA_R01.json';need(not contractfile.exists()and not markerfile.exists(),'Never overwrite prior interface profile/budget')
    changes={r['file']:Path(r['source']).read_bytes()for r in cm['files']}
    # Bind *administrative* current-life leaves of the transported interfaces;
    # learned metadata, arrays, clocks, receipts and historical fields stay literal.
    configs={}
    for name in('PI10_TRANSPORTE_ANCESTRAL_R01.json','PI10_EXPERIMENTO_R02.json','PI11_EXPERIMENTO_R01.json','PI11_FI8_SUMINISTRO_R01.json'):
        f=system/'capacidades'/name;v=read(f);v['life_id']=a.life;configs[name]=v
    for registry_name in('PI10_PLUGINS_R01.json','PI11_PLUGINS_R01.json'):
        v=read(system/'capacidades'/registry_name)
        if registry_name=='PI11_PLUGINS_R01.json':
            if 'pi11_lote_FI8_R01'not in v['plugins']:v['plugins'].append('pi11_lote_FI8_R01')
            v['files_sha256']['pi11_lote_FI8_R01.py']=sha(system/'capacidades/pi11_lote_FI8_R01.py')
            v['files_sha256']['PI11_FI8_SUMINISTRO_R01.json']=sha(system/'capacidades/PI11_FI8_SUMINISTRO_R01.json')
        for name,config in configs.items():
            if name in v['files_sha256']:v['files_sha256'][name]=hashlib.sha256((json.dumps(config,ensure_ascii=False,indent=2)+'\n').encode('utf8')).hexdigest()
        configs[registry_name]=v
    def future_hash(name):
        if name in configs:return hashlib.sha256((json.dumps(configs[name],ensure_ascii=False,indent=2)+'\n').encode('utf8')).hexdigest()
        key='capacidades/'+name
        return hashlib.sha256(changes[key]).hexdigest()if key in changes else sha(system/key)
    frozen_names=('pi11_actor_R01.py','pi11_habitat_persistente_R01.py','pi11_dispatcher_R01.py','pi11_identidad_heredada_R02.py','pi11_lote_FI8_R01.py','PI11_FI8_SUMINISTRO_R01.json','PROTOCOLO_PI11_R01.json','PI11_EXPERIMENTO_R01.json','PI11_PLUGINS_R01.json','pi10_transporte_ancestral_R01.py','pi10_permiso_operativo_R02.py')
    contract={'schema':'DEE.PI11.exact_operational_permission.R01','life_id':a.life,'profile':'fisica_directa','N':67,'status':'DIAGNOSTIC_INTERFACE_ONLY','all_adoption_gates_met':False,'adoption_decision_sha256':None,'diagnostic_scientific_basis_sha256':sha(basis_file),'previous_principal':{'life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01','tick':947395,'snapshot_sha256':'fd7372b7f2adc9040866fab8adfaca0d79e0bd18e997c0abc0651fe4fa3c23dc'},'allowed_modes':['eci01-pi11-episodio','eci01-pi11-estado'],'PI10_material_disabled':True,'historical_material_disabled':True,'public_FI_backend':'PI11_new_FI8_same_frozen_body','new_FI8_key':FI8,'new_FI8_total':8,'public_FI_domain':[0,20],'internal_FI_redirected':False,'public_arithmetic_policy':'legacy_partial','C2C_protocol_sha256':'0cf6bf8508e071a1c8cf1448023a096bc43336d66b8a1deb98f488b29b4205fd','source_ordinal':current['ordinal'],'PI11_protocol_sha256':current['protocol_sha256'],'PI10_history_sha256':hashlib.sha256(meta[OLD].encode('utf8')).hexdigest(),'frozen_files_sha256':{name:future_hash(name)for name in frozen_names},'diagnostic_passive_parser_source':str(parser_file)}
    encoded_contract=(json.dumps(contract,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    marker={'schema':'DEE.PI11.explicit_product_interface_diagnostic.R01','life_id':a.life,'system':str(system),'contract_sha256':hashlib.sha256(encoded_contract).hexdigest(),'allow_material_interface_test':True,'not_a_principal':True,'initial_tick':card['physical']['tick'],'maximum_new_Native_ticks':4032,'initial_material_calls':service['material_calls'],'maximum_material_calls':2,'allowed_material_modes':['eci01-pi11-episodio','eci01-balance'],'scientific_basis_sha256':sha(basis_file)}
    result={'schema':'DEE.PI11.explicit_R02_interface_code_preparation.R01','life_id':a.life,'scientific_basis':{'path':str(basis_file),'sha256':sha(basis_file)},'source_pair_manifest_sha256':context['prefix_manifest_sha256'],'initial_tick':card['physical']['tick'],'contract':contract,'diagnostic_marker':marker,'Native_executed':False,'product_originals_modified':False,'adoption_claimed':False}
    if not a.aplicar:print(json.dumps({**result,'mode':'PLAN_ONLY','writes':0},ensure_ascii=False,indent=2));return
    closed=load('PI11_interface_closed_import_guard',H/'comprobar_proceso_PI11_R01.py').inspect('PI11_explicit_R02_interface_preparation',system,a.life);need(closed.get('no_live_affected_writer')is True,'Actual imported/writer closure required')
    protected={str(f):sha(f)for f in(cardfile,snapshot,system/'estado/servicios_persistentes'/a.life/'cola.sqlite3')};backup=system.parent/'INTERFAZ_R02_ANTES';need(not backup.exists(),'Existing interface attempt preserved');backup.mkdir()
    manifestfile=system.parent/'SISTEMA_CODIGO_PI11.json';prepfile=system.parent/'PREPARACION_PI11.json'
    for f in(manifestfile,contextfile,prepfile):shutil.copyfile(f,backup/f.name)
    for relative,data in changes.items():
        target=system/relative
        if target.exists():out=backup/relative;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(target,out)
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    for name,v in configs.items():
        target=system/'capacidades'/name;out=backup/'capacidades'/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(target,out);replace(target,v)
    contractfile.write_bytes(encoded_contract);write_new(markerfile,marker)
    mf=read(manifestfile);files={r['file']:r for r in mf['files']}
    for target in[*(system/n for n in changes),*(system/'capacidades'/n for n in configs),contractfile,markerfile]:files[target.relative_to(system).as_posix()]={'file':target.relative_to(system).as_posix(),'bytes':target.stat().st_size,'sha256':sha(target)}
    mf['files']=[files[n]for n in sorted(files)];mf['PI11_product_interface_diagnostic_only']=True;replace(manifestfile,mf);context['source_code_manifest_sha256']=sha(manifestfile);replace(contextfile,context);prep=read(prepfile);prep.update(context_sha256=sha(contextfile),final_code_manifest_sha256=sha(manifestfile));replace(prepfile,prep)
    need(protected=={p:sha(Path(p))for p in protected},'Code/interface preparation changed Native/card/SQLite')
    result.update(applied=True,backup=str(backup),Native_card_SQLite_unchanged=True,closed_guard=closed,code_manifest_sha256=sha(manifestfile));output=P/'control'/('INTERFAZ_R02_PREPARADA_'+system.parent.name+'.json');write_new(output,result);print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
