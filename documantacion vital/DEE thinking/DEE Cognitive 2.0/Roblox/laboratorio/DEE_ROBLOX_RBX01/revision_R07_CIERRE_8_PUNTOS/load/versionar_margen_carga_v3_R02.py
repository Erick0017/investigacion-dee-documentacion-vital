"""Prospective admin timing only, before the first R07 LOAD episode."""
from pathlib import Path
import ast,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'load/PROTOCOLO_CARGA_V3_R01.json';v=json.loads(p.read_text('utf8'))
v.update(schema='DEE.R07.three_owner_focal_load.R02',latest_batch_start_epoch=1794856500,latest_GO_epoch=1794857100,
  prospective_revision_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
  revision_reason='Actual first Main material block was only scheduled18:00UTC after transport/infrastructure preparation. The old18:00load-start guard is obsolete. No R07 LOAD episode has been executed by this tool.',
  timing_basis={'R06_one_owner_three_episodes_seconds':451.31,'R06_two_owner_overlap_three_episodes_each_seconds':899.0204358100891,
    'estimate_three_owner_three_episodes_each_seconds':1348.5306537151336,'allowance_before20UTC_after_latest_GO_seconds':2100,
    'latest_batch_start_utc':'2026-11-16T19:15:00Z','latest_GO_utc':'2026-11-16T19:25:00Z',
    'last_new_episode_utc':'2026-11-16T20:00:00Z','hard_finish_utc':'2026-11-16T21:07:00Z'})
need=lambda x:None if x else (_ for _ in()).throw(ValueError('Prospective scope mismatch'))
need(v['last_new_episode_epoch']==1794859200 and v['hard_finish_epoch']==1794863220 and v['episodes_per_life']==3 and v['global_tick_limit']==160000)
out=ROOT/'load/PROTOCOLO_CARGA_V3_R02.json'
with out.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2)
rows=[]
for source,target in(('worker_carga_v3.py','worker_carga_v3_R02.py'),('ejecutar_carga3_v3.py','ejecutar_carga3_v3_R02.py')):
    text=(ROOT/'load'/source).read_text('utf8').replace('PROTOCOLO_CARGA_V3_R01.json','PROTOCOLO_CARGA_V3_R02.json')
    if source.startswith('ejecutar'):
        text=text.replace('worker_carga_v3.py','worker_carga_v3_R02.py').replace('before18:00UTC','before19:15UTC')
    ast.parse(text);q=ROOT/'load'/target
    with q.open('x',encoding='utf8')as f:f.write(text)
    rows.append({'file':str(q.relative_to(ROOT)),'bytes':q.stat().st_size,'sha256':hashlib.sha256(q.read_bytes()).hexdigest()})
proof={'Native_calls':0,'MCP_calls':0,'R01_sources_preserved':True,'changes':'Only prospective batch-start/GO margins and explicit new filenames; Native scopes/bundles/quotas/owner limits unchanged.',
  'protocol_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'files':rows}
with(ROOT/'load/MARGEN_CARGA_V3_R02.json').open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
print(json.dumps(proof,ensure_ascii=False))
