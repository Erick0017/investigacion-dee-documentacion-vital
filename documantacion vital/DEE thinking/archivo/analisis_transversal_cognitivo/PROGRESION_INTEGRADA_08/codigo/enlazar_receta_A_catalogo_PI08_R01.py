"""Root-only additive catalogue link to the actual preserved A RP recipe.

No Native imports, requests, state, selection or old entry replacement.
"""
from pathlib import Path
import argparse, hashlib, json, os
from datetime import datetime, timezone

P = Path(__file__).resolve().parents[1]
C = P.parents[2] / 'DEE Cognitive 2.0'
S = C / 'sistema'
RID = 'pi08_a_consolidada_uso_T861426_R02'

def read(p): return json.loads(p.read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main(a):
    cat = S/'capacidades/CATALOGO_CAPACIDADES.json'
    before = cat.read_bytes(); data = json.loads(before)
    recipe = C/'reproducibilidad/recetas'/(RID+'.json')
    verification = P/'control/RP_A_REQUISITOS_CLI_PI08_R02.json'
    replay = P/'control/RP_A01_REAL_PI08_R01.json'
    linked = P/'control/RP_A_CONSOLIDADA_INCORPORADA_PI08_R02.json'
    if not read(linked)['applied'] or read(verification)['exit_code'] != 0:
        raise ValueError('Actual RP incorporation and successful CLI requirements proof required')
    v = read(verification)['original_stdout'][0]
    if not v['requirements_available'] or v['DEE_imports'] != 0 or v['new_native_ticks'] != 0:
        raise ValueError('Do not infer material success from requirements')
    entry = next(e for e in data['entries'] if e['id']=='PI08_REGULACION_ADQUIRIDA_CONSOLIDADA_A_01')
    field = 'PI08_preserved_reproducibility'
    if field in entry: raise ValueError('Existing link must not be silently overwritten')
    entry[field] = {
        'recipe_id': RID, 'recipe_relative': 'reproducibilidad/recetas/'+RID+'.json',
        'recipe_sha256': sha(recipe), 'requirements_available': True,
        'requirements_CLI_proof': {'path': str(verification), 'sha256': sha(verification)},
        'incorporation_proof': {'path': str(linked), 'sha256': sha(linked)},
        'complete_prefix': 'reproducibilidad/materiales/PI08_A_CONSOLIDADA_T861426',
        'new_recipe_material_replay_verified': False,
        'historical_decisive_RP_replay': {'path': str(replay), 'sha256': sha(replay)},
        'scope': 'New current-prefix recipe requirements and documentary recalculation verified; its future OP12 is prepared, not materially replayed. Earlier POST4→OP4 decisive recipe was actually replayed separately.'
    }
    proof = P/'control/RECETA_A_ENLAZADA_CATALOGO_PI08_R01.json'
    backup = P/'control/CATALOGO_ANTES_ENLACE_RECETA_A_PI08_R01.json'
    if proof.exists() or backup.exists(): raise ValueError('Preserve prior application')
    if not a.aplicar:
        print(json.dumps({'mode': 'PLAN_ONLY', 'id': entry['id'], 'added_field': field, 'Native_ticks': 0}))
        return
    backup.write_bytes(before)
    if cat.read_bytes() != before: raise ValueError('Concurrent catalogue change')
    temporary = cat.with_name(cat.name+'.PI08_A_RECIPE_WRITING')
    with temporary.open('xb') as out:
        out.write((json.dumps(data, ensure_ascii=False, indent=2)+'\n').encode('utf8'))
        out.flush(); os.fsync(out.fileno())
    os.replace(temporary, cat)
    result={'schema':'DEE.PI08.actual_recipe_catalogue_link.v1','at_utc':datetime.now(timezone.utc).isoformat(),
            'applied':True,'catalogue':str(cat),'before_sha256':hashlib.sha256(before).hexdigest(),
            'after_sha256':sha(cat),'added_field':field,'life':entry['validated_lives'][0]['life_id'],
            'new_Native_ticks':0,'DEE_imports':0,'selected_or_physical_state_modified':False}
    with proof.open('x',encoding='utf8')as out:json.dump(result,out,ensure_ascii=False,indent=2);out.write('\n')
    print(json.dumps({'proof':str(proof),'sha256':sha(proof),'Native_ticks':0}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--aplicar',action='store_true');main(ap.parse_args())
