"""Literal R01 budget ledger plus the exact whole same-ID PI11 movement.

Read-only. The moved MAIN remains one charged world with its original import
tick. It never refunds a failed phase, creates a world, or edits any evidence.
"""
from pathlib import Path
import ast,hashlib,json,types
P=Path(__file__).resolve().parents[1]; C=P.parents[2]/'DEE Cognitive 2.0'
SOURCE=P/'codigo/ledger_PI11_R01.py'
PIN='5d18db1fe9e681b1b580dd52579b40a2a0824b87eb7b5e040c8ccfc37f23e7d2'
MAIN='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_MAIN01'
def ledger():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=PIN: raise ValueError('Reviewed R01 ledger changed')
    cards=sorted((P/'estados').glob('*/sistema/estado/vidas/*/VIDA.json'))
    moved=C/'sistema/estado/vidas'/MAIN/'VIDA.json'; original=P/'estados/MAIN01/sistema/estado/vidas'/MAIN/'VIDA.json'
    mapping=P/'control/MAPA_TRASLADO_PRODUCTO_PI11_R01.json'; included=False
    if moved.exists():
        if original.exists() or not mapping.exists(): raise ValueError('Ambiguous duplicate/unproven moved MAIN')
        proof=json.loads(mapping.read_text('utf-8-sig')); prepared=P/'control/PREPARACION_TRASLADO_PRODUCTO_PI11_R01.json'
        if not prepared.is_file(): raise ValueError('Actual completed same-ID relocation receipt required')
        receipt=json.loads(prepared.read_text('utf-8-sig')); ref=receipt.get('map',{})
        if receipt.get('phase')!='PREPARED_MOVED_NOT_PROMOTED' or receipt.get('life_id')!=MAIN or Path(ref.get('path','')).resolve()!=mapping.resolve() or ref.get('sha256')!=hashlib.sha256(mapping.read_bytes()).hexdigest(): raise ValueError('Exact immutable relocation map CAS required')
        if proof.get('same_life_id')!=MAIN or proof.get('same_world_id')!=MAIN or Path(proof['target_system']).resolve()!=(C/'sistema').resolve() or Path(proof['source_system']).resolve()!=(P/'estados/MAIN01/sistema').resolve(): raise ValueError('Exact complete same-ID movement proof required')
        cards.append(moved); included=True
    text=SOURCE.read_text('utf-8-sig')
    old="for cardfile in sorted((P/'estados').glob('*/sistema/estado/vidas/*/VIDA.json')):"
    if text.count(old)!=1: raise ValueError('Exact R01 card census anchor')
    text=text.replace(old,'for cardfile in EXPLICIT_CURRENT_CARDS:')
    old="initial=cardfile.parents[4]/'IMPORTACION_DIAGNOSTICA.json'"
    if text.count(old)!=1: raise ValueError('Exact R01 immutable import provenance anchor')
    text=text.replace(old,"initial=(P/'estados/MAIN01/IMPORTACION_DIAGNOSTICA.json') if cardfile==EXPLICIT_MOVED_MAIN else cardfile.parents[4]/'IMPORTACION_DIAGNOSTICA.json'")
    ast.parse(text); m=types.ModuleType('PI11_literal_same_ID_budget_continuity'); m.__file__=str(SOURCE); m.EXPLICIT_CURRENT_CARDS=cards; m.EXPLICIT_MOVED_MAIN=moved; exec(compile(text,str(SOURCE)+':exact_same_ID_move_census_only','exec'),m.__dict__)
    result=m.ledger(); extra={}
    for file in (P/'control').glob('PI11_*_OWNER_R*.json'):
        v=json.loads(file.read_text('utf-8-sig'))
        if v.get('schema')!='DEE.PI11.actual_public_interface_owner.R01' or (v.get('closed') is True and v.get('error') is None): continue
        life=v['life_id']
        if life not in result['worlds']: raise ValueError('Public proof refers to missing actual world')
        world=result['worlds'][life]; target=v['initial_tick']-world['import_tick']+v['finite_bound']; extra[life]=max(extra.get(life,0),target-world['observed_native_ticks'],0)
        result['unresolved_reserved_phases'].append({'proof':str(file),'conservatively_charged_bound':v['finite_bound']})
    result['charged_ticks']+=sum(extra.values())
    result.update(schema='DEE.PI11.readonly.aggregate_native_ledger.R02',same_ID_moved_MAIN_included=included,new_worlds_due_to_movement=0,ticks_refunded=0,original_ledger_sha256=PIN); return result
if __name__=='__main__': print(json.dumps(ledger(),ensure_ascii=False,indent=2))
