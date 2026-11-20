"""Selectively preserve exact executable dependencies; never edit historical sources."""
from __future__ import annotations
import ast, ctypes, hashlib, json, os, platform, shutil, sys, winreg
from ctypes import wintypes
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT.parents[2] / 'CPC8' / 'runs' / 'RECONSTRUCCION_20261019_002104'
WHL = 'dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
EXPECTED = '09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def copy_exact(source,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        if digest(target)!=digest(source):raise FileExistsError(target)
    else:shutil.copyfile(source,target)
    return {'source':str(source),'target':str(target.relative_to(ROOT)),'bytes':target.stat().st_size,'sha256':digest(target)}

def main():
    if not OLD.is_dir():raise FileNotFoundError(OLD)
    wheel=OLD/'runtime'/WHL
    if digest(wheel)!=EXPECTED:raise ValueError('Official wheel identity mismatch')
    rows=[copy_exact(wheel,ROOT/'runtime'/WHL)]
    source=OLD/'src';dest=ROOT/'base_validada'/'cpc8'/'src'
    seeds=['transferencia_magnitud/cts_integrado.py','regulacion_acoplada/mcts.py',
           'count_sign/coexist.py','count_sign/branch_session.py']
    queue=[Path(x) for x in seeds];visited=set()
    while queue:
        rel=queue.pop(0)
        if rel in visited:continue
        visited.add(rel);path=source/rel
        if not path.is_file():raise FileNotFoundError(path)
        rows.append(copy_exact(path,dest/rel))
        for parent in rel.parents:
            if parent==Path('.'):continue
            init=parent/'__init__.py'
            if (source/init).is_file() and init not in visited:queue.append(init)
        tree=ast.parse(path.read_text(encoding='utf-8-sig'))
        for node in ast.walk(tree):
            mods=[]
            if isinstance(node,ast.Import):mods=[x.name for x in node.names]
            elif isinstance(node,ast.ImportFrom) and node.level==0 and node.module:mods=[node.module]
            for mod in mods:
                local=Path(*mod.split('.')).with_suffix('.py')
                if (source/local).is_file() and local not in visited:queue.append(local)
    for rel in ('referencias/NSM65/NSM65_CATALOGO_4_5.json',):
        rows.append(copy_exact(OLD/rel,ROOT/'genealogia'/Path(rel).name))
    p=ROOT/'revision'/'BASE_HEREDADA_COPIAS.json';p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps({'source_cut':str(OLD),'files':rows,'meaning':'Byte-exact selective source dependencies, not claimed newly integrated'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    class MEMORY(ctypes.Structure):
        _fields_=[('dwLength',wintypes.DWORD),('dwMemoryLoad',wintypes.DWORD)]+[(n,ctypes.c_ulonglong)for n in('ullTotalPhys','ullAvailPhys','ullTotalPageFile','ullAvailPageFile','ullTotalVirtual','ullAvailVirtual','ullAvailExtendedVirtual')]
    memory=MEMORY();memory.dwLength=ctypes.sizeof(memory)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):raise ctypes.WinError()
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'HARDWARE\DESCRIPTION\System\CentralProcessor\0')as key:cpu=winreg.QueryValueEx(key,'ProcessorNameString')[0].strip()
    machine={'observed_utc':datetime.now(timezone.utc).isoformat(),'machine':platform.node(),'cpu':cpu,'logical_cpus':os.cpu_count(),'ram_total_bytes':memory.ullTotalPhys,'ram_available_bytes':memory.ullAvailPhys,'platform':platform.platform(),'python':sys.version,'executable':sys.executable,'cim_metadata_access':'Denied in initial command; this record uses registry and GlobalMemoryStatusEx','budget_not_restarted':True}
    (ROOT/'revision'/'MAQUINA.json').write_text(json.dumps(machine,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'copied_files':len(rows),'bytes':sum(x['bytes']for x in rows),'machine':machine},ensure_ascii=False))

if __name__=='__main__':main()
