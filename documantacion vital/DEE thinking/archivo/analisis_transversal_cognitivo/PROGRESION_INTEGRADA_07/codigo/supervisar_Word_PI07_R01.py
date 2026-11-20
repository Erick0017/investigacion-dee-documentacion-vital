"""Bounded document-only Word export. No Native imports or state access."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess
P=Path(__file__).resolve().parents[1]
def main(a):
 ps=P/'codigo/Exportar_DOCX_PI07_Word_Aislado_R01.ps1'
 command=[r'C:\Users\Erik\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe','-NoProfile','-NonInteractive','-File',str(ps),'-Docx',str(a.documento.resolve(strict=True)),'-Proof',str(a.prueba.resolve()),'-Ejecutar']
 prefix=a.prueba.with_suffix('');record=prefix.with_name(prefix.name+'_SUPERVISOR.json')
 if a.prueba.exists() or record.exists():raise FileExistsError('Existing Word attempt preserved')
 began=datetime.datetime.now(datetime.timezone.utc).isoformat();process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 timed_out=False
 try:out,err=process.communicate(timeout=120)
 except subprocess.TimeoutExpired:
  timed_out=True;process.terminate();out,err=process.communicate(timeout=15)
 # Only this owned PowerShell may be terminated. Never terminate any Word PID.
 prefix.with_name(prefix.name+'_stdout.txt').write_bytes(out);prefix.with_name(prefix.name+'_stderr.txt').write_bytes(err)
 value={'schema':'DEE.PI07.document_only.Word.supervisor.v1','started_utc':began,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,'script_sha256':hashlib.sha256(ps.read_bytes()).hexdigest(),'owned_powershell_pid':process.pid,'returncode':process.returncode,'timeout_seconds':120,'timed_out':timed_out,'any_Word_process_terminated_by_supervisor':False,'Native_executed':False,'proof_present':a.prueba.is_file()}
 record.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(value,ensure_ascii=False))
 return 2 if timed_out else process.returncode
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--documento',type=Path,required=True);p.add_argument('--prueba',type=Path,required=True);raise SystemExit(main(p.parse_args()))
