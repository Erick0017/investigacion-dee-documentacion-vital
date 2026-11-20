"""Index prospective records without feeding the index back into an entity."""
import argparse,json
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();root=Path(a.root).resolve();out=[]
    sources=[]
    sources+=list((root/'experimentos/continuidad/casos').glob('*.jsonl'))
    for rel in ['DIALOGOS.native.jsonl','experimentos/comunicacion/DIALOGOS_COMPARACION.native.jsonl']:
        if (root/rel).exists():sources.append(root/rel)
    for source in sorted(sources):
        for line_index,line in enumerate(source.read_text(encoding='utf-8').splitlines(),1):
            if not line.strip():continue
            value=json.loads(line)
            if value.get('kind') not in ('EMISSION','EVALUATION'):continue
            out.append({'source':source.relative_to(root).as_posix(),'source_line':line_index,'case':source.stem,'record':value,'index_role':'AUDITOR_ONLY_NOT_AN_ADDITIONAL_TRIAL'})
    (root/'PREDICCIONES.jsonl').write_text(''.join(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n' for row in out),encoding='utf-8')
    summary={'records':len(out),'emissions':sum(x['record']['kind']=='EMISSION' for x in out),'evaluations':sum(x['record']['kind']=='EVALUATION' for x in out),'sources':[s.relative_to(root).as_posix() for s in sources],'deduplication':'One source record per index row. Dialogues are presentation/protocol demonstrations, not added to independent scientific cases. No index is read by predictor.'}
    (root/'resultados/PREDICTION_INDEX.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary))

if __name__=='__main__':main()
