"""Participant-side protocol. Receives no teaching map or future outcome.

Input identity chooses its fixed sensor only. Direction is decoded AFTER v27;
the decoder does not choose an action. The same native product continues into
the habitat. No second future, oracle, target or lesson log is accessed here.
"""
from . import memory

def signal_only(world, signal, tick, translation=(0,0,0)):
    world.run_until(tick)
    before=memory.digest(world)
    receipt=memory.present_signal(world,signal,tick)
    world.run_until(tick+3)
    emission=memory.read_emission(world,signal,translation)
    return {'input_tick':tick,'emission_tick':world.runtime.current_tick,
            'before':before,'receipt':memory.receipt(world.runtime,receipt.id),
            'emission':emission,'action_selection':'native direction of this same product; no host routing callback',
            'attribution':'ENTE_NATIVE_EVOLUTION_WITH_FIXED_EXTERNAL_PRESENTATION'}
