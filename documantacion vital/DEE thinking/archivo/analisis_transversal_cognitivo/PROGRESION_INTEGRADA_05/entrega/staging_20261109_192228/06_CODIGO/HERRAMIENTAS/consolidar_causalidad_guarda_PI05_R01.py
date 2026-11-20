"""Documentary matched guard/sham causal chain from closed global inventories."""
from pathlib import Path
import argparse,hashlib,json,math,runpy

def info(p):
    p=Path(p);return {'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parent.parent);ap.add_argument('--salida',type=Path);args=ap.parse_args()
    p=args.root;out=args.salida or p/'control/CONTRASTE_CAUSAL_GUARD_SHAM_PI05_R01.json'
    if out.exists():raise FileExistsError('Preserve prior proof')
    tool=p/'codigo/recalcular_inventarios_globales_PI05_R02.py';m=runpy.run_path(str(tool),run_name='pure_global_inventory_reader')
    names=['REAL','NONE','YOKE','GUARD','SHAM'];views={};data={};sources={};summaries={}
    for name in names:
        proof=p/f'control/PI05_{name}_FI_GLOBAL_R01.json';d=read(proof)
        if not d['owner_closed_coherently']or d['status']!='COMPLETED_FI_RECORDED':raise ValueError('Closed actual proof required')
        root=p/f'control/INVENTARIO_{name}_FI_GLOBAL_R01';s=m['validate_inventory'](root);f=list(m['frames'](root,s))
        if len(f)!=69 or f[0]['tick']!=817876 or f[-1]['tick']!=818074:raise ValueError('Frozen matched calendar required')
        data[name]={r['tick']:r for r in f};summaries[name]=s;sources[name]={'closed_Native_proof':info(proof),'inventory_manifest':info(root/'MANIFIESTO_SHA256.json')}
        v=d['actual']['result']['rows'][0]
        views[name]={'life_id':d['life_id'],'before_tick':v['before_tick'],'after_tick':v['after_tick'],'Native_inputs':v['Native_inputs'],'early_q4':v['early_physical_choice'],'fixed_q6':v['old_q6_choice'],'public_literal':d['public_literal'],'instrument_protocol_sha256':d['instrument_protocol']['sha256'],'support':v.get('support'),'new_Native_ticks':d['new_Native_ticks']}
    def point(name,tick,site):
        f=data[name][tick];i=(site[0]*67+site[1])*67+site[2];v=f['values'].get(i,0)
        return {'site':site,'tick':tick,'clock':str(f['clock']),'RAW':str(v),**m['decode'](v)}
    critical=817884;target=[19,53,25];offsets=[(x,y,z)for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)if(x,y,z)!=(0,0,0)]
    neighbourhood={}
    for name in ['REAL','GUARD','SHAM']:
        n=[point(name,critical,[(target[i]+d[i])%67 for i in range(3)])for d in offsets]
        incoming=[x for x in n if any(x['direction'])and all((x['site'][i]+x['direction'][i])%67==target[i]for i in range(3))]
        alive=[x for x in n if x['state']>0 and x['semantic']!=5]
        neighbourhood[name]={'own_before':point(name,critical,target),'Moore26_before':n,'incoming_directed':incoming,'alive_count':len(alive),'after':point(name,critical+1,target)}
    ng=neighbourhood['GUARD'];ns=neighbourhood['SHAM']
    neighbour_equal=ng['Moore26_before']==ns['Moore26_before'];incoming_equal=ng['incoming_directed']==ns['incoming_directed']
    # The exact4corner pattern is not a frozen tetrahedron pattern. Literal
    # source constants and branch are transported in the source excerpt.
    assert neighbour_equal and incoming_equal and ng['alive_count']==ns['alive_count']==4
    assert ng['own_before']['RAW']=='0'and ns['own_before']['state']==1
    incoming=ng['incoming_directed'];charge=min(sum(x['s_reg']for x in incoming),19664)
    direction=[(s>0)-(s<0)for s in[sum(x['direction'][i]for x in incoming)for i in range(3)]]
    packed=1|(charge<<32)|((direction[0]&15)<<48)|((direction[1]&15)<<52)|((direction[2]&15)<<56)|(1<<60)
    predicted_empty={'rule':'empty-branch directional reducer;4incoming, below genesis/fusion thresholds','state':1,'s_reg':charge,'semantic':1,'direction':direction,'RAW':str(packed)}
    predicted_matter={'rule':'matter:floor(4*2.5/26+0.5)','rule_value':math.floor(4*2.5/26+0.5),'RAW':'0'}
    eg=m['event_diff'](summaries['REAL'],summaries['GUARD']);es=m['event_diff'](summaries['REAL'],summaries['SHAM']);gs=m['event_diff'](summaries['GUARD'],summaries['SHAM'])
    comparable=all(e['common_channel_tick_events']==e['identical_common_requests']==176 and not e['request_differences']and not e['receipt_outcome_differences']for e in [eg,es,gs])
    assert comparable and len(eg['events_only_b'])==len(es['events_only_b'])==1
    assert len(gs['events_only_a'])==len(gs['events_only_b'])==1
    first={name:data[name][817876]['summary']for name in names}
    same_initial=all(first['REAL']['RAW_sha256']==first[name]['RAW_sha256']and first['REAL']['clocks_sha256']==first[name]['clocks_sha256']for name in ['YOKE','GUARD','SHAM'])
    selected=[]
    for tick,site in [(817878,[19,53,20]),(817879,[19,53,20]),(817884,target),(817885,target),(817897,[29,65,35]),(817933,[12,17,18]),(817935,[14,15,16]),(817936,[15,15,15]),(817938,[13,17,13])]:
        selected.append({'tick':tick,'site':site,'conditions':{name:point(name,tick,site)for name in names}})
    bank_sites=[[18,53,5],[20,53,5],[14,14,15],[16,14,15]]
    banks_equal=all(point('GUARD',tick,site)==point('SHAM',tick,site)for tick in data['GUARD']for site in bank_sites)
    comparisons={name:read(p/f'control/RECALCULO_PORTABLE_{name}_R02/RECALCULO_GLOBAL_PORTABLE.json')for name in ['REAL_GUARD','REAL_SHAM','GUARD_SHAM']}
    result={'schema':'DEE.PI05.matched_guard_sham.causal_chain.passive.R01','mode':'PASSIVE_RECALCULATION_OF_ROOT_CLOSED_NATIVE_EXPERIMENTS','new_Native_ticks':0,'sources':sources,'code':info(Path(__file__)),'portable_reader':info(tool),'views':views,
      'preconditions':{'REAL_YOKE_GUARD_SHAM_initial_complete_RAW_clocks_equal':same_initial,'common176input_events_parameters_and_admissions_equal':comparable,'GUARD_SHAM_dose177applied_each':views['GUARD']['Native_inputs']['applied']==views['SHAM']['Native_inputs']['applied']==177,'same_original_instrument_hash':len(set(views[n]['instrument_protocol_sha256']for n in names))==1,'fixed_readers_and_original_operand_codec':True,'physical_identity_does_not_imply_whole_operational_identity':True},
      'event_alignment':{'REAL_GUARD':eg,'REAL_SHAM':es,'GUARD_SHAM':gs},'critical_local_neighbourhood':neighbourhood,'causal_update':{'Moore26_identical_GUARD_SHAM_at817884':neighbour_equal,'incoming_four_identical':incoming_equal,'own_state_differs':'GUARD RAW0 vsSHAM active zero-charge+Z','empty_reducer_prediction':predicted_empty,'guard_prediction_matches':predicted_empty['RAW']==ng['after']['RAW'],'matter_prediction':predicted_matter,'sham_prediction_matches':predicted_matter['RAW']==ns['after']['RAW'],'Native_input_at_update_tick':False},'selected_observations':selected,
      'four_reference_banks_RAW_clocks_equal_GUARD_SHAM_all69frames':banks_equal,'global_D_summary':{name:{'frame_count':d['frame_count'],'first_difference':d['first_observed_RAW_difference_tick'],'last_difference':d['last_observed_RAW_difference_tick'],'RAW_difference_counts':sorted(set(r['RAW_difference_sites']for r in d['frames'])),'all_clock_differences_zero':all(r['clocks_difference_sites']==0 for r in d['frames'])}for name,d in comparisons.items()},
      'conclusion':{'demonstrated':'Within this fixed prefix/opportunity, one legal prepared0/SEM4stationary sink intercepts the old zeroZconfiguration before its collision. The matched off-route dose control does not. The now-vacant parent forms17, C/Sforms31 and both original readers produce+1; sham retains C/S14and-1. This supports the specific interference mechanism and a local P0prepared protective capability.','not_demonstrated':'No learned/autonomous guard choice, general self-repair, indefinitely harmless sink, subjective state, unique lineage/source of old zeroZ, whole operational-state identity, new general control policy or integration/promotion is certified here. Reference-bank physical equality is not a material function-retention panel.','preserved_negative':'Unprotected REAL/NONE/YOKE and SHAM all retain the valid wrong negative response. No decoder retuning, RAW/clock cleaning or favourable-state restoration was used by this analysis.','phase_recovery_separate':'Reusing from818074changes phase and requires its own matched control; this prevention contrast cannot certify later recovery.'}}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'output':str(out.resolve()),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'same_initial':same_initial,'common176equal':comparable,'Moore26equal':neighbour_equal,'guard_prediction':result['causal_update']['guard_prediction_matches'],'sham_prediction':result['causal_update']['sham_prediction_matches'],'banks_equal69':banks_equal}))
if __name__=='__main__':main()
