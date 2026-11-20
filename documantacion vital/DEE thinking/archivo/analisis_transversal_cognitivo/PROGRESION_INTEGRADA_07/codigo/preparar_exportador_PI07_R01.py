"""Adapt the established closed-pair exporter to explicit PI07 source/dests.

Only source/diagnostic namespace and two bounded preservation destinations
change. Live-owner/SQLite/receipts/snapshot/member integrity checks remain.
"""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parents[1]

def main():
    src=P.parent/'PROGRESION_INTEGRADA_06/codigo/exportar_corte_aislado_PI06_R02.py'
    dest=P/'codigo/exportar_corte_aislado_PI07_R01.py'
    data=src.read_text(encoding='utf8').replace('PI06','PI07').replace('S6','S7')
    data=data.replace("parent=(CAMPAIGN/'pares').resolve(strict=True)","parent=(CAMPAIGN/'pares').resolve(strict=False)")
    data=data.replace("dest=ar.destino.resolve(strict=False);expected=parent/dest.name;regular(s);regular(dest)",
        "dest=ar.destino.resolve(strict=False)\n    allowed_parents={parent,(RP/'materiales').resolve(strict=True)}\n    if dest.parent not in allowed_parents:raise ValueError('Only PI07/pares or the stable Cognitive material store')\n    parent=dest.parent;expected=parent/dest.name;regular(s);regular(dest)")
    data=data.replace("if not re.fullmatch(r'[A-Za-z0-9_]{1,48}_T'+str(ar.tick),dest.name)",
        "if not re.fullmatch(r'PI07_[A-Za-z0-9_]{1,43}_T'+str(ar.tick),dest.name)")
    ast.parse(data)
    with dest.open('x',encoding='utf8')as f:f.write(data)
    proof={'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
        'output':str(dest),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
        'Native_ticks':0,'checks_retained':['closed owner/process','no SQLite auxiliaries','coherent native snapshot','last receipt reconciliation','all source/copy member hashes','no original writes'],
        'changes':'PI07 diagnostic source namespace and explicit stable RP/PI07 paired destinations only.'}
    (P/'control/EXPORTADOR_PREPARADO_PI07_R01.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(proof,ensure_ascii=False))

if __name__=='__main__':main()
