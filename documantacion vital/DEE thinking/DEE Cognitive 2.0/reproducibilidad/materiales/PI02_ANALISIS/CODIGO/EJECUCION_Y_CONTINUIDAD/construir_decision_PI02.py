"""Build the future reasoned PI02 decision from closed empirical evidence.

No Native import/tick, owner, experiment or product write. Default prints a
read-only plan. --write requires an explicit operational_adoption section in
CIERRE_CIENTIFICO_PI02.json with scientific_gates_finalized=true and approval.
This is independent of closed_for_authoring: final Word publication may follow
actual product adoption, so no authoring/adoption dependency cycle is created.
"""
from pathlib import Path
import argparse,ast,datetime,hashlib,importlib.util,json,os
P=Path(__file__).resolve().parent.parent;R=P.parent.parent.parent
C=R/'DEE Cognitive 2.0';S=C/'sistema';CS=P/'estados/candidato/sistema'
LIFE='ECI02_PI02_MAIN';PARENT='ECI02_PI01_MAIN';PARENT_T=735843
PARENT_SHA='4c585112f33b126a0ee6114e19ef203f0bab658f76545636a6e70f573d628a50'
CODE_FILES=[
 'app/mundo_genesis_apd05.py','app/cola_local.py',
 'capacidades/progresion_integrada_02.py','capacidades/pi02_desarrollo_base.py',
 'capacidades/pi02_retornos_base.py','capacidades/pi02_diagnostico_base.py',
 'capacidades/fi_async_R03.py','capacidades/diagnostico_FI_R03.py',
 'capacidades/pi02_advertencia_R03.py','capacidades/adapter_habitat_R04.py',
 'capacidades/pi02_habitat_R04.py','capacidades/fi_async_R04.py',
 'capacidades/diagnostico_puertos_OH_R04.py'
]
GATES=('functional_gain','conservation','source_reopening','new_function_at_final_cut')
MODES=['eci01-pi02-habitat-preparar','eci01-pi02-tiempo','eci01-pi02-pausar-habitat','eci01-pi02-reactivar-habitat','eci01-pi02-habitat-estado','eci01-pi02-habitat-trabajo']
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def descriptor(p):return {'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
def local(value):
    path=Path(value);path=path if path.is_absolute()else P/path
    path=path.resolve(strict=True)
    if not path.is_relative_to(P.resolve()):raise ValueError('Evidence must remain in this campaign:'+str(path))
    if not path.is_file()or path.is_symlink():raise ValueError('Literal evidence file required')
    return path
def evidence(item):
    if isinstance(item,str):return descriptor(local(item))
    if not isinstance(item,dict)or 'path'not in item:raise ValueError('Evidence needs a relative/absolute campaign path')
    path=local(item['path']);actual=descriptor(path)
    if item.get('sha256')and item['sha256']!=actual['sha256']:raise ValueError('Root-approved evidence hash changed:'+str(path))
    return {**item,**actual}
def dependency_check():
    """Static import closure; unchanged product dependencies are reused."""
    queue=list(CODE_FILES);seen=set();stable=[];missing=[]
    while queue:
        relative=queue.pop(0)
        if relative in seen:continue
        seen.add(relative);path=CS/relative
        if not path.is_file():missing.append({'file':relative,'reason':'Missing candidate module'});continue
        tree=ast.parse(path.read_text(encoding='utf-8-sig'));names=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):names.extend(alias.name for alias in node.names)
            elif isinstance(node,ast.ImportFrom):
                name=node.module or''
                if node.level:
                    parent=list(Path(relative).parts[:-1]);prefix=parent[:len(parent)-node.level+1]
                    name='.'.join(prefix+([name]if name else[]))
                if name in('app','capacidades'):names.extend(name+'.'+alias.name for alias in node.names if alias.name!='*')
                else:names.append(name)
        for name in names:
            parts=name.split('.')
            if len(parts)<2 or parts[0]not in('app','capacidades'):continue
            child='/'.join(parts)+'.py';src=CS/child
            if not src.is_file():continue # Named classes/external legacy modules are not guessed as files.
            if child not in CODE_FILES:
                product=S/child
                if not product.is_file()or sha(product)!=sha(src):missing.append({'file':child,'required_by':relative,'reason':'Unlisted changed or unavailable local dependency'})
                elif child not in{row['file']for row in stable}:stable.append({'file':child,'sha256':sha(src),'reused_unchanged_product_module':True})
            if child not in seen:queue.append(child)
    if missing:raise ValueError('The exact13-module plan is not sufficient:'+json.dumps(missing,ensure_ascii=False))
    return {'scope':'Static Python import closure, including lazy branches; no imported modules executed','modules_text_inspected':len(seen),'unchanged_dependencies_reused':stable,'missing_changed_dependencies':[]}
def pair_descriptor(data):
    if isinstance(data.get('pair'),dict):return data['pair']
    result=data.get('result',{})
    if isinstance(result,dict)and isinstance(result.get('paired_export'),dict):return result['paired_export']
    raise ValueError('PAR_FINAL_PI02 must identify the actual complete paired export')
def build(closure_path,pairfile,out):
    if out.exists():raise FileExistsError('An existing final decision must be reviewed, never overwritten')
    closure=read(closure_path);approval=closure.get('operational_adoption')
    if not isinstance(approval,dict)or approval.get('scientific_gates_finalized')is not True or approval.get('approved_for_adoption')is not True:
        raise ValueError('Root must first approve finalized empirical gates in operational_adoption; Word closed_for_authoring is deliberately independent')
    for field in('scope','gains','losses','uncertainties','assistance','regression_coverage','gates'):
        if field not in approval:raise ValueError('Missing reasoned operational approval:'+field)
    if any(marker in json.dumps(approval,ensure_ascii=False)for marker in('BORRADOR_NO_FINAL','T_FINAL_REAL','SHA_DEL_')):raise ValueError('Operational approval still contains unfinished placeholders')
    card_path=CS/'estado/vidas'/LIFE/'VIDA.json';card=read(card_path);cut=card['physical']
    if cut['N']!=67 or cut['tick']<=PARENT_T or card['operations'][-1].get('kind')!='PERSISTENT_GRACEFUL_CLOSE':raise ValueError('A real closed N67 final candidate is required')
    if (CS/'estado/locks'/(card['world_id']+'.lock')).exists()or(card_path.parent/'FUTURO_INTERRUMPIDO.json').exists():raise ValueError('Candidate still has a writer or interrupted future; no final decision may be generated')
    if sha(CS/card['snapshot'])!=card['snapshot_sha256']:raise ValueError('Final source snapshot bytes differ')
    if card.get('PI02_provenance',{}).get('physical_parent_life')!=PARENT:raise ValueError('Candidate has no explicit PI01 physical-history provenance')
    parent=read(S/'estado/vidas'/PARENT/'VIDA.json')
    if read(S/'estado/ACTIVO.json')['life_id']!=PARENT or parent['physical']['tick']!=PARENT_T or parent['snapshot_sha256']!=PARENT_SHA or sha(S/parent['snapshot'])!=PARENT_SHA:raise ValueError('Protected principal advanced or selection changed; reconcile before building')
    descriptor_source=read(pairfile);pair=pair_descriptor(descriptor_source);directory=Path(pair['directory']).resolve(strict=True)
    if not directory.is_relative_to(P.resolve()):raise ValueError('Final paired source must be in this campaign')
    manifest_path=directory/'EXPORTACION_SERVICIO.json';manifest=read(manifest_path)
    if sha(manifest_path)!=pair['manifest_sha256']or manifest['life_id']!=LIFE:raise ValueError('Final pair manifest does not match')
    if any(manifest['physical'][key]!=cut[key]for key in('N','tick','RAW_sha256','clocks_sha256')):raise ValueError('Pair is not the actual final physical cut')
    if descriptor_source.get('source_tick',cut['tick'])!=cut['tick']:raise ValueError('Pair descriptor/source current cut differ')
    gates={}
    for name in GATES:
        gate=approval['gates'].get(name)
        if not isinstance(gate,dict)or gate.get('satisfied')is not True or not gate.get('criterion')or not gate.get('result')or not gate.get('evidence'):
            raise ValueError('Root must approve a reasoned completed gate:'+name)
        gates[name]={**gate,'evidence':[evidence(item)for item in gate['evidence']]}
    through=gates['new_function_at_final_cut'].get('through_tick')
    if through!=cut['tick']:raise ValueError('New-function gate must explicitly identify through_tick equal to the real final cut; do not reuse an earlier panel as current')
    prep=read(P/'control/PREPARACION_CODIGO_PI02.json');baselines={item['file']:item['sha256']for item in prep['copied_files']}
    files=[]
    for relative in CODE_FILES:
        source=CS/relative;product=S/relative
        ast.parse(source.read_text(encoding='utf-8-sig'))
        before=sha(product)if product.is_file()else None
        if before is not None and baselines.get(relative)!=before:raise ValueError('Original product code changed since baseline:'+relative)
        files.append({'file':relative,'sha256':sha(source),'product_before_sha256':before})
    wrapper=ast.parse((CS/'capacidades/progresion_integrada_02.py').read_text(encoding='utf-8-sig'))
    strings={node.value for node in ast.walk(wrapper)if isinstance(node,ast.Constant)and isinstance(node.value,str)}
    if not set(MODES)<=strings:raise ValueError('The operational wrapper does not contain all declared R04/OP1 API modes; do not publish a nonexistent work API')
    dependencies=dependency_check()
    physical_parent={'life_id':PARENT,'tick':PARENT_T,'snapshot_sha256':PARENT_SHA}
    default_contract={'schema':'DEE.PI02.bounded_operational_contract.R04.OP1','version':approval.get('version','PI02.R04.OP1'),'life_id':LIFE,
      'source_cut':{'N':67,'tick':cut['tick'],'snapshot_sha256':card['snapshot_sha256']},'physical_parent':physical_parent,
      'scope':approval['scope'],'implementation':CODE_FILES,'gains':approval['gains'],'losses':approval['losses'],'assistance':approval['assistance'],'limits':approval.get('limits',approval['uncertainties']),
      'operator_literals':MODES,'initiative_scope':'Generic elapsed time and environment opportunities remain prepared; any acquired selection is limited to its actual recorded history and controls.',
      'continuity':'Keep full Native state, paired SQLite/outbox, R04 journal, resources/control packets and all operational progress. Never rebuildT0, reset the bank, refill coupons silently or fuse control histories.',
      'work_api_scope':'habitat-trabajo appends a bounded external public opportunity; it is not a Native action, policy update, new teaching or resource self-supply. Actual subsequent work still requires Native events and elapsed time.',
      'resource_scope':'64byte artifacts and finite control packets belong to a simulated local environment, not energy or biological food.',
      'source_empirical_gates':gates,'no_general_R2_or_consciousness_verdict':True,
      'owner_command':'motor/python313/python.exe -I -B -X utf8 sistema/gestionar.py mente-unificada-iniciar --vida ECI02_PI02_MAIN --backend mente_unificada --eci01 --pausado --intervalo 60 --guardar-cada 3600 --max-segundos 7200',
      'state_literal':[{'modo':'eci01-pi02-habitat-estado'}],
      'historical_panel_scope':'Use the actual panel gate/cut; no automatic12use claim at a later final tick.'}
    new_contract=approval.get('new_contract',{'file':'contratos/PROGRESION_INTEGRADA_02_R04.json','document':default_contract})
    new_contract=dict(new_contract);contract_product=S/new_contract['file']
    new_contract.setdefault('product_before_sha256',sha(contract_product)if contract_product.is_file()else None)
    catalog=approval.get('catalog_entry',{'id':'PI02_TRABAJO_CONTINUO_Y_ACCESO_R04','version':approval.get('version','PI02.R04.OP1'),'availability':'OPERATIVO_DOMINIO_ACOTADO','integration':approval['scope'],'physical_parent':physical_parent,'scope':approval['scope']})
    refs=[evidence(item)for item in approval.get('evidence',[])]
    if not refs:
        seen=set()
        for gate in gates.values():
            for item in gate['evidence']:
                key=(item['path'],item['sha256'])
                if key not in seen:refs.append(item);seen.add(key)
    decision={'schema':'PI02.reasoned_final_operational_decision.v1','built_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'approved_for_adoption':True,'life_id':LIFE,'decision_id':approval.get('decision_id','PI02_ADOPCION_OPERATIVA_01'),
      'desired_cut':{'N':67,'tick':cut['tick'],'snapshot_sha256':card['snapshot_sha256']},'pair':pair,
      'physical_parent':physical_parent,'genealogy_scope':'One actual main history. The imported final transport container is not the original physical parent. No control memories merged.',
      'approved_code_files':files,'gates':gates,'scope':approval['scope'],'gains':approval['gains'],'losses':approval['losses'],'uncertainties':approval['uncertainties'],'assistance':approval['assistance'],
      'limits':approval.get('limits',approval['uncertainties']),'evidence':refs,'regression_coverage':approval['regression_coverage'],
      'process_proof':str(Path(approval.get('process_proof',P/'control/PROCESOS_PRE_INCORPORACION_PI02.json'))),
      'catalog_entry':catalog,'new_contract':new_contract,'affected_contract_updates':approval.get('affected_contract_updates',[]),
      'authoring_input_at_build_historical':descriptor(closure_path),'final_pair_descriptor_at_build':descriptor(pairfile),
      'static_dependency_closure':dependencies,'Native_imports_by_builder':0,'new_ticks_by_builder':0,
      'approval_is_not_adoption':'Actual product import/reopening and Store.promoteCOMMITTED must still occur. No scientific experiment is repeated by this builder.'}
    if not Path(decision['process_proof']).is_absolute():decision['process_proof']=str(P/decision['process_proof'])
    pending=out.with_name(out.name+'.validated_build_tmp')
    if pending.exists():raise FileExistsError('An incomplete prospective decision is preserved; inspect before another build')
    pending.write_text(json.dumps(decision,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Reuse the incorporation helper's existing passive validation; its Native
    # imports occur only in prepare/adopt functions, not at module import.
    helper=P/'codigo/incorporar_PI02.py';spec=importlib.util.spec_from_file_location('pi02_decision_validation_only',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.load_decision(pending)
    if any(name.startswith('dee_thinking')for name in __import__('sys').modules):raise RuntimeError('Unexpected Native import while building the decision')
    if out.exists():raise FileExistsError('Another final decision appeared; do not replace it')
    os.replace(pending,out)
    return {'decision':descriptor(out),'actual_source_tick':cut['tick'],'approved_code_modules':len(files),'unchanged_dependencies_reused':len(dependencies['unchanged_dependencies_reused']),'Native_imports':0,'new_ticks':0,'product_changed':False}
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--closure',type=Path,default=P/'control/CIERRE_CIENTIFICO_PI02.json');parser.add_argument('--pair',type=Path,default=P/'control/PAR_FINAL_PI02.json');parser.add_argument('--out',type=Path,default=P/'control/DECISION_FINAL_PI02.json');parser.add_argument('--write',action='store_true');args=parser.parse_args()
    if not args.write:
        print(json.dumps({'mode':'STATIC_PLAN_NO_NATIVE_NO_WRITES','closure_exists':args.closure.is_file(),'pair_exists':args.pair.is_file(),'operational_approval_section':'operational_adoption, scientific_gates_finalized=true and approved_for_adoption=true','word_authoring_flag_is_independent':True,'required_gates':GATES,'required_final_function_cut_field':'gates.new_function_at_final_cut.through_tick equals actual closed source VIDA tick','exact_code_files':CODE_FILES,'code_module_count':len(CODE_FILES),'next':'Only root fills the real empirical approval after controls, panel and source reopening. Then --write constructs the decision but does not import or promote.'},ensure_ascii=False,indent=2));return
    print(json.dumps(build(args.closure,args.pair,args.out),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
