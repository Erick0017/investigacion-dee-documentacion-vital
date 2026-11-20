"""Seal R16 exact evidence and passive fields; no native runtime or ticks."""
from pathlib import Path
import gc,gzip,hashlib,importlib.util,json,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema'
SRC=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/servicio/PROTECCION_FASE_R16'
OUT=HERE/'ANALISIS_PROTECCION_FASE_R16'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2),encoding='utf8')
def main():
    if OUT.exists():raise FileExistsError('Closed R16 staging is immutable')
    OUT.mkdir();members=[]
    def copy(p,q):
        q=OUT/q;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
        if sha(p)!=sha(q):raise ValueError('Copy mismatch')
        members.append({'file':str(q.relative_to(OUT)).replace('\\','/'),'source':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)})
    for name in('PROTOCOLO.json','RESUMEN.json','AGENDAS.json.gz','COMPARACIONES_COMPLETAS.json.gz','unprotected_age_matched.json.gz','protected_R3.json.gz'):
        copy(SRC/name,'EVIDENCIA/'+name)
    for name in('probar_proteccion_fase_r16.py','recalcular_fase_r16.py','APROBACION_ROOT_R16.json'):
        copy(HERE/name,'CODIGO/'+name)
    copy(HERE/'RESULTADOS_PROTECCION_R16.md','RESULTADOS_PROTECCION_R16.md')
    for p in sorted((SRC/'codigo_congelado').iterdir()):copy(p,'CODIGO/R3_CONGELADO/'+p.name)
    copy(SYSTEM/'capacidades/mente_acumulativa_r02.py','CODIGO/R3_CONGELADO/mente_acumulativa_r02.py')
    # The source implementation is the standard library observer, not Runtime.
    op=SYSTEM/'capacidades/observador_causal_retrospectivo_01.py';sp=importlib.util.spec_from_file_location('observer_R16_export',op);ob=importlib.util.module_from_spec(sp);sp.loader.exec_module(ob)
    omitted=[]
    for p in sorted((SRC/'snapshots').iterdir()):
        omitted.append({'source':str(p.resolve()),'sha256':sha(p),'bytes':p.stat().st_size,'reason':'Complete world retained locally; exported exact physical arrays and agendas are analysis, not an operational life.'})
        if '_62548_BEFORE' in p.name:continue
        s=ob.Snapshot(p)
        for arr in(s.raw,s.clocks):
            b=ob.pbytes(arr);h=ob.sha(b);q=OUT/'EVIDENCIA/fields'/(h+'.u64le.gz');q.parent.mkdir(parents=True,exist_ok=True)
            if not q.exists():
                with q.open('xb')as f:
                    with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0)as z:z.write(b)
                members.append({'file':str(q.relative_to(OUT)).replace('\\','/'),'source':'Exact complete u64le field of '+str(p.resolve()),'uncompressed_bytes':len(b),'uncompressed_sha256':h,'bytes':q.stat().st_size,'sha256':sha(q)})
        del s;gc.collect()
    ref=SRC/'RECALCULO.json';cmd=[sys.executable,'-B',str(HERE/'recalcular_fase_r16.py'),str(OUT/'EVIDENCIA'),'--out',str(ref)]
    pr=subprocess.run(cmd,text=True,capture_output=True,timeout=60)
    if pr.returncode:raise RuntimeError('Recalc error: '+pr.stderr)
    copy(ref,'EVIDENCIA/RECALCULO.json')
    portable=OUT/'RECALCULO_PORTABLE.json';cmd=[sys.executable,'-B',str(OUT/'CODIGO/recalcular_fase_r16.py'),str(OUT/'EVIDENCIA'),'--out',str(portable)]
    pr=subprocess.run(cmd,text=True,capture_output=True,timeout=60)
    if pr.returncode or portable.read_bytes()!=ref.read_bytes():raise ValueError('Portable exact recalc failed: '+pr.stderr)
    write(OUT/'PLAN_RECALCULO.json',{'script':'CODIGO/recalcular_fase_r16.py','args':['EVIDENCIA','--out','RECALCULO_NUEVO.json'],'reference':'EVIDENCIA/RECALCULO.json','reference_sha256':sha(ref),'native_ticks':0,'stdlib_only':True})
    write(OUT/'PRUEBA_PORTABLE.json',{'command':cmd,'returncode':pr.returncode,'reference_sha256':sha(ref),'recalc_sha256':sha(portable),'identical_bytes':True,'native_ticks':0})
    write(OUT/'INDICE_FUENTES_Y_OMISIONES.json',{'included':members,'omitted':omitted,'operational_originals':'See exact PROTOCOLO source/root approval; R15 original/control history reused, never replayed or overwritten.','scope':'P0 scheduler application at one already identified phase; not autonomous regulation or a complete continuation bundle.'})
    manifest=[{'file':str(p.relative_to(OUT)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(OUT.rglob('*'))if p.is_file()]
    write(OUT/'MANIFIESTO_R16.json',{'members':manifest,'without_self_reference':True})
    print(json.dumps({'out':str(OUT),'files':len(manifest)+1,'bytes':sum(p.stat().st_size for p in OUT.rglob('*')if p.is_file()),'manifest_sha256':sha(OUT/'MANIFIESTO_R16.json')},ensure_ascii=False))
if __name__=='__main__':main()
