"""PI11 scoped exact closed paired export, no Native import or source write.

Adapts the literal PI10 closed-export implementation by explicit current
source identity/directory and destination. Default PLAN does not inspect or
write source state. Root alone invokes --exportar after proving owner closed.
"""
from pathlib import Path
import argparse,ast,hashlib,json,re,types
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema'
OLD=P.with_name('PROGRESION_INTEGRADA_10')/'codigo/exportar_principal_cerrado_PI10_R01.py'
ORIGINAL_SHA='8250c77947687afa6cd97a7eb3e53f8feb5f08e13fb44124f3610e802331cbad'
PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,msg):
    if not ok:raise ValueError(msg)
def adapt(source,*,system,life,slug):
    # Exact substitutions are administrative source/destination scope only.
    old="dest=(P/'pares'/('PRINCIPAL_D_T'+str(a.tick))).resolve();proof=dest.with_name(dest.name+'_PRESERVACION.json')"
    new="dest=(P/'pares'/EXPORT_SLUG).resolve();proof=dest.with_name(dest.name+'_PRESERVACION.json')"
    need(source.count(old)==1,'Exact export destination anchor');source=source.replace(old,new)
    old="activefile=S/'estado/ACTIVO.json';active=read(activefile);need(active['life_id']==LIFE,'Changed main: reconcile genealogy, never take highest tick')"
    new="activefile=S/'estado/ACTIVO.json';active=read(activefile)if activefile.exists()else{'life_id':LIFE,'tick':a.tick};need(active['life_id']==LIFE,'Changed source selection: never choose highest tick')"
    need(source.count(old)==1,'Exact source selection anchor');source=source.replace(old,new)
    old="protected={str(p):sha(p)for p in(activefile,cardfile,snapshot)}"
    new="protected={str(p):sha(p)for p in(activefile,cardfile,snapshot)if p.exists()}"
    need(source.count(old)==1,'Exact protection anchor');source=source.replace(old,new)
    source=source.replace("sha(activefile)==protected[str(activefile)]","(not activefile.exists()or sha(activefile)==protected[str(activefile)])")
    source=source.replace("P/'PI10_ROOT_NATIVE_WRITER.lock'","P/'PI11_ROOT_NATIVE_WRITER.lock'")
    ast.parse(source);m=types.ModuleType('PI11_closed_export_scoped_PI10_literal');m.__file__=str(OLD)
    exec(compile(source,str(OLD)+':PI11_explicit_identity_and_path_scope_only','exec'),m.__dict__)
    m.P=P;m.S=system;m.LIFE=life;m.EXPORT_SLUG=slug;m.PROC=H/'comprobar_proceso_PI11_R01.py';m.PROC_SHA=sha(m.PROC)
    return m
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--exportar',action='store_true');ap.add_argument('--sistema',type=Path,default=S);ap.add_argument('--vida',default=PARENT);ap.add_argument('--slug',required=True);ap.add_argument('--tick',type=int);ap.add_argument('--snapshot-sha256');a=ap.parse_args()
    system=a.sistema.resolve(strict=True)
    need(re.fullmatch('[A-Z][A-Z0-9_]{0,45}',a.slug),'Explicit unused finite export slug')
    main_source=system==S.resolve()and a.vida==PARENT
    diagnostic_source=system.name=='sistema'and system.parent.parent==(P/'estados').resolve()and re.fullmatch('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_[A-Z0-9_]{1,20}',a.vida)and not(system/'estado/ACTIVO.json').exists()
    need(main_source or diagnostic_source,'Only protected current PI10 or exact PI11 diagnostic source')
    if not a.exportar:
        print(json.dumps({'mode':'PLAN_ONLY','source_system':str(system),'life':a.vida,'destination':str(P/'pares'/a.slug),'Native':0}));return
    need(sha(OLD)==ORIGINAL_SHA,'Preserved reviewed PI10 export source changed')
    need(type(a.tick)is int and a.tick>=947395 and re.fullmatch('[a-f0-9]{64}',a.snapshot_sha256 or''),'Actual cut and hash must be supplied')
    m=adapt(OLD.read_text('utf-8-sig'),system=system,life=a.vida,slug=a.slug);m.export(a)
if __name__=='__main__':main()
