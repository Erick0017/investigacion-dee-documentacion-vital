"""Technical alias contracts; no scientific target or learned answer."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,identity,digest,operational
from integrated import create
import action_feedback,language
from action_feedback_access import deduplicate_requests


def main():
    s=create();w=s.world;before=digest(w);op=operational(w)
    batches={'late':action_feedback.query_protocol(s.geometry['adapter']),
             'teaching':language.teaching(s.geometry['language']),
             'name_query':language.query(s.geometry['language'])}
    rows={k:deduplicate_requests(w,v) for k,v in batches.items()}
    r=batches['late'][0]
    unequal=deduplicate_requests(w,[r,{**r,'payload':r['payload']+1}]);assert len(unequal['requests'])==2
    kind=deduplicate_requests(w,[r,{**r,'kind':'submit'}]);assert len(kind['requests'])==2
    identical=deduplicate_requests(w,[r,dict(r)]);assert len(identical['requests'])==1
    reversed_rows=deduplicate_requests(w,list(reversed(batches['late'])))
    assert reversed_rows['physical_request_count']==rows['late']['physical_request_count']==14
    errors=[]
    for request,error in (({**r,'port':'UNKNOWN'},ValueError),({**r,'payload':True},TypeError)):
        try:deduplicate_requests(w,[request])
        except error:errors.append(error.__name__)
        else:raise AssertionError('Expected invalidrequest rejection')
    assert before==digest(w) and op==operational(w),'Alias analysis mutated participant'
    out={'schema':'CPC6.alias_contracts.v1','engine':identity(),'source_sha256':sha(__file__),
         'helper_sha256':sha(Path(__file__).with_name('action_feedback_access.py')),
         'batches':rows,'tests':{'unequal_payload_retained':True,'different_kind_retained':True,
             'identical_collapsed':True,'reverse_order_same_physical_count':True,
             'unknown_and_bool_rejected':errors,'passive_RAW_clocks_operative_unchanged':True},
         'technical_status':'PASS','scientific_scope':'Alias transport admission only, not a learned selection or decoder change.'}
    put(ROOT/'resultados/ACCESS_CONTRACTS_01.json',out)
    print({k:(v['requested_count'],v['physical_request_count']) for k,v in rows.items()},flush=True)


if __name__=='__main__':main()
