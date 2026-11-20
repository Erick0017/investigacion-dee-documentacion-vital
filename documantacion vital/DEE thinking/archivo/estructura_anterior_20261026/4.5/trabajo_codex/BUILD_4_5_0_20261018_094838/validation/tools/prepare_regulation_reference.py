"""Select exact CPC5 preparation source members, never execute its runners."""
from pathlib import Path
import argparse,hashlib,json,sys,zipfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from neutral_differential import put,sha
EXPECTED={
 'src/network.py':'3c40daa03642500ce8e3aeba46a9a1921ed0dfca42250941976023cb45b87593',
 'src/regulation_forks.py':'021b84a77f9badc01f92bf49fbd1218af93cdcf866e71a9d531f481603bfe3e2',
 'referencias/cpc4_red/recipe_v3.py':'4837b0e705dd56a3522dd4234349f2e518fab67c680e8ecf14e87ad66a36be43',
 'referencias/cpc4_red/dual_session.py':'5beaa006c2a292d48e94ffffc3b65159810c621acc83790361c95b41e1aef3a6',
 'referencias/cpc4_red/regulated_session.py':'55c89e692fe6165c88146d5cea6171b5cfebd6899df79d60a94d6fe012ce265a'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--zip',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);rows=[]
    with zipfile.ZipFile(a.zip) as z:
        paths=list(EXPECTED)+['referencias/cpc4_red/common_helpers.py']
        for rel in paths:
            matches=[name for name in z.namelist() if name==rel or name.endswith('/'+rel)]
            if len(matches)!=1:raise ValueError('Ambiguous/missing exact source member '+rel+': '+str(matches))
            raw=z.read(matches[0]);digest=hashlib.sha256(raw).hexdigest()
            if rel in EXPECTED and digest!=EXPECTED[rel]:raise ValueError('Working/reference source differs for '+rel)
            target=a.out/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            rows.append({'member':matches[0],'path':rel,'bytes':len(raw),'sha256':digest})
    put(a.out/'PROVENANCE.json',{'schema':'DEE45.selected_CPC5_regulation_source.v1','source_zip_name':a.zip.name,'source_zip_sha256':sha(a.zip),'members':rows,'scope':'Exact selected preparation/reference files. No original runner was executed and no result table is an implementation dependency.'})
    print(json.dumps({'selected':len(rows),'source_zip_sha256':sha(a.zip)}))
if __name__=='__main__':main()
