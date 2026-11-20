"""Finite Spanish Research application: one native world, contact and two probes.

The preparation is explicit; all physical transitions are performed by the
installed DEE thinking4 library. No experimental runner or saved answer is read.
"""
from __future__ import annotations

import argparse
from array import array
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unicodedata


KEY = "dee4.application.native_online.v1"
HELP = "Instancia nueva; vive el encuentro; a esto lo llamaremos NOMBRE; presenta consulta13; observa respuesta; consulta nueva19; muestra el estado; guarda ARCHIVO; carga ARCHIVO; por qué; salir. Dos sondas consumibles, no conversación ilimitada."


def norm(text):
    return " ".join("".join(c for c in unicodedata.normalize("NFKD",text.casefold()) if not unicodedata.combining(c)).strip(" ¿?¡!.").split())


def physical(value):
    r=value.record
    return {"tick":value.tick,"coordinate":[value.coordinate.x,value.coordinate.y,value.coordinate.z],
            "raw":value.raw,"clock":value.clock,"state":r.state,"semantic":r.semantic,
            "s_reg":r.s_reg,"direction":[r.dx,r.dy,r.dz],"active":r.state>0 and r.semantic!=5}


def physical_digest(world):
    rt=world.runtime
    return {"tick":rt.current_tick,"raw_sha256":hashlib.sha256(array("Q",rt.raw_copy()).tobytes()).hexdigest(),
            "clock_sha256":hashlib.sha256(array("Q",rt.clock_copy()).tobytes()).hexdigest()}


class NativeWorldSession:
    """One MAIN. Metadata is an external protocol cursor and names, not answers."""
    def __init__(self,directory,preparation="principal"):
        import dee_thinking as d
        if d.__version__!="4.0.0" or d.kernel_identity()["kernel_version"]!=27:
            raise RuntimeError("This application requires the installed4.0.0/v27 product")
        self.d=d;self.directory=Path(directory);self.preparation=preparation;self.world=None;self.meta=None

    def point(self,q):return [(a+b)%47 for a,b in zip(q,self.meta["translation"])]

    def _persist(self):
        self.world.runtime.set_snapshot_metadata(KEY,json.dumps(self.meta,ensure_ascii=False,separators=(",",":")))

    def create(self):
        if self.world is not None:raise ValueError("MAIN ya existe; no se reinicia ni se recrea")
        d=self.d;shift=[0,0,0] if self.preparation=="principal" else [2,3,1]
        self.meta={"schema":1,"application":"native_online.v1","preparation":self.preparation,
                   "translation":shift,"stage":"T0","aliases":{},"requests":[]}
        placements=[]
        for site,load,direction,role in [([17,22,25],12,[1,0,0],"environment_A"),
                                       ([22,17,25],24,[0,1,0],"environment_B"),
                                       ([33,25,25],5,[-1,0,0],"finite_cue")]:
            p=d.InitialPlacement();p.site=d.Coordinate(*self.point(site));p.clock=0
            p.raw=d.pack_record(1,load,*direction,1);p.role=role;placements.append(p)
        recipe=d.OrganizationRecipe.research(47,placements,0);recipe.execution=d.TickOptions(d.Backend.LAZY,1)
        interfaces=[]
        for j,site in enumerate(([30,33,25],[25,38,25]),1):
            i=d.InterfaceSpec();i.name="world.query"+str(j)
            channel=d.ChannelSpec();channel.name=i.name;channel.injection_site=d.Coordinate(*self.point(site))
            channel.direction=d.Direction(-1,0,0);channel.allow_experience=False;channel.allow_probe=True
            i.channel=channel;interfaces.append(i)
        recipe.interfaces=interfaces;self.world=d.OrganizationalWorld.create(recipe);self._persist()
        return {"attribution":"INSTRUMENTO","text":"Preparación explícita nueva, tres recursos nativos y dos interfaces declaradas antesT0.","measurement":self.observe()}

    def need(self):
        if self.world is None:raise ValueError("Primero crea o carga una instancia explícita")

    def observe(self):
        self.need();sites={"contact":self.point([22,22,25]),"acquisition":self.point([25,25,25]),
                          "response1":self.point([25,33,25]),"response2":self.point([20,38,25])}
        return {"tick":self.world.runtime.current_tick,"modality":"PASSIVE_OBSERVATION","stage":self.meta["stage"],
                "readings":{k:physical(self.world.runtime.observe(self.d.Coordinate(*q))) for k,q in sites.items()},
                "scope":"Current declared-site panel; a moving relation can leave a site without being destroyed",
                "receipts":[self.receipt(x["id"]) for x in self.meta["requests"]]}

    def receipt(self,identity):
        r=self.world.runtime.receipt(identity)
        return {"id":identity,"status":"missing"} if r is None else {
            "id":r.id,"status":str(r.status),"requested_tick":r.requested_tick,"effective_tick":r.effective_tick,
            "channels":list(r.channels),"reason":r.reason}

    def experience(self):
        self.need()
        if self.meta["stage"]!="T0" or self.world.runtime.current_tick!=0:
            raise ValueError("La experiencia preparada ya evolucionó; no se instala de nuevo")
        captures=[]
        for t in (5,8,11):
            self.world.run_until(t);captures.append(self.observe())
        self.meta["stage"]="READY1";self._persist()
        return {"attribution":"INSTRUMENTO","text":"El mismo mundo evolucionó hasta su primera ocasión de consulta, sin teacher escrito por el host.",
                "modality":"NATIVE_WORLD_EXPERIENCE","captures":captures,"measurement":self.observe()}

    def submit_question(self,payload):
        self.need();stage=self.meta["stage"]
        j,t=(1,11) if stage=="READY1" else (2,16) if stage=="READY2" else (None,None)
        if j is None or self.world.runtime.current_tick!=t:
            raise ValueError("No hay una ocasión de sonda disponible; no se recoloca materia ni se reconstruye MAIN")
        if isinstance(payload,bool) or not isinstance(payload,int) or not 0<=payload<=65535:
            raise ValueError("La señal debe ser un entero uint16")
        r=self.world.probe("world.query"+str(j),payload,t)
        self.meta["requests"].append({"id":r.id,"port":j,"payload":payload,"requested_tick":t})
        self.meta["stage"]="PENDING"+str(j);self._persist()
        return {"attribution":"INSTRUMENTO","text":"Sonda física solicitada. Programada no equivale a aplicada; puedes guardar su cola antes de observar.",
                "modality":"PHYSICAL_PROBE_ON_MAIN","receipt":self.receipt(r.id),"measurement":self.observe()}

    def response(self):
        self.need();stage=self.meta["stage"]
        if stage not in ("PENDING1","PENDING2"):
            raise ValueError("No hay una sonda pendiente; no se devuelve una respuesta pasada como nueva")
        j=int(stage[-1]);target=16 if j==1 else 21
        self.world.run_until(target)
        site=[25,33,25] if j==1 else [20,38,25]
        current=physical(self.world.runtime.observe(self.d.Coordinate(*self.point(site))))
        admission=self.receipt(self.meta["requests"][-1]["id"])
        available=admission["status"]=="applied" and current["active"]
        self.meta["stage"]="READY2" if j==1 else "FINISHED";self._persist()
        return {"attribution":"ENTE" if available else "INSTRUMENTO","text":(
            "La respuesta física actual tiene carga "+str(current["s_reg"])+" y dirección "+str(current["direction"])+"."
            if available else "No hay una respuesta física actual admitida y activa; no se inventa un cero."),
            "modality":"CURRENT_NATIVE_QUERY_PRODUCT","available":available,"physical_output":current,
            "receipt":admission,"measurement":self.observe(),
            "scope":"Consumable mobile relation; current fields, no answer table or arbitrary learned dictionary"}

    def save(self,path):
        self.need();self._persist();target=Path(path)
        if not target.is_absolute():target=self.directory/target
        target.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="dee4-world-save-") as temp:
            bridge=Path(temp)/"world.deetsnap";self.world.save_snapshot(str(bridge))
            staging=target.with_suffix(target.suffix+".writing");shutil.copyfile(bridge,staging);os.replace(staging,target)
        return {"attribution":"INSTRUMENTO","text":"Mismo estado físico, cola nativa, recibos, fase de interfaz y nombres guardados.",
                "snapshot":str(target.resolve()),"snapshot_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
                "physical_digest":physical_digest(self.world)}

    def load(self,path):
        source=Path(path)
        if not source.is_absolute():source=self.directory/source
        with tempfile.TemporaryDirectory(prefix="dee4-world-load-") as temp:
            bridge=Path(temp)/"world.deetsnap";shutil.copyfile(source,bridge)
            restored=self.d.OrganizationalWorld.load_snapshot(str(bridge))
        packed=restored.runtime.snapshot_metadata(KEY)
        if packed is None or len(packed)>32768:raise ValueError("Falta el contrato operativo de esta aplicación")
        meta=json.loads(packed)
        if meta.get("schema")!=1 or meta.get("application")!="native_online.v1" or restored.runtime.dimension!=47:
            raise ValueError("Snapshot ajeno a esta aplicación; no se instaló otro cuerpo")
        shift=meta.get("translation")
        if not isinstance(shift,list) or len(shift)!=3 or any(type(v)is not int or not 0<=v<47 for v in shift):
            raise ValueError("Traslación inválida")
        stages={"T0":0,"READY1":11,"PENDING1":11,"READY2":16,"PENDING2":16,"FINISHED":21}
        if meta.get("stage") not in stages or stages[meta["stage"]]!=restored.runtime.current_tick:
            raise ValueError("Cursor de interfaz incompatible con el tick nativo")
        if not isinstance(meta.get("aliases"),dict) or len(meta["aliases"])>64 or any(not isinstance(k,str) or not 0<len(k)<=80 or v!="current_native_encounter" for k,v in meta["aliases"].items()):
            raise ValueError("Nombres externos malformados")
        requests=meta.get("requests")
        if not isinstance(requests,list) or len(requests)>2:raise ValueError("Historial de solicitudes inválido")
        expected_count={"T0":0,"READY1":0,"PENDING1":1,"READY2":1,"PENDING2":2,"FINISHED":2}[meta["stage"]]
        if len(requests)!=expected_count:raise ValueError("Cursor e historial de sondas incompatibles")
        if sorted(restored.runtime.channel_names)!=["world.query1","world.query2"]:raise ValueError("Interfaces físicas ausentes")
        for j,r in enumerate(requests,1):
            if (not isinstance(r,dict) or set(r)!={"id","port","payload","requested_tick"} or type(r["id"])is not int
                or not 0<r["id"]<2**64 or r["port"]!=j or type(r["payload"])is not int
                or not 0<=r["payload"]<=65535 or r["requested_tick"]!=(11 if j==1 else 16)
                or restored.runtime.receipt(r["id"]) is None):raise ValueError("Solicitud/recibo incompatible")
        # Assignment follows complete operational validation; load is explicit.
        self.world,self.meta=restored,meta
        return {"attribution":"INSTRUMENTO","text":"Continuación restaurada explícitamente; no se preparó otra historia.",
                "physical_digest":physical_digest(restored),"measurement":self.observe()}

    def execute(self,text):
        value=norm(text)
        if value in ("salir","fin"):return {"attribution":"INSTRUMENTO","text":"Cierre solicitado sin reinicio.","exit":True}
        if value=="ayuda":return {"attribution":"INSTRUMENTO","text":HELP}
        if value in ("instancia nueva","crear"):return self.create()
        if value in ("vive el encuentro","presenta experiencia","observa el acontecimiento"):return self.experience()
        if value in ("muestra el estado","observa el estado"):return {"attribution":"INSTRUMENTO","text":"Panel pasivo actual.","measurement":self.observe()}
        if value=="observa respuesta":return self.response()
        m=re.fullmatch(r"(presenta consulta|consulta nueva)\s*(\d+)",value)
        if m:
            result=self.submit_question(int(m[2]));return self.response() if m[1]=="consulta nueva" else result
        if value.startswith("a esto lo llamaremos "):
            self.need()
            if self.meta["stage"]=="T0":raise ValueError("Primero deja evolucionar la experiencia; el nombre no la sustituye")
            name=text.strip()[len("a esto lo llamaremos "):].strip()
            if not 0<len(name)<=80 or len(self.meta["aliases"])>=64:raise ValueError("Nombre de1–80 caracteres y presupuesto de64")
            self.meta["aliases"][name]="current_native_encounter";self._persist()
            return {"attribution":"INSTRUMENTO","text":"Nombre externo de una referencia observada; no diccionario aprendido ni respuesta escrita."}
        if value in ("por que","porque"):
            return {"attribution":"EXPLICACION_DOCUMENTAL","text":"Tres recursos declarados evolucionan bajo v27; las sondas interactúan físicamente con el estado. Esta explicación del contrato no es introspección ni una nueva prueba causal.","measurement":self.observe()}
        for prefix,method in (("guarda ",self.save),("carga ",self.load)):
            if value.startswith(prefix):return method(text.strip()[len(prefix):].strip())
        raise ValueError("Orden fuera de la gramática finita. "+HELP)


def engine(args):
    session=NativeWorldSession(args.sesion,args.preparacion)
    for line in sys.stdin:
        try:
            request=json.loads(line);response=session.execute(request["input"])
        except Exception as error:response={"attribution":"INSTRUMENTO","text":str(error),"error":type(error).__name__}
        print(json.dumps({"pid":os.getpid(),"response":response},ensure_ascii=True),flush=True)
        if response.get("exit"):break


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preparacion",choices=("principal","reservada"),default="principal")
    parser.add_argument("--sesion",type=Path,default=Path("sesion_mundo"));parser.add_argument("--eventos",type=Path)
    parser.add_argument("--transcripcion",type=Path,default=Path("MUNDO_DIALOGOS.jsonl"))
    parser.add_argument("--timeout",type=float,default=60);parser.add_argument("--json",action="store_true")
    parser.add_argument("--engine",action="store_true",help=argparse.SUPPRESS);args=parser.parse_args()
    if args.engine:engine(args);return
    if not 0<args.timeout<=180:parser.error("Timeout de llamada entre0 y180 segundos")
    args.sesion.mkdir(parents=True,exist_ok=True);args.transcripcion.parent.mkdir(parents=True,exist_ok=True)
    argv=[sys.executable,"-I","-B",str(Path(__file__).resolve()),"--engine","--sesion",str(args.sesion.resolve()),"--preparacion",args.preparacion]
    inbox=queue.Queue()
    with args.transcripcion.with_suffix(".stderr.log").open("w",encoding="utf-8") as errors:
        child=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=errors,text=True,encoding="utf-8",bufsize=1,
                               creationflags=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0)
        def reader():
            for line in child.stdout:inbox.put(line)
            inbox.put(None)
        thread=threading.Thread(target=reader,daemon=True);thread.start()
        def request(text):
            child.stdin.write(json.dumps({"input":text},ensure_ascii=True)+"\n");child.stdin.flush()
            try:line=inbox.get(timeout=args.timeout)
            except queue.Empty:
                child.kill();child.wait(timeout=10)
                raise TimeoutError("Sólo el engine propio fue cerrado; MAIN no se reconstruyó")
            if line is None:raise RuntimeError("El propietario nativo terminó sin respuesta")
            row={"wall_utc":datetime.now(timezone.utc).isoformat(),"input":text,"preparation":args.preparacion,**json.loads(line)}
            with args.transcripcion.open("a",encoding="utf-8") as f:
                f.write(json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n");f.flush();os.fsync(f.fileno())
            response=row["response"]
            print(json.dumps(row,ensure_ascii=False) if args.json else response["attribution"]+": "+response.get("text",""),flush=True)
            return response
        try:
            if args.eventos:
                for text in args.eventos.read_text(encoding="utf-8-sig").splitlines():
                    if text.strip() and not text.lstrip().startswith("#") and request(text.strip()).get("exit"):break
            else:
                print(HELP)
                while True:
                    try:text=input("> ")
                    except EOFError:text="Salir"
                    if request(text).get("exit"):break
        finally:
            child.stdin.close()
            try:child.wait(timeout=5)
            except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5)
            thread.join(timeout=2)
        if child.returncode:raise RuntimeError("Engine propio terminó con código "+str(child.returncode))


if __name__=="__main__":main()
