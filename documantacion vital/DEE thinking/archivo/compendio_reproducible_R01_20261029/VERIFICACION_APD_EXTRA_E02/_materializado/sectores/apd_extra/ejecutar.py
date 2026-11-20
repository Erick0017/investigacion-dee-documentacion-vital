from pathlib import Path,PurePosixPath
import argparse,base64,gzip,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def materialize(out):
    index=json.loads((ROOT/'almacen/INDICE.json').read_bytes());store=ROOT/'almacen/CONTENIDOS.jsonl.gz';assert sha(store)==index['store_sha256']
    dest=out.parent/'_apd_extra_materializado';marker=dest/'_ALMACEN_VALIDADO.json'
    if marker.exists():
        assert json.loads(marker.read_bytes())['store_sha256']==index['store_sha256'];return dest
    dest.mkdir(parents=True,exist_ok=True);byhash={}
    for name,r in index['paths'].items():
        q=PurePosixPath(name);assert not q.is_absolute() and '..' not in q.parts and ':' not in name and '\\' not in name
        byhash.setdefault(r['sha256'],[]).append(name)
    seen=set()
    with gzip.open(store,'rt',encoding='ascii') as f:
        for line in f:
            item=json.loads(line);data=base64.b64decode(item['base64'],validate=True);h=hashlib.sha256(data).hexdigest();assert h==item['sha256'] and len(data)==item['bytes'] and h not in seen;seen.add(h)
            for name in byhash[h]:
                p=dest/name;p.parent.mkdir(parents=True,exist_ok=True)
                if p.exists():assert sha(p)==h
                else:p.write_bytes(data)
    assert seen==set(byhash);put(marker,{'store_sha256':index['store_sha256'],'paths':len(index['paths']),'blobs':len(seen)});return dest
def main():
    p=argparse.ArgumentParser();p.add_argument('--mechanism',required=True,choices=['M306','M307','M308']);p.add_argument('--out',type=Path,required=True);p.add_argument('--recalc',action='store_true');a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    if (out/'RESULTADO.json').exists():raise FileExistsError('Existing result protected; choose a fresh output')
    package=next(x for x in ROOT.parents if (x/'CATALOGO.json').is_file());mat=materialize(out);plans=[x for x in json.loads((ROOT/'configuraciones/EPISODIOS.json').read_bytes())['plans'] if x['mechanism']==a.mechanism]
    if a.recalc:raise ValueError('Use the original archived recálculo tools in sectores/apd; this entry only reproduces the bounded native episodes.')
    rows=[]
    for plan in plans:
        run=out/plan['id'];system=run/'sistema';shutil.copytree(package/'codigo_comun/cognitive',system,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        overlay=mat/plan['source_overlay']
        for q in overlay.rglob('*'):
            if q.is_file():p=system/q.relative_to(overlay);p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(q,p)
        (system/'runtime').mkdir(exist_ok=True);shutil.copyfile(package/'motor/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl',system/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl')
        (system/'estado/checkpoints').mkdir(parents=True,exist_ok=True)
        fp=run/'PLAN_REPRODUCCION.json';put(fp,plan)
        cmd=[sys.executable,'-I','-B',str(ROOT/'worker.py'),'--system',str(system),'--pair',str(mat/plan['pair']),'--plan',str(fp),'--reference-root',str(mat)]
        with (run/'stdout.log').open('w',encoding='utf8') as so,(run/'stderr.log').open('w',encoding='utf8') as se:
            child=subprocess.Popen(cmd,cwd=run,stdout=so,stderr=se,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            try:code=child.wait(timeout=2100)
            except subprocess.TimeoutExpired:child.kill();child.wait();code=-1
        r=system/'estado/observatorios/COMPENDIO_NATIVE/RESULTADO.json';value=json.loads(r.read_bytes()) if r.exists() else {'status':'FAIL','error':'No worker result'}
        rows.append({'case':plan['id'],'status':'PASS' if code==0 and value['status']=='PASS' else 'FAIL','exit_code':code,'command':cmd,'result':str(r.relative_to(out)),'details':value})
        put(out/'RESULTADO.json',{'mechanism':a.mechanism,'status':'RUNNING','cases':rows})
    report={'mechanism':a.mechanism,'mode':'NATIVE_ORIGINAL_EPISODE_REPRODUCTION','status':'PASS' if rows and all(x['status']=='PASS' for x in rows) else 'FAIL','cases':rows,'history_scope':'Isolated technical replay from complete paired parents. This does not alter current Cognitive or repeat the original campaigns.'};put(out/'RESULTADO.json',report)
    print(json.dumps({'status':report['status'],'mechanism':a.mechanism,'cases':len(rows)},ensure_ascii=False))
    if report['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
