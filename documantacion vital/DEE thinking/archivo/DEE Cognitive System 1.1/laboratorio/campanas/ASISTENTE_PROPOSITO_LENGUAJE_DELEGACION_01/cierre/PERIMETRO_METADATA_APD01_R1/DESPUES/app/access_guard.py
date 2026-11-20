"""Auditable Python file boundary for normal life operations, not an OS sandbox."""
from pathlib import Path
import json,os,sys,tempfile,subprocess

def install(system_root,*,explicit_read=None,explicit_write=None,external_command=None):
    root=Path(system_root).resolve();owned=tempfile.TemporaryDirectory(prefix='dcs11-native-');temporary=Path(owned.name).resolve()
    if not str(temporary).isascii():owned.cleanup();raise ValueError('Native toolchain requires an ASCII temporary directory')
    tempfile.tempdir=str(temporary)
    runtime=[Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve(),temporary]
    read_exact={Path(x).resolve()for x in(explicit_read or[])};write_dirs=[Path(x).resolve()for x in(explicit_write or[])]
    denied=[];allowed_external=[];external_command=None if external_command is None else list(map(str,external_command))
    def inside(p,b):return p==b or p.is_relative_to(b)
    def hook(event,args):
        if event in('socket.connect','socket.connect_ex','os.system','subprocess.Popen'):
            argv_matches=external_command is not None and len(args)>1 and((isinstance(args[1],(list,tuple))and list(map(str,args[1]))==external_command)or(isinstance(args[1],str)and args[1]==subprocess.list2cmdline(external_command)))
            executable_matches=external_command is not None and((args[0]is None and os.name=='nt'and argv_matches)or(isinstance(args[0],(str,bytes,os.PathLike))and Path(args[0]).resolve()==Path(external_command[0]).resolve()))
            if event=='subprocess.Popen'and argv_matches and executable_matches:
                allowed_external.append({'event':event,'argv':external_command});return
            denied.append({'event':event});raise PermissionError('Normal native-life operations do not launch external decision processes or network requests')
        if event=='open'and args and isinstance(args[0],(str,bytes,os.PathLike)):
            p=Path(os.fsdecode(args[0])).resolve();mode=args[1]if len(args)>1 else'';flags=args[2]if len(args)>2 else 0
            write=(isinstance(mode,str)and any(c in mode for c in'wa+x'))or(isinstance(flags,int)and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
            if write:allowed=inside(p,root/'estado')or inside(p,temporary)or any(inside(p,b)for b in write_dirs)
            else:
                excluded=[root/'pruebas_minimas',root/'capacidades/core/mecanismos',root/'estado/cache_heredada',root/'capacidades/core/verificaciones']
                allowed=(inside(p,root)and not any(inside(p,b)for b in excluded))or any(inside(p,b)for b in runtime)or p in read_exact
            if not allowed:denied.append({'event':event,'path':str(p),'write':bool(write)});raise PermissionError('Normal participant path cannot read audit targets, historical folders or undeclared files: '+str(p))
    sys.addaudithook(hook)
    # Keep the temporary owner alive through process lifetime. Cleanup is hostI/O,
    # never a world edit, and applies only to this uniquely-created directory.
    return{'temporary_owner':owned,'temporary_path':str(temporary),'denied_operations':denied,'allowed_exact_external_calls':allowed_external,'scope':'Python open/subprocess/network audit hooks. Reads inside sistema, including operational life records, journals and cached results in estado, remain permitted except explicit exclusions; declared exact external inputs are permitted. Undeclared sibling laboratorio/evidencia and other external reads are blocked. An optional exact environment-worker argv does not authorize other processes or networks. This does not detect all response-history lookups and is not an operating-system sandbox.'}
