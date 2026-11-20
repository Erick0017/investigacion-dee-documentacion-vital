"""Prepare OP2 from preserved OP1; add an explicit material flag for new recipes.

Existing recipes keep their interface. No Native, RP deployment or state change.
"""
from pathlib import Path
import ast
import hashlib
import json

P = Path(__file__).resolve().parents[1]
BASE = P / 'codigo/RP_C2C_PROPUESTA_OP1'
OUT = P / 'codigo/RP_C2C_PROPUESTA_OP2'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def once(s, old, new):
    if s.count(old) != 1: raise ValueError('Changed explicit source locator')
    return s.replace(old, new, 1)


def main():
    if OUT.exists(): raise ValueError('Preserve previous proposal')
    revision = json.loads((BASE / 'PROPUESTA_Y_BASELINES.json').read_text(encoding='utf8'))
    for name, h in revision['proposals'].items():
        if sha(BASE / name) != h: raise ValueError('OP1 proposal changed')
    s = (BASE / 'reproducir.py').read_text(encoding='utf8')
    s = once(s, "    r = recipe(args.receta); c = config()\n    if args.variante not in r['variants']:",
        "    r = recipe(args.receta); c = config()\n    if r.get('requires_explicit_material') and not getattr(args, 'material', False):\n        raise ValueError('Esta receta exige --material para ejecutar DEE en la copia explícita')\n    if args.variante not in r['variants']:")
    s = once(s, "    run.add_argument('--vida', required=True); run.add_argument('--destino', required=True)",
        "    run.add_argument('--vida', required=True); run.add_argument('--destino', required=True)\n    run.add_argument('--material', action='store_true', help='Autoriza la ejecución material de una receta que lo exige; listar/verificar/recalcular no actúan')")
    ast.parse(s)
    OUT.mkdir()
    (OUT / 'reproducir.py').write_text(s, encoding='utf8', newline='')
    (OUT / 'ejecutar_diagnostico.py').write_bytes((BASE / 'ejecutar_diagnostico.py').read_bytes())
    revision['schema'] = 'PI04.C2C.RP_tool_proposal.OP2'
    revision['preceding_proposal_manifest_sha256'] = sha(BASE / 'PROPUESTA_Y_BASELINES.json')
    revision['proposals'] = {n: sha(OUT / n) for n in ('reproducir.py', 'ejecutar_diagnostico.py')}
    revision['changes'].append('C2C opt-in recipe requires --material; existing recipes unchanged and read-only modes remain without Native imports')
    (OUT / 'PROPUESTA_Y_BASELINES.json').write_text(json.dumps(revision, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(revision, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
