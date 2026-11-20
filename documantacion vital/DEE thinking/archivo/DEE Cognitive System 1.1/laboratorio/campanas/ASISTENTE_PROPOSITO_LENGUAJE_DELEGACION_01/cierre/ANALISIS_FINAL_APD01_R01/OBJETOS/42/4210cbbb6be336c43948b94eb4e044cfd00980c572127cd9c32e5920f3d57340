"""Close executed HOST references as a separate portable analysis stage, zero ticks."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
    import gzip
    b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def emit(p,v):
    if p.exists():raise FileExistsError(str(p))
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def copy(p,q):
    q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
    if sha(p)!=sha(q):raise ValueError('Copy changed bytes')
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in('actual','code','learner_initial','learner_reverse','system','out','check_root'):ap.add_argument('--'+name.replace('_','-'),dest=name,type=Path,required=True)
    a=ap.parse_args()
    if a.out.exists():raise FileExistsError('Fresh closed revision required')
    provenance=[]
    for domain,source in(('INITIAL_N1_E5',a.learner_initial),('REVERSE_N5_E1',a.learner_reverse)):
        dest=a.actual/'LEARNER_EXISTENTE'/domain
        if dest.exists():raise FileExistsError('Preserve existing comparison projection')
        dest.mkdir(parents=True);primary=source/'03_RESULTADO_COMPLETO.json.gz';data=load(primary)['result'];copy(primary,dest/'RESULTADO_COMPLETO.json.gz')
        copied=[primary]
        for row in data['rows']:
            if row['artifact']:
                p=source/row['artifact']['file'];copy(p,dest/p.name);copied.append(p)
        provenance.append({'domain':domain,'original_learner_repeated':False,'sources':[{'source_local_locator':str(p.resolve()),'sha256':sha(p),'bytes':p.stat().st_size}for p in copied]})
    emit(a.actual/'PROCEDENCIA_LEARNER_REUTILIZADO.json',{'native_ticks':0,'cases':provenance})
    comparison=a.code/'comparar_referencias_ejecutadas_r1.py';reference=a.actual/'COMPARACION_REFERENCIAS_OBSERVADAS_R1.json'
    result=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(comparison),'--evidencia',str(a.actual),'--salida',str(reference)],capture_output=True,text=True,encoding='utf8',timeout=60)
    if result.returncode:raise ValueError(result.stdout+result.stderr)
    a.out.mkdir(parents=True);omitted=[]
    for p in sorted(a.actual.rglob('*')):
        if not p.is_file():continue
        if p.name.endswith('.deetsnap.gz'):
            omitted.append({'local_locator':str(p.resolve()),'sha256':sha(p),'bytes':p.stat().st_size,'reason':'Complete reached native snapshot remains local; analysis is not a continuation bundle'})
        else:copy(p,a.out/'EVIDENCIA'/p.relative_to(a.actual))
    summary=load(a.actual/'RESULTADOS.json');frozen=load(a.actual/'ANTES_DEL_PRIMER_TICK.json')
    operational=[*frozen['parents']]
    for row in summary['outcomes']:
        record=row.get('final_record',row.get('reached'))
        if record:operational.append(record)
    for p in a.actual.glob('*/00_FORK_COMPLETO.json.gz'):operational.append(load(p))
    seen={row['local_locator']for row in omitted}
    for rec in operational:
        p=a.system/rec['snapshot'];name=str(p.resolve())
        if name in seen:continue
        seen.add(name)
        if sha(p)!=rec['snapshot_sha256']:raise ValueError('A named reference/parent saved state changed')
        omitted.append({'life_id':rec['life_id'],'tick':rec['physical']['tick'],'local_locator':name,'sha256':sha(p),'bytes':p.stat().st_size,'reason':'Complete protected parent or actual reference saved world remains local; no recipe replacement'})
    code_names=('ejecutar_referencias_externas_o2_r1.py','PROTOCOLO_REFERENCIAS_EJECUTADAS_O2_R1.json','recalcular_referencias_ejecutadas_o2_r1.py','recalcular_referencias_ejecutadas_ORIGINAL_ERROR_ORIGEN.py','comparar_referencias_ejecutadas_r1.py','preparar_stage_referencias_ejecutadas_r1.py')
    for name in code_names:copy(a.code/name,a.out/'CODIGO_Y_CONTEXTO'/name)
    for name in('recalcular_referencias_ejecutadas_o2_r1.py','comparar_referencias_ejecutadas_r1.py'):copy(a.code/name,a.out/'RECALCULO'/name)
    copy(a.actual/'RECALCULO_REFERENCIAS_EJECUTADAS_R02.json',a.out/'REFERENCIAS/ACTOS_REFERENCIA.json')
    copy(reference,a.out/'REFERENCIAS/COMPARACION.json')
    plan={'schema':'APD01.executed_host_reference.closed_portable_plan.v1','native_ticks':0,'jobs':[
        {'name':'REFERENCIAS_HOST_REALMENTE_EJECUTADAS','base':'.','script':'RECALCULO/recalcular_referencias_ejecutadas_o2_r1.py','args':['--evidencia','EVIDENCIA','--salida','{output}'],'reference':'REFERENCIAS/ACTOS_REFERENCIA.json'},
        {'name':'COMPARACION_REFERENCIAS_CON_LEARNER_EXISTENTE','base':'.','script':'RECALCULO/comparar_referencias_ejecutadas_r1.py','args':['--evidencia','EVIDENCIA','--salida','{output}'],'reference':'REFERENCIAS/COMPARACION.json'}]}
    emit(a.out/'PLAN_RECALCULO.json',plan)
    emit(a.out/'INDICE_ESTADOS_COMPLETOS_LOCALES.json',{'schema':'APD01.reference_complete_state_local_omissions.v1','native_ticks':0,'omitted_full_states':omitted,'no_failed_result_omitted':True,'not_an_operational_backup':True})
    with tempfile.TemporaryDirectory(prefix='_apd_actualrefs_',dir=a.check_root)as directory:
        tree=Path(directory)/'extraido';shutil.copytree(a.out,tree);checks=[]
        for index,item in enumerate(plan['jobs']):
            output=Path(directory)/(str(index)+'.json');argv=[sys.executable,'-I','-B','-X','utf8',str(tree/item['script']),*[str(output)if v=='{output}'else v for v in item['args']]]
            r=subprocess.run(argv,cwd=tree,capture_output=True,text=True,encoding='utf8',timeout=60)
            exact=r.returncode==0 and output.exists()and output.read_bytes()==(tree/item['reference']).read_bytes()
            checks.append({'name':item['name'],'returncode':r.returncode,'exact_reference_bytes':exact,'stdout':r.stdout,'stderr':r.stderr})
            if not exact:raise ValueError(json.dumps(checks[-1],ensure_ascii=False))
    emit(a.out/'COMPROBACION_PORTABLE.json',{'native_ticks':0,'checks':checks,'scope':'Archived recalculation only; actual native work happened in the prior15-task reference run, not this check'})
    emit(a.out/'MANIFIESTO.json',{'schema':'SHA256.members.no_self_reference.v1','members':[{'file':p.relative_to(a.out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(a.out.rglob('*'))if p.is_file()]})
    print(result.stdout,end='');print(json.dumps({'stage':str(a.out),'portable_cases':len(checks),'dense_snapshots_local_only':len(omitted),'native_ticks_in_closure':0}))

if __name__=='__main__':main()
