"""One exact compact preflight bundle, no engine imports or new native ticks."""
from pathlib import Path
import gzip,hashlib,json,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2]
EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01';OUT=HERE/'PREFLIGHT_R3'
REV='4ce1da2ec1d5bc638aadc273b1d1e60f5600d2bdbcc607a4d4be584ac489459d'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def main():
    if OUT.exists():raise FileExistsError('Closed preflight bundle will not be overwritten')
    OUT.mkdir();index=[]
    def copy(p,r):
        q=OUT/r;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
        if sha(q)!=sha(p):raise ValueError('Exact copy mismatch')
        index.append({'file':q.relative_to(OUT).as_posix(),'source':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)})
    ps=sorted(EV.glob('R3_[01][0-9]_*.json.gz'))
    if len(ps)!=13:raise ValueError('All thirteen exact closed primaries required')
    for p in ps:
        d=json.loads(gzip.decompress(p.read_bytes()))
        if d['code_revision_sha256']!=REV:raise ValueError('Different executed code archive')
        copy(p,'PRIMARIOS/'+p.name)
    for name in('PROTOCOLO_CANDIDATA_FASE_R3.json','candidata_fase_r3.py','ejecutar_operacion.py'):
        copy(LAB/name,('PREPROTOCOLO/'if name.endswith('.json')else'CODIGO/')+name)
    archive=EV/'codigo_ejecutado'/REV;signatures=json.loads((archive/'INDICE.json').read_bytes())
    selected=['sistema/gestionar.py','sistema/app/lives.py',*['sistema/capacidades/'+n for n in('mente_unificada_01.py','percepcion_cruda_fi01.py','selector_acrecion_nativo.py','mente_acumulativa_r02.py','eo02_trabajador_local.py')]]
    for rel in selected:
        p=archive/rel
        if sha(p)!=signatures[rel]:raise ValueError('Executed source no longer matches archived code index')
        copy(p,'CODIGO/REVISION_EJECUTADA/'+rel)
    copy(archive/'INDICE.json','CODIGO/REVISION_EJECUTADA/INDICE_CODIGO_COMPLETO.json')
    copy(HERE/'recalcular_preflight_r3.py','RECALCULO/recalcular_preflight_r3.py')
    copy(HERE/'RECALCULO_PREFLIGHT_R3.json','RECALCULO_REFERENCIA.json')
    copy(HERE/'INFORME_PREFLIGHT_R3.md','INFORME_PREFLIGHT_R3.md')
    output=OUT/'RECALCULADO/PREFLIGHT_R3.json';cmd=[sys.executable,'-I','-B',str(OUT/'RECALCULO/recalcular_preflight_r3.py'),'--evidencia',str(OUT/'PRIMARIOS'),'--salida',str(output)]
    pr=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',timeout=60)
    if pr.returncode:raise RuntimeError('Portable recalc failed: '+pr.stderr)
    equal=output.read_bytes()==(OUT/'RECALCULO_REFERENCIA.json').read_bytes()
    if not equal:raise ValueError('Portable reference differs in exact bytes')
    case={'script':'RECALCULO/recalcular_preflight_r3.py','args':['--evidencia','PRIMARIOS','--salida','RECALCULADO/PREFLIGHT_R3.json'],'reference':'RECALCULO_REFERENCIA.json','reference_sha256':sha(OUT/'RECALCULO_REFERENCIA.json')}
    dump(OUT/'PLAN_RECALCULO.json',{'cases':[case],'new_native_ticks':0,'stdlib_only':True})
    dump(OUT/'PRUEBA_PORTABLE.json',{'cases':[{**case,'command':cmd,'returncode':pr.returncode,'stdout':pr.stdout,'stderr':pr.stderr,'actual_sha256':sha(output),'byte_identical_to_reference':equal}],'new_native_ticks':0,'native_reproduction':False,'external_execution':False})
    dump(OUT/'INDICE_FUENTES_Y_LIMITES.json',{'included':index,'executed_revision':REV,'omitted':'No snapshots, no current lives/queues, no native binary, no3720sR04results. The full code index localizes other archived files; only relevant sources travel.','retrospective_scope':'Only R3_01..13 data enter the recalc; the code/preprotocol are interpretation provenance, not inputs to an E1 actor.'})
    manifest=[{'file':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(OUT.rglob('*'))if p.is_file()]
    dump(OUT/'MANIFIESTO.json',{'members':manifest,'without_self_reference':True})
    print(json.dumps({'out':str(OUT),'files':len(manifest)+1,'bytes':sum(p.stat().st_size for p in OUT.rglob('*')if p.is_file()),'manifest_sha256':sha(OUT/'MANIFIESTO.json'),'reference_sha256':sha(OUT/'RECALCULO_REFERENCIA.json')},ensure_ascii=False))
if __name__=='__main__':main()
