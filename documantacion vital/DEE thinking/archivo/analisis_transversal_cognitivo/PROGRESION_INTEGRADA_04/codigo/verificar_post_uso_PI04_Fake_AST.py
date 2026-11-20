"""Only fake transport/metadata tests; never opens a Native world or product GUI."""
from pathlib import Path
from types import SimpleNamespace
import ast,contextlib,hashlib,io,json,runpy,sys
P4=Path(__file__).resolve().parents[1];CODE=P4/'codigo/sincronizar_PI04_post_uso.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    proof_path=P4/'control/POST_USO_PI04_PREPARADO_FAKE_AST_R02.json'
    if proof_path.exists():raise FileExistsError('Preserve prior static test')
    g=runpy.run_path(str(CODE),run_name='pure_post_use_metadata_definition')
    source=(g['S']/'app/usar_dee.py');supervisor_module=runpy.run_path(str(source),run_name='pure_existing_supervisor_definition')
    genesis_path=g['C']/'aplicacion/GENESIS/genesis.py';genesis_text=genesis_path.read_text(encoding='utf-8-sig')
    fixture=P4/'control/POST_USO_PI04_FAKE_SUPERVISOR_R02'
    if fixture.exists():raise FileExistsError('Fake fixture already exists')
    home=fixture/'entrada/vidas';life=g['LIFE'];world='FAKE_WORLD_ONLY_NO_NATIVE'
    folder=home/life;folder.mkdir(parents=True)
    fake_card={'life_id':life,'world_id':world,'parent':{'encoded_sha256':'FAKE_HISTORICAL_SEED_ONLY'},'physical':{'N':67,'tick':101}}
    protocol=g['existing_entry_protocol'](fake_card,{'kind':'FAKE_TEST_ONLY_NO_ADOPTION'})
    (folder/'PROTOCOLO.json').write_text(json.dumps(protocol),encoding='utf-8')
    calls={'record':0,'import_new':0,'start':0}
    class Backend:
        protocol_home=home
        def record(self,identifier):
            if identifier!=life:raise AssertionError('Wrong fake identity')
            calls['record']+=1;return json.loads(json.dumps(fake_card))
        def import_new(self,*args):calls['import_new']+=1;raise AssertionError('Existing registered life must never reimport historical seed')
        def start(self,*args):calls['start']+=1;raise AssertionError('No actual owner in Fake test')
    supervisor=supervisor_module['Supervisor'](fixture,life,Backend(),{'status':'CLOSED_SELECTED_FOR_USE','source_tick':1})
    first=supervisor.open(new=False)
    assert first['physical']['tick']==101
    fake_card['physical']['tick']=102
    second=supervisor.open(new=False)
    assert second['physical']['tick']==102 and calls['import_new']==0 and calls['start']==0
    assert json.loads((folder/'PROTOCOLO.json').read_text())['source_snapshot_sha256']=='FAKE_HISTORICAL_SEED_ONLY'
    # Existing GUI literal behavior selects new=False once this metadata file
    # exists. No Genesis object/thread/server or GUI is constructed here.
    assert 'result = self.session.open(new=not existing)'in genesis_text
    assert 'existing = self.session.state_path.is_file()'in genesis_text
    tree=ast.parse(CODE.read_text(encoding='utf-8-sig'));calls_ast=[ast.unparse(n.func)for n in ast.walk(tree)if isinstance(n,ast.Call)]
    banned=['run_until','promote','import_pair','load_adapter','Owner','set_snapshot_metadata','declare_interface']
    assert not any(any(x==name or x.endswith('.'+name)for name in banned)for x in calls_ast)
    target=fixture/'CAS.json';g['atomic'](target,{'FAKE':1},expected=None);old_hash=sha(target)
    target.write_text('{"FAKE":2}\n',encoding='utf-8')
    try:g['atomic'](target,{'FAKE':'must_not_overwrite'},expected=old_hash);raise AssertionError('CAS failed to reject changed file')
    except ValueError:pass
    assert json.loads(target.read_text())=={'FAKE':2}
    try:g['relative']('../escape');raise AssertionError('Traversal accepted')
    except ValueError:pass
    try:g['actual_input_summary']({'requests':[],'native_arithmetic':{'native_operation':{'native_trial':{'requests':[]}}},'second_native_use':{'requests':[]},'before_tick':0,'after_tick':1});raise AssertionError('Missing material evidence accepted')
    except ValueError:pass
    # Plain invocation must only describe unmet evidence, never write a product.
    protected=[g['C']/'PROYECTO.json',g['C']/'CONTINUIDAD_DEE_COGNITIVE_2_0.json',g['S']/'estado/ACTIVO.json',g['S']/'estado/genesis/SELECCION_PERSONAL.json',g['C']/'aplicacion/GENESIS/SELECCION_CANDIDATA.json',g['S']/'capacidades/CATALOGO_CAPACIDADES.json']
    before={str(p):sha(p)for p in protected};saved=sys.argv;stream=io.StringIO()
    try:
        sys.argv=[str(CODE)]
        with contextlib.redirect_stdout(stream):g['main']()
    finally:sys.argv=saved
    plan=json.loads(stream.getvalue());assert plan['mode']=='PLAN_NO_NATIVE_NO_WRITES'
    after={str(p):sha(p)for p in protected}
    if before!=after:raise ValueError('A product metadata file changed concurrently; reconcile test scope')
    imports=[x for x in sys.modules if x=='app'or x.startswith(('app.','dee_thinking'))];assert not imports
    result={'schema':'PI04.post_use_metadata.prepared.Fake_AST.NOT_APPLIED.v1','code':{'path':str(CODE.resolve()),'bytes':CODE.stat().st_size,'sha256':sha(CODE)},
        'sources':{'existing_Supervisor':{'path':str(source.resolve()),'sha256':sha(source),'lines':'Supervisor.__init__/open, current local source304..324'},'GUI_consumer':{'path':str(genesis_path.resolve()),'sha256':sha(genesis_path),'lines':'Genesis.__init__ and perform(abrir), current local source266..397'},'CAS_style_reused':{'path':str((P4.parent/'PROGRESION_INTEGRADA_03/codigo/publicar_documentos_PI03_literal.py').resolve()),'scope':'Expected source hashes checked before temporary write and before atomic replacement; no document authoring invoked.'}},
        'Fake_only':True,'Fake_supervisor_open_existing':{'first_fake_tick':first['physical']['tick'],'second_fake_tick':second['physical']['tick'],'backend_calls':calls,'historical_fake_seed_preserved':True,'no_import_no_owner':True},
        'CAS_changed_file_rejected':True,'path_traversal_rejected':True,'missing186_Native_inputs_rejected':True,'AST_no_Native_or_promotion_calls':True,
        'default_plan':plan,'product_metadata_before_after_unchanged':after,'DEE_or_app_imports':imports,
        'applied':False,'new_Native_ticks':0,'actual_post_commit_use_not_yet_claimed':True,
        'limits':['Fake ticks101/102 belong exclusively to the metadata fixture, not DEE.','Actual COMMITTED adoption, exact current Native state, post-commit use, full-pair export, process closure and queue reconciliation are required by --aplicar and were not fabricated.','No actual GUI, backend manager subprocess, owner or Native test was executed by this script.']}
    proof_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'proof':str(proof_path),'bytes':proof_path.stat().st_size,'sha256':sha(proof_path),'code':result['code'],'fake_import_new_calls':calls['import_new'],'Native_ticks':0,'applied':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
