"""Actual isolated documentary-fence test; no ZIP and no Native world."""
from pathlib import Path
import argparse
import ast
import json
import runpy
import shutil
import subprocess
import sys

HERE=Path(__file__).resolve().parent


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--destino',type=Path,required=True);a=ap.parse_args()
    dest=a.destino.resolve()
    if dest.exists()or not dest.is_relative_to(HERE):raise ValueError('Fresh P8/codigo destination required')
    x=dest/'x';out=dest/'r';x.mkdir(parents=True);out.mkdir()
    fixture=HERE/'pruebas/RECALCULO_RP_A01_REAL_R01'
    ip='04_EVIDENCIAS/PRIMARIOS/INDICE_PRIMARIOS_PI08.json'
    index=json.loads((fixture/ip).read_text('utf-8'))
    for entry in index['primaries']+index['products']:
        target=x/entry['file'];target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(fixture/entry['file'],target)
    (x/ip).write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for relative in ('RECALCULAR_PRIMARIOS_PI08.py','auditoria_documental_PI08.py',
                     'heredado/RECALCULAR_PRIMARIOS_PI07_LITERAL.py'):
        target=x/'05_RECALCULO'/relative;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(HERE/relative,target)
    probe=x/'05_RECALCULO/CONTINUACION_PROBE.py'
    probe.write_text("from pathlib import Path\nimport json,sys\nPath(sys.argv[1]).write_text(json.dumps({'schema':'DEE.PI08.fence_continuation_probe.v1','ran_after_successful_SystemExit0':True,'new_Native_ticks':0}),encoding='utf-8')\nraise SystemExit(0)\n",encoding='utf-8')
    package=runpy.run_path(str(HERE/'empaquetar_PI08_R01.py'),run_name='pure_fence_test_source')
    ast.parse(package['FENCE']);fence=dest/'FENCE.py';fence.write_text(package['FENCE'],encoding='utf-8')
    jobs=[{'script':'05_RECALCULO/RECALCULAR_PRIMARIOS_PI08.py',
           'argv':['--raiz','{EXTRACTION}','--salida','{OUTPUT}/PRIMARIOS.json']},
          {'script':'05_RECALCULO/CONTINUACION_PROBE.py','argv':['{OUTPUT}/CONTINUACION.json']}]
    jp=dest/'JOBS.json';jp.write_text(json.dumps(jobs),encoding='utf-8');audit=out/'AUDIT.json'
    command=[sys.executable,'-I','-B','-X','utf8',str(fence),str(x),str(out),str(jp),str(audit)]
    cp=subprocess.run(command,cwd=x,capture_output=True,text=True,encoding='utf-8',timeout=60,
                      creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    (dest/'stdout.txt').write_text(cp.stdout,encoding='utf-8');(dest/'stderr.txt').write_text(cp.stderr,encoding='utf-8')
    av=json.loads(audit.read_text('utf-8'))
    assert cp.returncode==0 and av['error']is None and not av['denied']and not av['DEE_or_app_imports']
    primary=json.loads((out/'PRIMARIOS.json').read_text('utf-8'))
    continuation=json.loads((out/'CONTINUACION.json').read_text('utf-8'))
    assert primary['schema']=='DEE.PI08.portable_primary_recalculation.v1'
    assert primary['new_Native_ticks']==0 and primary['all_checks_passed']and primary['episodes_recalculated']==1
    assert continuation['ran_after_successful_SystemExit0']and len(av['jobs'])==2
    # A controlled illegal original-path read must fail before opening it.
    forbidden=x/'05_RECALCULO/ORIGINAL_PROBE.py'
    forbidden.write_text("from pathlib import Path\nimport sys\nPath(sys.argv[1]).read_bytes()\n",encoding='utf-8')
    badout=dest/'denied';badout.mkdir();badjobs=dest/'JOBS_DENIED.json'
    badjobs.write_text(json.dumps([{'script':'05_RECALCULO/ORIGINAL_PROBE.py','argv':[str(HERE/'auditoria_documental_PI08.py')]}]),encoding='utf-8')
    bad_audit=badout/'AUDIT.json'
    bad=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(fence),str(x),str(badout),str(badjobs),str(bad_audit)],
                       cwd=x,capture_output=True,text=True,encoding='utf-8',timeout=30,
                       creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    denied=json.loads(bad_audit.read_text('utf-8'))
    assert bad.returncode==2 and denied['denied']and denied['error']['type']=='PermissionError'
    proof={'schema':'DEE.PI08.documentary_fence_actual_test.v1','all_tests_passed':True,
           'positive_actual_returncode':cp.returncode,'positive_access_fence':av,
           'actual_PI08_RP_primary_recalculated':1,'checks':len(primary['checks']),
           'SystemExit0_followed_by_second_CLI_verified':True,
           'deliberate_original_path_probe_blocked_before_read':True,
           'negative_probe_returncode':bad.returncode,'negative_probe_audit':denied,
           'new_Native_ticks':0,'DEE_imports':0,'ZIP_created':False,'product_modified':False,
           'scope':'Actual isolated Python subprocesses for documentary tools only. '
                   'The deliberate denied file was a non-secret P8 code file; no world, DEE module or operational process was opened.'}
    pp=dest/'PRUEBA.json';pp.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'proof':str(pp),'all_tests_passed':True,'new_Native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
