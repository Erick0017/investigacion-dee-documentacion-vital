"""Incremental finite privacy review of an explicit closed-file plan. No secret values emitted."""
from __future__ import annotations
import argparse, datetime, hashlib, importlib.util, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CACHE_SHA256='1995ad8cec29cec7a324616457579cec11b33d618f06010fa55dd45d143763ca'
STRONG_NAMES={'id_ed25519','id_rsa','.env','credentials.json','creds.json','cookies.json','login.json'}
KEYS={'password','passwd','access_token','refresh_token','authorization','cookie','set-cookie','api_key','apikey','client_secret','private_key','.roblosecurity','roblosecurity'}
PATTERNS=[('PRIVATE_KEY_PEM_MARKER',re.compile(r'-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----')),
 ('BEARER_LITERAL',re.compile(r'(?i)\bBearer\s+[A-Za-z0-9._~+/-]{16,}')),
 ('ROBLOX_COOKIE_LITERAL',re.compile(r'''(?i)\.ROBLOSECURITY\s*[:=]\s*["']?[^\s"']{24,}''')),
 ('EMAIL_LIKE_PERSONAL_DATA',re.compile(r'(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'))]
def digest(raw):return hashlib.sha256(raw).hexdigest()
def candidate(source,archive,kind,locator):
    return {'source':source,'archive':archive,'kind':kind,'locator':locator,'value_in_report':False,'candidate_not_automatic_secret_determination':True}
def scan_text(data,source,archive):
    findings=[];limited=[]
    try:text=data.decode('utf-8-sig')
    except UnicodeDecodeError:return [],[{'source':source,'archive':archive,'reason':'Binary image/media; no visual or text privacy review claimed'}]
    def visit(value,where=''):
        if isinstance(value,dict):
            for key,item in value.items():
                pointer=where+'/'+str(key).replace('~','~0').replace('/','~1')
                if str(key).lower()in KEYS and isinstance(item,str)and item.strip():findings.append(candidate(source,archive,'NONEMPTY_SENSITIVE_KEY:'+str(key),pointer))
                visit(item,pointer)
        elif isinstance(value,list):
            for i,item in enumerate(value):visit(item,where+'/'+str(i))
    suffix=Path(archive).suffix.lower()
    if suffix=='.json':
        try:visit(json.loads(text))
        except json.JSONDecodeError:limited.append({'source':source,'archive':archive,'reason':'Not valid complete JSON for structured-key pass'})
    elif suffix=='.jsonl':
        for n,line in enumerate(text.splitlines(),1):
            if not line.strip():continue
            try:visit(json.loads(line),'line'+str(n))
            except json.JSONDecodeError:limited.append({'source':source,'archive':archive,'reason':'Incomplete/nonJSON row','line':n})
    for n,line in enumerate(text.splitlines(),1):
        for kind,pattern in PATTERNS:
            if pattern.search(line):findings.append(candidate(source,archive,kind,'line'+str(n)))
    return findings,limited

def review_member(data,source,archive,cache):
    h=digest(data);same=any(r.get('source')==source and r.get('sha256')==h and r.get('bytes')==len(data) for r in cache.get('coverage',[]))
    if same:
        findings=[dict(x,archive=archive)for x in cache.get('findings',[])if x.get('source')==source]
        limited=[dict(x,archive=archive)for x in cache.get('skipped_or_limited',[])if x.get('source')==source]
    else:findings,limited=scan_text(data,source,archive)
    return {'source':source,'archive':archive,'bytes':len(data),'sha256':h,'review':'REUSED_EXACT_CACHED_SHA'if same else'NEW_OR_CHANGED_BYTES_REVIEWED'},findings,limited

def run(a):
    spec=importlib.util.spec_from_file_location('passive_packager_R03',ROOT/'control/expediente_compacto_v3_R03.py')
    p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
    cache_raw=p.stable_read(p.no_links(a.cache),8_000_000)
    if digest(cache_raw)!=a.cache_sha256:raise ValueError('CACHE_PROOF_PIN_MISMATCH')
    cache=json.loads(cache_raw);plan_raw=p.stable_read(p.no_links(a.plan),80_000_000);plan=p.read_plan(a.plan)
    output=a.output.resolve()
    if not output.is_relative_to(ROOT)or output.exists()or not output.parent.is_dir():raise ValueError('FRESH_OUTPUT_INSIDE_R07_REQUIRED')
    coverage=[];findings=[];limited=[];reused=0
    for row in plan['files']:
        source=row['_path'];archive=row['archive'];text_source=str(source)
        if source.name.lower()in STRONG_NAMES or source.suffix.lower()in('.pem','.pfx','.p12','.key'):
            findings.append(candidate(text_source,archive,'SENSITIVE_FILENAME_NOT_OPENED','filename'))
            limited.append({'source':text_source,'archive':archive,'reason':'Potential secret file; contents not read'});continue
        raw=p.stable_read(source,row['_limit'])
        if digest(raw)!=row.get('sha256')or len(raw)!=row.get('bytes'):raise ValueError('SELECTED_SOURCE_DIFFERS_FROM_PLAN: '+archive)
        rec,found,limits=review_member(raw,text_source,archive,cache);coverage.append(rec);findings.extend(found);limited.extend(limits)
        reused+=int(rec['review']=='REUSED_EXACT_CACHED_SHA')
    by_source={r['source']:r for r in coverage}
    for row in plan['files']:
        rec=by_source.get(str(row['_path']))
        if rec and digest(p.stable_read(row['_path'],row['_limit']))!=rec['sha256']:
            raise ValueError('SELECTED_SOURCE_CHANGED_DURING_REVIEW: '+row['archive'])
    if p.stable_read(a.plan,80_000_000)!=plan_raw or p.stable_read(a.cache,8_000_000)!=cache_raw:raise ValueError('PLAN_OR_PRIOR_PROOF_CHANGED_DURING_REVIEW')
    report={'schema':'DEE.R07.SelectedPackagePrivacy.incremental.R08','inspection_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'plan':str(a.plan),'plan_sha256':digest(plan_raw),'plan_finalized':plan.get('finalized'),
      'cache_proof':str(a.cache),'cache_proof_sha256':digest(cache_raw),'prior_proof_preserved':True,
      'selected_members':len(plan['files']),'read_and_hashed_members':len(coverage),'exact_cached_members_not_rescanned':reused,
      'new_or_changed_members_reviewed':len(coverage)-reused,'coverage':coverage,'findings':findings,'skipped_or_limited':limited,
      'values_or_credentials_printed':False,'originals_modified':False,'Native_MCP_Studio_model_SQLite_calls':0,
      'limits':['Heuristics only for exact selected bytes; candidates require context judgment.',
        'Every current selected member is hash-checked; structured/regex scanning is reused only for same source and SHA/bytes.',
        'Cached binary limitations are retained; new screenshots/video still require separate visual privacy review.',
        'Changes after this cut require another extension. No whole-project or future-ZIP privacy certification.']}
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(output),'sha256':digest(output.read_bytes()),'members':len(coverage),'reused':reused,
      'new_changed':len(coverage)-reused,'candidate_count':len(findings),'limited':len(limited),'Native_calls':0},ensure_ascii=False))
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--plan',type=Path,required=True)
    ap.add_argument('--cache',type=Path,default=ROOT/'analisis/REVISION_PRIVACIDAD_PLAN_R03.json');ap.add_argument('--cache-sha256',default=CACHE_SHA256)
    ap.add_argument('--output',type=Path,required=True);run(ap.parse_args())
