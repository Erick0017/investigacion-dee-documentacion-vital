"""Copy closed worker outputs only; no execution, training or original mutation."""
from pathlib import Path
import argparse,gzip,hashlib,json,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from recalcular_eo02 import native_rows

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--primarios',type=Path,required=True);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--destino',type=Path,required=True);p.add_argument('--indice',type=Path,required=True);a=p.parse_args()
    if a.indice.exists():raise FileExistsError('Prior export index protected')
    base=(a.sistema/'estado/servicios_locales').resolve();rows=[];issues=[]
    for primary in sorted(a.primarios.glob('*.json.gz')):
        if not re.match(r'^\d+[A-Za-z]*_',primary.name):continue
        with gzip.open(primary,'rt',encoding='utf8')as f:record=json.load(f)
        manager=record.get('result',{});life=manager.get('INSTRUMENTO',{}).get('life_id')
        if not life:continue
        for i,r in enumerate(native_rows(manager.get('result',{}))):
            local=r.get('local_service')
            if not local or not local.get('worker_receipt'):continue
            receipt=local['worker_receipt'];before=local['before'];epoch=before.get('storage_epoch',before['domain']);name=receipt['output_name']
            if Path(name).name!=name or Path(life).name!=life or Path(epoch).name!=epoch:raise ValueError('Unsafe artifact path')
            source=(base/life/epoch/name).resolve()
            if not source.is_relative_to(base):raise ValueError('Artifact outside declared local service')
            row={'primary':primary.name,'ordinal':i,'life':life,'worker_revision':receipt['schema'],'operation':receipt['operation'],
                'accepted':receipt['accepted'],'source':str(source),'expected_sha256':receipt['output_sha256'],'expected_bytes':receipt['output_bytes']}
            if not source.is_file():row['status']='SOURCE_NOT_FOUND';issues.append(row.copy())
            else:
                row.update(actual_sha256=digest(source),actual_bytes=source.stat().st_size)
                if row['actual_sha256']!=row['expected_sha256']or row['actual_bytes']!=row['expected_bytes']:
                    row['status']='SOURCE_DIFFERS';issues.append(row.copy())
                else:
                    target=a.destino/life/epoch/name;target.parent.mkdir(parents=True,exist_ok=True)
                    if target.exists()and target.read_bytes()!=source.read_bytes():raise FileExistsError('Conflicting prior artifact export')
                    if not target.exists():target.write_bytes(source.read_bytes())
                    row.update(status='BYTE_IDENTICAL_EXPORTED',export_member=target.relative_to(a.destino).as_posix())
            rows.append(row)
    result={'schema':'EO02.actual_worker_output_export.v1','files_referenced':len(rows),'issues':issues,'rows':rows,
        'new_DEE_ticks':0,'new_worker_executions':0,'scope':'Actual closed local output bytes matched against primary receipts, copied without modification. This is not a new transaction or policy test.'}
    a.indice.parent.mkdir(parents=True,exist_ok=True);a.indice.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'referenced':len(rows),'issues':issues,'index':str(a.indice)},ensure_ascii=False))
    return bool(issues)
if __name__=='__main__':raise SystemExit(main())
