"""Equivalent packaging revision using existing source-capture hash indices.

No historical member is rehashed. Only the small existing INDICE.json files,
the prior published ZIP and newly generated logistical records are hashed.
"""
import importlib.util,json,shutil,sys
from pathlib import Path

def option(name):return Path(sys.argv[sys.argv.index('--'+name)+1])
base=Path(__file__).with_name('preparar_revision_logistica_r02.py')
spec=importlib.util.spec_from_file_location('preserved_logistical_R02',base);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
root=option('sistema').resolve().parent;selection=m.read(option('seleccion'))
packages=[p for p in selection['research_packages']if p['source'].endswith('/codigo_ejecutado')and p['target'].endswith('/REVISIONES_EXACTAS')and 'ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01'in p['source']]
if len(packages)!=1:raise ValueError('Exactly the previously approved APD revision package is required')
source=root/packages[0]['source'];indices={};witness=[];normal_sha=m.sha;normal_write=m.write;reused=[0]
for directory in sorted(source.iterdir()):
    if not directory.is_dir():continue
    index=directory/'INDICE.json'
    if not index.is_file():raise ValueError('Existing source capture index missing: '+str(directory))
    values=m.read(index)
    if not isinstance(values,dict):raise ValueError('Unexpected historical index schema')
    indices[directory.name]=values;witness.append({'source':index.relative_to(root).as_posix(),'bytes':index.stat().st_size,'sha256':normal_sha(index)})
if len(indices)!=25:raise ValueError('The diagnosed source comprised exactly 25 captured revisions')
def known_sha(path):
    path=Path(path)
    if path.is_relative_to(source):
        relative=path.relative_to(source);parts=relative.parts
        if len(parts)>1:
            value=indices.get(parts[0],{}).get(Path(*parts[1:]).as_posix())
            if not isinstance(value,str)or len(value)!=64:raise ValueError('Excluded source member lacks a previously recorded SHA: '+str(relative))
            reused[0]+=1;return value
    return normal_sha(path)
def witnessed_write(path,value):
    path=Path(path)
    if path.name=='INDICE_OMISIONES_REVISIONES.json':
        value['source_hash_provenance']='Each member SHA is reused from its existing closed INDICE.json, not freshly checked. Byte sizes are metadata measurements of the retained local file.'
        value['covering_source_indices']=witness
        value['member_hashes_reused']=reused[0]
        for row in value['files']:
            relative=Path(row['source']).relative_to(Path(packages[0]['source']));row['source_hash_origin_index']=(Path(packages[0]['source'])/relative.parts[0]/'INDICE.json').as_posix()
    if path==option('nuevo-sello').resolve():
        shutil.copyfile(Path(__file__),option('salida')/Path(__file__).name)
        value['logistical_revision']['hash_source']='25 previously existing captured INDICE.json manifests; no repeated member hashing or scientific audit.'
    return normal_write(path,value)
m.sha=known_sha;m.write=witnessed_write
if __name__=='__main__':m.main()
