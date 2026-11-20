"""Frozen recorded stencil/clock/reference analysis, not a Native replay.

Computes geometry from archived exact RAW and sites. Sampled compatible
motion is not a unique particle genealogy or proof of every intervening
encounter. History/functional attribution requires the separately fixed
controls; this tool does not score autonomy or promote a life.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('primary',H/'recalcular_primarios_PI10_R02.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)

def signed_offset(site,origin):
    values=[(site[k]-origin[k])%67 for k in range(3)]
    return [n-67 if n>33 else n for n in values]

def contacts(v,p):
    o=p['query_origin'];cal=v['calendar']['first'];start=v['before_tick'];m=v['first_stage']['actual_query_motor']
    cb=[a.exact_int(v['Q1_references_before'][k]['clock'])for k in('A','B')]
    residues=[(c+cal['contact_tick']-start)%782 for c in cb]
    a.need(residues==[391,391],'Fixed future reference-clock gate at391/782, not retimed after observing an answer')
    frames=[];returns=[]
    for frame in v['trace_observations']:
        stencil=frame.get('q1');a.need(stencil is not None,'Declared fixed q1 stencil')
        tick=stencil['tick'];sampled=[];nonzero=[]
        for observation in stencil['observations']:
            d=a.raw_observation(observation);a.need(d['tick']==tick,'One coherent recorded stencil tick')
            point={'site':d['site'],'offset_from_origin':signed_offset(d['site'],o),'state':d['state'],'s_reg':d['s_reg'],
              'semantic':d['semantic'],'direction':d['direction'],'RAW':str(d['raw'])}
            if d['raw']!=0:nonzero.append(point)
            if d['state']>0 and d['semantic']==1:sampled.append(point)
        row={'phase':frame['phase'],'tick':tick,'relative_to_seed':tick-cal['seed_tick'],
          'relative_to_collision':tick-cal['collision_tick'],'active_SEM1_samples':sampled,'all_nonzero_RAW_samples':nonzero}
        if 'q1_references'in frame:
            refs=frame['q1_references'];delta=a.reference(refs,o)
            row['references']={'A_s_reg':a.raw_observation(refs['A'])['s_reg'],'B_s_reg':a.raw_observation(refs['B'])['s_reg'],'A_minus_B':delta}
        frames.append(row)
        if frame['phase']=='q1_return_frame':returns.append(row)
    expected=[cal[k]for k in('outcome_injection_tick','collision_tick','contact_tick','settled_after_tick')]
    a.need([r['tick']for r in returns]==expected,'All four prospectively fixed return frames, no favorable snapshot selection')
    collision=returns[1];center=[x for x in collision['active_SEM1_samples']if x['offset_from_origin']==[0,-1,-2]]
    delta_before=returns[0]['references']['A_minus_B'];delta_after=returns[-1]['references']['A_minus_B']
    initial=a.reference(v['Q1_references_before'],o);final=a.reference(v['references_after']['q1'],o)
    return {'life_id':v['life_id'],'ordinal':v['ordinal'],'calibration':v['operator_calibration'],'forced_query':v['first_stage']['operator_forced_query'],
      'actual_motor_before_return':m,'returned_failure':v['returned_failed'],'sampled_seed_tick':cal['seed_tick'],
      'delay_ticks':cal['delay_ticks'],'delay_laps':cal['delay_laps'],'clock_gate_residues':residues,
      'frames':frames,'collision_hub_active_SEM1':center,
      'A_minus_B_before_episode':initial,'A_minus_B_at_return_injection':delta_before,
      'A_minus_B_after_return':delta_after,'A_minus_B_final':final,
      'change_during_recorded_return_window':delta_after-delta_before,
      'change_before_recorded_return_window':delta_before-initial,
      'sampled_trace_not_unique_lineage':True,
      'qualification':'These are recorded RAW states and reference differences, not invented intermediate trajectories. A same-load carrier is not uniquely identified across the unrecorded18laps. Control of formed trace and contingent returns is needed to attribute specific functional credit.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--indice',type=Path,required=True);parser.add_argument('--salida',type=Path,required=True);args=parser.parse_args()
    a.need(not args.salida.exists(),'No overwrite of prior causal recalc')
    index=a.read(args.indice);a.need(index['schema']==a.SCHEMA and index['closed']is True,'Explicit closed primary bundle only')
    pp=a.safe_file(args.indice.parent,index['protocol']['file']);pb=pp.read_bytes();a.need(a.sha(pb)==index['protocol']['sha256'],'Exact protocol')
    p=json.loads(pb);rows=[]
    for entry in index['episodes']:
        path=a.safe_file(args.indice.parent,entry['witness']['file']);b=path.read_bytes();a.need(a.sha(b)==entry['witness']['sha256']and len(b)==entry['witness']['bytes'],'Immutable primary witness')
        v=json.loads(b);a.project_episode(v,p);r=contacts(v,p);r['witness_sha256']=a.sha(b);rows.append(r)
    result={'schema':'DEE.PI10.archived_TC_contact_recalc.R01','Native_executed':False,'DEE_imported':False,'index_sha256':a.sha(args.indice.read_bytes()),'rows':rows,
      'scope':'Archived passive-sample geometry/clock/reference calculation. It does not extend observer passivity beyond original coverage or imply general learning, initiative or adoption.'}
    with args.salida.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(args.salida),'sha256':a.sha(args.salida.read_bytes()),'rows':len(rows),'Native_executed':False}))
if __name__=='__main__':main()
