"""Compact exact existing data, classify rejected receipts, export critical frames.
No native imports and no ticks. Does not delete the initial reflection export.
"""
import gzip,hashlib,json
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01';OUT=EV/'contraste_main_u'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def terminal(status):return status=='applied'or status.startswith(('rejected','cancelled','failed','expired'))
def main():
    source=OUT/'MAIN_U_COMPLETO_T14892_T16033_T16066.json.gz';target=OUT/'MAIN_U_COMPLETO_FINAL.json.gz'
    if target.exists():raise FileExistsError(target)
    x=json.loads(gzip.decompress(source.read_bytes()))
    for w in x['worlds'].values():
        w['unfinished_by_public_receipt_status']=[r for r in w['receipts']if not terminal(r['status'])]
        w['terminal_rejections']=[r for r in w['receipts']if r['status'].startswith('rejected')]
    for p in x['comparisons']:
        u,v=x['worlds'][p['left']],x['worlds'][p['right']]
        p['unfinished_receipts_equal']=u['unfinished_by_public_receipt_status']==v['unfinished_by_public_receipt_status']
    critical=[]
    for case,index in(('A42_MAIN_DOS_CONSECUENCIAS',1),('A45_MAIN_RESERVAS_UTILES',2),('A46_U_RESERVAS_UTILES',2)):
        source_primary=EV/(case+'.json.gz');r=json.loads(gzip.decompress(source_primary.read_bytes()))['result']['result']['rows'][index]
        frames=[]
        for f in r['frames']:
            points=[]
            for o in f['sites']:
                p=o['site'];axis=p[0]==15 and p[2]==15 and 12<=p[1]<=17;local=all(abs(p[i]-15)<=1 for i in range(3))
                if axis or local:points.append(o)
            frames.append({'tick':f['tick'],'sites':points})
        critical.append({'case':case,'source_primary':str(source_primary),'source_primary_sha256':sha(source_primary),'original_row_index':index,'query_tick':r['query_tick'],'read_tick':r['read_tick'],'reader_exact':r['reader'],'critical_frames_exact':frames,'coverage':'Exact axis12..17 plus Moore26/E from archived largerframes; not acomplete tick-state or unique lineage reconstruction.'})
    x['critical_existing_frames']=critical
    x['schema']='MUFI01.main_u.exact_read_only.v3'
    x['normalization']={'source_file_sha256':sha(source),'source_file':source.name,'source_code_sha256':sha(Path(__file__)),'receipt_fix':'rejected_occupied is terminal rejection, never pending. Exact receipts retained, no data erased.','deep_reflection_omitted_from_analysis':{'file':'MAIN_U_REFLEXION_R1_PROFUNDA.json.gz','sha256':'a97cd2addf1cc3896e4b3f959330ab0372975f5731a222991d8854d388569205','reason':'Redundant recursive enum classmembers; exactenumname/value andallinstancefields areincompactexport. FullRAW/clocks unchanged.'},'ticks_executed':0}
    target.write_bytes(gzip.compress(json.dumps(x,ensure_ascii=False,sort_keys=True).encode(),mtime=0));print(json.dumps({'bytes':target.stat().st_size,'sha256':sha(target),'unfinished':[len(w['unfinished_by_public_receipt_status'])for w in x['worlds'].values()],'rejections':[len(w['terminal_rejections'])for w in x['worlds'].values()]}))
if __name__=='__main__':main()
