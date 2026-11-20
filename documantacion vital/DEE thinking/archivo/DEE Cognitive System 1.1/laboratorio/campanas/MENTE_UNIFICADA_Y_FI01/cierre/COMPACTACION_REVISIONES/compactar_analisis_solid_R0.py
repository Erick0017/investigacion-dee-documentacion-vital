"""Fallback lossless: árbol sellado íntegro -> tar.xz solidario -> ZIP estándar.

No usar sobre una campaña viva. No elimina ni altera bytes, nombres, gzip,
referencias o manifiestos originales. No importa DEE ni avanza mundos.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,io,json,lzma,tarfile,tempfile,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('solid_deployer',HERE/'DESPLEGAR_DATOS.py');safe=importlib.util.module_from_spec(spec);spec.loader.exec_module(safe)
LIMIT=16000000

def sha(p):return safe.digest_file(p)
def js(v):return(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')

class HashReader:
    def __init__(self,stream):self.stream=stream;self.h=hashlib.sha256();self.count=0
    def read(self,n=-1):
        b=self.stream.read(n);self.h.update(b);self.count+=len(b);return b

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--stage',type=Path,required=True);ap.add_argument('--zip',type=Path,required=True);a=ap.parse_args()
    stage=a.stage.resolve(strict=True);archive=a.zip.resolve();report=archive.with_suffix('.SELLADO_SOLIDARIO_EXTERNO.json')
    if archive.exists()or report.exists()or archive.is_relative_to(stage):raise ValueError('ZIP/recibo nuevos y fuera del stage original')
    original,_,expected=safe.verify_tree(stage,safe.INNER_MANIFEST)
    if 'RECALCULO/REPETIR_TODO.py'not in original:raise ValueError('Se requiere el runner original final en RECALCULO/REPETIR_TODO.py')
    manifest=original[safe.INNER_MANIFEST];manifest_row={'path':safe.INNER_MANIFEST,'bytes':manifest.stat().st_size,'sha256':sha(manifest)}
    ordered=[safe.INNER_MANIFEST,*sorted(expected)];rows={**expected,safe.INNER_MANIFEST:manifest_row};expanded=sum(r['bytes']for r in rows.values())
    archive.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='DEE-solid-',dir=archive.parent)as tmp:
        tmp=Path(tmp);payload=tmp/safe.PAYLOAD
        with lzma.open(payload,'wb',format=lzma.FORMAT_XZ,preset=6)as compressed:
            with tarfile.open(fileobj=compressed,mode='w|',format=tarfile.PAX_FORMAT)as tf:
                for name in ordered:
                    p=original[name];row=rows[name];info=tarfile.TarInfo(name);info.size=row['bytes'];info.mode=0o644;info.mtime=0;info.uid=info.gid=0
                    with p.open('rb')as f:
                        reader=HashReader(f);tf.addfile(info,reader)
                        if reader.count!=row['bytes']or reader.h.hexdigest()!=row['sha256']:raise ValueError('Stage cambió durante la compresión: '+name)
        public={}
        for name,p in original.items():
            path=Path(name)
            if len(path.parts)==1 and(path.suffix.lower()in('.md','.csv')or name in('CAPACIDADES_POR_VIDA.json','COBERTURA.json','CONTINUIDAD_MENTE_UNIFICADA_Y_FI01.json')):
                public['DOCUMENTACION_ORIGINAL/'+name if name=='LEER_PRIMERO.md'else name]=p
            if path.parts[0]=='MANUAL'and path.suffix.lower()in('.docx','.md','.json'):public[name]=p
        extra={safe.PAYLOAD:payload,'RECALCULO/DESPLEGAR_DATOS.py':HERE/'DESPLEGAR_DATOS.py',**public}
        index={'schema':'DEE.analysis.lossless_solid_container.v1','payload':{'file':safe.PAYLOAD,'bytes':payload.stat().st_size,'sha256':sha(payload),'format':'tar.xz, lossless solid LZMA2 preset6'},
          'original_manifest':manifest_row,'original_file_count':len(original),'original_expanded_bytes':expanded,'original_members_omitted':0,
          'source_stage':str(stage),'representation':'One solid compression stream of EVERY exact original file, including existing gzip members as opaque original bytes. Names and bytes exact; tar filesystem metadata normalized, not a byte-identical historical ZIP.',
          'public_copies':[{'outer_file':n,'original_file':p.relative_to(stage).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}for n,p in sorted(public.items())],
          'coverage':'All positive/negative primaries, code and recalc references remain inside the payload; no counterexample omitted. Public copies are reading conveniences, not another scientific revision.',
          'native_ticks':0,'no_engine_required_for_decompression':True,'not_operational_life_backup':True}
        readme='''# Análisis DEE — contenedor solidario sin pérdida

Los informes y el Word en MANUAL/ pueden leerse directamente. TODOS los archivos
del análisis original, con sus nombres y bytes exactos, están además dentro de
DATOS_ANALISIS.tar.xz. No se ha eliminado ninguna evidencia positiva o negativa.
Los gzip originales se conservaron opacos; no se recalcularon ni reescribieron.

1. Extraiga este ZIP en una carpeta nueva, sin añadirle otros archivos.
2. Con Python3 estándar (incluido lzma), desde allí ejecute:

    python RECALCULO/DESPLEGAR_DATOS.py --destino RUTA_NUEVA_FUERA_DE_ESTA_CARPETA

3. El helper valida primero el contenedor, despliega a ese destino nuevo y valida
   cada nombre, tamaño y SHA contra el manifiesto ORIGINAL incluido íntegro.
   Rechaza enlaces, rutas inseguras, duplicados, faltantes y extras. Un fallo
   conserva sólo el destino nuevo parcial; no modifica el contenedor ni fuentes.
4. Desde el árbol desplegado, lea su LEER_PRIMERO.md original y ejecute:

    python RUTA_DESPLEGADA/RECALCULO/REPETIR_TODO.py --salida OTRA_RUTA_NUEVA_EXTERNA

Esto es descompresión y recálculo archivado: cero ticks DEE, ningún motor,
aprendizaje o reproducción nativa. No es un respaldo operativo completo de vidas.
El hash del ZIP se entrega fuera del propio contenedor. Material privado.
'''
        generated={safe.INDEX:js(index),'LEER_PRIMERO.md':readme.encode('utf8')}
        external_members=[]
        for name,p in sorted(extra.items()):safe.safe_name(name);external_members.append({'path':name,'bytes':p.stat().st_size,'sha256':sha(p)})
        for name,b in sorted(generated.items()):external_members.append({'path':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
        names=[r['path']for r in external_members]
        if len(names)!=len(set(n.casefold()for n in names)):raise ValueError('Colisión exterior de nombres')
        outer=js({'schema':'DEE.analysis.outer_member_manifest.v1','members':sorted(external_members,key=lambda r:r['path']),'self_hash_excluded':True,'original_manifest_sha256':manifest_row['sha256'],'native_ticks':0})
        with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
            for name,p in sorted(extra.items()):z.write(p,name)
            for name,b in sorted(generated.items()):z.writestr(name,b)
            z.writestr(safe.OUTER_MANIFEST,outer)
        with zipfile.ZipFile(archive)as z:
            if z.testzip()is not None or set(z.namelist())!=set(names)|{safe.OUTER_MANIFEST}:raise ValueError('ZIP íntegro/membresía exterior incorrecta')
            for r in external_members:
                b=z.read(r['path'])
                if len(b)!=r['bytes']or hashlib.sha256(b).hexdigest()!=r['sha256']:raise ValueError('Miembro ZIP no coincide')
        safe.verify_tree(stage,safe.INNER_MANIFEST)
        result={'status':'SEALED_WITHIN_LIMIT'if archive.stat().st_size<=LIMIT else'UNPUBLISHED_OVERSIZE_CANDIDATE','zip':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'compressed_limit_bytes':LIMIT,
          'outer_files':len(external_members)+1,'all_original_files':len(original),'all_original_expanded_bytes':expanded,'solid_payload_bytes':payload.stat().st_size,'original_manifest_sha256':manifest_row['sha256'],
          'source_unchanged':True,'no_original_member_omitted':True,'no_gzip_reencoding':True,'crc_and_outer_hashes_verified':True,'native_ticks':0,'decompression_test_required_from_exact_zip':True}
        report.write_bytes(js(result));print(json.dumps(result,ensure_ascii=False))
        return 0 if result['status']=='SEALED_WITHIN_LIMIT'else 2
if __name__=='__main__':raise SystemExit(main())
