"""Recover bounded historical documentary/source witnesses, not engine code."""
from pathlib import Path
import argparse,json,gzip,base64,hashlib,zipfile,sys
sys.stdout.reconfigure(encoding='utf8')
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--zip',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    selected={};rows=[];files={}
    with zipfile.ZipFile(a.zip)as z:
        m=json.loads(z.read('DEE_COGNITIVE_CORE/documentacion/MATRIZ_CAPACIDADES.json'));ix=json.loads(z.read('DEE_COGNITIVE_CORE/documentacion/INDICE_MIEMBROS.json'))['paths']
        for cap in m['rows']:
            for r in cap.get('historical_source_identities',[]):
                name=r.get('recovered_core_path')
                if not name or name not in ix or Path(name).suffix not in('.md','.py'):continue
                if cap['id']=='PRODUCT4_CONTRACT':continue
                selected.setdefault(ix[name]['sha256'],[]).append({'capability_id':cap['id'],'logical_path':name,'origin':ix[name].get('origin',{}),'row_status':cap['current_recovery_status']})
        for line in gzip.GzipFile(fileobj=z.open('DEE_COGNITIVE_CORE/mecanismos/RECUPERACION_POR_HASH.jsonl.gz')):
            x=json.loads(line)
            if x['sha256']not in selected:continue
            b=base64.b64decode(x['base64'],validate=True);h=sha(b)
            if h!=x['sha256']:raise ValueError('Historical source checksum mismatch')
            ext=Path(selected[h][0]['logical_path']).suffix;name=h[:24]+ext;f=a.out/name;f.write_bytes(b);files[h]=name
            rows.append({'file':name,'sha256':h,'bytes':len(b),'logical_sources':selected[h],'role':'Historical experiment source or documentary witness, NOT proof of new reproduction and not engine code'})
    if set(files)!=set(selected):raise ValueError('Historical documentary witness missing')
    (a.out/'INDICE_DOCUMENTAL.json').write_text(json.dumps({'archive':a.zip.name,'archive_sha256':'412a6819e36203a0086790003301a13722bd14fd3a3213b03681d827f7cca1a2','files':rows,'excluded':'Engine/product source, C++headers, kernel, binaries, WHL, unselected documentation'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'PASS','unique_text_witnesses':len(rows),'referenced_capability_rows':len({v['capability_id']for r in rows for v in r['logical_sources']}),'bytes':sum(r['bytes']for r in rows)}))
if __name__=='__main__':main()
