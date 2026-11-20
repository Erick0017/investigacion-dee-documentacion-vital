"""N0 structural comparison of the single added APD05 transport branch.

No application, actor or motor import. Does not claim physical equivalence of
new APD05 operations; checks the unchanged old request paths used by controls.
"""
from pathlib import Path
import argparse,ast,copy,gzip,hashlib,json


def compare(old_path,new_path):
    a=Path(old_path).read_bytes();a=gzip.decompress(a)if a[:2]==b'\x1f\x8b'else a
    b=Path(new_path).read_bytes();old=ast.parse(a);new=ast.parse(b)
    test=ast.parse("isinstance(row.get('modo'),str) and row['modo'].startswith('apd05')",mode='eval').body
    expected=ast.parse('from app.protocolo_apd05 import validate_literal\nvalidate_literal(row)\ncontinue').body
    test_dump=ast.dump(test,include_attributes=False);removed=[]
    for node in ast.walk(new):
        for field,value in ast.iter_fields(node):
            if not isinstance(value,list):continue
            kept=[]
            for child in value:
                if isinstance(child,ast.If)and ast.dump(child.test,include_attributes=False)==test_dump:
                    if child.orelse or [ast.dump(x,include_attributes=False)for x in child.body]!=[ast.dump(x,include_attributes=False)for x in expected]:
                        raise ValueError('Added APD05 branch is not the declared literal validation-only dispatch')
                    removed.append({'line':child.lineno,'source':ast.unparse(child)})
                else:kept.append(child)
            setattr(node,field,kept)
    equal=ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False)
    if len(removed)!=1 or not equal:raise ValueError('Transport edits exceed the declared single APD05 literal-validation branch')
    return {'Native_ticks':0,'old_source':str(old_path),'new_source':str(new_path),
            'old_decoded_sha256':hashlib.sha256(a).hexdigest(),'new_sha256':hashlib.sha256(b).hexdigest(),
            'removed_branch':removed,'old_complete_module_AST_equals_new_without_added_branch':equal,
            'scope':'Structural preservation of all previous Python statements; line numbers/comments are excluded only from the AST comparison. Original source byte hashes remain distinct. This is not new physical replication, execution of APD05 modes or proof of arbitrary runtime equivalence.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--old',type=Path,required=True);p.add_argument('--new',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    value=compare(a.old,a.new)
    with a.out.open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'Native_ticks':0,'old_complete_module_AST_equals_new_without_added_branch':True}))


if __name__=='__main__':main()
