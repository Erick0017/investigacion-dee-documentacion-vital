"""Copy exact closed evidence once; no engine, ticks or historical mutation."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2]
EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01';SRC=EV/'servicio/AUTOPSIA_FASE_R15'
OUT=HERE/'ANALISIS_AUTOPSIA_R15'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,sort_keys=True,indent=2),encoding='utf8')

def main():
    if OUT.exists():raise FileExistsError(OUT)
    OUT.mkdir();files=[]
    def copy(p,relative):
        target=OUT/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
        if sha(p)!=sha(target):raise ValueError('Copy differs')
        files.append({'file':relative,'source':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)})
    for name in('PROTOCOLO.json','RESUMEN.json','COMPARACIONES_COMPLETAS.json.gz','RECALCULO.json','FUENTE_AGENDA.json.gz'):
        copy(SRC/name,'EVIDENCIA/'+name)
    for name in('real','no_datum','sham_datum','no_query'):copy(SRC/(name+'.json.gz'),'EVIDENCIA/'+name+'.json.gz')
    for folder in('agendas','fields'):
        for p in sorted((SRC/folder).iterdir()):copy(p,'EVIDENCIA/'+folder+'/'+p.name)
    for name in('autopsia_fase_servicio_r15.py','recalcular_autopsia_r15.py','auditar_deriva_r13_sin_runtime.py'):
        copy(HERE/name,'CODIGO/'+name)
    copy(HERE/'RESULTADOS_AUTOPSIA_R15.md','RESULTADOS_AUTOPSIA_R15.md')
    copy(EV/'servicio/ANALISIS_DIRIGIDO_DERIVA_R13_B.json','ANTECEDENTE_CERO_TICKS/ANALISIS_DIRIGIDO_DERIVA_R13_B.json')
    for name in('mente_unificada_01.py','percepcion_cruda_fi01.py','selector_acrecion_nativo.py'):
        copy(EV/'servicio/SERVICIO_60MIN_FINAL_R11/codigo/capacidades'/name,'CODIGO/servicio_R11/'+name)
    # All complete restore bases remain local. Exported arrays are exact full
    # physical evidence but do not include interfaces/queues needed for a life.
    omitted=[]
    for p in sorted((SRC/'snapshots').iterdir()):omitted.append({'source':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p),'reason':'Complete diagnostic world kept locally; exact RAW/clocks and agendas exported, not an operational restore bundle.'})
    for p in[ROOT/'sistema/estado/checkpoints/MU_MAIN.T62525.25da49a2c759.deetsnap.gz',ROOT/'sistema/estado/checkpoints/MU_MAIN.T62564.20823c9e8739.deetsnap.gz']:
        omitted.append({'source':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p),'reason':'Original complete source never changed; only targeted exact observation/agenda extracts travel.'})
    write(OUT/'INDICE_FUENTES_Y_OMISIONES.json',{'included':files,'omitted':omitted,'never_claimed':'This analysis package is not a complete life or standalone native runtime. Recalc is stdlib-only; native replay needs declared engine and complete local source.','no_new_ticks_in_packaging':True})
    ref=SRC/'RECALCULO.json';result=OUT/'RECALCULO_PORTABLE.json'
    cmd=[sys.executable,'-B',str(OUT/'CODIGO/recalcular_autopsia_r15.py'),str(OUT/'EVIDENCIA'),'--out',str(result)]
    pr=subprocess.run(cmd,text=True,capture_output=True,timeout=60)
    if pr.returncode:raise RuntimeError(pr.stderr)
    if result.read_bytes()!=ref.read_bytes():raise ValueError('Portable recalc differs from exact archived reference')
    write(OUT/'PRUEBA_PORTABLE.json',{'command':cmd,'returncode':pr.returncode,'reference_sha256':sha(ref),'recalc_sha256':sha(result),'identical_bytes':True,'native_ticks':0})
    write(OUT/'PLAN_RECALCULO.json',{'script':'CODIGO/recalcular_autopsia_r15.py','args':['EVIDENCIA','--out','RECALCULO_NUEVO.json'],'reference':'EVIDENCIA/RECALCULO.json','reference_sha256':sha(ref),'stdlib_only':True,'native_ticks':0})
    manifest=[{'file':str(p.relative_to(OUT)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(OUT.rglob('*'))if p.is_file()]
    write(OUT/'MANIFIESTO_AUTOPSIA.json',{'schema':'exact_members_without_self_reference','members':manifest})
    print(json.dumps({'out':str(OUT),'files':len(manifest)+1,'bytes':sum(p.stat().st_size for p in OUT.rglob('*')if p.is_file()),'manifest_sha256':sha(OUT/'MANIFIESTO_AUTOPSIA.json')},ensure_ascii=False))

if __name__=='__main__':main()
