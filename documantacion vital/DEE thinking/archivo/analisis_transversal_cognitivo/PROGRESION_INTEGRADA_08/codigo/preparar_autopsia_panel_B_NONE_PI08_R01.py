"""Prepare one prospective diagnostic on the existing None continuation only."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';SOURCE=H/'ejecutar_conservacion_B_PI08_R02.py'
DEST=H/'ejecutar_autopsia_panel_B_NONE_PI08_R01.py'
PROTOCOL=P/'control/PROTOCOLO_AUTOPSIA_PANEL_B_NONE_PI08_R01.json'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def require(ok,text):
 if not ok:raise ValueError(text)
spec=importlib.util.spec_from_file_location('preserved_panel_plan_only',SOURCE);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_NONE_01';system=P/'estados/B_NONE_R01/sistema'
card=read(system/'estado/vidas'/life/'VIDA.json');closed=P/'control/PI08_B_NONE_R01.json';real=P/'control/PI08_B_CONSERVACION_R02.json'
require(card['physical']['tick']==875451 and read(closed)['closed']is True,'Exact existing closed None18 required')
protocol={'schema':'DEE.PI08.B.existing_NONE_panel_autopsy.prospective.R01','status':'SEALED_BEFORE_AUTOPSY_NATIVE','prepared_utc':datetime.now(timezone.utc).isoformat(),
 'existing_life_id':life,'new_worlds':0,'source_system':str(system),'initial_tick':875451,'source_snapshot_sha256':card['snapshot_sha256'],
 'source_closed18':{'path':str(closed),'sha256':sha(closed)},'reference_real_panel':{'path':str(real),'sha256':sha(real)},
 'source_full_pair_required_before_any_advance':str(P/'pares/PI08_B_NONE_POST18_T875451'),
 'source_full_pair_contents':'Native snapshot, closed SQLite, all outbox/worker/resource files and every empty directory; an isolated snapshot is insufficient.',
 'panel_recipe_sha256':sha(old.PANEL),'literal_steps':old.plan(),'finite_Native_bound':8684,'latest_start_local':'2026-11-10T18:15:00-06:00',
 'C2C_material_use':False,'C2C_state_before_after':True,'B_START_or_EPISODE':False,'B_KEY_progress_unchanged_required':True,
 'comparison':'Same nominal12-step panel and same initial absolute phase as the real conservation clone. Native outcomes, actual dynamic numeric binding, phases and doses are recorded; no equality is assumed.',
 'not_allowed':['restore/reset/reimport','rewrite_B_KEY_or_policy','correct_operand_to13','new_Native_reader_or_provider','automatic_retry','promote_B_from_this_control'],
 'interpretation_limits':['This is a new diagnostic in an existing future, not a fifth original B cohort or a redo of the18-opportunity comparison.','None-source RAW may differ from Real after18; no single microcausal explanation is guaranteed.','The original B10/12 conservation failure remains false regardless of this new diagnostic result.'],
 'source_runner':{'path':str(SOURCE),'sha256':sha(SOURCE)}}
put(PROTOCOL,protocol)
t=SOURCE.read_text('utf-8-sig')
def replace(oldtext,newtext):
 global t
 require(t.count(oldtext)==1,'Expected unique reviewed anchor: '+oldtext[:90]);t=t.replace(oldtext,newtext)
first=t.index('"""',3)+3
t='"""Root-only prospective panel on the EXISTING closed None18 future.\n\nNo clone, role re-admission, B episode, reset, repair or new provider. Preserve\nthe complete None prefix before advancing. This never repairs the B gate.\n"""'+t[first:]
replace('BOUND = 10184  # 7*512 +2*600 +3*1300 +1*1500; STATE/pause exactly0.',"BOUND = 8684  # Same12 witnesses; omit only the later C2C material use.\nAUTOPROTOCOL=P/'control/PROTOCOLO_AUTOPSIA_PANEL_B_NONE_PI08_R01.json'\nAUTOPROTOCOL_SHA='"+sha(PROTOCOL)+"'")
replace("'additional_C2C': {'modo': 'eci01-pi04-c2c-oportunidad'},\n            'C2C_expected_ordinal': 31,", "'additional_C2C': None,\n            'C2C_ordinal_preserved': 31,")
replace("'conservation_identity': 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_CONSERVACION_01'", "'existing_None_identity': 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_NONE_01'")
replace("seal = read(SEAL); life = seal['conservation_life_id']; real = seal['research_life_ids']['real']", "seal = read(SEAL); life = seal['research_life_ids']['none']; real = life\n    require(sha(AUTOPROTOCOL)==AUTOPROTOCOL_SHA,'Prospective None autopsy protocol changed')\n    autop=read(AUTOPROTOCOL); require(plan()==autop['literal_steps'],'Literal panel differs from sealed autopsy')\n    require(datetime.now(timezone.utc)<datetime.fromisoformat(autop['latest_start_local']).astimezone(timezone.utc),'Start deadline18:15 reached')")
replace("require(life == 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_CONSERVACION_01', 'Prospectively fixed read-only B conservation identity required')", "require(life == 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_NONE_01', 'Only the existing sealed None identity')")
replace("require(manifest['life_id'] == real and manifest['physical']['tick'] == args.tick_inicial,\n            'Actual final closed B_REAL full prefix required; no A or RAW-only substitute')", "require(manifest['life_id']==life and manifest['physical']['tick']==args.tick_inicial==875451 and manifest['snapshot_sha256']==autop['source_snapshot_sha256'],'Exact preserved full None18 prefix required')\n    preservation=read(prefix.parent/(prefix.name+'_PRESERVACION.json'))\n    require(preservation['source_files_all_unchanged']is True and preservation['manifest_sha256']==sha(prefix/'EXPORTACION_SERVICIO.json'),'Complete checked None preservation required')\n    require(sha(prefix/manifest['native_snapshot'])==manifest['snapshot_sha256'],'Preserved Native bytes changed')")
replace("require(mapping['source_life_id'] == real and mapping['verification']['manifest_sha256'] == sha(prefix / 'EXPORTACION_SERVICIO.json'),\n            'Conservation clone was not imported from the declared B_REAL pair')", "require(mapping['source_life_id']==A and mapping['verification']['manifest_sha256']==seal['source_prefix']['manifest_sha256'],'Existing None must retain its original A import mapping; no reimport')")
replace("require(card['physical']['N'] == 67 and card['physical']['tick'] == args.tick_inicial, 'No stale restore or prior material use of conservation future')", "require(system==(P/'estados/B_NONE_R01/sistema').resolve()and card['physical']['N']==67 and card['physical']['tick']==args.tick_inicial==875451 and card['snapshot_sha256']==autop['source_snapshot_sha256'],'No stale restore or prior new use of this None future')")
replace("bbefore['progress']['control']['arm'] == 'real'", "bbefore['progress']['control']['arm'] == 'none'")
replace("'Only completed real18 continuation is tested; no arbitrary development prefix'", "'Only the preserved existing None18 continuation; no role reset'")
start=t.index("            cuse = material('C2C31'")
end=t.index("            bafter = material('B_post'",start)
t=t[:start]+t[end:]
replace("require(cafter['progress']['ordinal'] == cafter['device']['ordinal'] == 32, 'Last C2C opportunity did not close exactly once')", "require(cafter['progress']==cpre['progress']and cafter['device']==cpre['device'],'C2C resource/history must remain literal; no material C2C use')")
replace("and len(witnesses) == 12 and all(r['correct'] for r in witnesses) and c2c.get('correct') is True", "and len(witnesses) == 12 and all(r['correct'] for r in witnesses)")
replace("'schema': 'DEE.PI08.B.real_clone_conservation.R02'", "'schema': 'DEE.PI08.B.existing_NONE_panel_autopsy.R01'")
replace("'source_B_REAL': real", "'source_B_NONE': life")
replace("'C2C_last_offer_product': c2c.get('correct')", "'C2C_material_use': False, 'C2C_resource_unchanged': states.get('C2C_pre')==states.get('C2C_post')")
replace("'B_episode_never_called': True, 'no_promotion_or_reset': True, 'budget_before_ticks': used, 'worlds_before': worlds}", "'B_episode_never_called': True, 'no_promotion_or_reset': True, 'budget_before_ticks': used, 'worlds_before': worlds,\n              'prospective_protocol':{'path':str(AUTOPROTOCOL),'sha256':AUTOPROTOCOL_SHA},\n              'original_B_conservation_gate_remains_false':True, 'reference_real_panel':autop['reference_real_panel']}\n    refrows={r['label']:r for r in read(Path(autop['reference_real_panel']['path']))['rows']}\n    result['phase_and_dose_comparison']=[{'label':r['label'],'before_tick_equal':r['before_tick']==refrows[r['label']]['before_tick'],'after_tick_equal':r['after_tick']==refrows[r['label']]['after_tick'],'current_Native_inputs':r.get('Native_inputs'),'reference_Native_inputs':refrows[r['label']].get('Native_inputs'),'same_nominal_mode':r['literal']['modo']==refrows[r['label']]['literal']['modo']}for r in rows if r['label']in refrows]\n    result['comparison_limits']='Same nominal schedule is not proof of same Native input dose/geometry. Any Native-dependent action or transported-number difference is preserved above; no single-factor causal claim is automatic.'")
replace("default='PI08_B_CONSERVACION_R02'", "default='PI08_B_NONE_AUTOPSIA_PANEL_R01'")
ast.parse(t)
with DEST.open('x',encoding='utf8')as f:f.write(t)
new=importlib.util.spec_from_file_location('new_None_panel_plan_only',DEST);m=importlib.util.module_from_spec(new);new.loader.exec_module(m)
require(old.plan()==m.plan(),'Prospective panel plan must preserve every old literal/path/bound/dynamic binding')
proof=P/'control/PREPARACION_AUTOPSIA_PANEL_B_NONE_PI08_R01.json'
put(proof,{'schema':'DEE.PI08.B.existing_NONE_panel_prepared.R01','Native_executed':False,'source_or_product_modified':False,'new_worlds':0,'runner':{'path':str(DEST),'sha256':sha(DEST)},'protocol':{'path':str(PROTOCOL),'sha256':sha(PROTOCOL)},'literal_plan_equals_original_R02':True,'finite_Native_bound':8684,'source_prefix_must_be_complete_before_execution':True,'source_snapshot_alone_not_sufficient':True})
print(json.dumps({'runner':str(DEST),'runner_sha256':sha(DEST),'protocol_sha256':sha(PROTOCOL),'preparation_proof':str(proof),'Native_executed':False}))
