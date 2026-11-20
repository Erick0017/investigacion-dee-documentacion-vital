"""Root's bounded package privacy screening and explicit plan approval; no DEE."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, zipfile

P=Path(__file__).resolve().parents[1]
f=P/'codigo/PLAN_ENTREGA_PI09_FINAL.json'
v=json.loads(f.read_text('utf-8-sig'))
assert v['status']=='DRAFT_EXPANDED_ACTUAL_BYTES_NOT_CLOSED'
patterns=[rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'(?:AKIA|ASIA)[A-Z0-9]{16}',rb'ghp_[A-Za-z0-9]{36}',rb'ya29\.[A-Za-z0-9_-]{35,}',rb'sk-(?:proj-)?[A-Za-z0-9_-]{30,}']
hits=[];n=0
for item in v['members']:
    p=Path(item['source']);data=p.read_bytes()
    assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
    assert p.suffix.lower() not in ('.sqlite3','.whl','.pyd','.exe','.zip')
    chunks=[data]
    if p.suffix.lower()=='.docx':
        with zipfile.ZipFile(p) as z:chunks=[z.read(s) for s in z.namelist() if s.endswith('.xml')]
    for expression in patterns:
        if any(re.search(expression,b) for b in chunks):hits.append({'file':item['file'],'pattern':expression.decode('ascii')})
    n+=1
assert not hits, 'Credential-pattern candidate requires Root review (values never printed): '+repr(hits)
backup=P/'control/PLAN_ANTES_SELLO_ROOT_PI09_R01.json'
assert not backup.exists();backup.write_bytes(f.read_bytes())
v.update(status='CLOSED_ACTUAL_FILES_READY_TO_PACKAGE',privacy_review='ROOT_APPROVED_LOCAL_ANALYSIS_SELECTION',visual_QA_status='NOT_VALIDATED_WITH_ACTUAL_LIMITATION')
v['Root_review']={'at_utc':datetime.now(timezone.utc).isoformat(),'content_members_reviewed':n,'strong_credential_pattern_candidates':0,
 'scope':'Explicit DEE scientific sources, necessary local paths and full official Cognitive documents. Strong-key pattern screening is limited, not a universal privacy certification. No external publication or upload.',
 'originals_or_world_states_modified':False,'prior_plan_sha256':hashlib.sha256(backup.read_bytes()).hexdigest()}
f.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'plan':str(f),'members':n,'privacy_review':v['privacy_review'],'status':v['status'],'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}))
