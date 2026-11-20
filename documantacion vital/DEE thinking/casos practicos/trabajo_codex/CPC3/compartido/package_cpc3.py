"""CPC3 atomic, idempotent packaging of a saved cut; no experiments here."""
import argparse,hashlib,json,os,shutil,sys,zipfile
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from supervise import Budget,atomic_json

NAME='CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip'
IGNORE={'staging','__pycache__','.venv','venv','.git','ACTIVE'}
def sha(data):return hashlib.sha256(data).hexdigest()
def files(root):
    for p in sorted(root.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(root)
        if any(x in IGNORE for x in rel.parts) or p.suffix in ('.pyc','.tmp','.zip','.lock'):continue
        if rel.as_posix() in ('MANIFEST.json','HASHES.sha256'):continue
        yield rel.as_posix(),p
def verify(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None;names=z.namelist();assert len(names)==len(set(names));prefix='CPC3/'
        m=json.loads(z.read(prefix+'MANIFEST.json'));assert set(names)=={prefix+r for r in m['files']}|{prefix+'MANIFEST.json'}
        for r,entry in m['files'].items():
            data=z.read(prefix+r);assert len(data)==entry['bytes'] and sha(data)==entry['sha256'],r
        for line in z.read(prefix+'HASHES.sha256').decode().splitlines():
            h,r=line.split('  ',1);assert sha(z.read(prefix+r))==h,r
        assert sha(z.read(prefix+'runtime/dee_thinking-3.5.0-cp313-cp313-win_amd64.whl'))=='721d4ad1610d6efc7e7101b49b9d68c6925efdcf596361aca09aabd0e315bcaa'
        assert sha(z.read(prefix+'fuentes_pertinentes/producto/source/src/kernel_v27.cpp'))=='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
        migration=json.loads(z.read(prefix+'MIGRACION_Y_LIMPIEZA.json'))
        for entry in migration['migrated']:assert sha(z.read(prefix+entry['destination']))==entry['sha256']
        errors=[]
        for n in names:
            if n.endswith('.py'):
                try:compile(z.read(n),n,'exec')
                except Exception as e:errors.append({'file':n,'error':repr(e)})
        assert not errors,errors
        for n in ['ejecutar.py','conversar.py','LEEME.md','INFORME_CIENTIFICO.md','CAPACIDADES.json','PREDICCIONES.jsonl','DIALOGOS.jsonl']:assert prefix+n in names,n
    return {'CRC':True,'hashes':True,'migrated_bytes_identical':True,'kernel_and_wheel_identity':True,'members':len(names),'bytes':Path(path).stat().st_size,'sha256':sha(Path(path).read_bytes()),'partial':m['partial']}
def package(root,partial=False,publish=False):
    root=Path(root).resolve();stage=root/'staging';stage.mkdir(exist_ok=True)
    if publish and not partial:
        # A valid scientific partial result may be published; 'partial' here
        # is only the emergency budget cut, NOT an ontological verdict.
        proof=json.loads((root/'resultados/CLEAN_REPRODUCTION.json').read_text(encoding='utf-8'))
        for key in ('verified','inherited_reference_reproduced','new_result_reproduced','snapshot_new_question','no_old_path_dependency'):
            assert proof.get(key) is True,('Independent qualification missing',key)
        assert (root/'compartido/CLOSED.json').is_file(),'Close owned workers before publication'
        active=[json.loads(p.read_text(encoding='utf-8')) for p in (root/'compartido/ACTIVE').glob('*.json')]
        assert not [x for x in active if x.get('status')=='RUNNING'],'Owned workers are still running'
        critical=proof.get('critical_source_hashes',proof.get('tested_source_hashes',{}))
        assert critical,'Empty independently qualified source map'
        assert {'ejecutar.py','conversar.py','src/core/entity.py','src/core/comparison_entity.py','src/core/policy_session.py','src/core/revisable_selection.py','src/habitat/native_loop.py'}.issubset(critical),'Final public profiles not qualified'
        for rel,digest in {**critical,**proof.get('critical_artifact_hashes',{})}.items():
            assert sha((root/rel).read_bytes())==digest,('Qualified code changed',rel)
    if partial:
        for name,content in [('LEEME.md','# Corte parcial CPC3\nConsulte evidencia preservada; no se declara integración no medida.\n'),('INFORME_CIENTIFICO.md','# Corte parcial por presupuesto CPC3\nVea controles, resultados y cobertura exacta.\n'),('ejecutar.py',"raise SystemExit('Partial cut; see experimental runners')\n"),('conversar.py',"raise SystemExit('Communication not completed in this cut')\n")]:
            if not (root/name).exists():(root/name).write_text(content,encoding='utf-8')
        if not (root/'CAPACIDADES.json').exists():atomic_json(root/'CAPACIDADES.json',{'status':'PARTIAL_BUDGET_CUTOFF'})
        for name in ['PREDICCIONES.jsonl','DIALOGOS.jsonl']:
            if not (root/name).exists():(root/name).write_text('',encoding='utf-8')
    rows={r:{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for r,p in files(root)}
    hp=root/'HASHES.sha256';hp.write_text(''.join(v['sha256']+'  '+r+'\n' for r,v in rows.items()),encoding='utf-8');rows['HASHES.sha256']={'bytes':hp.stat().st_size,'sha256':sha(hp.read_bytes())}
    atomic_json(root/'MANIFEST.json',{'schema':1,'campaign':'CPC3','author':'Ivan Erick Tlaltecatl Morales','version':'DEE thinking3.5.0','kernel':27,'partial':partial,'files':rows,'elapsed_seconds':Budget(root).elapsed(),'seal_utc':datetime.now(timezone.utc).isoformat(),'hash_scope':'MANIFEST excludes itself; HASHES excludes itself and MANIFEST; ZIP hash external'})
    temporary=stage/'CPC3.tmp.zip';failures=[]
    for attempt in range(2):
        try:
            with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
                for rel in sorted(set(rows)|{'MANIFEST.json'}):z.write(root/rel,'CPC3/'+rel)
            report=verify(temporary);atomic_json(stage/'ZIP_VERIFICATION.json',report)
            if publish:
                out=root.parent.parent/NAME;os.replace(temporary,out);assert sha(out.read_bytes())==report['sha256'];report['published']=str(out)
                atomic_json(stage/'PUBLICATION.json',report)
            return report
        except Exception as e:
            failures.append({'attempt':attempt+1,'error':repr(e)});atomic_json(stage/'PACKAGE_ERRORS.json',failures)
    raise RuntimeError('Bounded packaging retries exhausted; sealed staging preserved')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));p.add_argument('--partial',action='store_true');p.add_argument('--publish',action='store_true');p.add_argument('--verify');a=p.parse_args()
    print(json.dumps(verify(a.verify) if a.verify else package(a.root,a.partial,a.publish),indent=2))
