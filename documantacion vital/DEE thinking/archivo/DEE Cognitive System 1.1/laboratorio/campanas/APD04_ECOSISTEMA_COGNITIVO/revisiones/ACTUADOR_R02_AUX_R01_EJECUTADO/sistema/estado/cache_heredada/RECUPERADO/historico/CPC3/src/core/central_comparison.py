"""Explicit observed consequence perturbs the live MAIN relational gradient.

No prediction/error is read to choose a report. A Boolean physical sensor
outcome chooses its fixed signed diagonal codec, exactly as an input device.
The gradient and the resulting comparison emission are calculated by v27.
"""
import dee_thinking as d
from core.comparison import coordinate,make_interface,plus,observed


def declare_comparison_channels(entity):
    """Inert declarations, before experience; no RAW, clock or body edit."""
    for sign in (-1,1):
        name='actual_report.'+('positive' if sign>0 else 'negative')
        entity.world.declare_interface(make_interface(name,plus(entity.origin,(sign,0,sign)),(0,0,sign)))
    return entity


def present_current_actual_report(entity):
    """Observe an actual current packet, encode it, evolve one native tick.

    `habitat.sample` is the declared external environment's sensory law, not
    the evaluator's error or a rollout. Only its current observed result is
    allowed to select an input code. Pre-readout is audit data only.
    """
    before=entity.observe();actual=entity.habitat.sample()
    sign=1 if actual['arrived'] else -1
    name='actual_report.'+('positive' if sign>0 else 'negative')
    tick=entity.tick;r=entity.world.submit(name,1,tick)
    entity.operation_calls.append({'operation':'submit','channel':name,'value':1,'tick':tick,
        'receipt_id':r.id,'source':'CURRENT_ACTUAL_PACKET_OUTCOME_ONLY',
        'codec':'true -> positive diagonal/z; false -> negative diagonal/z; no comparison with prediction'})
    entity._advance_to(tick+1)
    after=entity.observe();rr=entity.world.runtime.receipt(r.id)
    old=before['physical_output']
    represented=bool(old['active'] and old['direction'][0] in (-1,1)
                     and old['direction'][2]==0)
    return entity._event('CURRENT_CONSEQUENCE_NATIVE_COMPARISON',{
        'source_actual':actual,'input_receipt':{'id':r.id,'status':str(rr.status),
          'reason':rr.reason,'effective_tick':rr.effective_tick},
        'before_audit_only':before,'after_native':after,
        'comparison_decoder':decode_current_comparison(entity,represented),
        'modality':'OBSERVED_EXTERNAL_EVENT_TO_NATIVE_GRADIENT',
        'computed_error_injected':False,'direct_RAW_clock_writes':0})


def decode_current_comparison(entity,represented_expectation=None):
    """Fixed passive decoder of the current physical output, not history."""
    o=observed(entity.world.runtime.observe(entity.world.view('body').spec.comparator))
    dr=o['direction'];has_marker=o['active'] and dr[2]!=0
    return {'physical_output':o,'signed_comparison_marker_present':has_marker,
            'represented_expectation_before_report':represented_expectation,
            'presentation':('coincidencia_direccional' if dr[0]==0 else 'discrepancia_direccional')
                            if has_marker and represented_expectation is not False else None,
            'validity':'OUTSIDE_SINGLETON_EXPECTATION_DOMAIN' if represented_expectation is False else 'CURRENT_NATIVE_MARKER',
            'scope':'Meaning applies to a represented singleton expectation in the finite +/-1 relation domain; H0 is not given a false expectation'}
