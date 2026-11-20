from pathlib import Path
from collections import Counter,defaultdict
import json,zipfile,re,hashlib
ROOT=Path(__file__).resolve().parent
RUNS=ROOT.parent
OUT=RUNS/'resultados'
def strings(x):
    if isinstance(x,dict):
        for k,v in x.items():yield from strings(v)
    elif isinstance(x,list):
        for v in x:yield from strings(v)
    elif isinstance(x,str):yield x
def main():
    with zipfile.ZipFile(OUT/'CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip')as z:
        idx=json.loads(z.read('CPC9/revision/INDICE_EVIDENCIA.json'))
        prim=[z.getinfo('CPC9/'+r['member'].replace('\\','/'))for r in idx['files']]
        groups=defaultdict(lambda:[0,0,0])
        for i in prim:
            k=i.filename.split('/')[1];g=groups[k];g[0]+=1;g[1]+=i.file_size;g[2]+=i.compress_size
        print('CPC9_PRIMARY',json.dumps(dict(groups)),sum(x.file_size for x in prim),sum(x.compress_size for x in prim))
    with zipfile.ZipFile(OUT/'DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip')as z:
        ix=json.loads(z.read('DEE_COGNITIVE_CORE/documentacion/INDICE_MIEMBROS.json'))
        mat=json.loads(z.read('DEE_COGNITIVE_CORE/documentacion/MATRIZ_CAPACIDADES.json'))
        docs=[json.loads(z.read(i.filename))for i in z.infolist()if i.filename.endswith('.json')and'/verificaciones/'in i.filename and 'CANDIDATO_'not in i.filename]
        proof=json.loads((OUT/'PRUEBA_RECUPERACION_DESDE_CERO.json').read_text(encoding='utf8'))
        refs=set(strings(mat))|set(strings(proof))
        for d in docs:refs.update(strings(d))
        chosen={n:r for n,r in ix['paths'].items()if r['sha256']in refs or n in refs}
        suffix=Counter();byte=Counter()
        for n,r in chosen.items():suffix[Path(n).suffix]+=1;byte[Path(n).suffix]+=r['bytes']
        print('CORE_SELECTED_REF',json.dumps(dict(suffix)),json.dumps(dict(byte)),len(chosen))
        (ROOT/'PREINVENTARIO.json').write_text(json.dumps({'cpc9_primary':[i.filename for i in prim],'core_index':{k:v for k,v in ix.items()if k!='paths'},'core_selected':chosen,'matrix':mat},ensure_ascii=False,indent=2),encoding='utf8')
        print('CORE_INDICE_FIRST',json.dumps(next(iter(ix['paths'].items())),ensure_ascii=False))
        print('MAX_BLOB',max(r['bytes']for r in ix['paths'].values()))
if __name__=='__main__':main()
