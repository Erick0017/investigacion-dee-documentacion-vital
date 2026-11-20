"""Static recalc of the exact recorded two-SEM4 P0 preparation, no Native.

Verifies archived stop RAW/receipts and bank observations. A preflight hash
with an empty conflict list is identified as a recorded assertion, not a
new independent read of all45 sites or universal future isolation.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('primary',H/'recalcular_primarios_PI10_R03.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)

def candidates(value):
    if isinstance(value,dict):
        if value.get('version')=='DEE.PI10.adaptive_query.two_native_traces.R02'and value.get('preparation',{}).get('version')=='PI10.R02.two_legal_postread_stops.P0':yield value
        for val in value.values():
            if isinstance(val,(dict,list)):yield from candidates(val)
    elif isinstance(value,list):
        for val in value:yield from candidates(val)

def check(v):
    p=v['preparation'];before=p['before_tick'];after=p['after_tick']
    a.need(before==922374 and after-before==3 and p['new_ticks']==3,'Declared additive three-tick preparation from exact neutral prefix')
    a.need(v['before_tick']==before and v['after_tick']==after and v['new_native_ticks']==3,'Outer/inner physical cut agreement')
    rows=p['requests'];ids=a.unique_receipts(rows);a.need(len(ids)==2 and all(x['status']=='applied'for x in ids.values()),'Exactly two actual admitted Native births')
    sites=[[30,40,32],[32,40,32]]
    for n,(r,site)in enumerate(zip(rows,sites)):
        a.need(r['channel']=='PI10.R02.device.postread_stop.'+str(n)and r['site']==site and r['payload']==0 and r['requested_tick']==before+2,'Fixed ordinary postread stop interface, no response-contingent placement')
    observed=[a.raw_observation(o)for o in p['stops_after']]
    a.need([o['site']for o in observed]==sites and all(o['raw']==4<<60 and o['state']==0 and o['semantic']==4 and o['tick']==after for o in observed),'Actual inactive-but-nonzero fullRAW SEM4 stops')
    pre=p['preflight'];a.need(pre['new_stops']==sites and pre['checked_sites']==45 and pre['conflicts']==[]and pre['eligible']is True,'Recorded wholeRAW+halo1 preflight, no skipped nonzero conflict')
    for key,origin in(('q1',[24,12,12]),('q2',[8,40,50])):
        first=p['references_before'][key];last=p['references_after'][key];a.reference(first,origin);a.reference(last,origin)
        for side in('A','B'):
            b=a.raw_observation(first[side]);e=a.raw_observation(last[side])
            a.need(b['raw']==e['raw']and a.exact_int(last[side]['clock'])-a.exact_int(first[side]['clock'])==3,'Bank material content preserved, clocks advanced with the world')
    a.need(p['references_before']['q1']['A_minus_B']==0 and p['references_before']['q1']['A']['s_reg']==0 and p['references_before']['q1']['B']['s_reg']==0 and p['references_before']['q2']['A_minus_B']==-1,'Neutral new q1 and actual inherited q2 retained')
    for flag in('TC_reinstalled','clock_edits','physical_bank_copy'):a.need(p[flag]is False,'No '+flag)
    a.need(p['ready']is True and p['not_learning']is True and v['old_metadata_literal_unchanged']is True and v['old_R01_P0_key_literal_unchanged']is True,'Preparation attribution and literal ancestral preservation assertions')
    return {'before_tick':before,'after_tick':after,'Native_ticks':3,'Native_requested':2,'Native_applied':2,'Native_rejected':0,
      'actual_stops':observed,'bank_material_and_3tick_clock_changes_checked':True,
      'whole_RAW_halo1_preflight_recorded':{'checked_sites':45,'conflicts':[],'observations_sha256':pre['observations_sha256']},
      'whole_preflight_independently_redecoded_from_snapshot':False,'old_metadata_equality_reported_by_pinned_actor':True,
      'classification':'External P0 physical sensor-route preparation, not learned self-protection or a memory transplant.',
      'future_isolation_or_conservation_not_proved_here':True}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--primario',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);args=p.parse_args()
    a.need(not args.salida.exists(),'No overwrite of a previous preparation recalc');b=args.primario.read_bytes();v=json.loads(b)
    if isinstance(v,dict)and isinstance(v.get('result'),str):v={**v,'result':json.loads(v['result'])}
    found=list(candidates(v));unique={json.dumps(x,sort_keys=True,separators=(',',':')):x for x in found};a.need(len(unique)==1,'One actual preparation result, not multiple favorable aliases or runs')
    result={'schema':'DEE.PI10.two_stop_preparation_recalc.R02','Native_executed':False,'DEE_imported':False,
      'source':{'file':str(args.primario.absolute()),'bytes':len(b),'sha256':a.sha(b)},'checked':check(next(iter(unique.values())))}
    with args.salida.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(args.salida),'sha256':a.sha(args.salida.read_bytes()),'Native_executed':False}))
if __name__=='__main__':main()
