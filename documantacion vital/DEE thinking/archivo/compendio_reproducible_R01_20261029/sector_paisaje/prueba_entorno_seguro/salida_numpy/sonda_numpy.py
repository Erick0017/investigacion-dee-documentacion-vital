
import sys,json,subprocess,tempfile
from pathlib import Path
import numpy as np
package,p312,p313=sys.argv[1:4]
expected=Path(package,'codigo_comun','terceros','numpy').resolve()
assert np.__version__=='2.2.6'and Path(np.__file__).resolve().is_relative_to(expected)
code="import sys,json,numpy as np,tempfile; print(json.dumps({'version':np.__version__,'file':np.__file__,'python':sys.version,'temp':tempfile.gettempdir()}))"
children=[]
for exe,version,folder in [(p312,'2.3.5','terceros312'),(p313,'2.2.6','terceros')]:
 result=subprocess.run([exe,'-I','-B','-c',code],capture_output=True,text=True,check=True)
 data=json.loads(result.stdout)
 assert data['version']==version and Path(data['file']).resolve().is_relative_to(Path(package,'codigo_comun',folder,'numpy').resolve())
 children.append(data)
temp=tempfile.gettempdir();temp.encode('ascii');assert len(temp)<120
print(json.dumps({'numpy_parent':{'version':np.__version__,'file':np.__file__},'children':children,'temp':temp,'native_ticks':0}))
