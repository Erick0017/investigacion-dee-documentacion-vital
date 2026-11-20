"""Single-entry operational check in a diagnostic paired copy, never APD03_MAIN."""
from pathlib import Path
import datetime as dt,hashlib,importlib.util,json,os,shutil,sys,time
ROOT=Path(__file__).resolve().parents[4];S=ROOT/"sistema";LAB=Path(__file__).parent
OUT=ROOT/"evidencia/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/ENTRADA_NATIVA_R01"
LIFE="DIAG_APD03_UI_R01"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):
    with Path(p).open("x",encoding="utf8",newline="\n")as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write("\n")
def main():
    if OUT.exists()or(S/"estado/vidas"/LIFE).exists():raise FileExistsError("Existing proof/life preserved, no retry")
    OUT.mkdir(parents=True);os.environ["OMP_NUM_THREADS"]="1"
    protected=[S/"estado/vidas/APD02_MAIN/VIDA.json",S/"estado/vidas/APD03_MAIN/VIDA.json",S/"estado/ACTIVO.json"]
    before={str(p):sha(p)for p in protected}
    sources=[Path(__file__),LAB/"GUION_UI_PRIMERO_R01.json",LAB/"GUION_UI_CONTINUAR_R01.json",S/"app/usar_dee.py",S/"contratos/ENTRADA_SENCILLA_APD03.json",S/"gestionar.py",S/"app/process_control.py",S/"app/servicio_persistente.py",S/"app/cola_local.py",S/"app/cliente_mente_unificada.py",S/"capacidades/mente_unificada_01.py",S/"capacidades/asistente_apd02.py"]
    frozen=[]
    for i,p in enumerate(sources):
        target=OUT/"CODIGO_EJECUTADO"/(str(i).zfill(2)+"_"+p.name);target.parent.mkdir(exist_ok=True);shutil.copyfile(p,target);frozen.append({"source":str(p),"file":target.relative_to(OUT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)})
    write(OUT/"ANTES_DEL_PRIMER_TICK.json",{"sources":frozen,"protected_before":before,"life":LIFE,"scope":"UI operational construction proof, not final APD03 cognitive reservation","utc":dt.datetime.now(dt.timezone.utc).isoformat()})
    spec=importlib.util.spec_from_file_location("ui_owned_job",S/"app/process_control.py");pc=importlib.util.module_from_spec(spec);spec.loader.exec_module(pc)
    runs=[];cuts=[]
    for index,script in enumerate(("GUION_UI_PRIMERO_R01.json","GUION_UI_CONTINUAR_R01.json")):
        command=[sys.executable,"-I","-B","-X","utf8",str(S/"app/usar_dee.py"),"--raiz",str(ROOT),"--nueva"if index==0 else"--vida",LIFE,"--guion",str(LAB/script)]
        start=time.monotonic()
        with(OUT/("UI_"+str(index)+".stdout.txt")).open("xb")as stdout,(OUT/("UI_"+str(index)+".stderr.txt")).open("xb")as stderr:
            proc,job,name=pc.spawn_owned(command,cwd=Path(sys.executable).parent,stdout=stdout,stderr=stderr,memory_limit=536870912)
            try:
                proc.wait(timeout=300);resources=pc.job_resources(job);deadline=time.monotonic()+5
                while resources.get("job_active_processes")and time.monotonic()<deadline:time.sleep(.02);resources=pc.job_resources(job)
                if resources.get("job_active_processes"):raise RuntimeError("Own tree not closed")
            finally:pc.close_job(job)
        row={"command":command,"pid":proc.pid,"returncode":proc.returncode,"elapsed_seconds":time.monotonic()-start,"resources":resources};runs.append(row);write(OUT/("EJECUCION_"+str(index)+".json"),row)
        if proc.returncode:raise RuntimeError("UI failure preserved: "+str(index))
        card=read(S/"estado/vidas"/LIFE/"VIDA.json");cut={"record":card,"record_sha256":sha(S/"estado/vidas"/LIFE/"VIDA.json"),"protocol":read(S/"estado/entrada_sencilla/vidas"/LIFE/"PROTOCOLO.json"),"journal_sha256":sha(S/"estado/servicios_persistentes"/LIFE/"cola.sqlite3")}
        shutil.copyfile(S/card["snapshot"],OUT/("CORTE_"+str(index)+"_COMPLETO.deetsnap.gz"));cuts.append(cut);write(OUT/("CORTE_"+str(index)+".json"),cut)
    log=S/"estado/entrada_sencilla/vidas"/LIFE/"SESIONES.jsonl";shutil.copyfile(log,OUT/"SESIONES_ORIGINALES.jsonl")
    after={str(p):sha(p)for p in protected};same_sources=all(sha(Path(r["source"]))==r["sha256"]for r in frozen)
    if before!=after or not same_sources:raise ValueError("Protected source/code changed during proof")
    if cuts[0]["record"]["world_id"]!=cuts[1]["record"]["world_id"]or cuts[1]["record"]["physical"]["tick"]<=cuts[0]["record"]["physical"]["tick"]:raise ValueError("Not the same advancing life")
    if any(c["protocol"]["pending_material"]is not None or c["protocol"]["uncertain_preserved"]for c in cuts):raise ValueError("Unfinished or uncertain material remains")
    result={"schema":"APD03.single_entry.operational_execution.R01","life":LIFE,"runs":runs,"cuts":cuts,"same_sources_before_after":same_sources,"protected_originals_unchanged":True,"one_native_owner_at_a_time":True,"first_process_new_paired_copy_second_process_same_registered_life":True,"source_snapshot_sha256":"64359d48edd49f8a1f5616ceacd04c4479a27383877c23381e217a39f0cc05a9","pending_or_uncertain":False,"scientific_value_audit_pending":True,"closed_utc":dt.datetime.now(dt.timezone.utc).isoformat()}
    write(OUT/"RESULTADOS_OPERATIVOS.json",result);print(json.dumps({"out":str(OUT),"life":LIFE,"ticks":[c["record"]["physical"]["tick"]for c in cuts],"returns":[r["returncode"]for r in runs],"protected_unchanged":True}))
if __name__=="__main__":main()
