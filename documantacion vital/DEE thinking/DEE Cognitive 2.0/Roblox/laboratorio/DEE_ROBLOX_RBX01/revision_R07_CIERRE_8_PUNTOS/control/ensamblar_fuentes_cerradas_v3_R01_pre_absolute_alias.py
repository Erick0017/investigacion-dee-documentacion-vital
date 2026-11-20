"""Merge explicitly pinned CLOSED campaign sources into a tentative R07 plan.

This is a file-only selector, not a Native run, experimental validation or ZIP
builder. No database, subprocess, DEE import, Studio or model API is used.
In an extracted package --package-root permits verification only.
"""
from pathlib import Path, PurePosixPath
import argparse, copy, datetime, hashlib, json, os, re

HERE=Path(__file__).resolve().parent.parent
MAX_FILE=8_000_000
MAX_FILES=750
FAMILIES={'MAIN','CTRL','PROGRAMMED','CONVENTIONAL_AI','LOAD','PILOT','P06','LEASE'}
SUFFIXES={'.json','.jsonl','.py','.luau','.rbxlx','.rbxmx','.txt','.md','.csv','.jpg','.png','.mp4'}
DENIED={'estado','site-packages','.git','.aws','credentials','cookies','secrets','motor'}
SHA=re.compile(r'^[a-f0-9]{64}$')

def ensure(value,message):
    if not value: raise ValueError(message)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def canon_source(value):
    return str(value).replace('\\','/').casefold()

def archive_name(value):
    ensure(isinstance(value,str) and '\\' not in value and ':' not in value,'UNSAFE_ARCHIVE')
    p=PurePosixPath(value)
    ensure(not p.is_absolute() and all(x not in ('','.','..') for x in p.parts),'UNSAFE_ARCHIVE')
    return p.as_posix()

def no_links(value):
    p=Path(value).absolute()
    for q in (p,*p.parents):
        if q.exists():
            ensure(not q.is_symlink() and not(getattr(q.lstat(),'st_file_attributes',0)&1024),'LINKED_SOURCE')
    return p.resolve(strict=True)

def stable_read(path,limit=MAX_FILE):
    p=no_links(path)
    a=p.stat()
    ensure(p.is_file() and a.st_size<=limit,'FILE_SIZE_OR_TYPE')
    raw=p.read_bytes()
    b=p.stat()
    ensure((a.st_size,a.st_mtime_ns,a.st_ino)==(b.st_size,b.st_mtime_ns,b.st_ino) and len(raw)==a.st_size,'SOURCE_CHANGED_DURING_READ')
    return raw

def parse_json(raw):
    def pairs(items):
        result={}
        for k,v in items:
            ensure(k not in result,'DUPLICATE_JSON_KEY')
            result[k]=v
        return result
    def finite(value): raise ValueError('NONFINITE_JSON')
    return json.loads(raw.decode('utf-8-sig'),object_pairs_hook=pairs,parse_constant=finite)

def pointer(obj,path):
    ensure(isinstance(path,str) and path.startswith('/'),'EXPLICIT_JSON_POINTER_REQUIRED')
    for item in path[1:].split('/'):
        item=item.replace('~1','/').replace('~0','~')
        obj=obj[int(item)] if isinstance(obj,list) else obj[item]
    return obj

class Sources:
    def __init__(self,root,package_root=None):
        self.root=no_links(root)
        self.package=no_links(package_root) if package_root else None
        self.observed={}
        self.members=[]
        if self.package:
            self.manifest=parse_json(stable_read(self.package/'CONTROL/MANIFIESTO_SHA256.json'))
            self.members=self.manifest['files']
    def local_path(self,source,archive=None):
        if self.package:
            candidates=[m for m in self.members if archive and m.get('archive')==archive]
            if not candidates:
                key=canon_source(source)
                candidates=[m for m in self.members if canon_source(m.get('source',''))==key]
            ensure(len(candidates)==1,'PORTABLE_SOURCE_NOT_UNIQUE_OR_NOT_TRANSPORTED')
            return no_links(self.package/archive_name(candidates[0]['archive']))
        p=Path(source)
        p=no_links(p if p.is_absolute() else self.root/p)
        roots=(self.root,self.root.parent/'revision_R05_C02',self.root.parent/'revision_R06_INTEGRAL_V2')
        ensure(any(p.is_relative_to(q) for q in roots),'SOURCE_OUTSIDE_CAMPAIGN_ROOTS')
        ensure(p.suffix.lower() in SUFFIXES and not any(x.casefold() in DENIED for x in p.parts),'EXCLUDED_SOURCE')
        return p
    def read(self,row):
        ensure(isinstance(row.get('source'),str),'EXPLICIT_SOURCE_REQUIRED')
        name=archive_name(row.get('archive',row['source']))
        expected=row.get('sha256')
        ensure(isinstance(expected,str) and SHA.fullmatch(expected),'PINNED_SHA256_REQUIRED')
        ensure(type(row.get('bytes')) is int and 0<=row['bytes']<=MAX_FILE,'PINNED_FINITE_BYTES_REQUIRED')
        p=self.local_path(row['source'],name)
        raw=stable_read(p)
        ensure(len(raw)==row['bytes'] and digest(raw)==expected,'SOURCE_DIFFERS_FROM_PIN')
        self.observed[row['source']]={'archive':name,'bytes':len(raw),'sha256':expected}
        return raw

def verify_basis(group,sources):
    basis=group['basis']
    raw=sources.read(basis)
    obj=parse_json(raw)
    assertions=basis.get('assertions',[])
    ensure(isinstance(assertions,list) and assertions,'EXPLICIT_CLOSURE_ASSERTIONS_REQUIRED')
    for claim in assertions:
        actual=pointer(obj,claim['pointer'])
        expected=claim['equals']
        ensure(type(actual) is type(expected) and actual==expected,'CLOSURE_ASSERTION_FAILED:'+claim['pointer'])
    kind=basis.get('proof_kind')
    if kind=='OWNER_CLOSED':
        ensure(pointer(obj,'/owner_closed') is True,'OWNER_NOT_CLOSED')
    elif kind=='FINITE_BENCHMARK_EXIT':
        ensure(pointer(obj,'/launcher/exit_code')==0 and pointer(obj,'/failure') is None,'BENCHMARK_NOT_CLOSED')
        ensure(pointer(obj,'/service_loop_started') is False and pointer(obj,'/queue_writer_created') is False,'BENCHMARK_NOT_PASSIVE')
    elif kind=='ADMINISTRATIVE_COMPLETE':
        ensure(pointer(obj,'/status')=='CLOSED_LEASE_RENEWAL_COMPLETE','ADMINISTRATION_NOT_COMPLETE')
        ensure(pointer(obj,'/new_native_ticks')==0,'ADMINISTRATION_HAS_MATERIAL_TICKS')
    elif kind=='EXPLICIT_ROOT_CLOSED_CONTRACT':
        ensure(group.get('root_reviewed_closure_contract') is True,'ROOT_CLOSURE_REVIEW_REQUIRED')
        ensure(any(c['pointer'].split('/')[-1] in ('status','closed','all_closed','owner_closed','workers_closed') for c in assertions),'NO_CLOSURE_FIELD_ASSERTED')
    else:
        raise ValueError('UNKNOWN_CLOSURE_PROOF_KIND')
    return {'proof_kind':kind,'source':basis['source'],'sha256':basis['sha256'],'assertions':assertions}

def assemble(plan,registry,sources):
    ensure(plan.get('finalized') is False,'TENTATIVE_PLAN_REQUIRED')
    ensure(registry.get('schema')=='DEE.R07.ClosedSourceRegistry.R01','REGISTRY_SCHEMA')
    groups=registry.get('groups')
    ensure(isinstance(groups,list) and 1<=len(groups)<=32,'FINITE_EXPLICIT_GROUPS')
    out=copy.deepcopy(plan)
    existing={archive_name(r['archive']).casefold():r for r in out['files']}
    summaries=[]
    for group in groups:
        ensure(group.get('family') in FAMILIES and isinstance(group.get('label'),str),'FAMILY_OR_LABEL')
        status=group.get('status')
        if status=='PENDING':
            summaries.append({'family':group['family'],'label':group['label'],'status':'PENDING','reason':group.get('reason','No closed source supplied')})
            continue
        ensure(status=='CLOSED','GROUP_STATUS_MUST_BE_EXPLICIT')
        files=group.get('files')
        ensure(isinstance(files,list) and 1<=len(files)<=100,'FINITE_EXPLICIT_FILE_LIST')
        ensure(any(f.get('source')==group['basis'].get('source') for f in files),'BASIS_MUST_BE_SELECTED')
        proof=verify_basis(group,sources)
        added=0
        for row in files:
            name=archive_name(row['archive'])
            sources.read(row)
            ensure(isinstance(row.get('role'),str) and row['role'],'ROLE_REQUIRED')
            limit=row.get('max_bytes',2_000_000)
            ensure(type(limit) is int and row['bytes']<=limit<=MAX_FILE,'MEMBER_BOUND')
            if limit>2_000_000:
                ensure(row['role'] in ('native_primary','native_control_primary'),'LARGE_PRIMARY_ROLE_REQUIRED')
            old=existing.get(name.casefold())
            if old:
                old_path=sources.local_path(old['source'],old['archive'])
                new_path=sources.local_path(row['source'],name)
                ensure(old_path==new_path and old['archive']==name,'ARCHIVE_COLLISION')
                continue
            item={k:row[k] for k in ('source','archive','role','bytes','sha256')}
            if limit>2_000_000:item['max_bytes']=limit
            out['files'].append(item);existing[name.casefold()]=item;added+=1
        summaries.append({'family':group['family'],'label':group['label'],'status':'CLOSED_SOURCE_VERIFIED_NOT_EXPERIMENTALLY_REPRODUCED','proof':proof,'selected_files':len(files),'added_files':added})
    ensure(len(out['files'])<=MAX_FILES,'TOO_MANY_SELECTED_FILES')
    ensure(sum(r.get('max_bytes',2_000_000)>2_000_000 for r in out['files'])<=4,'TOO_MANY_LARGE_EXCEPTIONS')
    out['finalized']=False
    out['closed_source_assembly']={'schema':'DEE.R07.ClosedSourceSelection.R01','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'groups':summaries,'file_only':True,'Native_calls':0,'DB_opened':False,'ZIP_created':False,'scientific_or_operational_approval':False,'portable_verification':bool(sources.package)}
    return out

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--registry',type=Path,required=True)
    p.add_argument('--output',type=Path)
    p.add_argument('--workspace-root',type=Path,default=HERE)
    p.add_argument('--package-root',type=Path)
    p.add_argument('--verify-only',action='store_true')
    a=p.parse_args(argv)
    ensure(a.verify_only or a.output is not None,'FRESH_OUTPUT_REQUIRED')
    ensure(not a.package_root or a.verify_only,'PACKAGE_MODE_VERIFIES_ONLY')
    root=no_links(a.workspace_root)
    plan_raw=stable_read(a.plan);registry_raw=stable_read(a.registry)
    src=Sources(root,a.package_root)
    result=assemble(parse_json(plan_raw),parse_json(registry_raw),src)
    result['closed_source_assembly'].update(plan_before_sha256=digest(plan_raw),registry_sha256=digest(registry_raw),selector_sha256=digest(stable_read(__file__)))
    if not a.verify_only:
        dest=a.output.absolute()
        ensure(dest.parent.resolve().is_relative_to(root/'control'),'OUTPUT_MUST_STAY_IN_CAMPAIGN_CONTROL')
        ensure(dest.suffix.lower()=='.json' and not dest.exists(),'FRESH_JSON_OUTPUT_REQUIRED')
        no_links(dest.parent)
        with dest.open('x',encoding='utf-8',newline='\n') as f:
            json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'status':'CLOSED_SOURCE_SELECTION_CHECKED','verify_only':a.verify_only,'selected_files':len(result['files']),'groups':result['closed_source_assembly']['groups'],'finalized':False,'output':str(a.output) if a.output and not a.verify_only else None,'Native_calls':0,'DB_opened':False,'ZIP_created':False},ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
