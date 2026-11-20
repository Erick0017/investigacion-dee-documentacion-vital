"""Same E1 after884: prospective selective update and reserved reuse.

Load exact physical/operative state. No constructor, reset, clock or RAW edit.
The parallel offpath arm is an auditor counterfactual, not another individual
whose knowledge may be added to MAIN.
"""
from pathlib import Path
import argparse,hashlib,json,sys,time,traceback
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from vida_integral import IntegralLifeSession
from integracion.relational_pair import physical,move
from ejecutar_retorno import write

def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--update',choices=['onpath','offpath','none'],default='onpath');p.add_argument('--addition',type=int,default=13);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False);started=time.monotonic();s=IntegralLifeSession.load(a.parent)
    if s.tick!=884:raise ValueError('This declared reserve requires the exact selected884 parent')
    parent_hash=hashlib.sha256(a.parent.read_bytes()).hexdigest();r={'schema':'CPC9.E1.reserved_continuation.v1','case_id':a.case,
        'parent_snapshot_sha256':parent_hash,'parent_identifier':s.identifier,'continuity_type':'MAIN_CONTINUATION'if a.update=='onpath'else'AUDITOR_COUNTERFACTUAL_CONTINUATION',
        'preparations':0,'restored_continuations':1,'MAIN_RAW_clock_edits':[],'architecture_changed':False,'configuration':vars(a)|{'parent':str(a.parent),'out':str(a.out)},
        'initial_physical':physical(s.world),'frames':[],'local_neighborhoods':[],'snapshots':[],
        'prediction_before_any_new_tick':{'reference_before':54,'actual_new_addition':a.addition,
            'reference_after':54+a.addition if a.update=='onpath'else 54,
            'current_object_payloads':[57,57,70,11],
            'comparison_ticks':[941,1008,1075,1142],
            'predicted_direction_X':[-1,1,-1,1]if a.update=='onpath'else[-1,-1,-1,1],
            'two_old_memories':'Try late old operands36/16 at942/1009/1076/1143, without operand re-exposure; outcomes not assumed',
            'old_count':'Try old acquired form at952/1019/1086/1153/1220 without contact/form reteaching',
            'old_joint':'Try old four candidate signs at951/1018/1085/1152/1219; no decoder repair after result'},
        'status':'PREDICTIONS_WRITTEN'}
    write(a.out/'MEDICIONES.json',r)
    # Generator inputs are actual material quantities, never their comparison.
    for index,value in enumerate((57,57,70,11),start=13):
        s.quantity.present_object(value,round_index=index)
        s.quantity.input('quantity.reader',7,69+67*index,True)
    if a.update!='none':
        prefix='quantity.reference.'if a.update=='onpath'else'quantity.other.'
        s.quantity.input(prefix+'cue',0,938)
        s.quantity.input(prefix+('resource'if a.update=='onpath'else'event'),a.addition,938)
    for tick in(942,1009,1076,1143):s.two_memory.input('quantity.reader',7,tick,True)
    for tick in(952,1019,1086,1153,1220):
        k=(tick-215)//67
        names={row['plus_port']if k%2==0 else row['minus_port']for row in s.geometry['cpc9_life']['count_repeated_readers']}
        for name in sorted(names):s.input(name,7,tick-3,'probe','RESERVED_OLD_COUNT_READER_NO_CONTACT_RETEACHING')
    for tick in(951,1018,1085,1152,1219):
        for bank in s.geometry['joint_names'].values():s.input(bank['query_port'],17,tick-3,'probe','RESERVED_OLD_JOINT_READER_NO_RETEACHING')
    try:
        ticks={884,936,938,940,941,942,943,951,952,1003,1007,1008,1009,1010,1018,1019,1070,1074,1075,1076,1077,1085,1086,1137,1141,1142,1143,1144,1152,1153,1219,1220}
        for tick in sorted(ticks):
            s.run_until(tick);r['frames'].append({'tick':tick,'physical':physical(s.world),'view':s.view()})
            if tick in(940,941,942,943,1007,1008,1009,1010):
                centers={'quantity':s.geometry['quantity']['center'],'two_memory':s.two_memory.geometry['center']}
                r['local_neighborhoods'].append({'tick':tick,'windows':{n:[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]for n,q in centers.items()}})
            if tick in(884,941,1008,1220):
                path=a.out/f'T{tick}.deetsnap.gz';r['snapshots'].append({'path':path.name,'storage':s.save(path),'physical':physical(s.world)})
            r.update(last_complete_tick=tick,requests=s.receipts(),elapsed_seconds=time.monotonic()-started,status='RUNNING');write(a.out/'MEDICIONES.json',r)
        r.update(status='MEASURED',final_physical=physical(s.world),receipt_statuses=dict(Counter(x['receipt']['status']for x in s.receipts())),
            parent_file_unchanged=hashlib.sha256(a.parent.read_bytes()).hexdigest()==parent_hash)
    except BaseException as e:r.update(status='TECHNICAL_ERROR',error=repr(e),traceback=traceback.format_exc());raise
    finally:write(a.out/'MEDICIONES.json',r)
    print(json.dumps({'case':a.case,'status':r['status'],'preparations':0,'parent':s.identifier,'tick':s.tick,'seconds':time.monotonic()-started}))
if __name__=='__main__':main()
