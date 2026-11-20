"""Portable read-only exact MAIN/U arrays and critical archived frames, stdlib."""
import argparse,gzip,hashlib,json,struct
from collections import Counter
from pathlib import Path
def digest(x):return hashlib.sha256(b''.join(struct.pack('<Q',int(v))for v in x)).hexdigest()
def fields(raw):
    r=int(raw);ds=[(r>>k)&15 for k in(48,52,56)]
    return {'state':r&0xffffffff,'s_reg':(r>>32)&65535,'semantic':(r>>60)&15,'direction':[v-16 if v>=8 else v for v in ds]}
def terminal(s):return s=='applied'or s.startswith(('rejected','cancelled','failed','expired'))
def calculate(p):
    b=p.read_bytes();x=json.loads(gzip.decompress(b));errors=[];values=0;rows=[]
    for name,w in x['worlds'].items():
        if w['tick_before']!=w['tick_after']or w['primary_reported_tick']!=w['tick_before']:errors.append(name+': agechanged')
        for k in('raw','clock'):
            vs=w[k];values+=len(vs)
            if len(vs)!=w['N']**3 or any(not 0<=int(v)<2**64 for v in vs):errors.append(name+': invaliduint64array')
            if digest(vs)!=w[k+'_le_uint64_sha256']:errors.append(name+': arraydigest')
        if dict(Counter(r['status']for r in w['receipts']))!=w['receipt_status_counts']:errors.append(name+': receiptdenominator')
        if [r for r in w['receipts']if not terminal(r['status'])]!=w['unfinished_by_public_receipt_status']:errors.append(name+': queuedclassification')
    for pair in x['comparisons']:
        u,v=x['worlds'][pair['left']],x['worlds'][pair['right']];N=u['N'];ri=[i for i,(a,b)in enumerate(zip(u['raw'],v['raw']))if a!=b];ci=[i for i,(a,b)in enumerate(zip(u['clock'],v['clock']))if a!=b]
        expected=[{'index':i,'site':[i//(N*N),(i//N)%N,i%N],'left_raw':u['raw'][i],'right_raw':v['raw'][i]}for i in ri]
        if expected!=pair['raw_differences']or ci!=[d['index']for d in pair['clock_differences']]:errors.append('pairarraydiff')
        for attr,result in(('interfaces','interfaces_equal'),('protocols','protocols_equal'),('channel_names','channels_equal'),('receipts','receipts_equal'),('unfinished_by_public_receipt_status','unfinished_receipts_equal')):
            if (u[attr]==v[attr])!=pair[result]:errors.append('contextcomparison:'+attr)
        rows.append({'tick':u['tick_before'],'same_age':u['tick_before']==v['tick_before'],'raw_differences':[dict(d,left_fields=fields(d['left_raw']),right_fields=fields(d['right_raw']))for d in expected],'clock_difference_count':len(ci),'interfaces_equal':u['interfaces']==v['interfaces'],'protocols_equal':u['protocols']==v['protocols'],'channels_equal':u['channel_names']==v['channel_names'],'receipts_equal':u['receipts']==v['receipts'],'unfinished_left':len(u['unfinished_by_public_receipt_status']),'unfinished_right':len(v['unfinished_by_public_receipt_status']),'metadata_different_keys':pair['metadata_different_keys'],'no_total_causal_identity_claim':True})
    frames=[];count=0
    for case in x['critical_existing_frames']:
        for f in case['critical_frames_exact']:
            for o in f['sites']:
                count+=1;ff=fields(o['raw'])
                if any(o[k]!=v for k,v in ff.items()):errors.append(case['case']+': framedecoding')
        reader=case['reader_exact'];out=[]
        for o in reader['observations']:
            ff=fields(o['raw']);dx=o['site'][0]-15;sign=dx//2
            if o['site'][1:]!=[17,15]or dx not in(-2,0,2):errors.append('readerposition')
            if ff['state']>0 and ff['semantic']==1 and ff['direction']==[sign,1,0]:out.append({'choice':sign,'s_reg':ff['s_reg'],'site':o['site']})
        choice=out[0]['choice']if len(out)==1 else None
        if choice!=reader['choice']:errors.append('readerchoice')
        axis=[{'tick':f['tick'],'observations':[o for o in f['sites']if o['site'][0]==15 and o['site'][2]==15 and o['state']>0]}for f in case['critical_frames_exact']]
        frames.append({'case':case['case'],'query_tick':case['query_tick'],'reader_choice':choice,'reader_candidates':out,'axis_exact':axis})
    torus={'snapshot_position':[15,52,15],'snapshot_tick':16033,'direction':[0,1,0],'N':67,'straight_path_ticks_to_E':(15-52)%67,'straight_path_arrival_tick':16033+(15-52)%67,'earlier_neutral_read_position':[15,17,15],'earlier_neutral_read_tick':15261,'predicted_position_at_16033':[15,(17+16033-15261)%67,15],'scope':'Geometric compatibility only. Long gap not recorded as complete lineage; no unique ancestry or causal effect established.'}
    return {'schema':'MUFI01.main_u.archived_recalculation.v1','native_ticks_executed':0,'source_primary_sha256':hashlib.sha256(b).hexdigest(),'exact_uint64_values_checked':values,'exact_critical_observations_checked':count,'errors':errors,'pairs':rows,'critical_frames':frames,'toroidal_compatibility':torus,'interpretation':'MAIN/U exact physicalequality beforeconsequences; aftertwofeedbacksAdifferenceplusone+Ycarrier; finalsnapshotonlyAdifference. Existingframe16062showsold+Y5neighborandnew+Z5inoccupiedE,16063Eturnsnegativewith5,readerretains5not10. Contextmaycontribute; no selectivecut or sole-cause claim.'}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--evidencia',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args();r=calculate(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_bytes(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2).encode());print(json.dumps({'errors':len(r['errors']),'uint64':r['exact_uint64_values_checked'],'observations':r['exact_critical_observations_checked'],'sha256':hashlib.sha256(a.salida.read_bytes()).hexdigest()}));raise SystemExit(bool(r['errors']))
