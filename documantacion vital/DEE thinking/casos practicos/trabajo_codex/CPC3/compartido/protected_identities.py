"""Read-only identities of explicitly protected products/evidence around cleanup."""
import argparse,hashlib,json
from pathlib import Path
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--phase',choices=['before','after'],required=True);a=p.parse_args();root=Path(a.root).resolve();product=root.parents[2];vital=root.parents[3]
    targets=[product/'3.5/dee_thinking-3.5.0-cp313-cp313-win_amd64.whl',product/'archivo/DEE_thinking_3_5_0_ENTREGA_FINAL_RESULTADOS.zip',product/'archivo/DEE_thinking_3_0_0_ENTREGA_FINAL_RESULTADOS.zip',product/'3.0/dee_thinking-3.0.0-cp313-cp313-win_amd64.whl',product/'archivo/DEE_thinking_3_0_0_FRONTERAS_COGNITIVAS_MULTIRRAMA_01_RESULTADOS.zip',vital/'mente basal/MENTE_BASAL_4_ORGANIZACION_BASAL_PERSISTENTE_VALIDACION_RESULTADOS.zip']
    targets+=list((product/'3.5').glob('*.docx'))
    rows=[{'path':str(q),'bytes':q.stat().st_size,'sha256':digest(q)} for q in targets if q.is_file()]
    report={'phase':a.phase,'files':rows,'scope':'Only explicitly protected products and original evidence; no reorganization or content edit'}
    if a.phase=='after':
        before=json.loads((root/'resultados/PROTECTED_BEFORE.json').read_text(encoding='utf-8'))
        assert {x['path']:(x['bytes'],x['sha256']) for x in before['files']}=={x['path']:(x['bytes'],x['sha256']) for x in rows},'Protected original changed or missing'
        report['unchanged_from_before']=True
    path=root/('resultados/PROTECTED_'+a.phase.upper()+'.json');path.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'phase':a.phase,'files':len(rows),'unchanged_from_before':report.get('unchanged_from_before')}))
if __name__=='__main__':main()
