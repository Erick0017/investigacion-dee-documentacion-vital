"""Root source-only preparation of the exact frozen-main import whitelist."""
from pathlib import Path
import ast, hashlib, json
P = Path(__file__).resolve().parents[1]
D = P/'codigo'

def main():
    paths = [D/'clonar_PI07_R01.py',D/'materializar_vacios_PI07.py']
    texts = [p.read_text(encoding='utf8') for p in paths]
    old = "if not(source.is_relative_to(C/'reproducibilidad/materiales')or source.is_relative_to(P/'estados')or source.is_relative_to(P/'pares')):raise ValueError('Only preserved full-pair stores accepted')"
    assert old in texts[0]
    first = texts[0].replace(old,"sys.path.insert(0,str(P/'codigo'))\nfrom fuentes_completas_PI07_R01 import allowed_pair\nif not allowed_pair(source):raise ValueError('Only reviewed complete frozen pair stores accepted')")
    first = first.replace('from materializar_vacios_PI07 import','from materializar_vacios_PI07_R02 import')
    old = "if not(pair.is_relative_to((P/'pares').resolve())or pair.is_relative_to((C/'reproducibilidad/materiales').resolve())):raise ValueError('Only preserved complete pair stores')"
    assert old in texts[1]
    second = texts[1].replace(old,"from fuentes_completas_PI07_R01 import allowed_pair\n if not allowed_pair(pair):raise ValueError('Only reviewed complete frozen pair stores accepted')")
    rows=[]
    for source,name,text in zip(paths,['clonar_PI07_R02.py','materializar_vacios_PI07_R02.py'],[first,second]):
        ast.parse(text)
        dest=D/name
        with dest.open('x',encoding='utf8') as f:f.write(text)
        rows.append({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'output':str(dest),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
    with (P/'control/ADAPTADORES_FUENTE_ACTUAL_PI07_R02.json').open('x',encoding='utf8') as f:
        json.dump({'Native_ticks':0,'change':'Exact pinned already-frozen current-main export additionally allowed; all import and directory coherence checks retained.','files':rows},f,ensure_ascii=False,indent=2)
    print('Two source adapters prepared; no Native')

if __name__=='__main__':main()
