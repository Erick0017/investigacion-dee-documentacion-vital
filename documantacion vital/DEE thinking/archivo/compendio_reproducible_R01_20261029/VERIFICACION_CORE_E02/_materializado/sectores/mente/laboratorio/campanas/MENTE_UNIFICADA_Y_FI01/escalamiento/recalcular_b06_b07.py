"""Portable archived reader/RAW/admission verification, zero native ticks.

Run against the exported escalamiento directory; never imported by the actor.
Full uint64 blocks are field exports, not complete operational snapshots.
"""
import argparse,gzip,hashlib,json,struct
from pathlib import Path
from recalcular_escalamiento_b_R3_B05_FINAL import raw_fields,observations,native_reader,old_reader

def counts(requests):
    out={'requested':len(requests),'applied':0,'rejected':0,'pending':0,'other':0}
    for r in requests:
        st=r['receipt']['status'];out['applied'if st=='applied'else'rejected'if st.startswith('rejected')else'pending'if st in('queued','pending')else'other']+=1
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    files=sorted(a.evidence.glob('B06_CADENCE_NOISE_R1/*.json.gz'))+sorted(a.evidence.glob('B07_FRESH_N67_N101_R1/*.json.gz'))+sorted(a.evidence.glob('B07_CADENCE_N67_N101_R2/*.json.gz'))+sorted(a.evidence.glob('B04_PHASE_PLUS6_R2/*.json.gz'))
    errors=[];rows=[];nobs=0;nread=0
    for p in files:
        data=p.read_bytes();x=json.loads(gzip.decompress(data));r=x.get('result',x)
        for o in observations(r):
            nobs+=1
            if raw_fields(o['raw'])!={k:o[k]for k in('state','s_reg','semantic','direction')}:errors.append(str(p)+':RAWdecode')
            if isinstance(o['clock'],float):errors.append(str(p)+':clockfloat')
        if'readers'in r:readers=r['readers']
        elif'episodes'in r:readers=[z['reader']for z in r['episodes']]
        elif'reader'in r:readers=[r['reader']]
        else:
            rows.append({'file':str(p.relative_to(a.evidence)),'sha256':hashlib.sha256(data).hexdigest(),'kind':'P0_PREPARATION'});continue
        choices=[]
        for rd in readers:
            choice=native_reader(rd['observations'],planes=(0,-1));nread+=1;choices.append(choice)
            if choice!=rd['choice']:errors.append(str(p)+':fixed_current_reader')
        post=[]
        for rd in r.get('post_3N_probe_readers',[]):
            choice=native_reader(rd['observations'],planes=(0,-1));nread+=1;post.append(choice)
            if choice!=rd['choice']:errors.append(str(p)+':fixed_post_3N_reader')
        old=[];old_counts=None
        old_panel=r.get('old_six_panel',r.get('old_six_panel_after_2N'))
        if old_panel:
            req=[]
            for q in old_panel['rows']:
                v=old_reader(q['reader']['panel']);nread+=1;old.append(v);req+=q['requests']
                if v!=q['reader']['formed_native_command']:errors.append(str(p)+':fixed_old_reader')
            old_counts=counts(req)
        rows.append({'file':str(p.relative_to(a.evidence)),'sha256':hashlib.sha256(data).hexdigest(),
          'life':r.get('life',x.get('INSTRUMENTO',{}).get('life_id')),'N':r.get('N',r.get('initial',{}).get('N')),
          'case':r.get('label',r.get('history_for_auditor_only')),'choices':choices,'post_3N_probe_choices':post,'counts':counts(r['requests']),
          'old_six_choices':old,'old_six_counts':old_counts,'passive':r.get('passive_common_horizon'),
          'final':r.get('final'),'new_T0':r.get('new_T0',False)})
    # Reconstruct occupancy from complete exported RAW, not only a helper verdict.
    fields=[];idx=a.evidence/'B06_CADENCE_NOISE_R1/CAMPOS_COMPLETOS_0_TICKS/INDICE_CAMPOS.json'
    if idx.exists():
        index=json.loads(idx.read_text(encoding='utf8'))
        for q in index['rows']:
            row={'delta':q['delta'],'label':q['label'],'N':q['N'],'tick':q['tick']}
            for name in('raw','clocks'):
                p=idx.parent/q[name]['file'];compressed=p.read_bytes();data=gzip.decompress(compressed)
                if hashlib.sha256(data).hexdigest()!=q[name]['sha256_uncompressed']:errors.append(str(p)+':rawhash')
                if hashlib.sha256(compressed).hexdigest()!=q[name]['sha256_compressed']:errors.append(str(p)+':compressedhash')
                vals=[z[0]for z in struct.iter_unpack('<Q',data)]
                if len(vals)!=q['N']**3:errors.append(str(p)+':dimension')
                if name=='raw':
                    occupied=sum(bool(v&0xffffffff)for v in vals);row['occupied']=occupied
                    row['max_s_reg']=max((v>>32)&65535 for v in vals)
                    if occupied!=q['occupied']:errors.append(str(p)+':occupation')
                else:row['clock_min_max']=[min(vals),max(vals)]
            fields.append(row)
    report={'native_ticks':0,'files':len(files),'RAW_observations_checked':nobs,'fixed_readers_reconstructed':nread,
      'errors':errors,'rows':rows,'complete_field_exports':fields,
      'scope':'Archived calculation only. B06afterpanel17427 is not passive17038; array export is not a full operational state. Fresh scale lives never inherit MAIN old6.'}
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:report[k]for k in('files','RAW_observations_checked','fixed_readers_reconstructed','errors')}))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
