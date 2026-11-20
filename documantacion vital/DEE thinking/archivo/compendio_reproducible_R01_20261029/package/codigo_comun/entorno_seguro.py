"""Auditor recursivo de I/O Python para reproducciones de paquete.

No es un sandbox del sistema operativo. Los hooks de CPython no interceptan
fopen directo de una extensión nativa ni el cargador DLL de Windows. Sí
controlan open/listdir/scandir/mutaciones de Python y propagan la misma
política a los subprocesos Python (incluidos -c y -m), sin tocar su stdout.
Los procesos no Python y los lanzamientos no envueltos se rechazan.
"""
from pathlib import Path
import argparse,atexit,json,os,runpy,sys,tempfile,time,subprocess,shlex

SELF=Path(__file__).resolve()
ORIGINAL_POPEN=subprocess.Popen
TRACKED_EVENTS=frozenset(('open','os.listdir','os.scandir','os.chdir','os.mkdir','os.remove','os.rmdir','os.chmod','os.utime','os.truncate','shutil.rmtree','os.rename','os.link','os.symlink','os.system','os.exec','os.posix_spawn','os.spawn','subprocess.Popen','import'))
_split_windows=None
if os.name=='nt':
    import ctypes
    _shell=ctypes.WinDLL('shell32',use_last_error=True)
    _kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    _shell.CommandLineToArgvW.argtypes=[ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_int)]
    _shell.CommandLineToArgvW.restype=ctypes.POINTER(ctypes.c_wchar_p)
    _kernel.LocalFree.argtypes=[ctypes.c_void_p]
    def _split_windows(command):
        count=ctypes.c_int();ptr=_shell.CommandLineToArgvW(command,ctypes.byref(count))
        if not ptr:raise OSError('CommandLineToArgvW failed')
        try:return[ptr[i]for i in range(count.value)]
        finally:_kernel.LocalFree(ptr)

def _parts(args):
    if isinstance(args,(str,bytes)):
        text=os.fsdecode(args)
        return _split_windows(text)if _split_windows else shlex.split(text)
    return[os.fsdecode(x)for x in args]

def _is_python(path):
    name=Path(os.fsdecode(path)).name.lower()
    return name in('python','python.exe','pythonw.exe','python3','python3.exe')or(name.startswith('python3.')and(name.endswith('.exe')or name[8:].isdigit()))

def _interpreter_split(args):
    """Preserve interpreter options; move only the execution target behind us."""
    flags=[];i=1
    while i<len(args):
        q=args[i]
        if q in('-c','-m'):return flags,args[i:]
        if q=='--':return flags,args[i+1:]
        if q=='-':raise PermissionError('Python stdin execution has no auditable target; use -c or a package script')
        if not q.startswith('-'):return flags,args[i:]
        if q in('-X','-W'):
            if i+1>=len(args):raise ValueError('Missing interpreter option value')
            flags.extend(args[i:i+2]);i+=2;continue
        if q in('-V','--version','-h','--help'):return flags,['-c','import sys; print(sys.version)']
        flags.append(q);i+=1
    raise PermissionError('Interactive Python is outside the reproduction protocol')

def _beneath(path,roots):
    return any(path.is_relative_to(root)for root in roots)

class Guard:
    def __init__(self,context,original_args):
        self.context=context;self.package=Path(context['package']).resolve();self.output=Path(context['output']).resolve();self.roottemp=Path(context['temporary_root']).resolve()
        self.temp=Path(tempfile.mkdtemp(prefix=str(os.getpid())+'_',dir=self.roottemp))
        os.environ.update(TEMP=str(self.temp),TMP=str(self.temp),TMPDIR=str(self.temp));tempfile.tempdir=str(self.temp)
        self.read_roots=[self.package,self.output,self.roottemp,Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve()]
        self.write_roots=[self.output,self.roottemp]
        self.read_executables={Path(x).resolve()for x in context.get('read_executables',[])}
        # A regular venv exposes stdlib under base_prefix and installed packages
        # under prefix. No historical project root is added implicitly.
        self.reads=set();self.blocks=[];self.processes=[];self.events=0;self.active=False;self.start=time.monotonic();self.error=None;self.original_args=original_args
        self.directory=self.output/'_aislamiento';self.directory.mkdir(parents=True,exist_ok=True)
        self.log=(self.directory/('proceso_'+str(os.getpid())+'.jsonl')).open('a',encoding='utf8',buffering=1)
        stamp=str(time.time_ns())
        self.report=self.directory/('proceso_'+str(os.getpid())+'_'+stamp+'.json')
        self.report_handle=self.report.open('x',encoding='utf8')
        self.contextfile=self.directory/('CONTEXTO_'+str(os.getpid())+'_'+stamp+'.json')
        self.contextfile.write_text(json.dumps(context,ensure_ascii=False,indent=2),encoding='utf8')
        atexit.register(self.finish)

    def note(self,row):
        if self.log.closed:return
        row={'pid':os.getpid(),'parent_pid':os.getppid(),**row};self.log.write(json.dumps(row,ensure_ascii=False,default=str)+'\n')

    def reject(self,event,path,write=False,reason=None):
        row={'event':event,'path':str(path),'write':write,'reason':reason or'outside_declared_roots'};self.blocks.append(row);self.note({'type':'blocked',**row})
        raise PermissionError('DEE isolation blocked '+event+': '+str(path))

    def check(self,event,value,write=False):
        if isinstance(value,int)or value is None:return
        if not isinstance(value,(str,bytes,os.PathLike)):return
        value=os.fsdecode(value)
        if value.lower()in('nul','con','\\\\.\\nul','/dev/null'):return
        path=Path(value).resolve()
        if write and path.is_relative_to(self.package):self.reject(event,path,True,'package_references_are_read_only')
        if not _beneath(path,self.write_roots if write else self.read_roots)and(write or path not in self.read_executables):self.reject(event,path,write)
        if not write and str(path)not in self.reads:
            self.reads.add(str(path));self.note({'type':'read','event':event,'path':str(path)})

    def audit(self,event,args):
        # No tratar millones de eventos ajenos a I/O como si fueran accesos.
        # Todos los eventos que el control interpreta permanecen en esta lista.
        if event not in TRACKED_EVENTS:return
        if self.active:return
        self.active=True
        try:
            self.events+=1
            if event=='open'and args:
                mode=args[1]if len(args)>1 else None;flags=args[2]if len(args)>2 and isinstance(args[2],int)else 0
                write=(isinstance(mode,str)and any(c in mode for c in'wax+'))or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
                self.check(event,args[0],write)
            elif event in('os.listdir','os.scandir','os.chdir')and args:self.check(event,args[0])
            elif event in('os.mkdir','os.remove','os.rmdir','os.chmod','os.utime','os.truncate','shutil.rmtree')and args:self.check(event,args[0],True)
            elif event in('os.rename','os.link')and len(args)>1:
                self.check(event,args[0],True);self.check(event,args[1],True)
            elif event=='os.symlink':self.reject(event,args,True,'symlink_creation_not_required_by_protocol')
            elif event in('os.system','os.exec','os.posix_spawn','os.spawn'):
                self.reject(event,args,False,'non_wrapped_process_creation')
            elif event=='subprocess.Popen':
                command=args[1]if len(args)>1 else'';parts=_parts(command)
                if not(any(str(SELF).lower()==str(p).lower()for p in parts)and'--child'in parts):self.reject(event,command,False,'process_not_wrapped')
            elif event=='import'and len(args)>1 and isinstance(args[1],str):self.check(event,args[1])
        finally:self.active=False

    def install(self):
        owner=self
        class AuditedPopen(ORIGINAL_POPEN):
            def __init__(self,*pos,**kwargs):
                original=kwargs.get('args',pos[0]if pos else None)
                if original is None:raise TypeError('Popen args are required')
                args=_parts(original);exe=kwargs.get('executable')or(args[0]if args else'')
                if kwargs.get('shell'):owner.reject('subprocess.Popen',original,False,'shell execution is not a Python protocol')
                if not _is_python(exe):owner.reject('subprocess.Popen',original,False,'only wrapped Python children are admitted')
                flags,payload=_interpreter_split(args)
                flags=[x for x in flags if x not in('-I','-B')]
                wrapped=[os.fsdecode(exe),'-I','-B',*flags,str(SELF),'--child',str(owner.contextfile),'--',*payload]
                env=dict(os.environ if kwargs.get('env')is None else kwargs['env']);env.update(TEMP=str(owner.temp),TMP=str(owner.temp),TMPDIR=str(owner.temp));kwargs['env']=env
                owner.processes.append({'original_argv':args,'wrapped_argv':wrapped,'cwd':str(kwargs.get('cwd')or Path.cwd()),'creationflags':kwargs.get('creationflags',0),'executable_override':None if kwargs.get('executable')is None else str(kwargs['executable'])})
                owner.note({'type':'python_child','argv':args,'wrapped':wrapped,'cwd':str(kwargs.get('cwd')or Path.cwd())})
                if 'args'in kwargs:kwargs['args']=wrapped
                else:pos=(wrapped,*pos[1:])
                super().__init__(*pos,**kwargs)
        subprocess.Popen=AuditedPopen
        sys.addaudithook(self.audit)

    def finish(self):
        if self.log.closed:return
        data={'schema':'DEE.recursive_python_io_audit.v1','pid':os.getpid(),'parent_pid':os.getppid(),'python':sys.executable,'version':sys.version,'isolated':bool(sys.flags.isolated),'dont_write_bytecode':bool(sys.dont_write_bytecode),'original_args':self.original_args,
              'package':str(self.package),'output':str(self.output),'temporary_directory':str(self.temp),'read_roots':list(map(str,self.read_roots)),'write_roots':list(map(str,self.write_roots)),
              'read_files':sorted(self.reads),'blocked':self.blocks,'children':self.processes,'audit_events':self.events,'seconds':time.monotonic()-self.start,'error':self.error,
              'coverage':'CPython audit events and subprocess.Popen recursion; script, -c and -m. stdin/stdout/stderr, cwd, Windows creationflags/startupinfo/job ownership are preserved.',
              'limitations':['Not an operating-system sandbox. Direct C/C++ file I/O and Windows DLL loading are outside CPython audit coverage.','File descriptor reads use descriptors opened before or under this policy; the hook cannot infer an inherited descriptor origin.','stat/exists metadata lookups are not content reads and do not all emit CPython audit events.']}
        self.report_handle.write(json.dumps(data,ensure_ascii=False,indent=2));self.report_handle.close();self.log.close()

def _execute(payload,guard):
    if not payload:raise ValueError('Missing Python target')
    common=guard.package/'codigo_comun';third=common/('terceros312'if sys.version_info[:2]==(3,12)else'terceros')
    sys.path[:0]=[str(common/'cognitive'),str(third),str(common)]
    if payload[0]=='-c':
        if len(payload)<2:raise ValueError('Missing -c code')
        sys.argv=['-c',*payload[2:]];exec(compile(payload[1],'<string>','exec'),{'__name__':'__main__','__builtins__':__builtins__,'__package__':None})
    elif payload[0]=='-m':
        if len(payload)<2:raise ValueError('Missing -m module')
        sys.argv=[payload[1],*payload[2:]];runpy._run_module_as_main(payload[1],alter_argv=True)
    else:
        script=Path(payload[0]).resolve(strict=True);guard.check('execution_target',script)
        if not _beneath(script,[guard.package,guard.output]):raise PermissionError('Execution target must belong to package or output materialization')
        sys.path.insert(0,str(script.parent));sys.argv=[str(script),*payload[1:]];runpy.run_path(str(script),run_name='__main__')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--script');ap.add_argument('--out',type=Path);ap.add_argument('--package',type=Path);ap.add_argument('--child',type=Path);ap.add_argument('--read-executable',type=Path,action='append',default=[]);ap.add_argument('args',nargs=argparse.REMAINDER);a=ap.parse_args()
    rest=a.args[1:]if a.args[:1]==['--']else a.args
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        return subprocess.call([sys.executable,'-I','-B',str(SELF),*sys.argv[1:]])
    if a.child:context=json.loads(a.child.read_text(encoding='utf8'));payload=rest
    else:
        if not a.script or not a.out:ap.error('--script and --out are required')
        package=(a.package or SELF.parents[1]).resolve();output=a.out.resolve();output.mkdir(parents=True,exist_ok=True)
        # La raíz es nueva y exclusiva. Nunca reutiliza ni borra TEMP de terceros.
        # El nombre ASCII corto evita el límite de fopen del v27 en Windows.
        temporary=Path(tempfile.mkdtemp(prefix='DEE_IO_')).resolve()
        for executable in a.read_executable:
            if not executable.is_file()or not _is_python(executable):raise ValueError('La excepción de lectura requiere un ejecutablePython declarado')
        context={'package':str(package),'output':str(output),'temporary_root':str(temporary),'root_pid':os.getpid(),'read_executables':list(map(lambda x:str(x.resolve()),a.read_executable))}
        target=Path(a.script);target=target if target.is_absolute()else package/target;payload=[str(target),*rest]
    guard=Guard(context,payload);guard.install();sys.dont_write_bytecode=True
    try:_execute(payload,guard);return 0
    except BaseException as exc:
        if not isinstance(exc,SystemExit)or exc.code not in(None,0):guard.error=repr(exc)
        raise
    finally:guard.finish()
if __name__=='__main__':raise SystemExit(main())
