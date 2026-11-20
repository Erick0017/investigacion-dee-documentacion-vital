"""Entrada común de las reproducciones Core, desde material privado incluido.

No calcula respuestas del participante. Materializa bytes; ejecuta el worker
original de recuperación; compara después de la evolución y publica su alcance.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))  # Explicit package-local adapters in isolated Python.
FAMILIES=['cpc1','cpc2','sem01','cpc4','cpc5','cpc6','cpc7','mcts','repertoire','rca','count','product','product_extra','ordered','stream','network','architectures','bridge','capacity','longitudinal','policy','native_loop','central','qfm','l15','need','missing','retain_early','retain_word','retain_late','social','initial_cpc8','core06','core07']
EXTENSIONS={'ordered','stream','network','architectures','bridge','capacity','longitudinal','policy','native_loop','central','qfm','l15','need','missing'}
RETENTION={'retain_early','retain_word','retain_late'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def package():
    for p in ROOT.parents:
        if (p/'CATALOGO.json').is_file():return p
    raise RuntimeError('No se encuentra la raíz con CATALOGO.json')
def materialize(out):
    dest=out.parent/'_core_materializado'
    marker=dest/'_CONTENIDO_VERIFICADO.json'
    index=ROOT/'documentacion/INDICE_MIEMBROS.json';store=ROOT/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz'
    identity={'index_sha256':sha(index),'store_sha256':sha(store)}
    if marker.is_file():
        assert json.loads(marker.read_text(encoding='utf8'))==identity,'Cache distinto; use un directorio de resultados nuevo'
        return dest
    spec=importlib.util.spec_from_file_location('materializador_bytes',ROOT/'scripts/materializar.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    mod.materialize(dest);put(marker,identity);return dest
def run(argv,cwd,stdout,stderr,timeout):
    with stdout.open('w',encoding='utf8') as so,stderr.open('w',encoding='utf8') as se:
        child=subprocess.Popen(list(map(str,argv)),cwd=cwd,stdout=so,stderr=se,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        try:return child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:child.kill();child.wait();raise
def main():
    p=argparse.ArgumentParser();p.add_argument('--mechanism',required=True);p.add_argument('--out',required=True,type=Path);p.add_argument('--numpy-root',type=Path);p.add_argument('--recalc',action='store_true');a=p.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=True);started=time.monotonic();pkg=package();mat=materialize(out)
    report={'mechanism':a.mechanism,'mode':'NATIVE_REPRODUCTION','status':'RUNNING','source_material':str(mat),'historical_folders_required':False,'new_E1_learning':False}
    if a.mechanism.startswith('M') and 1<=int(a.mechanism[1:])<=34:
        if a.recalc:raise ValueError('Este ID ofrece reproducción nativa; los recálculos de observadores son M039–M041. No se ejecutará el motor en modo recálculo.')
        family=FAMILIES[int(a.mechanism[1:])-1];target=out/'nativo';assert not target.exists(),'Se conserva el resultado existente; use otra salida'
        script='worker_legacy_core.py' if family in ('core06','core07') else 'worker_initial_cpc8.py' if family=='initial_cpc8' else 'worker_social.py' if family=='social' else 'worker_extension.py' if family in EXTENSIONS else 'worker_retention.py' if family in RETENTION else 'worker_core.py'
        if family in ('core06','core07'):
            np=a.numpy_root or pkg/'codigo_comun/terceros'
            argv=[sys.executable,'-I','-B',ROOT/'reproduccion'/script,'--family',family,'--numpy-root',np,'--materialized',mat,'--out',target]
        else:
            arg=family.removeprefix('retain_') if family in RETENTION else family
            argv=[sys.executable,'-I','-B',ROOT/'reproduccion'/script,arg,'--materialized',mat,'--out',target]
        code=run(argv,out,out/'stdout.log',out/'stderr.log',2400 if family=='core07' else 1800)
        result=target/'RECOVERY.json'
        observed=json.loads(result.read_text(encoding='utf8')) if result.is_file() else {'status':'PROCESS_FAILED_WITHOUT_RESULT'}
        report.update(family=family,command=list(map(str,argv)),exit_code=code,native=observed)
        if family in ('core06','core07') and (target/'PRIMARY_TRANSITIONS.json').is_file():
            ref=ROOT/'verificaciones'/(family.upper()+'_PRIMARY_TRANSITIONS.json');exp=json.loads(ref.read_text(encoding='utf8'));act=json.loads((target/'PRIMARY_TRANSITIONS.json').read_text(encoding='utf8'));keys=('family','worlds','transitions','physical_imports')
            report['full_state_port_comparison']={k:act[k]==exp[k] for k in keys}
        report['status']='PASS' if code==0 and observed.get('status')=='PASS' and all(report.get('full_state_port_comparison',{}).values()) else 'FAIL'
        report['scope']='Reproducción del contrato y controles originales; no facultades simultáneas ni nueva adquisición de la vida actual.'
    else:
        from ejecutar_cpc9 import execute
        report=execute(a.mechanism,mat,out,pkg,a.recalc)
    report['elapsed_seconds']=time.monotonic()-started;put(out/'RESULTADO.json',report);print(json.dumps({'id':a.mechanism,'status':report['status'],'seconds':report['elapsed_seconds'],'mode':report.get('mode')},ensure_ascii=False))
    if report['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
