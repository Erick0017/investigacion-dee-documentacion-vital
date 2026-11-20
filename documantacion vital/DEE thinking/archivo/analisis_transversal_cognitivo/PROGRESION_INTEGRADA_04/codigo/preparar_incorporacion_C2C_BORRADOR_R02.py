"""Prepare, never apply, the prior PI04 incorporation template with C2C JSON.

Actual decision/evidence gates and final cut still must be supplied by Root.
"""
from pathlib import Path
import ast
import hashlib
import json

P = Path(__file__).resolve().parents[1]
H = P / 'codigo'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    source = H / 'incorporar_PI04_BORRADOR.py'
    target = H / 'incorporar_PI04_C2C_BORRADOR_R02.py'
    if target.exists(): raise ValueError('Preserve prior template revision')
    before = source.read_bytes()
    text = before.decode('utf-8-sig')
    old = "'capacidades/PROTOCOLO_PI04_C2B_R01.json','capacidades/PROTOCOLO_E3_R01.json'"
    if text.count(old) != 1: raise ValueError('Explicit JSON whitelist locator changed')
    text = text.replace(old, "'capacidades/PROTOCOLO_PI04_C2B_R01.json','capacidades/PROTOCOLO_PI04_C2C_R01.json','capacidades/PROTOCOLO_E3_R01.json'", 1)
    text = text.replace('Only approved Cognitive Python files or the two exact PI04 protocol JSONs are admitted:',
        'Only approved Cognitive Python files or the exact listed historical/PI04 protocol JSONs are admitted:')
    ast.parse(text)
    if 'adapter_reviewed_for_PI04' not in text or 'UNEXECUTED PI04 ADAPTER TEMPLATE' not in text:
        raise ValueError('The actual-decision safety gate must remain')
    target.write_text(text, encoding='utf8', newline='')
    assert source.read_bytes() == before
    proof = {'schema': 'PI04.C2C.incorporation.template_only.R02',
        'source': str(source), 'source_sha256': sha(source), 'target': str(target), 'target_sha256': sha(target),
        'change': 'Add only the exact C2C protocol JSON to the permitted approved-file whitelist and correct its error description',
        'Native_ticks': 0, 'source_original_unchanged': True, 'decision_created': False,
        'preparation_or_adoption_executed': False,
        'requires': 'Root actual final gates/cut/code diff/full-pair/process witnesses and explicit adapter review; none inferred here'}
    out = P / 'control/PLANTILLA_INCORPORACION_C2C_NO_EJECUTADA_R02.json'
    if out.exists(): raise ValueError('Do not overwrite proof')
    out.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(proof, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
