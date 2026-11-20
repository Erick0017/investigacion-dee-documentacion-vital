"""Unlink ONLY this known temporary Windows junction; never traverse its target."""
import hashlib,json,os,stat
from pathlib import Path
HERE=Path(__file__).absolute().parent;LAB=HERE.parents[1]
LINK=HERE/'node_modules'
TARGET=r'C:\Users\Erik\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
def main():
    parent=LINK.parent.resolve(strict=True);allowed=LAB.resolve(strict=True)
    if not parent.is_relative_to(allowed)or LINK.name!='node_modules':raise ValueError('Not the declared local authoring link')
    try:s=LINK.lstat()
    except FileNotFoundError:
        print(json.dumps({'link_already_absent':True,'target_not_modified':True,'native_ticks':0}));return
    if not(s.st_file_attributes&stat.FILE_ATTRIBUTE_REPARSE_POINT)or s.st_reparse_tag!=stat.IO_REPARSE_TAG_MOUNT_POINT:
        raise ValueError('Refuse to delete anything except the exact Windows junction')
    named=os.readlink(LINK)
    normalized=named[4:]if named.startswith('\\\\?\\')else named
    if os.path.normcase(os.path.normpath(normalized))!=os.path.normcase(os.path.normpath(TARGET)):
        raise ValueError('Reparse target is not the declared runtime packages')
    os.rmdir(LINK)  # Windows junction unlink, nonrecursive. No target directory enumeration/deletion.
    try:LINK.lstat();raise AssertionError('Junction still present')
    except FileNotFoundError:pass
    value={'link_removed':str(LINK),'declared_target_untouched':TARGET,'operation':'os.rmdir on validated reparse mount-point only; never rmtree',
        'native_ticks':0,'runtime_or_system_modified':False}
    out=HERE/'RETIRADA_JUNCTION_N0.json'
    with out.open('xb')as f:f.write((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps({**value,'receipt_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
