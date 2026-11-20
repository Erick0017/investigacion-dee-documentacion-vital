"""Safe independent extraction of a closed Core candidate."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,zipfile
p=argparse.ArgumentParser();p.add_argument('--zip',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
dest=a.out.resolve();dest.mkdir(parents=True,exist_ok=False)
with zipfile.ZipFile(a.zip)as z:
 names=z.namelist()
 if len(names)!=len(set(x.casefold()for x in names)):raise ValueError('Duplicate archive paths')
 for name in names:
  q=PurePosixPath(name)
  if q.is_absolute()or'..'in q.parts or':'in name or'\\'in name or q.parts[0]!='DEE_COGNITIVE_CORE':raise ValueError('Unsafe archive member')
 assert z.testzip()is None;z.extractall(dest)
print(json.dumps({'extraction':str(dest),'members':len(names),'artifact_sha256':hashlib.sha256(a.zip.read_bytes()).hexdigest()}))
