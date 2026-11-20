from pathlib import Path
import hashlib,json,os
P=Path(__file__).resolve().parents[1]
f=P/'codigo/supervisar_Word_PI07_R01.py';old=f.read_bytes()
before=P/'codigo/revisiones/supervisar_Word_PI07_ANTES_PWSH_R01.py'
before.parent.mkdir(exist_ok=True)
with before.open('xb')as stream:stream.write(old)
needle="['powershell.exe'"
text=old.decode('utf8')
if text.count(needle)!=1:raise ValueError('Exact old launcher expected')
text=text.replace(needle,"[r'C:\\Users\\Erik\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\native\\powershell\\pwsh.exe'")
d=P/'documentos';rev=d/'revisiones_WORD_R01';rev.mkdir()
names=['RENDER_WORD_MANUAL_PI07_R01_SUPERVISOR.json','RENDER_WORD_MANUAL_PI07_R01_stdout.txt','RENDER_WORD_MANUAL_PI07_R01_stderr.txt']
rows=[]
for name in names:
 source=d/name;target=rev/name
 if source.resolve().parent!=d.resolve()or target.exists():raise ValueError('Exact unique document QA file only')
 rows.append({'file':name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
 os.rename(source,target)
f.write_text(text,encoding='utf8')
(rev/'PRESERVACION_Y_CORRECCION.json').write_text(json.dumps({'files':rows,'original_supervisor_sha256':hashlib.sha256(old).hexdigest(),'new_supervisor_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'reason':'Same Word export, existing bundled PowerShell instead of incompatible legacy command module environment. First attempt did not open a document or Word process.','Native_ticks':0},indent=2)+'\n',encoding='utf8')
print('PREVIOUS_ATTEMPT_PRESERVED_SAME_SCOPE_FIXED')
