"""Entrada única de la biblioteca experimental DEE R01.

Sólo biblioteca estándar. No ejecuta física al listar ni al abrir el menú.
"""
from pathlib import Path,PurePosixPath
import argparse,datetime,gzip,hashlib,json,os,re,shutil,struct,subprocess,sys,time,uuid
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(data):return hashlib.sha256(data).hexdigest()
def catalogue():return read(ROOT/'CATALOGO.json')
def safe(base,name):
    p=PurePosixPath(name)
    if p.is_absolute() or '..'in p.parts or ':'in name or '\\'in name:raise ValueError('Ruta lógica inválida: '+name)
    result=(base/Path(*p.parts)).resolve()
    if not result.is_relative_to(base.resolve()):raise ValueError('Ruta fuera de la biblioteca')
    return result
def content(item):
    data=safe(ROOT,item['storage']).read_bytes()
    if item['compression']=='gzip':data=gzip.decompress(data)
    if len(data)!=item['bytes']or sha(data)!=item['sha256']:raise ValueError('Integridad inválida: '+item['path'])
    return data
def verify(cat):
    seen=set();size=0
    for row in cat['files']:
        if row['storage']in seen:continue
        content(row);seen.add(row['storage']);size+=row['bytes']
    entries=cat.get('entrypoints')
    if not isinstance(entries,list)or not entries:raise ValueError('El catálogo no declara hashes de entrypoints')
    for entry in entries:
        p=safe(ROOT,entry['path']);data=p.read_bytes()
        if len(data)!=entry['bytes']or sha(data)!=entry['sha256']:raise ValueError('Integridad inválida del entrypoint: '+entry['path'])
    result=dict(unique_objects=len(seen),logical_files=len(cat['files']),entrypoints_checked=len(entries),unique_expanded_bytes=size,integrity='EXACT_SHA256_MATCHED')
    print(json.dumps(result,ensure_ascii=False));return result
def payload_fingerprint(cat):
    return sha(json.dumps([(r['path'],r['sha256'],r['bytes'])for r in cat['files']],sort_keys=True,separators=(',',':')).encode())
def materialize(cat,out,sectors=None):
    target=out/'_materializado';mark=target/'_MATERIALIZADO.json';fingerprint=payload_fingerprint(cat)
    selected=set(sectors)if sectors is not None else None
    rows=[r for r in cat['files']if selected is None or not r['path'].startswith('sectores/')or r['path'].split('/')[1]in selected]
    if mark.exists():
        metadata=read(mark)
        if metadata['payload_sha256']!=fingerprint:raise ValueError('La salida pertenece a otra selección; use una carpeta nueva')
        expected_catalog=sha((ROOT/'CATALOGO.json').read_bytes());cached_catalog=target/'CATALOGO.json'
        if metadata.get('source_catalog_sha256')!=expected_catalog or not cached_catalog.is_file()or sha(cached_catalog.read_bytes())!=expected_catalog:raise ValueError('El catálogo materializado cambió; conserve el intento y use otra salida')
        previous=set(metadata.get('materialized_paths',[r['path']for r in cat['files']]))
        for row in rows:
            if row['path']not in previous:
                p=safe(target,row['path']);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content(row));previous.add(row['path']);continue
            p=safe(target,row['path'])
            if not p.is_file():raise ValueError('Archivo ausente en la caché materializada: '+row['path'])
            data=p.read_bytes()
            if len(data)!=row['bytes']or sha(data)!=row['sha256']:raise ValueError('Archivo modificado en la caché materializada: '+row['path'])
        save(mark,dict(payload_sha256=fingerprint,logical_files=len(previous),materialized_paths=sorted(previous),source_catalog_sha256=expected_catalog))
        return target
    if target.exists()and any(target.iterdir()):raise ValueError('Materialización incompleta; conserve el intento y use una salida nueva')
    target.mkdir(parents=True,exist_ok=True)
    for row in rows:
        p=safe(target,row['path']);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content(row))
    shutil.copy2(ROOT/'CATALOGO.json',target/'CATALOGO.json')
    save(mark,dict(payload_sha256=fingerprint,logical_files=len(rows),materialized_paths=[r['path']for r in rows],source_catalog_sha256=sha((ROOT/'CATALOGO.json').read_bytes())))
    return target
def python313(requested=None):
    path=Path(requested).resolve()if requested else ROOT/'.entorno/Scripts/python.exe'
    if not path.exists():
        if sys.version_info[:2]==(3,13)and struct.calcsize('P')==8:path=Path(sys.executable)
        else:raise ValueError('Falta CPython3.13x64. Use preparar --python RUTA_PYTHON313 o --python al ejecutar. No se instalará en el sistema global.')
    check=subprocess.check_output([str(path),'-I','-B','-c','import sys,struct,json;print(json.dumps([list(sys.version_info[:2]),struct.calcsize("P")]))'],text=True)
    if json.loads(check)!=[[3,13],8]:raise ValueError('El intérprete seleccionado no es CPython3.13x64')
    return path
def prepare(cat,base):
    py=python313(base);env=ROOT/'.entorno'
    if env.exists():raise ValueError('El entorno ya existe; se conserva. Puede utilizar --python para otro entorno aislado.')
    subprocess.run([str(py),'-I','-B','-m','venv',str(env)],check=True)
    # El almacén por contenido puede comprimir el objeto y no conserva un
    # nombre .whl válido. pip necesita los bytes verificados y su nombre real.
    exe=env/'Scripts/python.exe';row=next(r for r in cat['files']if r['path']=='motor/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl')
    wheel=env/'_ruedas'/PurePosixPath(row['path']).name;wheel.parent.mkdir(parents=True,exist_ok=True);wheel.write_bytes(content(row))
    subprocess.run([str(exe),'-I','-B','-m','pip','install','--no-index','--no-deps',str(wheel)],check=True)
    print('Entorno local preparado:',exe)
def native_args(m,mode,py,mat,folder,external):
    block=m.get('native'if mode=='ejecutar'else'recalc')
    if not block:raise ValueError('Modo no preparado para '+m['id']+'; consulte el estado y pendiente del catálogo')
    values={'python':str(py),'out':str(folder),'sector':str(mat/'sectores'/m['sector']),'common':str(mat/'codigo_comun/cognitive'),'external_python':str(external or'')}
    command=[]
    for value in block['command']:
        value=str(value)
        for key,replacement in values.items():value=value.replace('{'+key+'}',replacement)
        if value.startswith(('sectores/','codigo_comun/')):value=str(mat/value)
        command.append(value)
    if any(re.search(r'\{[A-Za-z_][A-Za-z_0-9]*\}',v)for v in command):raise ValueError('Placeholder sin resolver')
    # El puente usa un segundo intérprete explícito. No confundir su NumPy
    # cp312 con el cp313 utilizado por el motor congelado.
    if mode=='ejecutar'and any(Path(v).name=='ejecutar_integrados.py'for v in command):
        local=mat/'sectores'/m['sector']/'sector.json';entry=next(x for x in read(local)['mechanisms']if x['id']==m['id'])
        if entry.get('bundle',{}).get('external')and not external:raise ValueError('Este protocolo requiere --external-python RUTA_CPYTHON312_X64; no usa otro intérprete silenciosamente')
        if external and'--external-python'not in command:command+=['--external-python',str(Path(external).resolve())]
    return command,block.get('timeout_seconds',m.get('timeout_seconds',2400))

def script_command(command):
    """Separa flags del intérprete sin confundir -I/-B/-X con el script."""
    flags=[];i=1
    while i<len(command)and command[i].startswith('-'):
        q=command[i]
        if q in('-c','-m'):raise ValueError('El catálogo debe nombrar un script de reproducción, no código inline o un módulo implícito')
        if q in('-X','-W'):
            if i+1>=len(command):raise ValueError('Opción de intérprete incompleta')
            flags+=command[i:i+2];i+=2
        else:flags.append(q);i+=1
    if i>=len(command):raise ValueError('El comando no contiene script')
    return flags,Path(command[i]),command[i+1:]

def terminate_owned_tree(proc):
    """El handle y poll certifican el proceso que inició este launcher."""
    report={'pid':proc.pid,'only_launcher_owned_process':True}
    if proc.poll()is not None:return{**report,'already_exited':True,'returncode':proc.returncode}
    if os.name=='nt':
        taskkill=Path(os.environ.get('SystemRoot',r'C:\Windows'))/'System32/taskkill.exe'
        try:
            result=subprocess.run([str(taskkill),'/PID',str(proc.pid),'/T','/F'],capture_output=True,text=True,encoding='utf8',errors='replace',timeout=20)
            report.update(tree_command=[str(taskkill),'/PID',str(proc.pid),'/T','/F'],tree_exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr)
        except Exception as exc:report['tree_error']=repr(exc)
    if proc.poll()is None:
        proc.kill();report['fallback_kill']=True
    try:proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill();proc.wait();report['second_fallback_kill']=True
    return{**report,'returncode':proc.returncode}
def execute(cat,ids,mode,out,requested,external,resume):
    selected={m['sector']for m in cat['mechanisms']if m['id']in ids}
    mat=materialize(cat,out,selected);py=python313(requested)if mode=='ejecutar'else Path(requested or sys.executable).resolve()
    results=[];progress=out/'PROGRESO.json';previous=read(progress)if progress.exists()else{'results':[]}
    for id in ids:
        m=next(x for x in cat['mechanisms']if x['id']==id)
        old=next((r for r in previous['results']if r['id']==id and r['mode']==mode and r.get('exit_code')==0),None)
        if resume and old:results.append(dict(old,resumed_without_new_execution=True));print(id,'conservado, no se repite',flush=True);continue
        folder=out/(mode+'_'+id+'_'+uuid.uuid4().hex[:6]);folder.mkdir(parents=True)
        begin=time.monotonic();error=None;returncode=None;command=[];termination=None
        try:
            command,timeout=native_args(m,mode,py,mat,folder,external)
            # Los intérpretes y su código estándar son dependencias declaradas.
            # Cada proceso Python queda auditado; las referencias son de lectura.
            flags,actor,args=script_command(command)
            permitted=['--read-executable',str(Path(external).resolve())]if external else[]
            wrapper=[str(py),'-I','-B','-X','utf8',*flags,str(mat/'codigo_comun/entorno_seguro.py'),'--script',str(actor),'--package',str(mat),'--out',str(out),*permitted,'--',*args]
            env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8');env.pop('PYTHONPATH',None)
            with(folder/'EJECUCION_STDOUT.log').open('w',encoding='utf8')as so,(folder/'EJECUCION_STDERR.log').open('w',encoding='utf8')as se:
                proc=subprocess.Popen(wrapper,cwd=mat,env=env,stdout=so,stderr=se,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                try:returncode=proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    termination=terminate_owned_tree(proc)if proc.poll()is None else{'already_exited':True,'pid':proc.pid,'returncode':proc.returncode}
                    returncode=124;error='Límite del proceso anfitrión; no es un resultado cognitivo.'
        except Exception as exc:error=repr(exc)
        row=dict(id=id,name=m['name'],mode=mode,exit_code=returncode,error=error,seconds=time.monotonic()-begin,command=command,output=str(folder),payload_sha256=payload_fingerprint(cat),not_current_Cognitive_life=True,termination=termination)
        save(folder/'EJECUCION_COMPENDIO.json',row);results.append(row);previous['results']=[r for r in previous['results']if(r['id'],r['mode'])!=(id,mode)]+[row];save(progress,previous)
        print(json.dumps({k:row[k]for k in('id','mode','exit_code','seconds','error')},ensure_ascii=False),flush=True)
    save(out/'RESULTADO_COMPENDIO.json',dict(results=results,mode=mode,payload_sha256=payload_fingerprint(cat),new_current_life_ticks=0))
    return int(any(r.get('exit_code')!=0 for r in results))
def show(cat):
    for m in cat['mechanisms']:
        kind='Instrumento sin ticksNative'if m.get('native_kind')=='instrumental_no_native'else'Ruta física disponible'
        print(m['id'],m['name'],'|',kind+':',bool(m.get('native')),'| Recálculo:',bool(m.get('recalc')),'|',m.get('new_validation_status','No verificado'))
def menu(cat):
    print('DEE Compendio reproducible R01\nWindowsx64 · CPython3.13 para Native\nSin ejecución física automática.\n')
    print('1 Catálogo\n2 Integridad\n3 Recalcular un ID\n4 Reproducir un ID\n5 Materializar para inspección\n0 Salir')
    choice=input('Opción: ').strip()
    if choice=='1':show(cat)
    elif choice=='2':verify(cat)
    elif choice in ('3','4'):
        id=input('ID Mxxx: ').strip().upper();out=ROOT/'resultados'/('run_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        print('Si no hay entorno, prepare primero con: reproducir.py preparar --python RUTA_PYTHON313')
        return execute(cat,[id],'recalcular'if choice=='3'else'ejecutar',out,None,None,False)
    elif choice=='5':print(materialize(cat,ROOT/'resultados'/('inspeccion_'+uuid.uuid4().hex[:6])))
    return 0
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['menu','catalogo','integridad','materializar','preparar','recalcular','ejecutar','todos']);p.add_argument('id',nargs='?');p.add_argument('--out',type=Path);p.add_argument('--python');p.add_argument('--external-python');p.add_argument('--sector');p.add_argument('--reanudar',action='store_true');a=p.parse_args();c=catalogue()
    if a.action=='menu':return menu(c)
    if a.action=='catalogo':show(c);return 0
    if a.action=='integridad':verify(c);return 0
    if a.action=='preparar':prepare(c,a.python);return 0
    out=(a.out or ROOT/'resultados'/('run_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))).resolve()
    if out==ROOT or any(out.is_relative_to(ROOT/k)for k in('motor','objetos')):raise ValueError('Los resultados necesitan un directorio separado de las referencias')
    if a.action=='materializar':print(materialize(c,out));return 0
    mode='recalcular'if a.action=='recalcular'else'ejecutar'
    if a.action=='todos':ids=[m['id']for m in c['mechanisms']if m.get('native')and(not a.sector or m['sector']==a.sector)]
    elif a.action=='recalcular'and a.id=='todos':ids=[m['id']for m in c['mechanisms']if m.get('recalc')and(not a.sector or m['sector']==a.sector)]
    else:ids=[a.id]
    if not ids or ids==[None]:p.error('Indique un ID del catálogo')
    return execute(c,ids,mode,out,a.python,a.external_python,a.reanudar)
if __name__=='__main__':raise SystemExit(main())
