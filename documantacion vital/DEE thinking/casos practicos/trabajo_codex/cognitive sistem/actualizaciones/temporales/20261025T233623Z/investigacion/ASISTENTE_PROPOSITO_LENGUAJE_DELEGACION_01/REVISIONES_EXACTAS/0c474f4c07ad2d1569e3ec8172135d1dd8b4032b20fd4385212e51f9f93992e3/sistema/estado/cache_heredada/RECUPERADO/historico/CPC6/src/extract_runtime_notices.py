"""Copy existing notices byte-exactly; do not assign a new project license."""
import argparse,hashlib,json
from pathlib import Path
import sys,zipfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from package_cpc6 import ROOT,WHL,WHL_SHA,PRODUCT_ZIP_SHA,sha,put


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--product',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    wheel=ROOT/'runtime'/WHL;assert sha(wheel)==WHL_SHA and sha(a.product)==PRODUCT_ZIP_SHA
    a.output.mkdir(parents=True,exist_ok=False);rows=[]
    for archive,member,destination in (
      (wheel,'dee_thinking/THIRD_PARTY_NOTICES.md','THIRD_PARTY_NOTICES_WHL.md'),
      (a.product,'DEE_thinking_4_0_0/source/THIRD_PARTY_NOTICES.md','THIRD_PARTY_NOTICES_CPP.md')):
        with zipfile.ZipFile(archive) as z:data=z.read(member)
        target=a.output/destination;target.write_bytes(data)
        rows.append({'artifact':archive.name,'artifact_sha256':sha(archive),'member':member,
          'copy':destination,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'byte_exact':target.read_bytes()==data})
    put(a.output/'PROCEDENCIA.json',{'schema':'CPC6.existing-notices.v1','files':rows,
      'scope':'Existing notices only, bytes preserved including their encoding. No license is invented or assigned to DEE Universe/DEE thinking. Full original wheel remains unchanged.'})
    print(json.dumps({'copied_existing_notices':len(rows),'byte_exact':all(x['byte_exact'] for x in rows)}))


if __name__=='__main__':main()
