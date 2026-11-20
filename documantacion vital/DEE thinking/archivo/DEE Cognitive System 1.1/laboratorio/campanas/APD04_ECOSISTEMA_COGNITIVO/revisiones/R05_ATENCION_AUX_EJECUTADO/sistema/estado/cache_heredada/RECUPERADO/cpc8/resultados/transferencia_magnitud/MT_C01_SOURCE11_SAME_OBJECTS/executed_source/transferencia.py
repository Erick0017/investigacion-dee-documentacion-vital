"""Acquire a magnitude, route that native carrier into a new comparator.

Both zero-load formatters and all recipient supports are prepared fromT0.
Only the source receives reference experience. No callback copies its value,
direction, output or state into the recipient. One ownerRuntime is constructed.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from integracion.quantity_core import QuantitySession, prepare as prepare_quantity


def move(site, direction, count=1):
    return [(int(site[i]) + int(direction[i]) * count) % 67 for i in range(3)]


def interface(name, site, direction):
    channel = d.ChannelSpec()
    channel.name = name
    channel.injection_site = d.Coordinate(*site)
    channel.direction = d.Direction(*direction)
    channel.state = 1
    channel.semantic = 1
    channel.allow_experience = True
    channel.allow_probe = True
    result = d.InterfaceSpec()
    result.name = name
    result.channel = channel
    return result


def prepare_component():
    """Return inert placements/interfaces/geometry for a fresh N67 world."""
    recipe, quantity = prepare_quantity(center=(21, 59, 40), profile='transient', guards='on_path')
    ports = list(recipe.interfaces)
    for port in ports:
        port.name = 'B.' + port.name
        channel = port.channel
        channel.name = 'B.' + channel.name
        port.channel = channel
    source = [10, 50, 40]
    destination = [20, 60, 40]
    additional = [interface('transfer.source.cue', move(source, (-1, 0, 0), -3), (-1, 0, 0)),
                  interface('transfer.source.resource', move(source, (1, 1, 0), -3), (1, 1, 0)),
                  interface('transfer.source.formatter', move(source, (1, 0, 0), -3), (1, 0, 0)),
                  interface('transfer.recipient.formatter', move(destination, (-1, 0, 0), -3), (-1, 0, 0))]
    ports += additional
    if len({port.name for port in ports}) != len(ports):
        raise ValueError('Transfer interface collision')
    geometry = {'schema': 'CPC8R.native.magnitude.transfer.component.v1', 'N': 67, 'quantity': quantity,
                'source': source, 'destination_reference_hub': destination, 'reference_time': 77,
                'ticks': {'source_acquired': 3, 'source_arrival': 70, 'receiver_arrival': 80,
                          'comparisons': [147, 214, 281]},
                'fixed_interface_translation': 'quantity.* -> B.quantity.*, purely lexical fixed port addressing',
                'prepared': 'Seven recipient supports/interceptors, two zero-load formatting opportunities and all ports atT0. No source reference in initialplacements.',
                'acquired': 'Only source receives cue5+actualvalue. Its native value+5 carrier changes direction through zero-load native encounters and becomes recipient reference.',
                'scope': 'Finite N67 native magnitude-transfer construction; no cloning, assistance, history table, host output-to-input copy or arbitrary organization reinstantiation.',
                'resources': {'initial_material_sites': len(recipe.placements), 'interfaces': len(ports), 'source_training_inputs': 2,
                              'fixed_zero_load_formatters': 2, 'recipient_object_inputs': 6, 'recipient_reader_requests': 3,
                              'basic_buffers_bytes': 32 * 67 ** 3}}
    return list(recipe.placements), ports, geometry


class RecipientQuantitySession(QuantitySession):
    def input(self, port, payload, tick, probe=False):
        if not port.startswith('quantity.'):
            raise ValueError('Only fixed recipientquantity operations are translated')
        return super().input('B.' + port, payload, tick, probe)


def attach_recipient(world, geometry, state=None):
    return RecipientQuantitySession(world, deepcopy(geometry['quantity']), state)


def schedule_source(world, value, mode='paired'):
    """Schedule literal source experience and identical formatter opportunities."""
    if type(value) is not int or not 0 <= value <= 19600 or mode not in ('paired', 'unpaired', 'omitted'):
        raise ValueError('Outside finite actual-value source protocol')
    requests = []
    inputs = [] if mode == 'omitted' else [('transfer.source.cue', 5, int(mode == 'unpaired')),
                                           ('transfer.source.resource', value, 0)]
    inputs += [('transfer.source.formatter', 0, 67), ('transfer.recipient.formatter', 0, 77)]
    for port, payload, tick in inputs:
        receipt = world.submit(port, payload, tick)
        requests.append({'port': port, 'payload': payload, 'requested_tick': tick, 'id': int(receipt.id),
                         'initial_receipt': exact_receipt(receipt)})
    return requests


def prepare_standalone():
    placements, ports, geometry = prepare_component()
    recipe = d.OrganizationRecipe.research(67, placements, 0)
    recipe.interfaces = ports
    recipe.execution = d.TickOptions(d.Backend.LAZY, 1)
    recipe.domain = geometry['scope']
    organization = d.OrganizationSpec()
    organization.id = 'MAGNITUDE_TRANSFER_A_B'
    organization.recipe_id = geometry['schema']
    organization.ports = {'source': d.Coordinate(*geometry['source']),
                          'recipient_reference': d.Coordinate(*geometry['destination_reference_hub']),
                          'recipient_reader': d.Coordinate(*geometry['quantity']['center'])}
    recipe.organizations = [organization]
    return d.OrganizationalWorld.create(recipe), geometry
