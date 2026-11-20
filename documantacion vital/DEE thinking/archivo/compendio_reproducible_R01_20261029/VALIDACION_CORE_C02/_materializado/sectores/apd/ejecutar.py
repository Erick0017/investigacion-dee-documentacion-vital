"""Reproduce protocolos APD archivados; los targets sólo se leen al comparar."""
from pathlib import Path
import argparse,ast,datetime,gzip,hashlib,importlib.util,json,os,shutil,subprocess,sys,time
BASE=Path(__file__).resolve().parent
def read(p):
    data=Path(p).read_bytes()
    if str(p).endswith('.gz'):data=gzip.decompress(data)
    return json.loads(data)
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def package():
    return next(p for p in BASE.parents if (p/'CATALOGO.json').exists())
def load_namespace(path,overrides):
    tree=ast.parse(path.read_text(encoding='utf-8-sig'))
    tree.body=[n for n in tree.body if not isinstance(n,ast.Assign) or not any(isinstance(x,ast.Name) and x.id in overrides for x in n.targets)]
    ns=dict(__name__='APD_PROTOCOLO_ARCHIVADO',__file__=str(path),**overrides)
    exec(compile(tree,str(path),'exec'),ns);return ns
def ficha(system,source):
    # El observador lee el formato completo; esta ficha no escribe memoria.
    source=BASE/source;target=system/'estado/checkpoints'/source.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    path=system/'capacidades/observador_causal_retrospectivo_01.py'
    spec=importlib.util.spec_from_file_location('snapshot_pasivo',path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    snap=mod.Snapshot(target);summary=snap.summary();meta=json.loads(snap.metadata[mod.LIFE_KEY])
    rec={k:meta[k] for k in ('life_id','world_id','profile','branch','parent')}
    rec.update(schema='DCS1.1.life.v1',snapshot=target.relative_to(system).as_posix(),snapshot_sha256=snap.encoded_sha256,
        physical={k:summary[k] for k in ('N','tick','RAW_sha256','clocks_sha256','occupied')},operations=[],operation_count_offset=meta['operation_count'],
        knowledge={'scope':'Ficha documental extraída del snapshot completo y su SYSTEM_KEY; ninguna memoria física modificada'})
    save(system/'estado/vidas'/rec['life_id']/'VIDA.json',rec);return rec
def _compare_values(label,actual,expected,checks):checks.append(dict(label=label,matches=actual==expected,actual=actual,reference=expected))
def compare(job,output):
    checks=[];kind=job['comparison'];ref=BASE/job['reference']
    if kind=='lexical':
        for mode in ('paired','reversed','omitted'):
            a=read(output/(mode+'_02_SUMMARY.json'));e=read(ref/(mode+'_02_SUMMARY.json'))
            for k in ('tick','old_first','first_new','later_panel','native_regression','after_numeric_panel','admission'):_compare_values(mode+'/'+k,a[k],e[k],checks)
            pa=read(output/(mode+'_01_PRIMARY.json.gz'));pe=read(ref/(mode+'_01_PRIMARY.json.gz'))
            for k in ('tick','RAW_sha256','clocks_sha256'):_compare_values(mode+'/physical/'+k,pa['physical'][k],pe['physical'][k],checks)
    elif kind=='delta':
        for mode in ('T','U','D','H','CUT','SHAM'):
            a=read(output/mode/'05_RESULTADO_COMPLETO.json.gz');e=read(ref/mode/'05_RESULTADO_COMPLETO.json.gz')
            for k in ('tick','RAW_sha256','clocks_sha256'):_compare_values(mode+'/physical/'+k,a['physical'][k],e['physical'][k],checks)
            _compare_values(mode+'/numeric_outputs',[r['numeric_result']for r in a['result']['uses']],[r['numeric_result']for r in e['result']['uses']],checks)
    elif kind=='accumulator':
        for mode in ('real','omit','sham'):
            a=read(output/(mode+'_PRIMARY.json.gz'));e=read(ref/(mode+'_PRIMARY.json.gz'))
            for k in ('tick','RAW_sha256','clocks_sha256'):_compare_values(mode+'/physical/'+k,a['after'][k],e['after'][k],checks)
            _compare_values(mode+'/numbers',[r['numeric_result']for r in a['uses']],[r['numeric_result']for r in e['uses']],checks)
    elif kind=='sensor':
        a=read(output/'RESULTADOS.json');e=read(ref/'RESULTADOS.json')
        _compare_values('winning_family',a['winning_family'],e['winning_family'],checks)
        for x,y in zip(a['families'],e['families']):
            _compare_values('native_link_criterion',x['native_link_criterion'],y['native_link_criterion'],checks)
            for arm,earm in zip(x['arms'],y['arms']):
                for k in ('tick','RAW_sha256','clocks_sha256'):_compare_values('arm'+str(arm['arm'])+'/'+k,arm['final'][k],earm['final'][k],checks)
    elif kind=='r04':
        refs=[]
        for f in (BASE/'archivo/APD02').rglob('RESULTADOS.json'):
            try:v=read(f)
            except Exception:continue
            if v.get('schema')=='APD02.R04.actual_ABAB_and_short_controls.v1':refs.append(v)
        if not refs:raise FileNotFoundError('Primario R04 ABAB con sus controles')
        a=read(output/'RESULTADOS.json');e=refs[0]
        for arm,old in zip(a['arms'],e['arms']):
            _compare_values(arm['mode']+'/rows',arm['rows'],old['rows'],checks)
            for k in ('tick','RAW_sha256','clocks_sha256'):_compare_values(arm['mode']+'/physical/'+k,arm['final_record']['physical'][k],old['final_record']['physical'][k],checks)
    elif kind=='quality':
        a=read(output/'RESULTADOS_CALIDAD.json');_compare_values('issues',a['issues'],[],checks);_compare_values('fixture_not_Native',a['native_Runtime_imported'],False,checks)
    return checks
def child_job(job,out,common):
    root=out/'trabajo';system=root/'sistema';shutil.copytree(common,system,ignore=shutil.ignore_patterns('estado','__pycache__','*.pyc'))
    records=[ficha(system,p)for p in job['parents']]
    save(system/'estado/ACTIVO.json',dict(life_id=records[0]['life_id'] if records else 'NO_ACTIVE',copy_only=True))
    source=BASE/job['script'];here=source.parent
    lab=root/'laboratorio/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01'
    if job.get('budget_file'):save(lab/'PRESUPUESTO.json',dict(deadline_utc=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=1800)).isoformat()))
    destination=root/job['output'];overrides=dict(HERE=here,ROOT=root,SYSTEM=system,LAB=lab)
    if job.get('deadline'):overrides['DEADLINE']=datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=580)
    for k,v in job.get('global_paths',{}).items():overrides[k]=system/'estado/checkpoints'/Path(v).name
    sys.path[:0]=[str(system),str(here)]
    namespace=load_namespace(source,overrides)
    if job['kind']=='system_out':args=['--system',str(system),'--out',str(destination)]+job.get('argv',[])
    elif job['kind']=='pure_quality':args=['--salida',str(destination)]
    elif job['comparison']=='lexical':args=[]
    else:args=['--out',str(destination)]
    sys.path[:0]=[str(system),str(here)];sys.argv=[str(source)]+args
    result=namespace['main']()
    if result not in (None,False,0):raise RuntimeError('El protocolo archivado devolvió error: '+str(result))
    checks=compare(job,destination);save(out/'RESULTADO.json',dict(mechanism=job['id'],mode='INSTRUMENTAL_NO_NATIVE'if job['kind']=='pure_quality'else'NATIVE_PROTOCOL_REPRODUCTION',checks=checks,status='MATCHED'if checks and all(c['matches']for c in checks)else'DIFFERENT',output=str(destination),parents=records))
    if not checks or not all(c['matches']for c in checks):raise SystemExit(1)
def walk(value):
    if isinstance(value,dict):
        yield value
        for k,v in value.items():
            if k in ('result_json','result')and isinstance(v,str)and v.lstrip().startswith(('{','[')):
                try:v=json.loads(v)
                except ValueError:pass
            yield from walk(v)
    elif isinstance(value,list):
        for v in value:yield from walk(v)
def recalc(id,out):
    campaign={'M301':['APD01'],'M302':['APD01'],'M303':['APD02'],'M304':['APD02'],'M305':['APD03'],'M306':['APD03'],'M307':['APD04'],'M308':['APD05'],'M309':['APD02']}[id]
    errors=[];fields=0;files=0;decoder=0;out.mkdir(parents=True,exist_ok=True)
    historical=[]
    selected={
        'M301':('archivo/APD01/APD_P01_P26/RECALCULO/recalcular_lexico_r04.py',['--primarios',str(BASE/'archivo/APD01/APD_P01_P26/CURRICULO_LEXICO_R04'),'--salida',str(out/'LEXICO_RECALCULADO.json')]),
        'M302':('archivo/APD01/MECANISMO/RECALCULO/recalcular_perfil_delta_r1.py',['--evidencia',str(BASE/'archivo/APD01/MECANISMO/EVIDENCIA/PERFIL_DELTA_R1'),'--salida',str(out/'DELTA_RECALCULADO.json')]),
        'M303':('archivo/APD02/ACUMULADOR_LEXICO/CODIGO/recalcular_acumulador_r01_r02.py',['--evidence',str(BASE/'archivo/APD02/ACUMULADOR_LEXICO/EVIDENCIA/ACUMULADOR'),'--output',str(out/'ACUMULADOR_RECALCULADO.json')])}
    if id in selected:
        script,args=selected[id]
        with(out/'RECALCULO_ORIGINAL_STDOUT.log').open('w',encoding='utf8')as so,(out/'RECALCULO_ORIGINAL_STDERR.log').open('w',encoding='utf8')as se:
            result=subprocess.run([sys.executable,'-I','-B',str(BASE/script),*args],cwd=out,stdout=so,stderr=se)
        historical.append(dict(script=script,exit_code=result.returncode))
        if result.returncode:errors.append(dict(error='original_recalculator_failed',script=script,exit_code=result.returncode))
    for name in campaign:
        for p in (BASE/'archivo'/name).rglob('*'):
            if not p.is_file() or not str(p).endswith(('.json','.json.gz','.jsonl','.jsonl.gz')):continue
            if any(k in p.parts for k in ('FUENTES','CODIGO_EJECUTADO','FUENTES_ANTES_DE_NATIVE','CODIGO_DELTA')):continue
            try:
                data=p.read_bytes();data=gzip.decompress(data)if p.suffix=='.gz'else data
                objs=[json.loads(x)for x in data.splitlines()if x.strip()]if '.jsonl'in p.name else [json.loads(data)]
            except (ValueError,UnicodeError,OSError):continue
            files+=1
            for obj in objs:
                for row in walk(obj):
                    if 'raw'not in row or not any(k in row for k in ('s_reg','semantic','state')):continue
                    try:r=int(row['raw'])
                    except (ValueError,TypeError):continue
                    if isinstance(row['raw'],float) or not 0<=r<2**64:errors.append(dict(file=str(p.relative_to(BASE)),error='uint64_domain'));continue
                    actual=dict(state=r&0xffffffff,s_reg=(r>>32)&65535,semantic=(r>>60)&15)
                    for k,v in actual.items():
                        if k in row:
                            fields+=1
                            if row[k]!=v:errors.append(dict(file=str(p.relative_to(BASE)),field=k,raw=str(r),stored=row[k],computed=v))
    save(out/'RECALCULO.json',dict(mechanism=id,mode='RECALCULO_DE_PRIMARIOS_SIN_MOTOR',new_native_ticks=0,files=files,fields_recomputed=fields,original_recalculators=historical,errors=errors))
    print(json.dumps(dict(id=id,files=files,fields=fields,errors=len(errors))))
    if errors:raise SystemExit(1)
def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['native','recalc','_child']);p.add_argument('mechanism');p.add_argument('--out',type=Path,required=True);p.add_argument('--common',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    if a.mode=='recalc':return recalc(a.mechanism,a.out)
    job=next(j for j in read(BASE/'native_jobs.json')if j['id']==a.mechanism)
    common=a.common or package()/'codigo_comun/cognitive'
    if a.mode=='_child':return child_job(job,a.out,common)
    # Proceso separado por mecanismo, sin importar el original Cognitive.
    cmd=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'_child',a.mechanism,'--out',str(a.out),'--common',str(common)]
    with(a.out/'stdout.log').open('w',encoding='utf8')as so,(a.out/'stderr.log').open('w',encoding='utf8')as se:r=subprocess.run(cmd,cwd=a.out,stdout=so,stderr=se,timeout=1800,env=dict(os.environ,OMP_NUM_THREADS='1'))
    if r.returncode:raise SystemExit(r.returncode)
if __name__=='__main__':main()
