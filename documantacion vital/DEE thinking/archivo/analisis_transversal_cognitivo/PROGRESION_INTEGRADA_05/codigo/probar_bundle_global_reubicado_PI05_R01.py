"""Relocated stdlib-only bundle test with original-workspace read denial."""
from pathlib import Path
import argparse,array,contextlib,csv,gzip,hashlib,io,json,os,runpy,shutil,struct,sys

def main():
    p=Path(__file__).resolve().parent.parent;source=p/'fuentes/RECALCULO_GLOBAL_PORTABLE_PI05_R01';stage=p/'control/PRUEBA_BUNDLE_GLOBAL_REUBICADO_PI05_R01'
    if stage.exists():raise FileExistsError('Preserve prior relocation test')
    stage.mkdir();target=stage/'paquete';shutil.copytree(source,target)
    python_root=Path(sys.base_prefix).resolve();allowed_root=stage.resolve();reads=set();blocked=[];imports=[]
    def under(path,root):return path==root or root in path.parents
    def audit(event,args):
        if event=='import':
            name=args[0]
            if name=='app'or name.startswith('app.')or name=='dee_thinking'or name.startswith('dee_thinking.'):
                imports.append(name);raise PermissionError('No DEE/app import allowed')
        if event!='open'or not args or not isinstance(args[0],(str,bytes,os.PathLike)):return
        path=Path(os.fsdecode(args[0])).resolve();mode=str(args[1]if len(args)>1 else'r')
        write=any(x in mode for x in('w','a','x','+'))
        if under(path,allowed_root):
            if not write:reads.add(path.relative_to(allowed_root).as_posix())
            return
        if under(path,python_root)and not write:return
        blocked.append(str(path));raise PermissionError('Original workspace access prohibited during relocated test')
    sys.addaudithook(audit)
    sys.argv=[str(target/'verificar_y_recalcular.py'),'--recalcular','--grupo','todos','--destino',str(stage/'resultado_nuevo')]
    runpy.run_path(str(target/'verificar_y_recalcular.py'),run_name='__main__')
    result=json.loads((stage/'resultado_nuevo/VERIFICACION_RECALCULO_PORTABLE.json').read_text(encoding='utf-8'))
    report={'schema':'DEE.PI05.portable_global.relocation_audited.R01','Native_ticks':0,'DEE_imports_attempted':imports,'original_workspace_reads_denied_during_execution':True,'blocked_attempts':blocked,'read_files_relative_to_isolated_stage':sorted(reads),'source_bundle_path_not_accessed_during_execution':True,'comparisons':len(result['comparisons']),'all_original_buffer_hashes_and_supports_match':result['all_frozen_support_and_original_buffer_hashes_match'],'cold_Native_not_rerun':True,'local_staging_path':str(stage.resolve()),'scope':'Copies and documentary recalculation only; source copies were made before read-denial hook. The hook permits this isolated stage and stdlib under the interpreter prefix. No Native world, original snapshot or original capture is opened.'}
    out=stage/'VERIFICACION_REUBICADA_SIN_ORIGINALES.json'
    with out.open('x',encoding='utf-8')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'verification':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'comparisons':len(result['comparisons']),'Native_ticks':0,'blocked_original_accesses':len(blocked)}))
if __name__=='__main__':main()
