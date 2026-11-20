"""Pure fixed D yoke from actual closed Real6; accepts documentary R02/R03.

R02 creator, actor and permutation remain untouched. No outcome optimization,
world read, Native input or permission is performed by this constructor.
"""
from pathlib import Path
import argparse,hashlib,json
P=Path(__file__).resolve().parents[1]
def require(ok,why):
    if not ok:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build(recalculation,evidence):
    r=read(recalculation);e=read(evidence)
    require(r.get('schema')in('DEE.PI09.D.recalculated_persistent_environment.R02','DEE.PI09.D.recalculated_persistent_environment.R03')and r.get('integrity_passed')is True and r.get('Native_executed')is False,'Verified D documentary result, compatible technical STATE parser')
    require(e.get('schema')in('DEE.PI09.D.actual.finite_owner_phase.R02','DEE.PI09.D.actual.finite_owner_phase.R03')and e.get('closed')is True and e.get('arm')=='real'and e.get('error')is None,'Actual closed Real phase without transport ambiguity')
    require(any(c['arm']=='real'and c['sha256']==sha(evidence)and c['life_id']==e['life_id']for c in r['closures']),'This exact actual closure must be included in the verified result')
    rr=sorted([x for x in r['rows']if x['arm']=='real'and x['ordinal']<6],key=lambda x:x['ordinal']);require([x['ordinal']for x in rr]==list(range(6)),'Six evaluation rows; future rows never select the vector')
    values=[x['second']['actual_failed']for x in rr];require(all(type(v)is bool for v in values)and all(x['second']['returned_failed']is x['second']['actual_failed']for x in rr),'Actual real physical failures and actual returned valences must agree')
    perm=[2,0,4,1,5,3]
    return {'schema':'DEE.PI09.D.yoked_return.fixed_permutation.v1','permutation':perm,'source_failed':values,'values':[values[i]for i in perm],'source_evidence_sha256':sha(evidence)}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--recalculo',required=True);ap.add_argument('--evidencia',required=True);ap.add_argument('--salida',required=True);a=ap.parse_args()
    if not Path(a.recalculo).is_file()or not Path(a.evidencia).is_file():print(json.dumps({'status':'WAIT','output_written':False,'Native_executed':False}));raise SystemExit(0)
    result=build(a.recalculo,a.evidencia);out=Path(a.salida).absolute();require(out.parent==(P/'control').resolve()and not out.exists(),'Fresh PI09/control plan only')
    with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'output':str(out),'sha256':sha(out),'source_failed':result['source_failed'],'values':result['values'],'optimization_performed':False,'Native_executed':False}))
