import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import dee_thinking as d
from laboratorio import *
from supervision import atomic_json


def main(root):
    e=CaseEvidence(root,'DISCOVERY_01',{'type':'discovery before freeze','methods':['online relative body','external habitat feedback','mobile query continuation'],'not_holdout':True})
    rows=[]
    for history in ['AB','BA','AA','BB','']:
        w=make_body();receipts=body_experience(w,list(history)) if history else []
        if not history:w.run_until(34)
        row={'history':history,'receipts':receipts,'panel':body_panel(w)};p,f=body_probe(w);row['probe']=p;rows.append(row)
    w=make_body();body_experience(w,['A','B']);e.snapshot(w,'BODY_AFTER_AB');p,w=body_probe(w,in_fork=False)
    before_return=body_panel(w);response_tick=w.runtime.current_tick
    r=w.submit('E_B',0,response_tick+255);w.run_until(response_tick+255)
    rows.append({'feedback_before':body_panel(w),'feedback_queued_receipt':receipt(w.runtime.receipt(r.id))});w.advance();rows.append({'feedback_after':body_panel(w),'receipt':receipt(w.runtime.receipt(r.id))});w.advance(8)
    p2,f=body_probe(w);rows.append({'post_return_retention':body_panel(w),'probe':p2,'emission':p,'native_memory_not_edited':True});e.snapshot(w,'BODY_AFTER_RETURN')
    mobile,rs=learned_mobile();mobile.run_until(56);m,f=mobile_query(mobile,13);rows.append({'mobile_retention50':m,'input_receipts':rs})
    result=e.finish(rows);atomic_json(Path(root)/'resultados/DISCOVERY_01.json',result);print(json.dumps(rows,indent=2))


if __name__=='__main__':main(sys.argv[1])
