"""Fixtures técnicas propias, no evidencia de campaña ni DEE."""
import gzip,hashlib,io,json,shutil,subprocess,sys,tarfile,tempfile,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def write_json(p,x):p.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def update_outer(folder):
    ix=folder/'INDICE_COMPRESION_SOLIDARIA.json';x=json.loads(ix.read_bytes());b=(folder/'DATOS_ANALISIS.tar.xz').read_bytes();x['payload'].update(bytes=len(b),sha256=sha(b));write_json(ix,x)
    mf=folder/'MANIFIESTO_CONTENEDOR.json';m=json.loads(mf.read_bytes())
    for r in m['members']:
        b=(folder/r['path']).read_bytes();r.update(bytes=len(b),sha256=sha(b))
    write_json(mf,m)
def main():
    base=Path(tempfile.mkdtemp(prefix='FIXTURE_SOLID_0TICKS_',dir=HERE));stage=base/'original';stage.mkdir()
    files={'LEER_PRIMERO.md':b'# Fixture tecnica, no DEE\n','INFORME_RESULTADOS.md':b'No son resultados cientificos: prueba de archivos.\n',
      'RECALCULO/REPETIR_TODO.py':b'print("Technical fixture only; no motor or campaign")\n',
      'PRIMARIOS/opaco_original.json.gz':gzip.compress((b'{"technical_fixture":true,"value":123}\n')*1000,mtime=0),
      'PRIMARIOS/exactos.bin':bytes(range(256))*20,'EVIDENCIA/subcarpeta/nombre_largo_'+('x'*110)+'.txt':b'Long name PAX fixture\n'}
    for j in range(8):files['DATOS/TABLA_'+str(j)+'.csv']=(('indice,valor\n'+''.join(str(k)+','+str((k+j)%17)+'\n'for k in range(5000))).encode())
    for name,b in files.items():p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    manifest={'members':[{'path':n,'bytes':len(b),'sha256':sha(b)}for n,b in sorted(files.items())],'self_hash_excluded':True};write_json(stage/'MANIFIESTO_HASHES.json',manifest)
    archive=base/'fixture.zip';cmd=[sys.executable,'-I','-B',str(HERE/'compactar_analisis_solid.py'),'--stage',str(stage),'--zip',str(archive)]
    built=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',timeout=90)
    if built.returncode:raise AssertionError(built.stdout+built.stderr)
    container=base/'contenedor'
    with zipfile.ZipFile(archive)as z:z.extractall(container)
    dest=base/'desplegado';used=subprocess.run([sys.executable,'-I','-B',str(container/'RECALCULO/DESPLEGAR_DATOS.py'),'--destino',str(dest)],capture_output=True,text=True,encoding='utf8',timeout=90)
    if used.returncode:raise AssertionError(used.stdout+used.stderr)
    original={p.relative_to(stage).as_posix():p.read_bytes()for p in stage.rglob('*')if p.is_file()};restored={p.relative_to(dest).as_posix():p.read_bytes()for p in dest.rglob('*')if p.is_file()}
    assert original==restored
    attacks=[]
    for kind in('traversal','symlink','extra','duplicate'):
        outer=base/('ataque_'+kind);shutil.copytree(container,outer);payload=outer/'DATOS_ANALISIS.tar.xz'
        with tarfile.open(payload,'w:xz',format=tarfile.PAX_FORMAT,preset=6)as t:
            b=original['MANIFIESTO_HASHES.json'];info=tarfile.TarInfo('MANIFIESTO_HASHES.json');info.size=len(b);t.addfile(info,io.BytesIO(b))
            name='../OUTSIDE.txt'if kind=='traversal'else'EXTRA.txt'if kind=='extra'else'INFORME_RESULTADOS.md'
            info=tarfile.TarInfo(name)
            if kind=='symlink':info.type=tarfile.SYMTYPE;info.linkname='../OUTSIDE.txt';t.addfile(info)
            else:
                b=original.get(name,b'x');info.size=len(b);t.addfile(info,io.BytesIO(b))
                if kind=='duplicate':t.addfile(info,io.BytesIO(b))
        update_outer(outer)
        target=base/('rechazado_'+kind);r=subprocess.run([sys.executable,'-I','-B',str(outer/'RECALCULO/DESPLEGAR_DATOS.py'),'--destino',str(target)],capture_output=True,text=True,encoding='utf8',timeout=60)
        assert r.returncode!=0,(kind,r.stdout,r.stderr)
        assert not(base/'OUTSIDE.txt').exists()
        attacks.append({'kind':kind,'rejected':True,'exit_code':r.returncode,'stderr':r.stderr})
    result={'schema':'DEE.solid_container.technical_fixture_proof.v1','native_ticks':0,'campaign_stages_read':0,'DEE_imports':0,'fixture_directory':str(base),
      'source_files':len(original),'exact_all_names_and_bytes_restored':True,'opaque_original_gzip_sha256':sha(original['PRIMARIOS/opaco_original.json.gz']),
      'long_path_PAX_restored':True,'zip_sha256':sha(archive.read_bytes()),'zip_bytes':archive.stat().st_size,'malicious_tar_rejections':attacks,
      'packer_sha256':sha((HERE/'compactar_analisis_solid.py').read_bytes()),'deployer_sha256':sha((HERE/'DESPLEGAR_DATOS.py').read_bytes()),
      'scope':'Technical own fixture only. Not a final campaign build, no scientific archive copied, no native/runtime/actor execution.'}
    output=HERE/'PRUEBA_COMPACTACION_SOLID_TECNICA.json'
    if output.exists():raise FileExistsError(output)
    write_json(output,result);print(json.dumps({'files':len(original),'zip_bytes':archive.stat().st_size,'exact':True,'attacks_rejected':len(attacks),'proof_sha256':sha(output.read_bytes())}))
if __name__=='__main__':main()
