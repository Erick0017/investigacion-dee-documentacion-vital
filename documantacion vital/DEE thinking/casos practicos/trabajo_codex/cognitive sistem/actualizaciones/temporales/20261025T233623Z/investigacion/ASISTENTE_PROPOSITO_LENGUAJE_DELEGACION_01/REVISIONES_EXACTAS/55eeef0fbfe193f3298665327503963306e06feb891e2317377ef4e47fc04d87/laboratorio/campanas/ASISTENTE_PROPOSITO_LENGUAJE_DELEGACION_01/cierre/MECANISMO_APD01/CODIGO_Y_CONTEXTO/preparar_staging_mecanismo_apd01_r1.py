"""Copy closed APD01 mechanism evidence; retain exact bytes, omit only indexed full snapshots."""
import argparse,gzip,hashlib,importlib.util,json,shutil,subprocess,sys,tempfile
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    if p.exists():raise FileExistsError(str(p))
    p.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def copy(source,target):
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    if sha(source)!=sha(target):raise ValueError('Copy changed bytes')
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in('code','evidence','antecedent','out'):ap.add_argument('--'+key,type=Path,required=True)
    a=ap.parse_args()
    if a.out.exists():raise FileExistsError('New closed stage only')
    a.out.mkdir(parents=True);omissions=[]
    for source in sorted(a.evidence.rglob('*')):
        if not source.is_file():continue
        rel=source.relative_to(a.evidence)
        if source.name.endswith('.deetsnap.gz'):
            omissions.append({'file':rel.as_posix(),'local_locator':str(source.resolve()),'bytes':source.stat().st_size,'sha256':sha(source),'reason':'Full local operational snapshot; analysis contains decisive archived observations and matched whole-field projections, not an operational backup.'})
        else:copy(source,a.out/'EVIDENCIA'/rel)
    for source in sorted(a.code.iterdir()):
        if source.is_file():copy(source,a.out/'CODIGO_Y_CONTEXTO'/source.name)
    names=('recalcular_perfil_delta_r1.py','recalcular_consecuencias_y_campo_r1.py','recalcular_agregacion_previa.py')
    for name in names:copy(a.code/name,a.out/'RECALCULO'/name)
    copy(a.code/'INFORME_ARITMETICA_Y_RETORNO_COMUN.md',a.out/'INFORME_ARITMETICA_Y_RETORNO_COMUN.md')
    copy(a.evidence/'PERFIL_DELTA_R1/RECALCULO_DELTA_R1.json',a.out/'REFERENCIAS/DELTA.json')
    copy(a.evidence/'RUTA_O2_R3/RECALCULO_CONSECUENCIAS_Y_CAMPO_R1.json',a.out/'REFERENCIAS/CONSECUENCIAS_Y_CAMPO.json')
    # Exact JSON-value projection of the 12 original R17 transport rows selected by the original fixed predicate.
    spec=importlib.util.spec_from_file_location('PRIOR_RECALC',a.code/'recalcular_agregacion_previa.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    original=a.antecedent.read_bytes();rows=json.loads(gzip.decompress(original));chosen=[];locations=[]
    for index,row in enumerate(rows):
        if str(row.get('id','')).startswith('fi60r3_')and any(True for _ in module.walk(row)):
            chosen.append(row);locations.append({'row_index':index,'id':row['id'],'canonical_value_sha256':hashlib.sha256(json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()})
    prior=a.out/'EVIDENCIA/ANTECEDENTE_R17';prior.mkdir()
    target=prior/'REGISTROS_NUMERICOS_R17_PROYECCION.json.gz'
    target.write_bytes(gzip.compress((json.dumps(chosen,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8'),mtime=0))
    write(prior/'PROCEDENCIA.json',{'schema':'APD01.R17.exact_JSON_value_projection.v1','source_local_locator':str(a.antecedent.resolve()),'original_compressed_sha256':hashlib.sha256(original).hexdigest(),'original_compressed_bytes':len(original),'selection':'IDs start fi60r3_ and contain native_joint_raw_perception; no success filter','rows':locations,'projected_file_sha256':sha(target),'byte_identity_to_original_container_claimed':False,'all_integer_values_and_order_preserved':True})
    write(a.out/'REFERENCIAS/ANTECEDENTE_R17.json',module.calculate(target))
    plan={'schema':'APD01.mechanism.portable_recalculation_plan.v1','native_ticks':0,'jobs':[
        {'name':'DESPLAZAMIENTO_ADQUIRIDO_CINCO_USOS','base':'.','script':'RECALCULO/recalcular_perfil_delta_r1.py','args':['--evidencia','EVIDENCIA/PERFIL_DELTA_R1','--salida','{output}'],'reference':'REFERENCIAS/DELTA.json'},
        {'name':'RETORNO_FASE_O2_REVERSO_Y_CAMPO_COMPLETO','base':'.','script':'RECALCULO/recalcular_consecuencias_y_campo_r1.py','args':['--evidencia','EVIDENCIA','--salida','{output}'],'reference':'REFERENCIAS/CONSECUENCIAS_Y_CAMPO.json'},
        {'name':'ANTECEDENTE_R17_DOCE_EMISIONES','base':'.','script':'RECALCULO/recalcular_agregacion_previa.py','args':['--registro','EVIDENCIA/ANTECEDENTE_R17/REGISTROS_NUMERICOS_R17_PROYECCION.json.gz','--salida','{output}'],'reference':'REFERENCIAS/ANTECEDENTE_R17.json'}]}
    write(a.out/'PLAN_RECALCULO.json',plan)
    write(a.out/'INDICE_OMISIONES.json',{'schema':'APD01.mechanism.local_operational_snapshots_omitted.v1','omitted':omissions,'no_negative_primary_omitted':True,'scope':'Snapshot bytes remain local. This stage is analysis evidence, not an autonomous continuation bundle. Source paths are locators only, never runtime dependencies of portable recalculations.'})
    checks=[]
    with tempfile.TemporaryDirectory(prefix='APD_MECHANISM_PORTABLE_',dir=a.out.parent)as temporary:
        for index,job in enumerate(plan['jobs']):
            output=Path(temporary)/(str(index)+'.json');argv=[sys.executable,'-I','-B','-X','utf8',str(a.out/job['script'])]+[str(output)if v=='{output}'else v for v in job['args']]
            result=subprocess.run(argv,cwd=a.out,capture_output=True,text=True,encoding='utf8',timeout=60)
            equal=result.returncode==0 and output.is_file()and output.read_bytes()==(a.out/job['reference']).read_bytes()
            checks.append({'name':job['name'],'returncode':result.returncode,'byte_identical_to_reference':equal,'stdout':result.stdout,'stderr':result.stderr})
            if not equal:raise ValueError(json.dumps(checks[-1],ensure_ascii=False))
    write(a.out/'COMPROBACION_PORTABLE.json',{'native_ticks':0,'checks':checks,'scope':'Archived recalculation only; not native reproduction or a new acquisition.'})
    files=[p for p in sorted(a.out.rglob('*'))if p.is_file()]
    write(a.out/'MANIFIESTO.json',{'schema':'SHA256.members.no_self_reference.v1','members':[{'file':p.relative_to(a.out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in files]})
    print(json.dumps({'files_including_manifest':len(files)+1,'omitted_full_snapshots':len(omissions),'recalculations':len(checks),'native_ticks':0,'stage':str(a.out)}))

if __name__=='__main__':main()
