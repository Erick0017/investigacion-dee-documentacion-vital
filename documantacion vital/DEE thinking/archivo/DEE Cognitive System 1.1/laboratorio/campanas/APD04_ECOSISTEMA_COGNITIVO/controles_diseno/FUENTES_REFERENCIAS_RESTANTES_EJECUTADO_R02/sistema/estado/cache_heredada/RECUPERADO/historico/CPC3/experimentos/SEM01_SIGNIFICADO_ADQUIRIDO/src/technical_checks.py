"""Bounded technical replays and field-level event reconstruction, not teaching."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.common import identity,put,digest,obs,receipt,sha
from src import habitat,memory,participant

def local_fibre(world,target):
    target=tuple(target);neighbors=[];incoming=[]
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for dz in (-1,0,1):
                if (dx,dy,dz)==(0,0,0):continue
                site=tuple((target[j]+(dx,dy,dz)[j])%67 for j in range(3));value=obs(world,site);neighbors.append(value)
                if value['active'] and value['semantic']==1 and tuple((site[j]+value['direction'][j])%67 for j in range(3))==target:incoming.append(value)
    return {'tick':world.runtime.current_tick,'center':obs(world,target),'Moore26_including_absences':neighbors,'direct_normal_active_incoming':incoming,
            'scope':'Kinematic incoming candidates and observed context, not automatic necessity or a universal inverse of v27'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--wheel',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    import dee_thinking as d
    ident=identity(a.wheel);base=ROOT/'resultados/confirmacion/A_future_UV';case=json.loads((base/'MEASUREMENTS.json').read_text(encoding='utf-8'))
    # Passive on/off from a full native operational state; no research-array clone.
    direct=d.OrganizationalWorld.load_snapshot(str(base/'BEFORE_SIGNAL_S1.deetsnap'));observed=direct.fork();initial=digest(direct)
    for j in range(50):
        obs(observed,memory.hub('S1'));obs(observed,memory.hub('S2'))
    assert digest(observed)==initial==digest(direct)
    a1=participant.signal_only(direct,'S1',84);a2=participant.signal_only(observed,'S1',84)
    assert digest(direct)==digest(observed)
    expected=d.OrganizationalWorld.load_snapshot(str(base/'EMISSION_S1.deetsnap'));assert digest(direct)==digest(expected)
    put(a.output/'PASSIVE_AND_FORK_CHECK.json',{'passive_observations':100,'before_and_after_passive_equal':True,'continued_raw_clocks_equal':True,'direct_and_observed_emissions_equal':a1==a2,'before':initial,'after':digest(direct),'snapshot_restored_target_equal':True})
    # A pending future supply exists in this native snapshot. Each backend uses
    # the complete channels/queue/receipts, not just RAW and clocks.
    physical=[]
    for name,backend,threads in [('lazy',d.Backend.LAZY,1),('dense',d.Backend.DENSE_SEQUENTIAL,1),('parallel',d.Backend.DENSE_PARALLEL,2)]:
        world=d.OrganizationalWorld.load_snapshot(str(base/'S1_USE_T91.deetsnap'))
        pending=[receipt(world,r.id) for r in world.runtime.receipts if str(r.status).lower()=='scheduled']
        world.runtime.execution_options=d.TickOptions(backend,threads);world.run_until(101)
        record={'backend':name,'threads':threads,'final':digest(world),'pending_before':pending,'receipts_after':[receipt(world,r.id) for r in world.runtime.receipts]}
        physical.append(record)
    assert all(x['final']==physical[0]['final'] and x['receipts_after']==physical[0]['receipts_after'] for x in physical)
    expected=d.OrganizationalWorld.load_snapshot(str(base/'S1_USE_T101.deetsnap'));assert digest(expected)==physical[0]['final']
    put(a.output/'BACKEND_PENDING_CONTINUATION.json',{'equal':True,'records':physical,'historical_physical_state_equal':True,'not_new_scientific_replicates':True})
    bank=habitat.bank_spec(memory.hub('S1'),'use.S1',version='v2_delayed_supply');events=[]
    # Two reducer encounters and the later preserved delivery. These are tiny
    # forward replay windows ending at already recorded scientific boundaries.
    for filename,before_tick,after_tick,target,kind,expected_filename in [
      ('EMISSION_S1.deetsnap',90,91,bank['cost_meeting'],'action_consumes_optional_resource','S1_USE_T91.deetsnap'),
      ('S1_USE_T91.deetsnap',94,95,bank['interception'],'native_product_intercepts_threat','S1_USE_T95.deetsnap'),
      ('S1_USE_T95.deetsnap',100,101,bank['function_receiver'],'primary_supply_reaches_receiver','S1_USE_T101.deetsnap')]:
        world=d.OrganizationalWorld.load_snapshot(str(base/filename))
        if filename=='EMISSION_S1.deetsnap':
            habitat.submit_resources(world,bank,87);world.run_until(88);habitat.submit_event(world,bank,'U',87)
        world.run_until(before_tick);pre=local_fibre(world,target);world.run_until(after_tick);post=obs(world,target)
        expected=d.OrganizationalWorld.load_snapshot(str(base/expected_filename));assert digest(world)==digest(expected)
        events.append({'type':kind,'transition':[before_tick,after_tick],'context':pre,'post':post,'complete_raw_clocks_equal_historical_boundary':True})
    parents=[]
    for signal,acquired,sign in [('S1',20,1),('S2',48,-1)]:
        world=d.OrganizationalWorld.load_snapshot(str(base/'BEFORE_SIGNAL_S1.deetsnap'));q=memory.plus(memory.hub(signal),(0,sign,0),83-acquired);parents.append({'signal':signal,'retained_record_before_query':obs(world,q),'actual_acquired_tick':acquired,'scope':'Verified free mobile segment; causal need adjudicated by the separate single-record diagnostic'})
    chain={'initial_history':'EXPERIENCIAS in A_future_UV','actual_sensor_times':[17,45],'memory_at83':parents,'signal_receipt':case['uses'][0]['anticipation']['receipt'],'native_emission':case['uses'][0]['anticipation']['emission'],
      'event_introduced_after_emission':{'emission87':True,'threat_input88':True,'primary_delivery101':True},'replayed_events':events,
      'causal_contrasts':'resultados/causal_memory02/SUMMARY.json','attribution':'EXTERNAL_RECONSTRUCTION_OF_NATIVE_EVENTS','no_interventions_in_replays':True}
    put(a.output/'CAUSAL_CHAIN.json',chain);put(a.output/'IDENTITY.json',ident);print('PASSIVE_BACKEND_PENDING_REPLAYS_AND_NATIVE_CHAIN_VERIFIED')
if __name__=='__main__':main()
