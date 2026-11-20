"""Supplement only the new audit construction, never an original archive."""
from pathlib import Path
from collections import OrderedDict
import argparse,json,zipfile,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from extraer import Writer
from codec import sha
def main():
    p=argparse.ArgumentParser();p.add_argument('--zip',type=Path,required=True);p.add_argument('--package',type=Path,required=True);a=p.parse_args();root=a.package/'EVIDENCIA_PRIMARIA_ESENCIAL';idx=json.loads((root/'INDICE_DOCUMENTOS.json').read_bytes())
    w=Writer.__new__(Writer);w.root=root;w.rows=idx['documents'];w.aliases=idx['source_aliases'];w.seen={r['canonical_sha256']:r for r in w.rows};w.bases={};w.cache=OrderedDict();before=len(w.rows);texts=[]
    with zipfile.ZipFile(a.zip)as z:
        nsm=json.loads(z.read('CPC9/revision/NSM65_EVIDENCIAS.json'));selected={r['member'].replace('\\','/')for e in nsm['entries']for r in e.get('primary_witnesses',[])}
        selected.update(n for n in z.namelist()if n.startswith('CPC9/front_relations/revision/')and n.endswith('.json'))
        selected.update(n for n in z.namelist()if n.startswith('CPC9/front_semantics/revision/')and n.endswith('.json'))
        for name in sorted(selected):
            if not name.startswith('CPC9/'):name='CPC9/'+name
            if name not in z.namelist():raise ValueError('An original semantic witness is absent: '+name)
            b=z.read(name)
            if name.endswith('.json'):
                w.add(b,{'kind':'ZIP_MEMBER','archive':a.zip.name,'archive_sha256':'917a559b917388fc63a6948762d73c3e87a00c30199c5b65c635a8d39bf96bad','member':name},'SOURCE_REFERENCED_ANALYSIS_OR_CONFIGURATION')
            elif name.endswith('.py'):
                f=a.package/'CONFIGURACIONES_Y_REPRODUCCION/FUENTES_EXPERIMENTALES'/name[5:];f.parent.mkdir(parents=True,exist_ok=True)
                if f.exists()and f.read_bytes()!=b:raise ValueError('Conflicting source witness')
                f.write_bytes(b);texts.append({'included':f.relative_to(a.package).as_posix(),'archive':a.zip.name,'member':name,'sha256':sha(b),'bytes':len(b)})
        # The original complete68-row continuity matrix, not a new promotion.
        name='CPC9/revision/CPC01_A_CPC09_MATRIZ_CAPACIDADES.csv';b=z.read(name);f=a.package/'EVIDENCIA_PRIMARIA_ESENCIAL/MATRIZ_ORIGINAL_CPC01_A_CPC09.csv';f.write_bytes(b)
        texts.append({'included':f.relative_to(a.package).as_posix(),'archive':a.zip.name,'member':name,'sha256':sha(b),'bytes':len(b)})
    w.finish();(a.package/'TESTIGOS_ADICIONALES_ORIGEN.json').write_text(json.dumps({'new_json_documents':len(w.rows)-before,'text_files':texts},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'status':'PASS','new_json':len(w.rows)-before,'documents':len(w.rows),'text':len(texts)}))
if __name__=='__main__':main()
