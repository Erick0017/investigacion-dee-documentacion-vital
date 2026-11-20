"""Packaging-only test using an immutable existing snapshot; no DEE world."""
import argparse,hashlib,importlib.util,json,shutil,sys,tempfile,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from importacion_emparejada import verify_export


def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--origen',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();source=a.origen.resolve();here=Path(__file__).resolve().parent
    checks={};loaded=[]
    with tempfile.TemporaryDirectory(prefix='mu-portable-bundle-')as name:
        root=Path(name).resolve();update=module(here/'distribucion/actualizar.py','mu_update_candidate');update.ROOT=root;update.OWNER=root/'actualizaciones/ARCHIVOS_GESTIONADOS.json'
        build=update.Build(source,bootstrap=True);build.release='PACKAGING_TEST_ONLY';build.seal_mtime=time.time()+1
        snapshot=source/'sistema/estado/checkpoints/MU_MAIN.T16634.ba61eac94a01.deetsnap.gz'
        # Immutable A-cut, not whichever future the current mutable VIDA points to.
        row={'alias':'TEST_ONLY','source_life':'MU_MAIN','world_id':'MU_MAIN','profile':'fisica_directa','tick':16634,
            'snapshot':'entes/estados/MU_MAIN_T16634.deetsnap.gz','snapshot_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest(),
            'physical':{'N':67,'tick':16634,'RAW_sha256':'0f532cb67d5103f4e1779d49632bde76baa576925f53ee6b59cb15177cf1b0ae','clocks_sha256':'e5aeee64c32139260c6db6809ac9835a6a4cbb8609eff38f42cdf8f6fed1bc0a'}}
        build.copy(snapshot,row['snapshot']);record={'life_id':'MU_MAIN','world_id':'MU_MAIN','parent':None}
        descriptor={'sidecar_directory':'servicios_persistentes/MU_MAIN','worker_directory':'servicios_locales/MU_MAIN'}
        build.service_bundle(record,row,snapshot,descriptor)
        for relative,staged in build.staged.items():
            dest=root/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(staged,dest)
        checks['one_packaged_native_snapshot_only']=len(list((root/'entes').rglob('*.deetsnap.gz')))==1
        launch=module(here/'distribucion/arrancar.py','mu_launch_candidate');launch.ROOT=root;launch.SYSTEM=root/'sistema';launch.catalog=lambda:[row]
        def fake_native_call(args,capture=False):
            if args[0]!='mente-unificada-importar':raise AssertionError('Unexpected simulated call; no engine is executed by this test')
            directory=Path(args[args.index('--paquete')+1]);r,m,v=verify_export(directory);loaded.append({'argv_operation':args[0],'verification':v,'physical':m['physical'],'native_engine_was_not_executed':True})
            return {'scope':'Packaging-only stub, no imported life or native ticks','verified_members':v['members_verified']}
        launch.call=fake_native_call;launch.open_copy('TEST_ONLY','PACKAGING_ONLY_NOT_A_REAL_LIFE',activate=False)
        checks['paired_import_materializes_complete_verified_bundle']=len(loaded)==1 and loaded[0]['verification']['members_verified']>2
        checks['no_original_paths_required_for_materialization']=loaded[0]['physical']==row['physical']
        source_text=(source/'sistema/app/lives.py').read_bytes();transformed=update.transformed('sistema/app/lives.py',source_text).decode('utf8')
        checks['personal_state_transform_retains_operation_offset']='operation_count_offset'in transformed and "self.state=(self.root/'../trabajo_personal/estado').resolve()"in transformed
        compact_text=(source/'sistema/app/compactar_historia_operativa.py').read_bytes();translated=update.transformed('sistema/app/compactar_historia_operativa.py',compact_text).decode('utf8')
        checks['archive_path_transform_is_relative']='Path(os.path.relpath(target,store.root)).as_posix()'in translated
    native_modules=sorted(k for k in sys.modules if k=='dee_thinking'or k.startswith('dee_thinking.'));checks['no_native_modules_or_Runtime_loaded']=not native_modules
    result={'schema':'DEE.unified.packaging_stdlib_tests.v1','checks':checks,'issues':[k for k,v in checks.items()if not v],'materialized_bundle':loaded,'native_ticks':0,
        'scope':'Existing closed snapshot bytes, file layout/hash checks and stubbed manager call only. This is NOT native import/continuation or exact final-ZIP verification; those remain release tests.'}
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8');print(json.dumps({'checks':checks,'issues':result['issues'],'native_ticks':0}));return bool(result['issues'])


if __name__=='__main__':raise SystemExit(main())
