"""Actual .bat-to-launcher help only; no owner/life or Native execution."""
import argparse,base64,hashlib,json,subprocess
from pathlib import Path
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--raiz-extraida',required=True,type=Path);p.add_argument('--salida',required=True,type=Path);a=p.parse_args();root=a.raiz_extraida.resolve(strict=True)
    if not(root/'INICIAR.bat').is_file():raise FileNotFoundError('Missing actual extracted entry .bat')
    if len(str(root))>240:raise ValueError('Use the same short exact extraction root to test cmd cwd')
    life='APD03_FULL_R01';paths=[root/'trabajo_personal/estado/vidas'/life/'VIDA.json',root/'trabajo_personal/entrada_sencilla/vidas'/life/'PROTOCOLO.json',root/'trabajo_personal/entrada_sencilla/vidas'/life/'SESIONES.jsonl']
    before=[{'file':path.relative_to(root).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)}for path in paths]
    argv=['cmd.exe','/d','/c','INICIAR.bat','usar','--help'];result=subprocess.run(argv,cwd=root,capture_output=True,timeout=60)
    stdout=result.stdout.decode('utf8',errors='replace');stderr=result.stderr.decode('utf8',errors='replace')
    after=[{'file':path.relative_to(root).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)}for path in paths]
    issues=[]
    if result.returncode:issues.append('Actual .bat help returned nonzero')
    if '--nueva'not in stdout or'--vida'not in stdout:issues.append('Actual launcher did not reach the explicit-mode APD03 help')
    if before!=after:issues.append('Help unexpectedly changed personal state/protocol/session bytes')
    report={'schema':'APD03.actual_bat_help.N0.R01','argv':argv,'cwd':str(root),'returncode':result.returncode,'stdout':stdout,'stderr':stderr,'stdout_exact_base64':base64.b64encode(result.stdout).decode('ascii'),'stderr_exact_base64':base64.b64encode(result.stderr).decode('ascii'),'display_decoding':'UTF8 replace only for display; original bytes preserved as base64.','before':before,'after':after,'issues':issues,'new_native_ticks':0,'new_lives':0,'scope':'One actual cmd/bat/launcher argparse-help invocation on the exact extraction. No UI owner or human interaction; existing personal life bytes unchanged. Separate from the preceding Native proof.'}
    with a.salida.open('x',encoding='utf8',newline='\n')as f:json.dump(report,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'returncode':result.returncode,'issues':issues,'new_native_ticks':0}));return bool(issues)
if __name__=='__main__':raise SystemExit(main())
