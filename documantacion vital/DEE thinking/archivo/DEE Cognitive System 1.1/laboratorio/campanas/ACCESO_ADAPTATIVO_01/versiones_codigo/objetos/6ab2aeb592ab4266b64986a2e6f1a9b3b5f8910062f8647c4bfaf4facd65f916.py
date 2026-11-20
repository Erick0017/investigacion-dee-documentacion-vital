"""Engine-free localization from existing sparse complete-field frames."""
from pathlib import Path
import argparse,json,gzip,hashlib
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();rows=[]
def unpack(v):
    v=int(v)
    def s(k):
        b=(v>>k)&15
        return b-16 if b&8 else b
    return{'state':v&0xffffffff,'s_reg':(v>>32)&65535,'direction':[s(k)for k in(48,52,56)],'semantic':(v>>60)&15}
for batch in('ACCESO_LOCAL_25','ACCESO_LOCAL_25_V2'):
    for source in sorted((a.evidence/batch).glob('*/PRIMARIOS.json.gz')):
        d=json.loads(gzip.decompress(source.read_bytes()));epoch=d['epoch'];n=d['pre']['N'];r=[];frames=source.parent/'CAMPOS_LOCALES.jsonl.gz'
        for line in gzip.open(frames,'rt',encoding='utf8'):
            f=json.loads(line);relative=f['tick']-epoch
            if not 161<=relative<=165:continue
            hits=[]
            for row in f['rows']:
                site=[row[0]//(n*n),(row[0]//n)%n,row[0]%n]
                if all(min((x-y)%n,(y-x)%n)<=4 for x,y in zip(site,[21,21,13])):hits.append({'site':site,'raw':row[1],'clock':row[2],**unpack(row[1])})
            r.append({'relative_tick':relative,'records_in_bounded_ROI':hits,'global_RAW_sha256':f['RAW_sha256'],'global_clocks_sha256':f['clocks_sha256']})
        acquired=[]
        for sample in d['samples']:
            if sample['relative_tick']==161:
                for key,row in sample['memories'].items():
                    q=unpack(row['raw']);qualified=q['state']==1 and q['semantic']==1 and q['direction'][0]==1 and abs(q['direction'][1])==abs(q['direction'][2])==1
                    acquired.append({'bank':key,'raw':row['raw'],'native_fields':q,'qualified_XYZ_access':qualified})
        rows.append({'batch':batch,'case':d['case'],'life':d['life'],'primary_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'frame_source_sha256':hashlib.sha256(frames.read_bytes()).hexdigest(),'at_actual_access_161':acquired,'subsequent_ROI':r,'caution':'No identity/lineage inferred solely from equal loads. This is a locator for native causal controls, not a full causal proof.'})
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps({'no_new_simulation':True,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'cases':len(rows),'qualified_local_accesses':sum(z['qualified_XYZ_access']for row in rows for z in row['at_actual_access_161'])}))
