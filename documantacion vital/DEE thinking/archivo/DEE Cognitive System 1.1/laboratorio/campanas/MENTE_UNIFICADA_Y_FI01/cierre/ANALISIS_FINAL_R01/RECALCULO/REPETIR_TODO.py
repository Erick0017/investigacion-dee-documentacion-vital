"""Recálculos archivados del ZIP exacto; estándar Python, cero ticks DEE."""
from __future__ import annotations
import argparse,gzip,hashlib,json,os,subprocess,sys,time
from pathlib import Path

def digest(data):return hashlib.sha256(data).hexdigest()
def read_reference(p):return gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--salida',type=Path,required=True);ap.add_argument('--allow-newline-differences',action='store_true',help='Explicitly accept only CRLF/LF output serialization differences; original member hashes and calculator exit codes remain strict.');a=ap.parse_args()
    root=Path(__file__).resolve().parents[1]
    manifest=json.loads((root/'MANIFIESTO_HASHES.json').read_text(encoding='utf-8'))
    errors=[]
    declared={x['path'] for x in manifest['members']}|{'MANIFIESTO_HASHES.json'}
    actual_members={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    if declared!=actual_members:raise ValueError({'missing':sorted(declared-actual_members),'extra':sorted(actual_members-declared)})
    for entry in manifest['members']:
        p=root/entry['path']
        if not p.is_file()or p.stat().st_size!=entry['bytes']or digest(p.read_bytes())!=entry['sha256']:errors.append({'member':entry['path'],'error':'Missing or altered bytes'})
    if errors:raise ValueError(errors)
    if a.salida.resolve().is_relative_to(root.resolve()):raise ValueError('Results must be outside the immutable extracted analysis tree')
    if a.salida.exists():raise FileExistsError('Use a new result directory; do not overwrite a previous verification')
    a.salida.mkdir(parents=True)
    plan=json.loads((root/'RECALCULO/PLAN_GLOBAL.json').read_text(encoding='utf-8'))
    runs=[]
    for number,item in enumerate(plan['cases']):
        base=root/item.get('base','.')
        script=base/item['script'];assert script.is_file()
        output=a.salida/(str(number).zfill(2)+'_'+item['case']+'.json')
        args=[];want_output=False
        for value in item['args']:
            if want_output:args.append(str(output.resolve()));want_output=False;continue
            args.append(str((base/value).resolve())if(base/value).exists()else value)
            if value in('--salida','--out'):want_output=True
        cmd=[sys.executable,'-I','-B','-X','utf8',str(script.resolve()),*args]
        start=time.monotonic();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8');env.pop('PYTHONPATH',None)
        p=subprocess.run(cmd,cwd=a.salida,env=env,capture_output=True,encoding='utf-8',errors='replace',timeout=item.get('timeout_seconds',180))
        expected=read_reference(base/item['reference']);actual=output.read_bytes()if output.exists()else b''
        exact=actual==expected
        newline_only=not exact and bool(actual) and actual.replace(b'\r\n',b'\n')==expected.replace(b'\r\n',b'\n')
        accepted=p.returncode==0 and(exact or(a.allow_newline_differences and newline_only))
        check={'case':item['case'],'command':cmd,'cwd':str(a.salida.resolve()),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'elapsed_seconds':time.monotonic()-start,'expected_sha256':digest(expected),'actual_sha256':digest(actual),'exact_bytes_equal':exact,'line_endings_only':newline_only,'explicit_newline_compatibility_enabled':a.allow_newline_differences,'accepted':accepted,'native_ticks':0}
        if not accepted:errors.append({'case':item['case'],'error':'Recalculation failed or output differs from fixed reference','line_endings_only':newline_only})
        runs.append(check)
    result={'native_ticks':0,'requires':'Python3 standard library only; no DEE engine imported','source_member_hashes_checked':len(manifest['members']),'recalculations':runs,'errors':errors,'all_exact':all(x['exact_bytes_equal']and x['returncode']==0 for x in runs),'all_recalculations_accepted':not errors,'original_bytes_never_rewritten':True}
    (a.salida/'VERIFICACION_RECALCULOS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'cases':len(runs),'members':len(manifest['members']),'errors':errors,'native_ticks':0}))
    if errors:raise SystemExit(2)
if __name__=='__main__':main()
