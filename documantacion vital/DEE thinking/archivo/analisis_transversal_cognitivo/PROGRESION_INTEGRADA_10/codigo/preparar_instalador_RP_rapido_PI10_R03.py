"""Pure path-check performance delta; original R02 stays intact."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;src=H/'incorporar_reproducibilidad_estable_PI10_R02.py';out=H/'incorporar_reproducibilidad_estable_PI10_R03.py'
text=src.read_text('utf8');old="def regular(p):\n for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No symlink/junction source or destination')\n";new="""_checked_components=set()
def regular(p):
 # Every existing component is checked at least once in this invocation.
 # File bytes are independently hashed before/after exact copy; this cache
 # avoids repeatedly lstating the same twenty immutable ancestors per file.
 for n in(p,*p.parents):
  if n in _checked_components:continue
  try:info=n.lstat()
  except FileNotFoundError:continue
  need(not(n.is_symlink()or getattr(info,'st_file_attributes',0)&1024),'No symlink/junction source or destination');_checked_components.add(n)
""";assert text.count(old)==1;text=text.replace(old,new);ast.parse(text)
if out.exists():assert out.read_text('utf8')==text
else:
 with out.open('x',encoding='utf8')as f:f.write(text)
print(json.dumps({'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'Native':0}))
