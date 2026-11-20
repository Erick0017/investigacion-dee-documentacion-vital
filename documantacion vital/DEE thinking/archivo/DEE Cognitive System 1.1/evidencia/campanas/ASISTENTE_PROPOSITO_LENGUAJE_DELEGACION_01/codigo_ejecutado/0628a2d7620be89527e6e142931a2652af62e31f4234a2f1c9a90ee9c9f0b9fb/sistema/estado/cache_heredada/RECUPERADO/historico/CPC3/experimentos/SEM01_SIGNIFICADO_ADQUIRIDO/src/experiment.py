"""SEM01 experience generator and external evaluator over one native MAIN.

Only generate_training knows the pairing. Participant signal_only has a
separate minimal signature. Outcome teachers come from present native supply
delivery, not from the generator's event label or the evaluator's answer.
"""
from pathlib import Path
import json
from . import memory,habitat,participant
from .common import put,append,digest,obs,receipt

TRAINING={'S1':17,'S2':45}
QUERY={'S1':84,'S2':112}
TRAIN_EMIT={'S1':3,'S2':31}
SIGNALS=('S1','S2')

def descriptors(translation=(0,0,0)):
    t=translation
    return {
      'train.S1':habitat.bank_spec(memory.plus((10,10,58),(0,0,0),translation=t),'train.S1',version='v2_delayed_supply'),
      'train.S2':habitat.bank_spec(memory.plus((50,10,58),(0,0,0),translation=t),'train.S2',version='v2_delayed_supply'),
      'use.S1':habitat.bank_spec(memory.hub('S1',t),'use.S1',version='v2_delayed_supply'),
      'use.S2':habitat.bank_spec(memory.hub('S2',t),'use.S2',version='v2_delayed_supply')}

def prepare(d,translation=(0,0,0),signal_order=SIGNALS,signal_payload=5):
    if tuple(sorted(signal_order))!=SIGNALS or len(signal_order)!=2:raise ValueError('Two distinct fixed signal identities required')
    if type(signal_payload) is not int or signal_payload not in (5,7):raise ValueError('Published campaign signal payload5 or7 required')
    world=memory.create_world(d,translation)
    banks=descriptors(translation)
    for bank in banks.values():habitat.declare_bank_interfaces(world,bank,True)
    # Neutral operational metadata: no U/V assignment, target, case ID, lesson
    # log or answer. The body never reads these values to choose a direction.
    world.runtime.set_snapshot_metadata('sem01.neutral_protocol',json.dumps({'version':1,'translation':list(translation),'signal_order':list(signal_order),'signal_payload':signal_payload,'training_slots':[17,45],'query_slots':[84,112]},separators=(',',':')))
    return world,banks

def current_outcome_sensor(world,bank):
    """Fixed EXTERNAL sensor of present function, not a label/utility sensor.

    U denotes absence of the declared supply; V its actual present delivery.
    Every RAW/clock is retained so a failure of this sensor can be examined.
    """
    value=obs(world,bank['function_receiver'])
    delivered=value['active'] and value['s_reg']==7 and value['direction']==[0,1,0]
    return {'observation':value,'observed_class':'V' if delivered else 'U',
            'scope':'current local delivery; absence is classified by an external fixed transducer, not a native absence detector'}

def generate_training(world,banks,pairing,mode,out,translation=(0,0,0),signal_order=SIGNALS,signal_payload=5):
    rows=[];ids=[]
    for slot,signal in enumerate(signal_order):
        emit=3+28*slot;tick=17+28*slot;bank=banks['train.'+signal]
        if mode not in ('signals_only','empty'):
            world.run_until(emit);resources=habitat.submit_resources(world,bank,emit);ids.extend(r.id for r in resources)
            world.run_until(emit+1);r=habitat.submit_event(world,bank,pairing[signal],emit);ids.append(r.id)
        world.run_until(tick)
        sensed=current_outcome_sensor(world,bank)
        row={'signal':signal,'effect_tick':tick,'generator_physical_event':pairing[signal],
             'present_sensor':sensed,'mode':mode,'signal_accompanies':'current supply effect, not the earlier threat launch',
             'body_edits':[]}
        # In all paired cases this packet is generated from the actual local
        # sensor. It is broadcast to BOTH fixed sensory regions independently
        # of signal identity or the proposed association.
        if mode not in ('signals_only','empty'):
            receivers=memory.broadcast_outcome(world,sensed['observed_class'],tick);ids.extend(r.id for r in receivers)
            row['outcome_receipts']=[r.id for r in receivers]
        if mode not in ('outcomes_only','empty'):
            signal_tick=tick+1 if mode=='unpaired' else tick
            r=world.submit('signal.'+signal,signal_payload,signal_tick);ids.append(r.id);row['signal_receipt']=r.id;row['signal_tick']=signal_tick;row['signal_payload']=signal_payload
        append(out/'EXPERIENCIAS.jsonl',row);rows.append(row)
        world.run_until(tick+5)
        world.save_snapshot(str(out/('AFTER_'+signal+'_EXPERIENCE.deetsnap')))
    world.run_until(83)
    world.save_snapshot(str(out/'BEFORE_SIGNAL_S1.deetsnap'))
    world.save_snapshot(str(out/'BEFORE_FIRST_SIGNAL.deetsnap'))
    return {'experiences':rows,'actual_receipts':[receipt(world,i) for i in ids],
            'all_teachers_derived_from_current_physical_sensor':True,
            'history_during_native_continuity':digest(world)}

def execute_uses(world,banks,events,out,translation=(0,0,0),control=None,signal_order=SIGNALS,signal_payload=5):
    """World events are introduced only AFTER the native antecedent emission."""
    uses=[]
    for slot,signal in enumerate(signal_order):
        tick=84+28*slot;world.run_until(tick-1)
        world.save_snapshot(str(out/('BEFORE_SIGNAL_'+signal+'.deetsnap')))
        operations_before=list(world.external_operations)
        # No events/resources for this future episode exist in the queue here.
        anticipation=participant.signal_only(world,signal,tick,translation,signal_payload)
        emit=anticipation['emission_tick'];bank=banks['use.'+signal]
        append(out/'PREDICCIONES.jsonl',anticipation)
        world.save_snapshot(str(out/('EMISSION_'+signal+'.deetsnap')))
        diagnostic=None
        if control in ('no_action','always_protect'):
            import dee_thinking as d
            site=memory.hub(signal,translation);pre=obs(world,site)
            edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.raw=0;edit.label='explicit emitted-product cut after antecedent measurement'
            world=world.diagnostic_fork([edit],True)
            post=obs(world,site);assert post['raw']==0 and post['clock']==pre['clock']
            diagnostic={'type':'DIAGNOSTIC_FORK_AFTER_EMISSION','pre':pre,'post':post,'clock_unchanged':True,'shared_memory_product_also_removed':True}
        ids=[r.id for r in habitat.submit_resources(world,bank,emit)]
        if control=='always_protect':
            r=world.submit(bank['prefix']+'.reference_action',21,emit);ids.append(r.id)
            diagnostic['constant_reference_action']=r.id
        captures={};trace=[]
        for now in range(emit,emit+15):
            if now==emit+1:
                # This is the independent, fixed episode generator. Neither
                # anticipated_class nor native RAW is read to choose the event.
                event=habitat.submit_event(world,bank,events[signal],emit);ids.append(event.id)
            trace.append(habitat.read_bank(world,bank,emit,captures))
            if now in (emit+4,emit+8,emit+14):world.save_snapshot(str(out/(signal+'_USE_T'+str(now)+'.deetsnap')))
            if now<emit+14:world.advance()
        evaluation=habitat.evaluate_captures(captures)
        predicted=anticipation['emission']['anticipated_class']
        uses.append({'signal':signal,'anticipation':anticipation,'generator_later_event':events[signal],
          'prediction_correct':None if predicted is None else predicted==events[signal],
          'context_before_query':operations_before,'diagnostic':diagnostic,'bank':bank,'trace':trace,
          'evaluation':evaluation,'actual_receipts':[receipt(world,i) for i in ids]})
        append(out/'USES.jsonl',uses[-1])
    return world,uses

def run_case(spec,out):
    import dee_thinking as d
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    translation=tuple(spec.get('translation',(0,0,0)))
    order=tuple(spec.get('signal_order',SIGNALS));payload=spec.get('signal_payload',5)
    world,banks=prepare(d,translation,order,payload);initial=digest(world)
    world.save_snapshot(str(out/'MAIN_T0.deetsnap'))
    pairing=spec.get('pairing',{'S1':'U','S2':'V'})
    teaching=generate_training(world,banks,pairing,spec.get('mode','paired'),out,translation,order,payload)
    world,uses=execute_uses(world,banks,spec.get('future_events',pairing),out,translation,spec.get('control'),order,payload)
    world.save_snapshot(str(out/'MAIN_FINAL.deetsnap'))
    result={'case':spec,'mode':'EXPERIENCE_PROTOCOL_AND_NATIVE_ACTION_ONE_RUNTIME','instrument_version':d.__version__,
      'initial':initial,'teaching':teaching,'uses':uses,'final':digest(world),
      'external_operations_actual':list(world.external_operations),'diagnostic_edits_actual':[str(x) for x in world.diagnostic_edits],
      'scope':'S1/S2 learn directional consequences through fixed external current-outcome transduction; the useful action coupling is prepared, not independently acquired utility'}
    put(out/'MEASUREMENTS.json',result);return result
