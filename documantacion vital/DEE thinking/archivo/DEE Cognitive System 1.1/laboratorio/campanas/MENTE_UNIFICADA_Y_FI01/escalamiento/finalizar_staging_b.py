"""Finish the already-copied stage using a short working directory, zero ticks."""
from pathlib import Path
import gzip,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parents[2]
EVIDENCE=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento';STAGE=HERE/'ANALISIS_B_CERRADO_R2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):
    value=json.dumps(x,ensure_ascii=False,indent=2)
    if p.exists():
        if p.read_text(encoding='utf8')==value:return
        raise FileExistsError(p)
    p.write_text(value,encoding='utf8')
def main():
    assert STAGE.is_dir();proofdir=ROOT.parents[4]/'_fi01_b_recalc_20261025_R3';proofdir.mkdir(exist_ok=True)
    launcher='CODIGO_Y_RECALCULO/escalamiento/RUN_RECALCULO_B.py';evid='EVIDENCIA_ESENCIAL/escalamiento'
    runs=[];plan=[];prior=json.loads((STAGE/'PRUEBA_PORTABLE.json').read_text(encoding='utf8'))['runs']if(STAGE/'PRUEBA_PORTABLE.json').exists()else[]
    for label,calculator,reference in[
      ('B05','recalcular_escalamiento_b_R3_B05_FINAL.py','RECALCULO_B05_FINAL.json'),
      ('B06_B07','recalcular_b06_b07_R2_FINAL.py','RECALCULO_B06_B07_FINAL.json')]:
        output=proofdir/('RECALCULADO_'+label+'.json');expected=EVIDENCE/reference
        cmd=[sys.executable,str(STAGE/launcher),label,'--evidence',str(STAGE/evid),'--out',str(output)]
        saved=next((x for x in prior if x['case']==label),None)
        if saved:
            from types import SimpleNamespace
            result=SimpleNamespace(returncode=saved['returncode'],stdout=saved['stdout'],stderr=saved['stderr'])
        else:result=subprocess.run(cmd,cwd=proofdir,capture_output=True,encoding='utf8',errors='replace',timeout=120)
        okay=result.returncode==0 and output.exists()and output.read_bytes()==expected.read_bytes()
        runs.append({'case':label,'command':cmd,'cwd':str(proofdir),'returncode':result.returncode,'stdout':result.stdout,
          'stderr':result.stderr,'reference_sha256':sha(expected),'output_sha256':sha(output)if output.exists()else None,
          'exact_bytes_equal':okay,'native_ticks':0})
        if not okay:raise ValueError('Portable verification failed: '+str(runs[-1]))
        plan.append({'case':label,'script':launcher,'script_sha256':sha(STAGE/launcher),
          'args':[label,'--evidence',evid,'--out','RECALCULADO_'+label+'.json'],
          'frozen_calculator':'CODIGO_Y_RECALCULO/escalamiento/'+calculator,
          'frozen_calculator_sha256':sha(STAGE/'CODIGO_Y_RECALCULO/escalamiento'/calculator),
          'reference':'RECALCULO_REFERENCIAS/'+reference+'.gz','reference_expanded_sha256':sha(expected)})
    put(STAGE/'PLAN_RECALCULO.json',{'native_ticks':0,'requires':'Python3 standard library only','cases':plan,
      'scope':'Archived calculations, NOT native reproduction or life continuation; all relative sources live inside this stage.'})
    put(STAGE/'PRUEBA_PORTABLE.json',{'native_ticks':0,'all_exact':True,'runs':runs,
      'technical_issues':'Initial bundled interpreter could not import adjacent module without explicit local path; fixed by included launcher. First long working-directory CreateProcess call failed; short workspace cwd fixes only process launch, not evidence or calculators.'})
    copies=[]
    for p in sorted(STAGE.rglob('*')):
        if not p.is_file()or'__pycache__'in p.parts:continue
        rel=p.relative_to(STAGE);q=None
        if rel.parts[0]=='EVIDENCIA_ESENCIAL':q=EVIDENCE/Path(*rel.parts[2:])
        elif rel.parts[0]=='INFORMES':q=HERE/p.name
        elif rel.parts[0]=='INDICES':q=EVIDENCE/p.name
        elif rel.parts[0]=='CODIGO_Y_RECALCULO':q=HERE/p.name if rel.parts[1]=='escalamiento'else HERE.parent/'transferencia_b'/p.name
        if q:
            if sha(q)!=sha(p):raise ValueError('Exact copy mismatch: '+str(p))
            copies.append({'member':rel.as_posix(),'source':q.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size})
    put(STAGE/'OMISIONES_Y_PROCEDENCIA.json',{'exact_copies':copies,'native_ticks':0,
      'omitted_complete_worlds':'Full checkpoints stay local at all paths and SHA256 indexed in INDICES; no full checkpoint is copied here. RAW/clocks field export is explicitly not continuable.',
      'omitted_engine':'No kernel/WHL/official engine or historicalZIP; the installed official system plus indexed full worlds is required for native replay.',
      'negative_coverage':'All399closed primaries copied without favorable-result selection, including P0steps and individual reserves. Adverse futures and instrument-error source revisions remain indexed.',
      'horizon_limit':'B06passive17038not fully snapshotted; exported before16640/final17427are exact attheir own ticks.',
      'technical_stages':'Earlier unsealed staging attempts remain local, not duplicate scientific evidence.'})
    readme=STAGE/'LEER_ANALISIS_B.md'
    readme.write_text('''# Escalamiento B cerrado

Se incluyen todos los primarios cerrados B02–B07, controles, reservas y negativos, fuentes exactas y tres informes. El resultado128es relevancia física de128entradas crudas simultáneas cerca de una frontera0/2 y uso con una referencia adquirida; no128conceptos ni selección autónoma general.

Ejecute con Python3los dos comandos relativos de PLAN_RECALCULO.json. El lanzador resuelve sólo los dos calculadores congelados de su carpeta; no requiere DEE ni rutas históricas. PRUEBA_PORTABLE.json acredita salida idéntica byte a byte desde esta copia, ejecutada en otra carpeta corta. Los grandes JSONde referencia se guardan comprimidos sin pérdida; sus hashes expandidos están en el plan.

INDICESlocaliza los snapshots completos locales, excluidos de este análisis. Los bloques globales B06contienen RAW/clocks sin pérdida, no agendas ni interfaces completas: no permiten continuar vidas. Los finales17427son posteriores al panelmaterial, no equivalen a la medida pasiva17038.

No se ocultan la guarda instrumental excesiva sobre la ficha MAINmutable, las variantes con pérdidas antiguas, el fallo de cadencia2, el ruido local de carga0, la igualación de referencias N101o el control de faseD8+6. La mejora de retención de ese caso no se atribuye exclusivamente a S. La incorporación al sistema y la vida MAINse acredita por separado en la campaña principal.
''',encoding='utf8')
    members=[{'member':p.relative_to(STAGE).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(STAGE.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
    put(STAGE/'MANIFIESTO_B.json',{'members':members,'scope':'No self-reference; sealed after exact portable recalculation. Originals untouched.'})
    print(json.dumps({'stage':str(STAGE),'members':len(members)+1,'bytes':sum(x['bytes']for x in members),'portable_exact':True,'manifest_sha256':sha(STAGE/'MANIFIESTO_B.json')}))
if __name__=='__main__':main()
