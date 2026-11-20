"""APD03 exact paired import and bounded official identity check. Zero new ticks."""
from pathlib import Path
import datetime as dt,hashlib,importlib.util,json,os,sys,time
ROOT=Path(__file__).resolve().parents[3]
S=ROOT/"sistema";LAB=Path(__file__).parent;EV=ROOT/"evidencia/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION"
PAIR=ROOT/"evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION/CORTE_POSTSTOP_FINAL_R01/PAQUETE_FINAL_POSTSTOP"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(p,v):
    with p.open("x",encoding="utf8",newline="\n")as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write("\n")
def main():
    out=EV/"ARRANQUE_R01"
    if out.exists()or(S/"estado/vidas/APD03_MAIN").exists():raise FileExistsError("Existing startup/life: inspect, never repeat or replace")
    out.mkdir(parents=True)
    card=read(S/"estado/vidas/APD02_MAIN/VIDA.json");cont=read(ROOT/"CONTINUIDAD_APD02_CONTINUIDAD_CALIDAD_ADAPTACION.json")
    if card["physical"]["tick"]!=548407 or card["snapshot_sha256"]!="64359d48edd49f8a1f5616ceacd04c4479a27383877c23381e217a39f0cc05a9":raise ValueError("Real parent changed: no implicit rewind")
    if sha(PAIR/"EXPORTACION_SERVICIO.json")!="847355b6d5bee3d2719c69daf47a86926a2a3d9500f98a429c6715fadbb530dd":raise ValueError("Different paired state")
    paths=[S/"estado/vidas/APD02_MAIN/VIDA.json",S/card["snapshot"],S/"estado/servicios_persistentes/APD02_MAIN/cola.sqlite3",S/"estado/ACTIVO.json",ROOT/cont["manual"]["file"],PAIR/"EXPORTACION_SERVICIO.json"]
    before={str(p):{"bytes":p.stat().st_size,"sha256":sha(p)}for p in paths};write(out/"ORIGINALES_ANTES.json",before)
    spec=importlib.util.spec_from_file_location("apd03_own_job",S/"app/process_control.py");pc=importlib.util.module_from_spec(spec);spec.loader.exec_module(pc)
    os.environ["OMP_NUM_THREADS"]="1";runs=[]
    for label,args in [("IDENTIDAD",["version"]),("IMPORTACION_EMPAREJADA",["mente-unificada-importar","--paquete",str(PAIR),"--vida","APD03_MAIN"])]:
        cmd=[sys.executable,"-I","-B","-X","utf8",str(S/"gestionar.py"),*args];start=time.monotonic()
        with (out/(label+".stdout.json")).open("xb")as stdout,(out/(label+".stderr.txt")).open("xb")as stderr:
            proc,job,name=pc.spawn_owned(cmd,cwd=Path(sys.executable).parent,stdout=stdout,stderr=stderr,memory_limit=536870912)
            try:
                proc.wait(timeout=180);resources=pc.job_resources(job);deadline=time.monotonic()+5
                while resources.get("job_active_processes")and time.monotonic()<deadline:time.sleep(.02);resources=pc.job_resources(job)
                if resources.get("job_active_processes"):raise RuntimeError("Own bounded process did not close")
            finally:pc.close_job(job)
        run={"label":label,"command":cmd,"pid":proc.pid,"returncode":proc.returncode,"elapsed_seconds":time.monotonic()-start,"resources":resources,"stdout_sha256":sha(out/(label+".stdout.json"))}
        runs.append(run);write(out/(label+".EJECUCION.json"),run)
        if proc.returncode:raise RuntimeError("Preserved failed command "+label)
    imported=read(out/"IMPORTACION_EMPAREJADA.stdout.json")
    if imported["physical"]!={k:imported["physical"][k]for k in imported["physical"]}:raise AssertionError("Unreachable")
    for key in ("N","tick","RAW_sha256","clocks_sha256"):
        if imported["physical"][key]!=card["physical"][key]:raise ValueError("Imported physical difference "+key)
    after={str(p):{"bytes":p.stat().st_size,"sha256":sha(p)}for p in paths}
    if after!=before:raise ValueError("Protected source changed during import")
    result={"schema":"APD03.exact_initial_import.v1","closed_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"parent_life":"APD02_MAIN","new_life":"APD03_MAIN","new_ticks":0,"originals_unchanged":True,"before":before,"runs":runs,"import":imported,"owner_started":False,"epoch_expected_open":6,"no_T0_no_snapshot_only":True}
    write(out/"PREPARACION_COMPLETA.json",result);print(json.dumps({"out":str(out),"life":"APD03_MAIN","physical":imported["physical"],"new_ticks":0,"originals_unchanged":True}))
if __name__=="__main__":main()
