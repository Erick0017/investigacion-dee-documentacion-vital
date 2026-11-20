"""Preserve an unpublished updater attempt and narrow only revision-capture copying.

Zero Runtime. The operating system, selected lives, motor and paired bundles
remain untouched; the exact APD material protocol is not read or modified.
"""
import argparse,copy,fnmatch,hashlib,importlib.util,json,shutil
from datetime import datetime,timezone
from pathlib import Path

def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(p,x):
    with p.open('x',encoding='utf8')as f:json.dump(x,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in('sistema','colaborador','seleccion','sello','salida','nueva-seleccion','nuevo-sello'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();root=a.sistema.resolve().parent;col=a.colaborador.resolve();out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False);selection=read(a.seleccion);oldseal=read(a.sello)
    spec=importlib.util.spec_from_file_location('existing_updater_filters_only',col/'actualizaciones/actualizar.py');u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)
    targets=[x for x in selection['research_packages']if x['source'].endswith('/codigo_ejecutado')and x['target'].endswith('/REVISIONES_EXACTAS')and 'ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01'in x['source']]
    if len(targets)!=1:raise ValueError('Only the one explicitly approved APD revision-capture package may change')
    package=targets[0];before=copy.deepcopy(package);patterns=['*/sistema/estado/*','*/sistema/runtime/*'];package['exclude_patterns']=list(dict.fromkeys(package.get('exclude_patterns',[])+patterns));source=root/package['source'];omitted=[]
    for f in sorted(source.rglob('*')):
        if not f.is_file():continue
        rel=f.relative_to(source).as_posix()
        if u.research_member(rel,before)and not u.research_member(rel,package):
            if not any(fnmatch.fnmatchcase(rel,x)for x in patterns):raise ValueError('Unexpected exclusion outside the two approved regions')
            omitted.append({'source':f.relative_to(root).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
    if not omitted:raise ValueError('The diagnosed duplicate cache exclusion has no witness')
    write(out/'INDICE_OMISIONES_REVISIONES.json',{'schema':'DEE.APD01.capture_copy_exclusions.R02','research_package_source':package['source'],'research_package_target':package['target'],'exact_added_patterns':patterns,'files':omitted,'bytes':sum(x['bytes']for x in omitted),'scope':'Only files that the previous research-copy filter would include, under historical revision captures sistema/estado or sistema/runtime. Every original remains local. This is not applied to the operational sistema, motor or selected complete life/journal/outbox/artifact bundles.'})
    previous=col/'entregas/cognitive_sistem_colaborador.zip';managed=col/'actualizaciones/ARCHIVOS_GESTIONADOS.json'
    if sha(previous)!=oldseal['previous_collaboration_zip']['sha256']:raise ValueError('Previous published FullZIP changed during the unpublished attempt')
    write(out/'INTENTO_ACTUALIZADOR_R01_NO_PUBLICADO.json',{'native_ticks':0,'original_selection':{'file':str(a.seleccion),'sha256':sha(a.seleccion)},'original_seal':{'file':str(a.sello),'sha256':sha(a.sello)},'preserved_temporary_directory':str(col/'actualizaciones/temporales/20261025T233623Z'),'own_stopped_pids':[90848,91536],'verified_owned_command_before_stop':True,'reason':'Revision source capture also contained materialized historical estado/cache_heredada; maintainers authorized exclusion of only historical estado/runtime regions. The updater was stopped before manifest commit and before new ZIP publication.','previous_published_zip':{'bytes':previous.stat().st_size,'sha256':sha(previous)},'uncommitted_old_manifest':{'sha256':sha(managed)},'no_experiment_or_native_process_stopped':True})
    shutil.copyfile(Path(__file__),out/'preparar_revision_logistica_r02.py')
    selection['research_packages'].append({'source':out.relative_to(root).as_posix(),'target':package['target'].rsplit('/',1)[0]+'/DISTRIBUCION_OMISIONES','exclude_patterns':['*.docx']});selection['verification']=a.nuevo_sello.resolve().relative_to(root).as_posix();write(a.nueva_seleccion,selection)
    seal=copy.deepcopy(oldseal);seal['registered_utc']=datetime.now(timezone.utc).isoformat();seal['logistical_revision']={'revision':'R02','previous_closed_seal':{'file':str(a.sello),'sha256':sha(a.sello)},'authorization':'Maintainer explicitly authorized only two research-capture exclusions after an unpublished read-only updater attempt; same scientific cut/manual, no native change.','selection':{'file':str(a.nueva_seleccion),'sha256':sha(a.nueva_seleccion)},'omission_index':{'file':str(out/'INDICE_OMISIONES_REVISIONES.json'),'sha256':sha(out/'INDICE_OMISIONES_REVISIONES.json')},'source_regions_changed':patterns,'operational_life_and_motor_bundles_unchanged':True};write(a.nuevo_sello,seal)
    print(json.dumps({'omitted_capture_members':len(omitted),'omitted_duplicate_bytes':sum(x['bytes']for x in omitted),'selection_sha256':sha(a.nueva_seleccion),'seal_sha256':sha(a.nuevo_sello),'new_ticks':0}))
if __name__=='__main__':main()
