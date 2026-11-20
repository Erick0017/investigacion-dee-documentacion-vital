"""Passive exact comparison; preserves all result and event originals."""
from pathlib import Path
import hashlib
import json

ANALISIS=Path(__file__).resolve().parent
R07=ANALISIS.parent
OUT=ANALISIS/'RECALCULO_MAIN6_R01'
facts=json.loads((OUT/'HECHOS_CIERRE8_R07.json').read_text('utf-8'))
spec=json.loads((ANALISIS/'RECALCULO_MAIN6_INPUTS_R02.json').read_text('utf-8'))
block=spec['arms'][0]['blocks'][0]
result_path=Path(block['result'])
result=json.loads(result_path.read_text('utf-8'))
event_rows={}
for source in block['event_fragments']:
    for n,line in enumerate(Path(source).read_text('utf-8').splitlines(),1):
        if not line.strip():continue
        e=json.loads(line)
        if e.get('kind')=='OPPORTUNITY_COMPLETED':event_rows[e['cycle']]=(e,source,n)
rows=[]
for raw in result['rows']:
    c=raw['cycle'];event,source,line=event_rows[c]
    norm_event={k:v for k,v in event.items()if k not in('utc','kind')}
    norm_result={k:v for k,v in raw.items()if k not in('utc','kind')}
    differences=[k for k in set(raw)|set(norm_event)if raw.get(k)!=norm_event.get(k)or(k in raw)!=(k in norm_event)]
    equal=norm_result==norm_event
    assert equal,'Scientific/source field discrepancy for cycle '+str(c)
    assert all(k in('utc','kind')for k in differences)
    rows.append({'cycle':c,'original_event_source':source,'event_line':line,
        'combined_result_pointer':'/rows/'+str(result['rows'].index(raw)),
        'all_different_top_level_fields':sorted(differences),
        'all_scientific_and_source_fields_equal':equal,
        'original_decorators_preserved_in_combined_row':{k:raw[k]for k in('utc','kind')if k in raw}})
proof={'schema':'DEE.R07.MAIN6.ResultEventDecorators.R01','rows':rows,
    'explanation':'The five R02 notes compare undecorated events with original event objects copied literally into RESULTADO rows. Their only differing keys are kind and utc; no scientific field or source ID was discarded.',
    'original_files_modified':False,'Native_calls':0,'MCP_calls':0,'model_calls':0}
out=OUT/'CONTRASTE_FILAS_KIND_UTC_R01.json'
assert not out.exists();out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
members=[]
for row in facts['sources']:
    source=Path(row['source'])
    archive=str(source.relative_to(R07)).replace('\\','/')if source.is_relative_to(R07)else'ANTECEDENTES/R06_WORLD_PAR28.json'
    assert hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256']
    members.append({'source':str(source),'archive':archive,'sha256':row['sha256'],'bytes':row['bytes']})
mapping={'schema':'DEE.R07.MAIN6.RequiredPortableAliases.R02','members':members,
    'recalculator':'analisis/RECALCULO_CIERRE8_R07_R02.py','inputs':'analisis/RECALCULO_MAIN6_INPUTS_R02.json',
    'limitation':'Mapping only; package assembly must copy these exact bytes and verify its own content manifest. No original D path is opened when --package-root is used.'}
mp=OUT/'MAPA_PORTABLE_MIEMBROS_R02.json'
assert not mp.exists();mp.write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'scientific_fields_equal':len(rows),'decorators_only':[r['cycle']for r in rows if r['all_different_top_level_fields']],
    'proof_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'portable_sources':len(members)},ensure_ascii=False))
