"""Recover the static import closure of actual CPC9 life constructors."""
from pathlib import Path,PurePosixPath
import argparse,ast,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[4]
def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);a=p.parse_args()
    prefixes=['CPC9/src/','CPC9/base_validada/cpc8/src/','CPC9/front_semantics/src/','CPC9/front_relations/src/']
    with zipfile.ZipFile(a.archive)as z:
        available={n:z.read(n)for n in z.namelist()if n.endswith('.py')and any(n.startswith(p)for p in prefixes)};lookup={}
        for prefix in prefixes:
            for n in available:
                if not n.startswith(prefix):continue
                module=n[len(prefix):-3].replace('/','.')
                if module.endswith('.__init__'):module=module[:-9]
                lookup.setdefault(module,n)
        queue=['vida_repertorio_extension','vida_integral','repertorio_n67'];selected=set();external=set()
        while queue:
            mod=queue.pop();name=lookup.get(mod)
            if name is None:external.add(mod);continue
            if name in selected:continue
            selected.add(name)
            parts=mod.split('.')
            for k in range(1,len(parts)):
                parent='.'.join(parts[:k])
                if parent in lookup:queue.append(parent)
            tree=ast.parse(available[name].decode('utf-8-sig'))
            for node in ast.walk(tree):
                if isinstance(node,ast.Import):queue.extend(x.name for x in node.names)
                if isinstance(node,ast.ImportFrom):
                    if node.level:
                        base=parts[:-node.level];m='.'.join([*base,*((node.module or'').split('.')if node.module else[])])
                    else:m=node.module or''
                    if m:queue.append(m)
                    for item in node.names:
                        key=m+'.'+item.name
                        if key in lookup:queue.append(key)
        records=[];dest=ROOT/'sistema/organizaciones/cpc9'
        for name in sorted(selected):
            relative=PurePosixPath(name).relative_to('CPC9');target=dest.joinpath(*relative.parts);target.parent.mkdir(parents=True,exist_ok=True);b=available[name]
            if target.exists()and target.read_bytes()!=b:raise FileExistsError('Different recovered source protected')
            target.write_bytes(b);records.append({'origin_member':name,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'system_path':str(target.relative_to(ROOT/'sistema'))})
        # Catalogue and original measurement configs are genealogy/fixtures, never participant imports.
        for name in z.namelist():
            if name.startswith('CPC9/configuraciones/')and name.endswith('.json'):
                f=ROOT/'evidencia/genealogia/configuraciones_CPC9'/name.removeprefix('CPC9/configuraciones/');f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(z.read(name))
        out=ROOT/'evidencia/genealogia/CODIGO_CPC9_RECUPERADO.json';out.write_text(json.dumps({'schema':'DCS1.1.import_closure.v1','roots':['vida_repertorio_extension','vida_integral','repertorio_n67'],'source_archive_sha256':hashlib.sha256(a.archive.read_bytes()).hexdigest(),'files':records,'external_imports':sorted(external),'source_edits':[],'scope':'Exact constructor/session sources only. Experiment references and targets are not copied into participant memory.'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(json.dumps({'status':'PASS','files':len(records),'bytes':sum(x['bytes']for x in records),'external_imports':sorted(external)}))
if __name__=='__main__':main()
