from pathlib import Path
import argparse,datetime,gzip,hashlib,json,shutil,zipfile
B=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(x):return hashlib.sha256(x).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def files(root):
 for p in sorted(root.rglob('*')):
  if not p.is_file()or '__pycache__'in p.parts or p.suffix in('.pyc','.pyo'):continue
  yield p
def main():
 a=argparse.ArgumentParser();a.add_argument('name');x=a.parse_args();target=B/x.name
 if target.exists():raise SystemExit('Ya existe: se conserva; elija otro candidato')
 target.mkdir();logical={};origins={};mechanisms=[];sectors=[]
 for p in files(B/'package'):
  rel=p.relative_to(B/'package').as_posix()
  if rel=='codigo_comun/ejecucion_aislada.py':continue
  if rel in('reproducir.py','INICIAR_REPRODUCCION.bat'):shutil.copy2(p,target/p.name);continue
  logical[rel]=p
 for sector in('core','paisaje','mente','apd','apd_extra'):
  source=B/('sector_'+sector);info=read(source/'sector.json');sectors.append(info)
  for m in info['mechanisms']:
   m=dict(m,sector=sector,location='sectores/'+sector,word_sections=[str(v)for v in m.get('word_families',[])])
   m.setdefault('new_validation_status','PENDIENTE_DE_EJECUCION_DESDE_ZIP')
   mechanisms.append(m)
  for p in files(source/'stage'):
   rel='sectores/'+sector+'/'+p.relative_to(source/'stage').as_posix()
   if p.suffix.lower()in('.whl','.pyd','.mp4','.docx','.pdf','.zip'):raise ValueError('Motor o distribución duplicados en sector: '+rel)
   logical[rel]=p
  for name in('seleccion.json',):
   if(source/name).exists():logical['sectores/'+sector+'/'+name]=source/name
 for p in files(B/'package/motor'):
  logical['motor/'+p.name]=p
 unique={};rows=[];total=0;cache={}
 old=B/'CANDIDATO_01/CATALOGO.json'
 if old.exists():
  for r in read(old)['files']:cache.setdefault(r['sha256'],r)
 # Los wheels se guardan una sola vez con su nombre instalable.
 for rel,p in logical.items():
  if rel.startswith('motor/'):
   data=p.read_bytes();h=sha(data);dest=target/rel;dest.parent.mkdir(exist_ok=True);dest.write_bytes(data);unique[h]=(rel,'raw')
 for rel,p in sorted(logical.items()):
  data=p.read_bytes();h=sha(data);total+=len(data)
  if h not in unique:
   if h in cache:
    oldrow=cache[h];storage=oldrow['storage'];codec=oldrow['compression'];dest=target/storage
    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(B/'CANDIDATO_01'/storage,dest);unique[h]=(storage,codec)
    rows.append(dict(path=rel,sha256=h,bytes=len(data),storage=storage,compression=codec));continue
   # Mantener exactos los bytes; compresión sin pérdida sólo como transporte.
   comp=gzip.compress(data,compresslevel=6,mtime=0)if len(data)>128 and p.suffix.lower()not in('.gz','.whl','.pyd','.dll','.bin')else data
   codec='gzip'if len(comp)<len(data)else'raw';stored=comp if codec=='gzip'else data
   storage='objetos/'+h[:2]+'/'+h+('.gz'if codec=='gzip'else'')
   dest=target/storage;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(stored);unique[h]=(storage,codec)
  storage,codec=unique[h]
  rows.append(dict(path=rel,sha256=h,bytes=len(data),storage=storage,compression=codec))
 cat=dict(schema='DEE.Compendio.Reproducible.R01',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 title='Compendio experimental consolidado, sin modificación del ente activo',
 boundary='Biblioteca de mecanismos y protocolos aislados. No fusiona biografías ni atribuye todo el catálogo aE1.',
 software=dict(kernel='Universev27congelado',product='DEE thinking4.5.0oficial',official_whl_sha256='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'),
 dependencies=[dict(name='Windowsx64/CPython3.13x64',included=False,scope='Runtime oficial y ABI histórico; preparar crea unvenv local, sin instalación global'),dict(name='CPython3.12x64',included=False,scope='Pendulum externo histórico; argumento--external-python'),dict(name='NumPy2.2.6cp313',included=True,location='codigo_comun/terceros'),dict(name='NumPy2.3.5cp312+Gymnasium1.4.0+FaramaNotifications0.0.6',included=True,scope='Sólo puente externo histórico, licencias incluidas')],
 methodology=dict(native='Reejecución física conRuntime y estados completos aislados.',recalculation='Cálculo desde primarios archivados; cero nuevos ticks.',continuation='Carga/uso posterior de un estado aprendido: no repetición de toda su adquisición.',negative='Un negativo histórico reproducido es evidencia; no se transforma en capacidad positiva.'),
 security=dict(auditor='codigo_comun/entorno_seguro.py',scope='Audita accesos y subprocesosPython; deniega lectura de fuentes originales y escritura fuera del resultado/temporal propio.',limits='No es un contenedor de sistema operativo: fopenC++/cargadorDLL y metadatosstat no quedan cubiertos porCPython. Se usan artefactos congelados, rutas locales, intérpretes aislados y sin importación delCognitive original.'),
 mechanisms=sorted(mechanisms,key=lambda z:z['id']),files=rows,
 compression=dict(logical_files=len(rows),logical_bytes=total,unique_blobs=len(unique),unique_stored_bytes=sum((target/path).stat().st_size for path,codec in unique.values()),method='SHA256 por bytes exactos; alias lógicos comparten objeto. Core y estados emparejados conservan sus índices internos verificados.'),
 omissions=['No incluye entornoPython, vídeos, interfaz gráficaCognitive, distribucionesZIPhistóricas, telemetría repetitiva ni el mundo activoDEE20_DEMO_01.','Cada sector conserva procedencia y exclusiones concretas. Los casos sólo documentales o sin revisión ejecutable exacta permanecen pendientes; no se sustituyen por otra vida.'],
 entrypoints=[dict(path=p,bytes=(target/p).stat().st_size,sha256=sha((target/p).read_bytes()))for p in('reproducir.py','INICIAR_REPRODUCCION.bat')])
 if len({m['id']for m in mechanisms})!=len(mechanisms):raise ValueError('ID duplicado')
 write(target/'CATALOGO.json',cat)
 zip_path=B/(x.name+'.zip')
 with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True)as z:
  for p in files(target):z.write(p,'DEE_COMPENDIO_REPRODUCIBLE/'+p.relative_to(target).as_posix())
 result=dict(folder=str(target),zip=str(zip_path),bytes=zip_path.stat().st_size,sha256=sha(zip_path.read_bytes()),members=len(files_list:=list(files(target))),mechanisms=len(mechanisms),native=sum(bool(m.get('native'))for m in mechanisms),recalc=sum(bool(m.get('recalc'))for m in mechanisms),compression=cat['compression'])
 write(B/(x.name+'_SELLO.json'),result);print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
