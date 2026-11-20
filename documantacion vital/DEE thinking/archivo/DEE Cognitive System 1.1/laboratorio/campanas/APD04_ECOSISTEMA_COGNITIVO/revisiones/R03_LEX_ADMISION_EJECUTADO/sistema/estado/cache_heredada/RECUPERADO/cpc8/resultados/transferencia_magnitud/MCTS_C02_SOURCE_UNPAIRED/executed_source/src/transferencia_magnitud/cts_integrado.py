"""Fresh CTS profile plus magnitude transfer, with one ownerRuntime.

The base CTS sources are imported unchanged. Source training is a separately
counted real exposure, not a copy of the primary E1 quantity memory.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from dee_thinking.persistence import encode_metadata
from comunicacion.contact_social_regulated import RegulatedContactSocialE1Session, prepare_regulated_contact_social
from transferencia_magnitud.transferencia import prepare_component, attach_recipient, schedule_source


def prepare_magnitude_cts(**options):
    recipe, geometry = prepare_regulated_contact_social(**options)
    material, ports, transfer = prepare_component()
    combined = list(recipe.placements) + material
    sites = [(placement.site.x, placement.site.y, placement.site.z) for placement in combined]
    if len(sites) != len(set(sites)):
        raise ValueError('Fresh CTS magnitude initial support overlap; no overwrite allowed')
    interfaces = list(recipe.interfaces) + ports
    if len({port.name for port in interfaces}) != len(interfaces):
        raise ValueError('Fresh CTS magnitude interface overlap')
    recipe.placements = combined
    recipe.interfaces = interfaces
    geometry['magnitude_transfer'] = transfer
    geometry['resources']['initial_material_sites'] = len(combined)
    geometry['resources']['interfaces'] = len(interfaces)
    geometry['finite_protocol'] = 'CPC8R.magnitudeCTS.0_to616.v1'
    geometry['representation_version'] += '+nativeMagnitudeTransfer1'
    recipe.options = {'CPC8R.relational_pair.geometry': encode_metadata(geometry)}
    return recipe, geometry


class MagnitudeCTSSession(RegulatedContactSocialE1Session):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transferred_quantity = attach_recipient(self.world, self.geometry['magnitude_transfer'], self.state.get('transferred_quantity'))
        self.state.setdefault('magnitude_source_requests', [])
        self.state.setdefault('magnitude_observations', [])

    @classmethod
    def create(cls, identifier='MAGNITUDE_TRANSFER_CTS', **options):
        recipe, geometry = prepare_magnitude_cts(**options)
        return cls(d.OrganizationalWorld.create(recipe), geometry, identifier=identifier)

    def curriculum(self, *, magnitude_value=31, magnitude_mode='paired', magnitude_objects=(18, 45, 31), **options):
        if len(magnitude_objects) != 3:
            raise ValueError('Exactly three recipient actual objects are frozen')
        super().curriculum(**options)
        self.state['magnitude_source_requests'] = schedule_source(self.world, magnitude_value, magnitude_mode)
        for index, value in enumerate(magnitude_objects):
            self.transferred_quantity.present_object(value, reference_time=77, round_index=index)
        self.transferred_quantity.reader_opportunity(reference_time=77)

    def capture_magnitude(self):
        quantity = self.geometry['magnitude_transfer']['quantity']
        self.state['magnitude_observations'].append({'tick': self.tick,
            'reference': self.observe(quantity['reference_site']), 'object': self.observe(quantity['object_site']),
            'center': self.observe(quantity['center']), 'reference_hub': self.observe(quantity['reference_hub'])})

    def run_until(self, tick):
        if type(tick) is not int or tick < self.tick:
            raise ValueError('Monotone tick required')
        for boundary in sorted(value for value in (3, 69, 70, 73, 79, 80, 146, 147, 213, 214, 280, 281) if self.tick < value <= tick):
            super().run_until(boundary)
            self.capture_magnitude()
        return super().run_until(tick)

    def view(self):
        value = super().view()
        quantity = self.geometry['magnitude_transfer']['quantity']
        value['magnitude_transfer'] = {key: self.observe(quantity[key]) for key in ('center', 'reference_site', 'object_site', 'reference_hub')}
        return value

    def receipts(self):
        source = [{**row, 'receipt': exact_receipt(self.world.runtime.receipt(row['id']))} for row in self.state['magnitude_source_requests']]
        return super().receipts() + source + self.transferred_quantity.receipts()

    def save(self, path):
        self.state['transferred_quantity'] = deepcopy(self.transferred_quantity.state)
        return super().save(path)
