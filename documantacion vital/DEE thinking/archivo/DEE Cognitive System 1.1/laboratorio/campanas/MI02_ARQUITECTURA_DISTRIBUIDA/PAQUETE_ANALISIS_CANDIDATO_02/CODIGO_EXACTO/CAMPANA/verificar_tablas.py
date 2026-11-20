"""Read-only CSV comparison with the typed matrices authored by Artifact Tool."""
import csv,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];data=json.loads((root/'RECALCULO/TABLAS_DATOS_MI02.json').read_bytes());result=[]
def text(v):
    if v is None:return''
    if v is True:return'true'
    if v is False:return'false'
    return str(v)
for t in data['tables']:
    with(root/t['filename']).open('r',encoding='utf-8-sig',newline='')as f:actual=list(csv.reader(f))
    expected=[[text(v)for v in r]for r in[t['headers'],*t['rows']]]
    if actual!=expected:raise AssertionError('CSV/matrix mismatch '+t['filename'])
    result.append({'file':t['filename'],'rows':len(actual)-1,'columns':len(actual[0]),'all_cells_match':True})
sys.stdout.reconfigure(encoding='utf8');print(json.dumps({'tables':result,'native_ticks':0},ensure_ascii=False))
