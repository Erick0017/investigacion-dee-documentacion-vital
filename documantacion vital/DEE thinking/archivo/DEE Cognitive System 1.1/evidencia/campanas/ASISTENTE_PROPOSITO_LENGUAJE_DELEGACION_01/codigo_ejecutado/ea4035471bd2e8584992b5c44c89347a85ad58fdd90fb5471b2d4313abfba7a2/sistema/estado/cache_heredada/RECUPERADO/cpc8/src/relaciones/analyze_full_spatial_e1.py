"""Independent exact-window comparison. Never imported by any participant."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def obs(o):return{k:o[k]for k in('raw','clock','state','s_reg','direction','semantic','active')}
def receipt(m,port,tick):
    found=[x for x in m.get('requests',[])if x['port']==port and x['tick']==tick]
    return[{'id':x['id'],'status':x.get('receipt',{}).get('status'),'reason':x.get('receipt',{}).get('reason')}for x in found]
def functional_windows(m):
    """Apply criteria already frozen in LONGITUDINAL_E1_CONFIRMATORY, not RAW equality."""
    frames={f['tick']:f for f in m['frames']};g=m['geometry'];case=m['case'];out=[]
    axis=1 if case.get('order','AB')=='AB'else -1;z=1 if case.get('actor_mode','contact')=='contact'else 0
    def add(kind,tick,q,expected,receipts=None,load_rule=None):
        receipts=receipts if receipts is not None else []
        admitted=all(x['status']=='applied'for x in receipts)if receipts else None
        active=q['active']and q['semantic']==1;structural=active and q['direction']==expected and (load_rule(q['s_reg'])if load_rule else True)
        # The inherited frozen detector is a native-state functional reader.
        # Admission of a newly requested consumable is a DIFFERENT variable:
        # a reader already physically available can use a new current object.
        valid=bool(structural)
        reason=('VALID_NATIVE_READOUT_NEW_QUERY_REJECTED'if admitted is False else'VALID_FROZEN_FUNCTIONAL_READOUT')if valid else'INACTIVE'if not q['active']else'OUTSIDE_FROZEN_DIRECTION_OR_LOAD'
        out.append({'family':kind,'tick':tick,'physical':q,'expected_direction':expected,'query_receipts':receipts,'request_admitted':admitted,'valid_functional_readout':valid,'attributable_to_admitted_new_query':bool(valid and admitted is True),'status':reason,'causal_attribution':'A matching native detector reading is not by itself proof that this rejected/new query caused it. Current-object and memory controls are reported separately.','criterion_origin':'configuraciones/integracion/LONGITUDINAL_E1_CONFIRMATORY_FROZEN.json; input-derived expectations are auditor-only and never enter MAIN'})
    for t in(31,165):
        label='plus'if axis>0 else'minus';q=frames[t]['order'][label]['query_site'];add('ORDER',t,q,[axis,0,1],receipt(m,g['order'][label]['query_port'],t-3),lambda x:x>7)
    contact_key='right.'+('changed'if z else'free')
    for t,key,port in((76,'query_site','query_port'),(143,'renewed_site','renew_port')):
        q=frames[t]['contact'][contact_key][key];add('CONTACT',t,q,[-1,1,z-1],receipt(m,g['contact'][contact_key][port],73 if t==76 else 142),lambda x:x>5)
    add('COMMON_USE_INPUT',206,frames[206]['common_join'],[axis,1,z])
    joint_key=('plus'if axis>0 else'minus')+'.'+('changed'if z else'free')
    for t,payload in((281,7),(348,7),(415,9),(549,11)):
        q=frames[t]['joint'][joint_key]['delivery_site'];add('JOINT_WORD',t,q,[0,1,1],receipt(m,g['joint_names'][joint_key]['query_port'],t-3),lambda x,p=payload:x>p)
    values=list(case.get('quantity_objects',(16,45,31)))+list(case.get('later_quantity_objects',(36,42,31,50)))
    reference=case.get('quantity_reference',31)
    for index,(t,value)in enumerate(zip((70,137,204,338,405,472,539),values)):
        target_ref=reference+(case.get('addition_value',11)if index>=3 and case.get('addition_mode','paired')=='paired'else 0)
        dx=(target_ref>value)-(target_ref<value);q=frames[t]['quantity']['center'];add('QUANTITY',t,q,[dx,0,0],receipt(m,'quantity.reader',t-1),lambda x:x==7)
    return out
def frozen_windows(m):
    out={};frames={x['tick']:x for x in m['frames']}
    for tick in(31,165):
        f=frames.get(tick)
        if f:
            for key,q in f['order'].items():out['order:'+str(tick)+':'+key]=obs(q['query_site'])
    for tick,field in((76,'query_site'),(143,'renewed_site')):
        f=frames.get(tick)
        if f:
            for key,q in f['contact'].items():out['contact:'+str(tick)+':'+key]=obs(q[field])
    if 206 in frames:out['common:206']=obs(frames[206]['common_join'])
    for tick in(281,348,415,549):
        f=frames.get(tick)
        if f:
            for key,q in f['joint'].items():out['joint:'+str(tick)+':'+key]=obs(q['delivery_site'])
    for tick in(70,137,204,338,405,472,539):
        f=frames.get(tick)
        if f:out['quantity:'+str(tick)]=obs(f['quantity']['center'])
    return out
def spatial_functions(m):
    caps=m.get('spatial_social_captures',[]);g=m['geometry']['spatial'];case=m['case'];a=case.get('spatial_reference_axis',1);b=case.get('spatial_objects',[1,-1])[1];c=case.get('spatial_context',1)
    expected_relation='LIKE_REFERENCE_Y_SIDE'if a==b else'DIFFERENT_Y_SIDE';y=a if a==b else 0;expected_query=[a,y,-1];expected_use=[a,(y+c>0)-(y+c<0),-1]
    queries=[x for x in caps if x['phase']=='FORM_QUERY'and x['covered']];out=[]
    for q in queries:
        rid=q['receiver'];context=[x for x in caps if x['phase']=='CONTEXT_CONTACT'and x['receiver']==rid];delivery=[x for x in caps if x['phase']=='DELIVERY'and x['receiver']==rid and x['context_candidate']==c]
        out.append({'receiver':rid,'query235':q,'expected_query_direction':expected_query,'query_matches_frozen_relation':q['relation']==expected_relation and q['physical']['direction']==expected_query,'context240':context,'delivery243':delivery,'expected_context_delivery_direction':expected_use,'native_context_use_matches':any(x['physical']['active']and x['physical']['semantic']==1 and x['physical']['direction']==expected_use for x in context),'native_delivery_matches':any(x['physical']['active']and x['physical']['semantic']==1 and x['physical']['direction']==expected_use for x in delivery)})
    return out
def summarize(root):
    bp=root/'resultados/integracion/LCE_P01_FRESH_LONGITUDINAL/MEASUREMENTS.json';base=json.loads(bp.read_text(encoding='utf8'));bo=frozen_windows(base);rows=[]
    for path in sorted((root/'resultados/semantica').glob('FSP_P*/MEASUREMENTS.json')):
        m=json.loads(path.read_text(encoding='utf8'));candidate=frozen_windows(m);pairs=[]
        for key,wanted in bo.items():
            got=candidate.get(key);pairs.append({'window':key,'reference':wanted,'candidate':got,'same_RAW_clock_fields':got==wanted if got is not None else None})
        mode=m.get('mode_captures',[]);bs=base.get('mode_captures',[]);social=m.get('social_captures',[]);bss=base.get('social_captures',[])
        spatial=m.get('spatial_social_captures',[])
        function=functional_windows(m)if m['status']=='MEASURED'else []
        sf=spatial_functions(m)if m['status']=='MEASURED'else []
        rows.append({'case_id':m['case']['id'],'primary':path.relative_to(root).as_posix(),'sha256':sha(path),'status':m['status'],'preparations':m['preparations'],'last_complete_tick':m.get('last_complete_tick'),'resources':m.get('geometry',{}).get('resources'),'initial_merge':m.get('geometry',{}).get('spatial_merge'),'matched_reference_windows':sum(x['same_RAW_clock_fields']is True for x in pairs),'compared_reference_windows':len(pairs),'window_comparisons':pairs,'functional_windows':function,'functional_summary':{kind:{'valid':sum(x['valid_functional_readout']for x in function if x['family']==kind),'windows':sum(x['family']==kind for x in function)}for kind in sorted({x['family']for x in function})},'first_functional_miss':next((x for x in sorted(function,key=lambda x:x['tick'])if not x['valid_functional_readout']),None),'MODE_captures_exact':mode==bs,'MODE_social_captures_exact':social==bss,'MODE_valid_queries':sum(x.get('covered',False)for x in social if x['phase']=='FORM_QUERY'),'SPX_valid_queries':sum(x.get('covered',False)for x in spatial if x['phase']=='FORM_QUERY'),'SPX_query_classes':[x['relation']for x in spatial if x['phase']=='FORM_QUERY'and x['covered']],'SPX_functional_chain':sf,'SPX_active_deliveries':[{'tick':x['tick'],'receiver':x['receiver'],'physical':x['physical']}for x in spatial if x['phase']=='DELIVERY'and x['physical']['active']],'technical_error':m.get('error')})
    return{'schema':'CPC8R.full_spatialE1.analysis.v3','reference':{'path':bp.relative_to(root).as_posix(),'sha256':sha(bp),'case_id':base['case']['id']},'scope':'Comparison computed after each frozen trajectory. No data returns to MAIN. Exact-state match is supplementary only: a new preparation need not preserve RAW to preserve function. Functional criteria and per-query admission are separately calculated from predeclared readers. Whole-state differences alone never declare loss.','interpretation_revision':'V2 added an unwarranted admission gate to the inherited functional detector. A paired access cut/sham showed equal valid quantity137 in both while only cut admitted the new query. V3 follows the ORIGINAL native detector and reports admission separately; oldV2 calculation preserved, no trajectory/decoder edited.','predeclared_origin_limit':3,'cases':rows}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,default=ROOT/'resultados/semantica/FULL_SPATIAL_E1_ANALYSIS.json');a=p.parse_args();r=summarize(a.root);a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps([{'id':x['case_id'],'status':x['status'],'exact':str(x['matched_reference_windows'])+'/'+str(x['compared_reference_windows']),'spatial_queries':x['SPX_valid_queries'],'mode_social':x['MODE_valid_queries']}for x in r['cases']]))
