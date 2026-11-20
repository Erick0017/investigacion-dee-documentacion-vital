"""Ejecutor aislado de un protocolo histórico sin referencias de respuestas."""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys,tempfile,traceback,zipfile,shutil
p=argparse.ArgumentParser();p.add_argument('--script',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--allow-root',required=True,type=Path);p.add_argument('--module-path',action='append',default=[],type=Path);p.add_argument('--legacy-wheel',type=Path);p.add_argument('--flat-legacy-runtime',action='store_true');p.add_argument('arguments',nargs=argparse.REMAINDER);a=p.parse_args()
script=a.script.resolve();out=a.output.resolve();root=a.allow_root.resolve();owner=tempfile.TemporaryDirectory(prefix='dee-compendio-native-');native_temp=Path(owner.name).resolve();assert str(native_temp).isascii()
os.environ['TEMP']=str(native_temp);os.environ['TMP']=str(native_temp);tempfile.tempdir=str(native_temp)
package=next(p for p in Path(__file__).resolve().parents if (p/'CATALOGO.json').is_file())
if a.legacy_wheel:
    assert hashlib.sha256(a.legacy_wheel.read_bytes()).hexdigest()=='69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939'
    api=native_temp/'DEE_CODEX_NATIVE_DISCOVERY_AND_CLOSURE_V1_WORK/ANALYSIS/binary_api/wheel_extracted'
    with zipfile.ZipFile(a.legacy_wheel) as z:
        for member in z.namelist():
            if member.startswith('dee_universe_v27/') and not member.endswith('/'):
                assert '..' not in Path(member).parts;dest=api/member;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(member))
    shutil.copy2(a.legacy_wheel,native_temp/a.legacy_wheel.name)
    os.environ['DEE_V27_TESTS_ROOT']=str(native_temp)
    if a.flat_legacy_runtime:
        pyd=next((api/'dee_universe_v27').glob('*.pyd'));shutil.copy2(pyd,script.parent/pyd.name);shutil.copy2(a.legacy_wheel,script.parent/a.legacy_wheel.name)
sys.path[:0]=[str(x.resolve()) for x in a.module_path]
allowed=(package,root,out,Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve(),native_temp,Path(os.environ.get('WINDIR','C:/Windows')).resolve())
reads=[];denied=[]
def audit(event,args):
    if event!='open' or not args or isinstance(args[0],int) or not isinstance(args[0],(str,bytes,os.PathLike)):return
    target=Path(os.fsdecode(args[0])).resolve()
    if not any(target==x or target.is_relative_to(x) for x in allowed):denied.append(str(target));raise PermissionError('Lectura/escritura externa no declarada: '+str(target))
    reads.append(str(target))
sys.addaudithook(audit)
assert sys.flags.isolated and sys.dont_write_bytecode and sys.version_info[:2]==(3,13)
arguments=a.arguments[1:] if a.arguments[:1]==['--'] else a.arguments
sys.argv=[str(script),*arguments]
result={'script':str(script),'python':sys.executable,'arguments':arguments,'allowed_roots':list(map(str,allowed)),'native_temporary':str(native_temp),'new_scientific_protocol':False}
try:runpy.run_path(str(script),run_name='__main__');result['status']='COMPLETED'
except BaseException as e:result.update(status='ERROR',error=repr(e),traceback=traceback.format_exc());raise
finally:
    result.update(opened_files=sorted(set(reads)),denied_files=denied)
    out.mkdir(parents=True,exist_ok=True);(out/'ACCESOS_DEL_PROCESO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
