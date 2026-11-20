"""Build the final evidence plan from closed stages, not live runtime trees.

This is packaging instrumentation only. It does not import DEE or select actions.
It refuses missing closure/manual/distribution proofs rather than inventing them.
"""
from __future__ import annotations
import argparse,gzip,hashlib,json
from pathlib import Path

HERE=Path(__file__).resolve().parent
LAB=HERE.parent
ROOT=LAB.parents[2]
S=ROOT/'sistema'
EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def expanded(p):
    b=Path(p).read_bytes()
    return gzip.decompress(b) if Path(p).suffix=='.gz' else b
def write(p,v):
    if p.exists():raise FileExistsError(p)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--service-stage',type=Path,required=True)
    ap.add_argument('--verification-tree',type=Path,required=True)
    ap.add_argument('--distribution-proof',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    a=ap.parse_args()
    if a.output_dir.exists():raise FileExistsError(a.output_dir)
    closure=read(LAB/'CONTINUIDAD_MENTE_UNIFICADA_Y_FI01.json')
    assert closure['status']=='CLOSED_SCIENTIFIC_CUT'
    editorial=read(LAB/'documentos/EDICION_MANUAL_MUFI01.json')
    manual=Path(editorial['document'])
    assert manual.is_file() and sha(manual)==editorial['sha256']
    assert a.distribution_proof.is_file() and a.verification_tree.is_dir()
    distribution=read(a.distribution_proof)
    assert distribution['status']=='COMPLETED_WITH_RECORDED_SCOPE',distribution.get('error')
    assert distribution['originals_unchanged'] and distribution['zip_unchanged']
    assert Path(distribution['zip']).is_file() and sha(Path(distribution['zip']))==distribution['zip_sha256']
    functional_issues=distribution.get('service_sequence',{}).get('functional_issues',[])
    draft=read(HERE/'PLAN_GLOBAL_BORRADOR.json')
    cases=list(draft['cases'])
    stages=[(x['package_base'],LAB/x['source_tree_relative_to_lab']) for x in draft['stages']]
    stages.extend([('PREFLIGHT_R3',HERE/'PREFLIGHT_R3'),('SERVICIO_FASE_R3',a.service_stage),('PRUEBA_DISTRIBUCION',a.verification_tree)])
    for namespace,folder in stages[len(draft['stages']):]:
        plan=read(folder/'PLAN_RECALCULO.json')
        jobs=plan.get('cases',plan.get('jobs',[])) if isinstance(plan,dict) else plan
        assert jobs,folder
        for i,item in enumerate(jobs):
            if 'argv' in item:
                argv=item['argv'];at=next(j for j,x in enumerate(argv) if str(x).endswith('.py'))
                script=argv[at];args=argv[at+1:]
            else:script=item['script'];args=item['args']
            ref=folder/item['reference'];source=folder/script
            assert source.is_file() and ref.is_file()
            cases.append({'case':namespace+'_'+str(i+1),'base':namespace,'script':script,'args':args,'reference':item['reference'],'script_sha256':sha(source),'reference_expanded_sha256':hashlib.sha256(expanded(ref)).hexdigest(),'native_ticks':0,'timeout_seconds':240})
    cases.extend([
        {'case':'MAIN_A','base':'.','script':'CODIGO_MAIN/recalcular_corte_A.py','args':['--evidencia','TRAYECTORIA_MAIN','--salida','unused_A.json'],'reference':'TRAYECTORIA_MAIN/RECALCULO_CORTE_A.json','timeout_seconds':180},
        {'case':'MAIN_B_128','base':'.','script':'CODIGO_MAIN/recalcular_aplicacion_B.py','args':['--evidencia','TRAYECTORIA_MAIN','--salida','unused_B.json'],'reference':'TRAYECTORIA_MAIN/RECALCULO_APLICACION_B_CON_128.json','timeout_seconds':180}
    ])
    global_plan={'schema':'MUFI01.final.archived_global_recalculation.v1','status':'CLOSED_APPROVED_FOR_PACKAGING','native_ticks':0,'requires':'Python3 standard library only; exact arithmetic/decoding and archived tool-byte verification, not native replay','cases':cases,'scope_limits':['Correlated forks are not independent learners','A recalculation does not continue a learned life','Deep complete worlds and official engine are deliberately outside this analysis ZIP','The full collaboration ZIP has a separate exact-extraction native verification']}
    files=[]
    def add(source,to=None):
        source=Path(source);assert source.is_file(),source
        files.append({'source':str(source),'to':to or source.name})
    for name in ('INFORME_RESULTADOS.md','CAPACIDADES_POR_VIDA.json','COBERTURA.json','CONTINUIDAD_MENTE_UNIFICADA_Y_FI01.json','CONTINUIDAD_R11_PRESERVADA.json','CIERRE_INTERNO_A.json','PRESUPUESTO.json','DECISIONES_E_INCORPORACIONES.md'):
        add(LAB/name)
    add(HERE/'LEER_ANALISIS.md','LEER_PRIMERO.md')
    add(HERE/'repetir_todo.py','RECALCULO/REPETIR_TODO.py')
    add(HERE/'extraer_revision.py','RECALCULO/EXTRAER_REVISION.py')
    add(HERE/'armar_analisis.py','RECALCULO/SELLAR_EXTRACCION.py')
    add(HERE/'preparar_plan_analisis_final.py','RECALCULO/PREPARAR_PLAN_FINAL.py')
    add(HERE/'verificar_cierre_externo.py','RECALCULO/VERIFICAR_CIERRE_EXTERNO.py')
    add(HERE/'REVISION_HELPERS_Y_PLAN_GLOBAL.md','RECALCULO/REVISION_DEPENDENCIAS.md')
    add(manual,'MANUAL/'+manual.name)
    add(LAB/'documentos/EDICION_MANUAL_MUFI01.json','MANUAL/EDICION_MANUAL_MUFI01.json')
    for name in ('actualizar_manual_mufi01.py','preparar_datos_manual.py'):
        add(LAB/'documentos'/name,'MANUAL/CODIGO/'+name)
    add(a.distribution_proof,'VERIFICACION_DISTRIBUCION/'+a.distribution_proof.name)
    add(S/'gestionar.py','DELTA_SISTEMA/gestionar.py')
    for source in sorted((S/'app').glob('*.py')):add(source,'DELTA_SISTEMA/app/'+source.name)
    for name in ('mente_unificada_01.py','selector_acrecion_nativo.py','percepcion_cruda_fi01.py','mente_acumulativa_r02.py','acceso_nativo_mufi01.py','eo02_trabajador_local.py'):
        add(S/'capacidades'/name,'DELTA_SISTEMA/capacidades/'+name)
    for name in ('MENTE_UNIFICADA_01.json','FI01_PERCEPCION_CRUDA.json','ACCESO_NATIVO_MUFI01.json','PROTECCION_FASE_SENSOR_R3P0.json','SERVICIO_PERSISTENTE_MU01.json'):
        add(S/'contratos'/name,'DELTA_SISTEMA/contratos/'+name)
    add(S/'capacidades/CATALOGO_CAPACIDADES.json','DELTA_SISTEMA/capacidades/CATALOGO_CAPACIDADES.json')
    for pattern in ('GUIA*MU01*','GUIA*R3P0*','GUIA*UNIFICADA*','GUIA*ACCESO*NATIVO*'):
        for source in sorted((S/'documentacion').glob(pattern)):
            if source.is_file():add(source,'DELTA_SISTEMA/documentacion/'+source.name)
    for source in sorted((LAB/'fase_r3').glob('*')):
        if source.is_file() and source.suffix in('.json','.md'):add(source,'REVISION_FASE_R3/'+source.name)
    trees=[{'source':str(path),'to':namespace} for namespace,path in stages]
    expression_omitted=[]
    if (EV/'expresion').is_dir():
        for source in sorted((EV/'expresion').rglob('*')):
            if not source.is_file() or '__pycache__' in source.parts:continue
            if source.name.endswith('.deetsnap.gz'):
                expression_omitted.append({'source':str(source),'reason':'Unique complete auxiliary calibration world retained locally; exact primary observations, failed outputs and execution source are included, but analysis is not a continuation backup.'})
            else:add(source,'EXPRESION/EVIDENCIA/'+source.relative_to(EV/'expresion').as_posix())
    trees.append({'source':str(LAB/'expresion'),'to':'EXPRESION/CODIGO'})
    omitted=list(expression_omitted)
    for rel in (closure['main']['snapshot'],'estado/checkpoints/MU_MAIN.T68924.dc0d69393fc9.deetsnap.gz'):
        omitted.append({'source':str(S/rel),'reason':'Complete local life checkpoint; analysis is not an operational backup. Full paired continuation package distributed separately.'})
    omitted.append({'source':editorial['baseline'],'reason':'Previous manual preserved locally with exact identity. Only one current Word is included in the analysis.'})
    a.output_dir.mkdir(parents=True)
    write(a.output_dir/'PLAN_GLOBAL.json',global_plan)
    add(a.output_dir/'PLAN_GLOBAL.json','RECALCULO/PLAN_GLOBAL.json')
    plan={'status':'CLOSED_APPROVED_FOR_PACKAGING','files':files,'trees':trees,'omitted_files':omitted,'distribution_functional_issues_preserved':functional_issues,'declared_limits':['Private scientific extraction, not full historical archive or life continuation backup','Snapshots, full paired databases and deep telemetry remain at the stage indexes and current continuity locators','All failed scientific variants and material rejection denominators are retained in compact closed primaries','Official engine/WHL/kernel are not duplicated here; version and identity were checked once and remain frozen','Manual is an actual DOCX update; consult its editorial record for the exact visual-render limitation','Full collaboration ZIP verification is a distinct native/protocol test, not inferred from these archived recalculations','Technical completion of a ZIP test does not erase the functional issues recorded in its primary proof']}
    write(a.output_dir/'PLAN_PAQUETE.json',plan)
    print(json.dumps({'cases':len(cases),'stages':len(stages),'files':len(files),'trees':len(trees),'native_ticks':0}))
if __name__=='__main__':main()
