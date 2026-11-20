"""Root-only complete same-ID PI11 relocation/adoption. Default read-only.

Reuses the pinned whole-state movement engine preserved in PI10. Root must
supply actual scientific gates, code CAS, closed-process evidence, source
conservation/reopening/replay/interface proofs and an exact decision SHA.
No result is manufactured here; bounded positive tradeoffs are allowed only
when the sealed criterion and actual evidence are explicitly recorded.
"""
from pathlib import Path
import argparse,ast,hashlib,json,re,sys,types
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema'
BASE=P.with_name('PROGRESION_INTEGRADA_10')/'codigo/MOTOR_TRASLADO_PI09_R03_LITERAL.py'
BASE_SHA='a4011725610dac74c2fe3322bc83ebdc3b55d2b08ca24a7e3092a4e1ea4b4ea3'
PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01';PARENT_T=947395;PARENT_SHA='fd7372b7f2adc9040866fab8adfaca0d79e0bd18e997c0abc0651fe4fa3c23dc'
CONTRACT='PI11_USO_OPERATIVO_R01.json';SCHEMA='DEE.PI11.exact_operational_permission.R01'
KEY='DEE.Cognitive.PI11.persistent_habitat.native_continuation.R01';PI10KEY='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02'
GATES=('functional_gain','conservation','causal_controls','source_reopening','new_function_at_final_cut','decisive_recipe_replay')
PROOFS=('source_final_owner','conservation_owner','source_reopening_owner','replay_owner','replay_comparison','product_interface_test')
SELECTORS=('PROYECTO.json','CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/ACTIVO.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json')
def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regular(p):
    for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No linked adoption path')
def bounded(p,root=P):
    p=Path(p);regular(p);p=p.resolve(strict=True);need(p.is_relative_to(root.resolve()),'Evidence/code outside declared PI11 campaign');return p
def pointer(value,path):
    for part in path.strip('/').split('/')if path else[]:value=value[int(part)]if isinstance(value,list)else value[part.replace('~1','/').replace('~0','~')]
    return value
def evidence(ref,*,checks_required=False):
    need(isinstance(ref,dict)and {'path','sha256'}<=set(ref),'Exact local evidence reference')
    file=bounded(ref['path']);need(sha(file)==ref['sha256'],'Actual proof bytes changed: '+str(file));v=read(file)
    if checks_required:need(isinstance(ref.get('checks'),dict)and bool(ref['checks']),'Prospectively explicit evidence checks required')
    for path,expected in ref.get('checks',{}).items():need(pointer(v,path)==expected,'Actual evidence check differs: '+path)
    return v
def parent(selected=True):
    card=read(S/'estado/vidas'/PARENT/'VIDA.json');need(card['physical']['N']==67 and card['physical']['tick']==PARENT_T and card['snapshot_sha256']==PARENT_SHA and sha(S/card['snapshot'])==PARENT_SHA,'Protected principal changed or advanced; no stale promotion')
    if selected:need(read(S/'estado/ACTIVO.json')['life_id']==PARENT,'Another principal is selected')
    return card
def decision(file):
    d=read(file);required={'schema','approved_for_adoption','decision_id','life_id','source_system','source_snapshot_sha256','source_tick','source_ordinal','source_code_manifest','gates','proofs','approved_code_files','selectors_cas','catalog_entry','new_contract','scope','gains','losses','uncertainties','assistance','evidence','regression_coverage','process_proof','sealed_criterion'}
    need(required<=set(d)and d['schema']=='DEE.PI11.reasoned_adoption_decision.R01'and d['approved_for_adoption']is True,'Actual explicit Root decision required')
    need(re.fullmatch('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_[A-Z0-9_]{1,20}',d['life_id'])and type(d['source_tick'])is int and d['source_tick']>PARENT_T and re.fullmatch('[a-f0-9]{64}',d['source_snapshot_sha256']),'Actual reached PI11 continuation/cut')
    source=Path(d['source_system']).resolve(strict=True);regular(source);need(source.name=='sistema'and source.parent.parent==(P/'estados').resolve()and not(source/'estado/ACTIVO.json').exists(),'Exact unselected diagnostic source')
    need(set(d['selectors_cas'])==set(SELECTORS)and set(d['gates'])==set(GATES)and set(d['proofs'])==set(PROOFS),'All selector CAS, gates and evidence modalities required')
    sealed=evidence(d['sealed_criterion'],checks_required=True);need(sealed is not None,'Actual prior scientific criterion')
    for name,gate in d['gates'].items():
        need(gate.get('satisfied')is True and gate.get('criterion')and gate.get('result')and isinstance(gate.get('evidence'),list)and bool(gate['evidence']),'Missing actual scientific gate: '+name)
        for ref in gate['evidence']:evidence(ref,checks_required=True)
    for ref in d['evidence']:evidence(ref)
    proofs={name:evidence(ref,checks_required=True)for name,ref in d['proofs'].items()}
    final=proofs['source_final_owner'];need(final.get('life_id')==d['life_id']and final.get('closed')is True and final.get('error')is None and final.get('final_tick')==d['source_tick'],'Exact coherent final source owner proof')
    for name in('conservation_owner','source_reopening_owner'):
        v=proofs[name];need(v.get('life_id')==d['life_id']and v.get('closed')is True and v.get('error')is None,'Actual source preservation/reopening proof: '+name)
    replay=proofs['replay_owner'];need(replay.get('life_id',replay.get('life'))!=d['life_id'],'Replay is an independent diagnostic identity, not source rereading')
    replay_closed=replay.get('closed')is True or(replay.get('status')=='COMPLETED'and replay.get('owner_closed_coherently')is True)
    need(replay_closed and replay.get('error')is None,'Actual coherently closed Native replay')
    interface=proofs['product_interface_test'];need(interface.get('Native_executed')is True and interface.get('owner_closed')is True and interface.get('material_use_completed')is True and interface.get('product_originals_modified')is False,'Actual isolated material interface test before adoption')
    c=d['new_contract'];need(c.get('schema')==SCHEMA and c.get('life_id')==d['life_id']and c.get('profile')=='fisica_directa'and c.get('N')==67 and c.get('status')=='PREPARED_DIAGNOSTIC'and c.get('all_adoption_gates_met')is True and c.get('adoption_decision_sha256')is None,'Exact separately prepared PI11 permission')
    need(c.get('allowed_modes')==['eci01-pi11-episodio','eci01-pi11-estado']and c.get('PI10_material_disabled')is True and c.get('historical_material_disabled')is True and c.get('public_FI_backend')=='PI11_new_FI8_same_frozen_body'and c.get('new_FI8_key')=='DEE.Cognitive.PI11.explicit_FI_eight_offer_lot.R01'and c.get('new_FI8_total')==8 and c.get('public_FI_domain')==[0,20]and c.get('internal_FI_redirected')is False and c.get('public_arithmetic_policy')=='legacy_partial','Explicit new eight-offer supply, no old reset, FI body reroute or historical calendar reopening')
    need(c.get('previous_principal')=={'life_id':PARENT,'tick':PARENT_T,'snapshot_sha256':PARENT_SHA}and c.get('source_ordinal')==d['source_ordinal']and 1<=d['source_ordinal']<24,'Exact parent and unexhausted reached habitat')
    need(c.get('PI11_protocol_sha256')==sha(source/'capacidades/PROTOCOLO_PI11_R01.json')and c.get('C2C_protocol_sha256')=='0cf6bf8508e071a1c8cf1448023a096bc43336d66b8a1deb98f488b29b4205fd','Exact scientific protocol bindings')
    parent();return d
def code(d,b):
    source=Path(d['source_system']).resolve();rows=[];seen=set()
    for row in d['approved_code_files']:
        rel=b.relative(row['file']);name=rel.as_posix();f=Path(row['source']).resolve(strict=True);regular(f);target=S/rel
        need(name not in seen and(f.is_relative_to(source)or f.is_relative_to(H.resolve()))and f.suffix in('.py','.json')and(rel.parts[0]in('app','capacidades','contratos')or name=='gestionar.py'),'Only explicit local Cognitive code/config delta')
        need(sha(f)==row['sha256']and(sha(target)if target.exists()else None)==row.get('before_sha256'),'Code CAS mismatch: '+name)
        ast.parse(f.read_bytes())if f.suffix=='.py'else read(f)
        if rel.parts[0]=='contratos':
            need(name in('contratos/'+CONTRACT,'contratos/PI10_USO_OPERATIVO_R01.json'),'No unrelated contract deployment')
            if name=='contratos/'+CONTRACT:need(read(f)==d['new_contract'],'Exact prepared permission')
            else:need(sha(f)==sha(target),'PI10 contract must remain literal and be included in rollback backup')
        seen.add(name);rows.append({**row,'source':str(f),'target':str(target),'bytes':f.stat().st_size})
    manifest=evidence(d['source_code_manifest'])
    for row in manifest['files']:
        name=row['file']
        if name in seen:continue
        target=S/b.relative(name);need(target.is_file()and sha(target)==row['sha256'],'Uncovered source dependency: '+name);seen.add(name)
    required={'app/mundo_genesis_apd05.py','app/cola_local.py','app/pi11_identidad_c2c_R01.py','app/pi11_gestor_publico_R01.py','gestionar.py','capacidades/pi11_actor_R01.py','capacidades/pi11_habitat_persistente_R01.py','capacidades/pi11_identidad_heredada_R01.py','capacidades/pi11_identidad_heredada_R02.py','capacidades/pi11_dispatcher_R01.py','capacidades/pi11_lote_FI8_R01.py','capacidades/PI11_FI8_SUMINISTRO_R01.json','capacidades/PROTOCOLO_PI11_R01.json','capacidades/PI11_EXPERIMENTO_R01.json','capacidades/PI11_PLUGINS_R01.json','contratos/'+CONTRACT,'contratos/PI10_USO_OPERATIVO_R01.json'}
    need(required<=seen,'Complete PI11 public/ancestral/permission closure')
    for name,digest in d['new_contract']['frozen_files_sha256'].items():
        rel='capacidades/'+name;approved=next((r for r in rows if r['file']==rel),None);path=Path(approved['source'])if approved else S/rel;need(sha(path)==digest,'Frozen permission/code differs: '+name)
    return rows
def base(d):
    need(sha(BASE)==BASE_SHA,'Preserved whole-state movement engine changed')
    text=BASE.read_text('utf-8-sig')
    replacements={'PI09_CONSULTA_OPERATIVA_R01.json':CONTRACT,'app.pi09_identidad_c2c_R01':'app.pi11_identidad_c2c_R01','MAPA_TRASLADO_PRODUCTO_PI09.json':'MAPA_TRASLADO_PRODUCTO_PI11_R01.json','DECISION_PROMOCION_PRODUCTO_PI09.json':'DECISION_PROMOCION_PRODUCTO_PI11_R01.json','PERFIL_PREPARADO_ANTES_COMMITTED_PI09.json':'PERFIL_PREPARADO_ANTES_COMMITTED_PI11_R01.json','DEE.PI09.same_identity.prepared_product.R01':'DEE.PI11.same_identity.prepared_product.R01','DEE.PI09.same_identity.adopted_product.R01':'DEE.PI11.same_identity.adopted_product.R01','DEE.PI09.exact_native_consultation_permission.v1':SCHEMA,'prior_selection_PI09':'prior_selection_PI11','prior_cut_PI09':'prior_cut_PI11','PI09_prior_selected_seed':'PI11_prior_selected_seed','PI09_prior_current_principal':'PI11_prior_current_principal'}
    for old,new in replacements.items():text=text.replace(old,new)
    text=text.replace("'source_PI09_NATIVE_closed12':d['PI09_actual_closed_arms']['native_real']","'source_PI11_actual_closed_use':d['proofs']['source_final_owner']")
    text=text.replace('Actual Native12 source before same-ID relocation. Selected public use remains a separate operational test.','Actual PI11 acquired history before same-ID relocation. Selected material use remains a separate operational test.')
    b=types.ModuleType('PI11_whole_same_identity_movement');b.__file__=str(BASE);exec(compile(text,str(BASE)+':PI11_administrative_scope_only','exec'),b.__dict__)
    b.P=P;b.C=C;b.S=S;b.CS=Path(d['source_system']).resolve();b.H=H;b.CONTROL=P/'control';b.LIFE=d['life_id'];b.PARENT=PARENT;b.PARENT_T=PARENT_T;b.PARENT_SHA=PARENT_SHA;b.GATES=GATES
    b.PREPARED=P/'control/PREPARACION_TRASLADO_PRODUCTO_PI11_R01.json';b.ADOPTED=P/'control/ADOPCION_PRODUCTO_PI11_R01.json';b.INTENT=P/'control/TRASLADO_PRODUCTO_PI11_R01_EN_CURSO.json';b.BACKUP=P/'control/RESPALDO_INCORPORACION_PI11_R01'
    original_inventory=b.inventory
    def inventory(data):
        card,roots,snapshots,items=original_inventory(data);v=b.parser().snapshot_view(b.CS/card['snapshot']);m=json.loads(v['metadata'][KEY]);old=v['metadata'][PI10KEY];scope=read(b.CS/'capacidades/PI11_EXPERIMENTO_R01.json')
        need(m.get('ready')and m.get('ordinal')==data['source_ordinal']==len(m.get('rows',[]))and not m.get('pending')and not m.get('uncertain'),'Exact closed source PI11 history')
        need(scope.get('life_id')==data['life_id']and scope.get('return_arm')=='real'and scope.get('continuation')=='native','Only the real accumulated candidate, never a control or forced continuation')
        need(hashlib.sha256(old.encode('utf8')).hexdigest()==data['new_contract']['PI10_history_sha256'],'No inherited PI10 progress reset or rewrite')
        environment=read(b.CS/'estado/servicios_locales'/data['life_id']/'PI11_HABITAT_ADAPTATIVO_R01/PI11_HABITAT_R01/ESTADO.json')
        need(environment['tick']==data['source_tick']and environment['open_offer']is None,'Complete saved habitat/Native coherence')
        return card,roots,snapshots,items
    b.inventory=inventory;b.parent=parent;b.decision=decision;b.code=lambda data:code(data,b)
    original_adopt=b.adopt
    def adopt(data,file,reopening,process):
        need(read(S/'contratos'/CONTRACT)==data['new_contract'],'Actual exact PREPARED permission before Store.promote')
        return original_adopt(data,file,reopening,process)
    b.adopt=adopt;return b
def main():
    ap=argparse.ArgumentParser(description=__doc__);g=ap.add_mutually_exclusive_group();g.add_argument('--prepare-move',action='store_true');g.add_argument('--adopt',action='store_true');ap.add_argument('--decision',type=Path);ap.add_argument('--decision-sha256');ap.add_argument('--process-proof',type=Path);ap.add_argument('--reopening-proof',type=Path);a=ap.parse_args()
    if a.decision is None:
        need(not a.prepare_move and not a.adopt,'An exact final decision is mandatory')
        print(json.dumps({'mode':'READ_ONLY_NO_NATIVE_IMPORT_NO_WRITES','gates':GATES,'proofs':PROOFS,'selectors':SELECTORS,'protected_principal':PARENT,'protected_tick':PARENT_T,'execution_requires':'exact decision SHA, fresh closed-process proof; adoption also actual moved unselected reopening0'}));return
    file=bounded(a.decision);d=decision(file);b=base(d)
    if not a.prepare_move and not a.adopt:
        print(json.dumps({'mode':'VALIDATED_READ_ONLY','life_id':d['life_id'],'decision_sha256':sha(file),'Native_imported':False,'writes':0}));return
    need(sha(file)==a.decision_sha256,'Explicit actual sealed decision hash required for any administrative effect')
    process=a.process_proof or Path(d['process_proof'])
    if a.adopt:need(a.reopening_proof is not None,'Actual unselected reopening0 witness required')
    result=b.prepare(d,file,process)if a.prepare_move else b.adopt(d,file,b.bounded(a.reopening_proof,P),process)
    print(json.dumps({'proof':str(b.PREPARED if a.prepare_move else b.ADOPTED),'phase':result['phase'],'new_ticks':0},ensure_ascii=False))
if __name__=='__main__':main()
