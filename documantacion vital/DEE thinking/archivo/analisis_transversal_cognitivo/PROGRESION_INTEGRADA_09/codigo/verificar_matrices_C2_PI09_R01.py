"""Pure CSV/source-locator check. Closed documentary files only, no Native."""
from pathlib import Path
import csv,hashlib,json
P=Path(__file__).resolve().parents[1]
files=['MATRIZ_CAPACIDADES_ANTES_DESPUES_PI09_R01.csv','COBERTURA_Y_GAPS_PI09_R01.csv']
checks=[];outputs=[]
for name in files:
    file=P/'mapas'/name
    with file.open(encoding='utf-8-sig',newline='')as f:rows=list(csv.DictReader(f))
    assert rows and len({r['id']for r in rows})==len(rows)
    for r in rows:
        assert None not in r and all(v is not None for v in r.values())
        source=P/r['fuente'];assert source.is_file()and hashlib.sha256(source.read_bytes()).hexdigest()==r['sha256'],r['id']
        pointer=r.get('localizador_JSON',r.get('localizador'))
        if source.suffix=='.json':
            value=json.loads(source.read_text('utf-8-sig'))
            if pointer:
                assert pointer.startswith('/'),(r['id'],pointer)
                for piece in pointer[1:].split('/'):
                    piece=piece.replace('~1','/').replace('~0','~');value=value[int(piece)]if isinstance(value,list)else value[piece]
        if 'credito_query1_aislado'in r:
            assert r['credito_query1_aislado']=='false'and r['agencia_P2_general_demostrada']=='false'
            if r['numerador']and r['denominador']:assert 0<=int(r['numerador'])<=int(r['denominador'])
    outputs.append({'file':name,'rows':len(rows),'columns':len(rows[0]),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()});checks.append(name+': rectangular/unique IDs, literal SHA and exact JSON locators')
result={'schema':'DEE.PI09.C2.CSV_source_and_scope_validation.R01','passed':True,'Native_executed':False,'DEE_imported':False,'SQLite_or_live_world_read':False,'checks':checks,'outputs':outputs,'query1_credit_and_general_P2_false_explicit':True,'CSV_blank_is_not_zero':True}
out=P/'control/VERIFICACION_MATRICES_C2_PI09_R01.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(result,ensure_ascii=False))
