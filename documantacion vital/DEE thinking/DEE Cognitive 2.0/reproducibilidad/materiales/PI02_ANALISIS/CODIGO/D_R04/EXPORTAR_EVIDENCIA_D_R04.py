"""Export exact closed R04 historical evidence; stdlib only, no DEE or ticks.

The historical journal prefix is fixed by the committed summary, even if the
same life subsequently continues. No live SQLite is inspected or copied.
"""
from pathlib import Path
import argparse,datetime,gzip,hashlib,json,runpy

def sha(b):return hashlib.sha256(b).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--campaign',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();p=a.campaign.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    verify=runpy.run_path(str(p/'codigo/RECALCULAR_HABITAT_R04.py'))['run']
    entries=[];arms=[]
    def write(data,dest,source,scope):
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.name=='RECALCULO.json.gz'and dest.exists():
            old=gzip.decompress(dest.read_bytes());old_json=json.loads(old);new_json=json.loads(data)
            old_json.pop('calculated_utc',None);new_json.pop('calculated_utc',None)
            if old_json!=new_json:raise ValueError('Portable recálculo content changed: '+str(dest))
            data=old # preserve the original calculation timestamp on reruns
        payload=gzip.compress(data,compresslevel=9,mtime=0)if dest.suffix=='.gz'else data
        if dest.exists()and dest.read_bytes()!=payload:raise ValueError('Immutable export differs: '+str(dest))
        dest.write_bytes(payload)
        entries.append({'file':dest.relative_to(out).as_posix(),'bytes':len(payload),'sha256':sha(payload),
                        'decoded_bytes':len(data),'decoded_sha256':sha(data),'source':str(source),'scope':scope})
    tags=['DEV_HAB','RES_MAIN','RES_UNPAIRED','RES_NO_TRAIN','RES_WARNING_CUT','RES_VALENCE_OMIT','RES_ACTUATOR_NULL']
    for tag in tags:
        sp=p/'ensayos'/('RESUMEN_PI02_R04_'+tag+'.json')
        if not sp.exists():raise ValueError('Not yet closed: '+str(sp))
        sb=sp.read_bytes();s=json.loads(sb.decode('utf-8-sig'));jp=Path(s['journal'])
        final=s['requests'][-1]['result']['result']['rows'][0]['habitat'];n=final['log_count']
        jb=b''.join(jp.read_bytes().splitlines(keepends=True)[:n])
        if sha(jb)!=s['journal_sha256']:raise ValueError('Historical journal identity: '+tag)
        dest=out/tag
        write(sb,dest/'summary.json.gz',sp,'Full original committed summary')
        write(jb,dest/'eventos.jsonl.gz',jp,'Exact committed historical prefix; '+str(n)+' events, not later continuation')
        for request in s['requests']:
            rp=p/'ensayos'/(request['id']+'.json')
            if rp.exists():write(rp.read_bytes(),dest/(request['id']+'.json.gz'),rp,'Full original Cognitive request/result primary')
        result=verify(dest/'eventos.jsonl.gz',dest/'summary.json.gz',jp.parent)
        if result['inconsistencies']:raise ValueError(tag+': '+str(result['inconsistencies']))
        for item in result['artifacts']:
            name=item['file']
            if Path(name).name!=name or ':'in name:raise ValueError('Unsafe artifact name')
            fp=jp.parent/item['folder']/name
            write(fp.read_bytes(),dest/item['folder']/name,fp,'Actual external 64-byte resource/control packet, not Native energy')
        # Recalculate from the portable export, including bytes of its artifacts.
        portable=verify(dest/'eventos.jsonl.gz',dest/'summary.json.gz',dest)
        if portable['inconsistencies']:raise ValueError(tag+' portable: '+str(portable['inconsistencies']))
        rb=(json.dumps(portable,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        write(rb,dest/'RECALCULO.json.gz','RECALCULAR_HABITAT_R04.py','Passive portable recálculo; no Native execution')
        arms.append({k:portable[k]for k in('life','series','history','arm','before_tick','after_tick','completed_opportunities','actual_work_frames','actual_resources','CLOSE_signatures','actual_device_commands','actual_applied_device_commands','device_cost_bytes','returns','Native_receipts_unique','Native_receipt_statuses','inconsistencies')})
    # Observation-control primaries are small; full Native states remain locally
    # identified unless separately selected for export by the campaign owner.
    for rel in ['control/COMPARACION_PUERTOS_OH_R04.json','ensayos/PI02_R04_OH_ON.json','ensayos/PI02_R04_OH_OFF.json']:
        src=p/rel
        write(src.read_bytes(),out/'OH_CONTROL'/(src.name+'.gz'),src,'Observation equivalence control, full original record')
    index={'schema':'PI02.R04.closed_evidence_export.v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'new_native_ticks':0,'DEE_imports':0,'arms':arms,'files':entries,
           'limits':['Historical Main reserve cut is T750137 even if its live life subsequently advances',
                     'Closed summaries select exact journal prefixes, not outcome-selected samples',
                     'This export is evidence and recálculo, not a Cognitive operational backup',
                     'Branches share a physical prefix; they are matched controls, not independent populations']}
    (out/'INDICE_D_R04.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'arms':arms,'exported_files':len(entries),'exported_bytes':sum(x['bytes']for x in entries),'decoded_bytes':sum(x['decoded_bytes']for x in entries),'index':str(out/'INDICE_D_R04.json')},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
