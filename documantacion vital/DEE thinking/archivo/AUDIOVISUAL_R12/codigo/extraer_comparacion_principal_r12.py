"""Read the already executed ECI02 comparison; never invokes the engine."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent/'analisis_transversal_cognitivo/ECI02/CONSOLIDACION_OPERATIVA'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    index=json.loads((BASE/'datos/PRIMARIOS_OUTBOX_CIERRE_R01.json').read_text(encoding='utf8'))
    item=next(r for r in index['rows']if r['label']=='FI_PLUS')
    path=Path(item['source'])
    if not path.is_file():path=BASE/item['member']
    assert sha(path)==item['sha256']
    d=json.loads(path.read_text(encoding='utf8'));row=d['result']['rows'][0]
    point=row['early_observation'];choice=row['early_physical_choice']
    assert point['tick']==row['early_tick'] and point['raw']!='0' and choice==1
    out=ROOT/'evidencia_reutilizada';copy=out/'FI_PLUS_PRIMARIO.json'
    if copy.exists():assert copy.read_bytes()==path.read_bytes()
    else:shutil.copy2(path,copy)
    data={'source':{'path':str(path),'sha256':sha(path),'pointer':'/result/rows/0'},
        'included_original':str(copy.relative_to(ROOT)),
        'N':67,'life':'ECI02_CIERRE_CANDIDATA_01','published_as':'ECI02_OPERATIVA_PRINCIPAL_01',
        'parent':'ECI02_CONSOLIDADA_OPERATIVA','query_tick':row['query_tick'],
        'tick':row['early_tick'],'point':point,'choice':choice,
        'input_receipts':row['all_material_receipts'],'reader_contract':row['version'],
        'old_q6_choice':row['old_q6_choice'],'NULL_is_not_zero':row['NULL_is_not_zero'],
        'initiative':row['initiative'],'scope':row['scope'],'new_DEE_ticks':0,
        'limitation':'Prepared comparison and explicit access; not a learned arithmetic algorithm or autonomous request.'}
    dest=out/'COMPARACION_PRINCIPAL_R12.json'
    if dest.exists():assert json.loads(dest.read_text(encoding='utf8'))==data
    else:dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'file':str(dest),'sha256':sha(dest),'query_tick':row['query_tick'],'read_tick':row['early_tick'],'choice':choice,'new_DEE_ticks':0}))
if __name__=='__main__':main()
