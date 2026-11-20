"""Select current closed evidence for the one PI02 ZIP; never deletes staging.

Re-run after the Manual/E_FINAL/final records are complete. Only exact,
hash-verified duplicates named in the ABC selection are omitted. New files
are included by default; no prefix-based exclusion hides later unique data.
This list is not the self-referential ZIP/content manifest.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,stat

def sha(b):return hashlib.sha256(b).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,required=True);ap.add_argument('--abc',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    root=args.root.resolve();abc=json.loads(args.abc.read_text(encoding='utf-8-sig'));excluded={x['file']:x for x in abc['ZIP_only_exact_exclusions']};rows=[];omissions=[]
    for rel,item in excluded.items():
        file=root/rel;b=file.read_bytes()
        if len(b)!=item['bytes']or sha(b)!=item['sha256']:raise ValueError('Omission no longer equals the verified duplicate: '+rel)
    for file in sorted(root.rglob('*')):
        info=file.lstat()
        if stat.S_ISLNK(info.st_mode)or getattr(info,'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0):raise ValueError('No linked evidence roots allowed: '+str(file))
        if not file.is_file():continue
        resolved=file.resolve()
        if os.path.commonpath([str(root),str(resolved)])!=str(root):raise ValueError('Evidence escaped selected root')
        rel=file.relative_to(root).as_posix();b=file.read_bytes();after=file.stat()
        if info.st_size!=after.st_size or info.st_mtime_ns!=after.st_mtime_ns:raise ValueError('Evidence changed during selection: '+rel)
        entry={'file':rel,'bytes':len(b),'sha256':sha(b)}
        if rel in excluded:omissions.append({**entry,'canonical_equivalent':excluded[rel]['canonical_equivalent'],'reason':excluded[rel]['equivalence'],'ZIP_only':True,'local_file_preserved':True})
        else:rows.append(entry)
    index={'schema':'PI02.current_canonical_export_selection.v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'root':str(root),'inclusions':rows,'omissions':omissions,'selected_file_count':len(rows),'selected_uncompressed_bytes':sum(x['bytes']for x in rows),
           'omitted_uncompressed_bytes':sum(x['bytes']for x in omissions),'new_ticks':0,'DEE_imports':0,'staging_files_deleted':0,
           'source_ABC_selection':{'path':str(args.abc),'sha256':sha(args.abc.read_bytes())},
           'scope':'Exact current snapshot of delivery members. Re-run after all final file writes; this does not certify the not-yet-created ZIP nor replace its final manifest.',
           'manual_candidates':[x['file']for x in rows if x['file'].lower().endswith('.docx')],
           'required_after_selection':['Generate/verify the final content manifest without self hashes','Create one Deflate ZIP <=15000000bytes','Extract cleanly and run RECALCULO_TODO from exported files only']}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:index[k]for k in('selected_file_count','selected_uncompressed_bytes','omitted_uncompressed_bytes','manual_candidates','staging_files_deleted')},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
