"""Global archived APD03 recalculation, stdlib only, zero Native ticks.

Actual component CLIs are invoked on archived inputs, in another output
directory. Every produced file must equal its preserved expected bytes/hash.
This does not restore a life, execute providers or verify the pending Full.
"""
import argparse,hashlib,json,subprocess,sys,tempfile,time
from pathlib import Path

PATH_FLAGS={'--evidence','--evidencia','--io-evidence','--quality-artifacts',
    '--salida','--out','--snapshot','--source','--sources'}


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as stream:
        for block in iter(lambda:stream.read(1048576),b''):h.update(block)
    return h.hexdigest()


def safe(root,name):
    name=Path(name)
    if name.is_absolute():raise ValueError('Absolute dependency not admitted in global plan')
    result=(root/name).resolve()
    if not result.is_relative_to(root.resolve()):raise ValueError('Archive path escapes supplied root')
    return result


def write(path,value):
    with Path(path).open('x',encoding='utf8')as stream:
        json.dump(value,stream,sort_keys=True,ensure_ascii=False,indent=2);stream.write('\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out',required=True,type=Path);args=parser.parse_args()
    root=args.root.resolve();out=args.out.resolve()
    if out.is_relative_to(root):raise ValueError('Write recalculation outside the read-only package')
    out.mkdir(parents=True,exist_ok=False)
    plan=json.loads((root/'RECALCULO/PLAN_GLOBAL.json').read_bytes())
    inventory=json.loads((root/'RECALCULO/ENTRADAS_ESPERADAS.json').read_bytes())
    input_checks=[]
    for row in inventory['files']:
        path=safe(root,row['file']);actual=sha(path)
        ok=path.stat().st_size==row['bytes']and actual==row['sha256']
        input_checks.append({'file':row['file'],'byte_hash_identical':ok})
        if not ok:raise ValueError('Input/script/expected file differs: '+row['file'])
    results=[]
    for number,job in enumerate(plan['jobs']):
        base=safe(root,job['base']);script=safe(base,job['script']);expected=safe(base,job['expected'])
        if sha(expected)!=job['expected_sha256']:raise ValueError('Expected changed before job')
        result_path=out/(str(number).zfill(2)+'_'+job['name']+'.json')
        argv=[];last=None
        for value in job['args']:
            if value=='{output}':argv.append(str(result_path))
            elif last in PATH_FLAGS:argv.append(str(safe(base,value)))
            else:argv.append(value)
            last=value
        command=[sys.executable,'-I','-B',str(script),*argv];began=time.monotonic()
        run=subprocess.run(command,cwd=tempfile.gettempdir(),capture_output=True,text=True,encoding='utf8',timeout=180)
        same=run.returncode==0 and result_path.is_file()and result_path.read_bytes()==expected.read_bytes()
        row={'name':job['name'],'command':command,'exit_code':run.returncode,'stdout':run.stdout,'stderr':run.stderr,
            'wall_seconds_of_archived_recalculation':time.monotonic()-began,'byte_identical':same,
            'expected_file':expected.relative_to(root).as_posix(),'expected_sha256':job['expected_sha256'],
            'actual_sha256':sha(result_path)if result_path.is_file()else None}
        if result_path.is_file():
            value=json.loads(result_path.read_bytes())
            row['result_fields']={key:value[key]for key in('checks','issues','counts','new_native_ticks','new_provider_calls')if key in value}
        results.append(row)
        write(out/(str(number).zfill(2)+'_RECIBO_'+job['name']+'.json'),row)
        if not same:raise ValueError('Archived result not byte-identical: '+job['name'])
    # Preserve the combined report and also cross-check its declared task
    # totals against independently recalculated component results.
    comparison=json.loads((root/'COMPARACION_FUNCIONAL_Y_COSTE_MAIN_REFERENCIAS.json').read_bytes())
    main_result=json.loads((out/'00_MAIN.json').read_bytes())
    goals=main_result['counts']['correct_actual_files']
    quality=[r for r in main_result['APD02_quality_uses']if r['scope_group']=='three_two_provider_cases']
    cross={'Main_goals':goals==comparison['main']['goal_completed_total'][0]==8,
        'Main_quality':sum(r['success']for r in quality)==comparison['main']['quality_completed_total'][0]==2,
        'Main_comparable_opportunities':main_result['counts']['opportunities']+len(quality)==17==comparison['main']['comparable_opportunities'],
        'not_a_verification_of_pending_Full':True}
    if not all(cross.values()):raise ValueError('Combined functional report differs from component recalculation')
    write(out/'RESULTADO_GLOBAL.json',{'schema':'APD03.analysis.global_archived_recalculation.R01',
        'jobs':results,'jobs_executed':len(results),'all_byte_identical':all(r['byte_identical']for r in results),
        'input_files_verified':len(input_checks),'combined_report_checks':cross,'new_native_ticks':0,
        'new_provider_calls':0,'full_status':plan['full_status'],'energy':'NO MEDIDA',
        'scope':'Actual archived CLIs, exact expected bytes/hashes; not Native replay, new learning, Full execution or another computer.'})
    print(json.dumps({'jobs':len(results),'all_byte_identical':True,'inputs':len(input_checks),
        'out':str(out),'scope':'ARCHIVED_RECALCULATION_ONLY','full_status':plan['full_status']}))


if __name__=='__main__':main()
