"""Copy closed B scientific records exactly; no DEE imports or native ticks."""
from pathlib import Path
import gzip,hashlib,json,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2]
EVIDENCE=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento'
STAGE=HERE/'ANALISIS_B_CERRADO_R2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def main():
    if STAGE.exists():raise FileExistsError(STAGE)
    STAGE.mkdir();copies=[];compressed=[]
    def copy(src,dst):
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        if sha(src)!=sha(dst):raise ValueError('Copy mismatch: '+str(src))
        copies.append({'source':src.relative_to(ROOT).as_posix(),'member':dst.relative_to(STAGE).as_posix(),'bytes':dst.stat().st_size,'sha256':sha(dst)})
    for p in sorted(HERE.iterdir()):
        if not p.is_file()or p.name=='preparar_staging_b.py':continue
        if p.suffix not in('.py','.md','.json')and not p.name.endswith('.json.gz'):continue
        target=STAGE/('INFORMES'if p.name.startswith('RESULTADOS_')else'CODIGO_Y_RECALCULO/escalamiento')/p.name
        copy(p,target)
    copy(LAB/'transferencia_b/frontend_b01_r2.py',STAGE/'CODIGO_Y_RECALCULO/transferencia_b/frontend_b01_r2.py')
    # Every positive/negative/reserve/technical primary, plus frozen protocols.
    for folder in sorted(EVIDENCE.glob('B*')):
        if not folder.is_dir():continue
        for p in sorted(folder.iterdir()):
            if p.is_file()and(p.name.endswith('.json.gz')or p.suffix=='.json'):
                copy(p,STAGE/'EVIDENCIA_ESENCIAL/escalamiento'/folder.name/p.name)
    fields=EVIDENCE/'B06_CADENCE_NOISE_R1/CAMPOS_COMPLETOS_0_TICKS'
    for p in sorted(fields.iterdir()):
        if p.is_file():copy(p,STAGE/'EVIDENCIA_ESENCIAL/escalamiento'/p.relative_to(EVIDENCE))
    for name in('INDICE_B05_CERRADO.json','INDICE_B06_B07_CERRADO.json'):
        copy(EVIDENCE/name,STAGE/'INDICES'/name)
    for name in('RECALCULO_B05_FINAL.json','RECALCULO_B06_B07_FINAL.json'):
        src=EVIDENCE/name;dst=STAGE/'RECALCULO_REFERENCIAS'/(name+'.gz');dst.parent.mkdir(parents=True,exist_ok=True)
        with dst.open('xb')as f:
            with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0)as z:z.write(src.read_bytes())
        if gzip.decompress(dst.read_bytes())!=src.read_bytes():raise ValueError('Lossless reference mismatch')
        compressed.append({'source':src.relative_to(ROOT).as_posix(),'member':dst.relative_to(STAGE).as_posix(),
          'source_sha256':sha(src),'compressed_sha256':sha(dst),'expanded_bytes':src.stat().st_size,'compressed_bytes':dst.stat().st_size})
    evid='EVIDENCIA_ESENCIAL/escalamiento';code='CODIGO_Y_RECALCULO/escalamiento'
    cases=[('B05',code+'/recalcular_escalamiento_b_R3_B05_FINAL.py','RECALCULO_B05_FINAL.json'),
           ('B06_B07',code+'/recalcular_b06_b07_R2_FINAL.py','RECALCULO_B06_B07_FINAL.json')]
    plan=[];proof=[]
    proof_dir=EVIDENCE/'PRUEBA_PORTABLE_B_CERRADO_R2';proof_dir.mkdir()
    for label,script,reference in cases:
        output=proof_dir/('RECALCULADO_'+label+'.json');launcher=code+'/RUN_RECALCULO_B.py';cmd=[sys.executable,str(STAGE/launcher),label,'--evidence',str(STAGE/evid),'--out',str(output)]
        run=subprocess.run(cmd,cwd=proof_dir,capture_output=True,encoding='utf8',errors='replace',timeout=120)
        expected=EVIDENCE/reference;equal=run.returncode==0 and output.exists()and output.read_bytes()==expected.read_bytes()
        proof.append({'case':label,'command':cmd,'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr,
          'output_sha256':sha(output)if output.exists()else None,'reference_sha256':sha(expected),'exact_bytes_equal':equal,'native_ticks':0})
        plan.append({'case':label,'script':launcher,'script_sha256':sha(STAGE/launcher),'frozen_calculator':script,'frozen_calculator_sha256':sha(STAGE/script),
          'args':[label,'--evidence',evid,'--out','RECALCULADO_'+label+'.json'],
          'reference':'RECALCULO_REFERENCIAS/'+reference+'.gz','reference_expanded_sha256':sha(expected),
          'scope':'Portable archived calculation only; no native engine, Runtime, historical path or actor decisions.'})
        if not equal:raise ValueError('Portable archived recalculation differs: '+label+' '+run.stdout+' '+run.stderr)
    put(STAGE/'PLAN_RECALCULO.json',{'native_ticks':0,'requires':'Python3 standard library only','cases':plan})
    put(STAGE/'PRUEBA_PORTABLE.json',{'native_ticks':0,'runs':proof,'all_exact':all(x['exact_bytes_equal']for x in proof)})
    put(STAGE/'OMISIONES_Y_PROCEDENCIA.json',{'native_ticks':0,'exact_copies':copies,'lossless_reference_compression':compressed,
      'omitted_complete_snapshots':'All complete local operational and diagnostic worlds stay in the original indexed paths and SHA256; field blocks do not replace their queues/interfaces/protocol.',
      'omitted_original_software':'No engine/WHL/kernel, no general historical corpus. Existing installed system is required for native replay; only archived recalculation is self-contained here.',
      'negative_coverage':'All399closed primaries including preparation, malformed/conditional functional outcomes and held-out individual relevance are copied without filtering for success. Technical source revisions and incidents are retained.',
      'not_reconstructed':'B06passive17038had a measured count but no complete saved snapshot; exported fullfields arebefore16640andafterpanel17427.',
      'unchanged_originals':True})
    (STAGE/'LEER_ANALISIS_B.md').write_text('''# Análisis cerrado de escalamiento B

Este conjunto conserva los primarios positivos, negativos, reservas y controles de B02–B07, sus fuentes exactas y tres informes complementarios. El límite demostrado es relevancia causal de128componentes crudos simultáneos cerca de una frontera0/2 y su uso con una referencia adquirida; no128conceptos ni una política general. Los ensayos de escala son vidas nuevas, no MAINredimensionado.

Para recalcular sin DEE, use Python3 y los comandos relativos de PLAN_RECALCULO.json. PRUEBA_PORTABLE.json registra ejecución desde esta copia y comparación exacta de bytes con las referencias descomprimidas. El script B06/B07importa únicamente el recálculo B05congelado presente en su misma carpeta. No lee resultados históricos fuera del paquete.

EVIDENCIA_ESENCIALcontiene todos los primarios cerrados y los bloques RAW/clocks completos exportados0ticks de B06. INDICESidentifica los snapshots completos que permanecen localmente; el paquete no es un respaldo operativo ni permite continuar vidas sin dichos estados y el sistema oficial. Los campos exportados finales17427no equivalen al horizonte pasivo17038.

La guarda final del barrido128comparó una ficha MAINmutable que otro escritor legítimo había avanzado: el error instrumental se conserva y no invalida los128primarios ya escritos ni altera su checkpoint de origen inmutable. El control de fase posterior muestra que seis ticks pasivos bastan para evitar la pérdida vieja de un caso B04D8; no se atribuye esa retención exclusivamente al nuevoS.
''',encoding='utf8')
    members=[{'member':p.relative_to(STAGE).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(STAGE.rglob('*'))if p.is_file()]
    put(STAGE/'MANIFIESTO_B.json',{'members':members,'scope':'No self-reference. All listed bytes are final at stage seal; originals remain untouched.'})
    print(json.dumps({'stage':str(STAGE),'members':len(members)+1,'bytes':sum(x['bytes']for x in members),'portable_exact':True,'manifest_sha256':sha(STAGE/'MANIFIESTO_B.json')}))
if __name__=='__main__':main()
