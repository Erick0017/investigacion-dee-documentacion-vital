"""PI11 export R02: complete declared reference for an unselected source.

One correction to preserved R01 only: the no-ACTIVO reference also carries
the caller's exact snapshot_sha256. The unchanged exporter still compares
that value with VIDA, actual snapshot bytes and HISTORIA before any mkdir.
No export or Native action occurs on import; Root explicitly calls main.
"""
from pathlib import Path
import ast,hashlib,types
SOURCE=Path(__file__).with_name('pi11_exportar_R01.py')
SOURCE_SHA='1ae4d4a44fc1700230e25de87012932ec7c31d206a2190256b297f42fd688f10'
OLD="else{'life_id':LIFE,'tick':a.tick};need(active['life_id']==LIFE"
NEW="else{'life_id':LIFE,'tick':a.tick,'snapshot_sha256':a.snapshot_sha256};need(active['life_id']==LIFE"
def adapted_source():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SOURCE_SHA:raise ValueError('Preserved R01 export adapter changed')
    text=SOURCE.read_text('utf-8-sig')
    if text.count(OLD)!=1:raise ValueError('Exact R01 no-ACTIVO anchor changed')
    text=text.replace(OLD,NEW);ast.parse(text);return text
def base():
    m=types.ModuleType('PI11_closed_export_R02_reference_completeness');m.__file__=str(SOURCE)
    exec(compile(adapted_source(),str(SOURCE)+':R02_no_ACTIVO_reference_hash_only','exec'),m.__dict__)
    return m
if __name__=='__main__':base().main()
