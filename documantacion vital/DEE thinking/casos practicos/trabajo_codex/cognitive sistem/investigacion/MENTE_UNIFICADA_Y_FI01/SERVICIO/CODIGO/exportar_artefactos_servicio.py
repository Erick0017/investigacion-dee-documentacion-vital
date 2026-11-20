"""Copy only actual bounded worker bytes referenced by the R04 receipts."""
import argparse,gzip,hashlib,json,shutil
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--primario',type=Path,required=True);a=p.parse_args()
    j=json.loads(gzip.decompress(a.primario.read_bytes()));source=a.sistema/'estado/servicios_locales/MU_MAIN';target=a.primario.parent/'artefactos';target.mkdir(exist_ok=True);rows=[]
    for key in('mu_a50_work1','mu_a50_work2'):
        receipt=json.loads(j['records'][key]['result'])['result']['rows'][0]['external']['worker_receipt'];matches=list(source.rglob(receipt['output_name']))
        if len(matches)!=1:raise ValueError('Worker output is missing or ambiguous; do not fabricate or regenerate it.')
        data=matches[0].read_bytes()
        if len(data)!=receipt['output_bytes']or hashlib.sha256(data).hexdigest()!=receipt['output_sha256']:raise ValueError('Actual worker bytes differ from original receipt')
        destination=target/receipt['output_name']
        if destination.exists()and destination.read_bytes()!=data:raise FileExistsError('Different archived artifact protected')
        if not destination.exists():shutil.copyfile(matches[0],destination)
        rows.append({'request_id':key,'original':str(matches[0]),'exported':'artefactos/'+destination.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'actual_file_read_now':True})
    output=a.primario.parent/'ARTEFACTOS_TRABAJADOR.json';output.write_text(json.dumps({'schema':'DEE.actual_worker_artifact_export.v1','rows':rows,'new_native_ticks':0,'no_worker_reexecuted':True},ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'files':len(rows),'bytes':sum(r['bytes']for r in rows),'new_native_ticks':0}))


if __name__=='__main__':main()
