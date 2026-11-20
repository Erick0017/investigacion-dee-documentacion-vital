
import sys,json,subprocess
from pathlib import Path
forbidden,out,p312,p313,child=sys.argv[1:6]
ok=False
try:Path(forbidden).read_text()
except PermissionError:ok=True
writing=False
try:Path(forbidden).write_text('must not overwrite')
except PermissionError:writing=True
assert Path(__file__).with_name('dato.txt').read_text()=='allowed'
r=subprocess.run([p312,'-I','-B','-c',child,forbidden,out,p313],capture_output=True,text=True,check=True,creationflags=0)
f=Path(out,'json.json');f.write_text('{"ok":true}')
m=subprocess.run([p312,'-I','-B','-m','json.tool',str(f)],capture_output=True,text=True,check=True)
print(json.dumps({'parent_blocked':ok,'outside_write_blocked':writing,'child':json.loads(r.stdout),'module':json.loads(m.stdout)}))
