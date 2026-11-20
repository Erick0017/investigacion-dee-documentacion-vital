"""Passive finite selected-file review. Never emits potential secret values."""
from pathlib import Path
import datetime
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R03.json'
OUTPUT=ROOT/'analisis/REVISION_PRIVACIDAD_PLAN_R03.json'
raw_plan=PLAN.read_bytes();plan=json.loads(raw_plan)
items=plan['files'];records=[];findings=[];skipped=[]
strong_names={'id_ed25519','id_rsa','.env','credentials.json','creds.json','cookies.json','login.json'}
keys={'password','passwd','access_token','refresh_token','authorization','cookie','set-cookie',
      'api_key','apikey','client_secret','private_key','.roblosecurity','roblosecurity'}
patterns=[('PRIVATE_KEY_PEM_MARKER',re.compile(r'-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----')),
    ('BEARER_LITERAL',re.compile(r'(?i)\bBearer\s+[A-Za-z0-9._~+/-]{16,}')),
    ('ROBLOX_COOKIE_LITERAL',re.compile(r'(?i)\.ROBLOSECURITY\s*[:=]\s*[\"\']?[^\s\"\']{24,}')),
    ('EMAIL_LIKE_PERSONAL_DATA',re.compile(r'(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'))]
def digest(raw):return hashlib.sha256(raw).hexdigest()
def add(source,archive,kind,locator):
    findings.append({'source':str(source),'archive':archive,'kind':kind,'locator':locator,
        'value_in_report':False,'candidate_not_automatic_secret_determination':True})
def visit(value,source,archive,path=''):
    if isinstance(value,dict):
        for k,v in value.items():
            pointer=path+'/'+str(k).replace('~','~0').replace('/','~1')
            if str(k).lower()in keys and isinstance(v,str)and v.strip():
                add(source,archive,'NONEMPTY_SENSITIVE_KEY:'+str(k),pointer)
            visit(v,source,archive,pointer)
    elif isinstance(value,list):
        for i,v in enumerate(value):visit(v,source,archive,path+'/'+str(i))

for item in items:
    source=Path(item['source']);source=source if source.is_absolute()else ROOT/source
    # Only explicit project members; no search of user profiles or unrelated files.
    source=source.resolve(strict=True);archive=item['archive']
    assert source.is_relative_to(ROOT.parents[2]),'Selected member outside the DEE product'
    if source.name.lower()in strong_names or source.suffix.lower()in('.pem','.pfx','.p12','.key'):
        add(source,archive,'SENSITIVE_FILENAME_NOT_OPENED','filename')
        skipped.append({'source':str(source),'reason':'Potential secret file; contents not read'});continue
    if source.stat().st_size>20000000:
        skipped.append({'source':str(source),'reason':'Over finite20MB text-review bound'});continue
    data=source.read_bytes()
    records.append({'source':str(source),'archive':archive,'bytes':len(data),'sha256':digest(data)})
    try:text=data.decode('utf-8-sig')
    except UnicodeDecodeError:
        skipped.append({'source':str(source),'reason':'Binary image/media; no visual or text privacy review claimed'});continue
    if source.suffix.lower()=='.json':
        try:visit(json.loads(text),source,archive)
        except json.JSONDecodeError:skipped.append({'source':str(source),'reason':'Not valid complete JSON for structured-key pass'})
    elif source.suffix.lower()=='.jsonl':
        for line_no,line in enumerate(text.splitlines(),1):
            if not line.strip():continue
            try:visit(json.loads(line),source,archive,'line'+str(line_no))
            except json.JSONDecodeError:skipped.append({'source':str(source),'reason':'Incomplete/nonJSON row','line':line_no})
    for line_no,line in enumerate(text.splitlines(),1):
        for name,pattern in patterns:
            if pattern.search(line):add(source,archive,name,'line'+str(line_no))

assert PLAN.read_bytes()==raw_plan,'Plan changed during selected-file review'
for row in records:
    assert digest(Path(row['source']).read_bytes())==row['sha256'],'Selected source changed during review'
report={'schema':'DEE.R07.SelectedPackagePrivacy.R01','inspection_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'plan':str(PLAN),'plan_sha256':digest(raw_plan),'plan_finalized':plan.get('finalized'),
    'selected_members':len(items),'read_and_hashed_members':len(records),
    'findings':findings,'skipped_or_limited':skipped,'coverage':records,
    'values_or_credentials_printed':False,'originals_modified':False,'Native_MCP_model_calls':0,
    'limits':['Heuristic review of these exact selected bytes only, not a complete project secret audit.',
      'Sensitive key names or email-like text can be code/documentation declarations; candidates require source-context judgment.',
      'Binary screenshots/video have not been visually reviewed by this script.',
      'Any later new members require their own review; this is not certification of a future finalized ZIP.']}
assert not OUTPUT.exists()
OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'output':str(OUTPUT),'sha256':digest(OUTPUT.read_bytes()),'members':len(records),
    'candidate_count':len(findings),'candidates':[{'archive':r['archive'],'kind':r['kind'],'locator':r['locator']}for r in findings],
    'limited':len(skipped),'Native_MCP_model_calls':0},ensure_ascii=False))
