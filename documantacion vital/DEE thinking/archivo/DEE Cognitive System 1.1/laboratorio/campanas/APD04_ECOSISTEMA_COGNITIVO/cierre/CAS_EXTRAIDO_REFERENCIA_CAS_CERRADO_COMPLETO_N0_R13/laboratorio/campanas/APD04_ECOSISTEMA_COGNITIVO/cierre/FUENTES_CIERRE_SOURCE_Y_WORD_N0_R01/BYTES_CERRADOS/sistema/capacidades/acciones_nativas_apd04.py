"""APD04 candidate: existing lived choices, no target-aware Python selector.

Importing creates no Runtime and advances no tick. The existing owner passes
its complete lived adapter. This candidate does not install anatomy, teach,
edit RAW/clocks, load a favorable snapshot or store acquired answers.

BALANCE_BIAS20 is a frozen independent-operand representation. Its antecedent
is the retained relative reference difference20 in archived APD03 primaries.
Whether that inherited physical relation can be reused to balance a new world
is a NEW experimental question; installing this module does not establish it.
"""
from capacidades import mente_unificada_01 as comparison
from capacidades import percepcion_cruda_fi01 as perception
from capacidades import ruta_adaptativa_apd02_04 as route
from capacidades import sensor_balanceado_apd03_r02 as presence


VERSION = 'APD04.existing_native_affordances.candidate.R01'
BALANCE_BIAS = 20
BALANCE_COMPONENTS = 128


def select(adapter, raw_bit, detail=False):
    """Return the physical three-way route emission, not a chosen source.

    The caller must freeze its source/primitive-action conversion prospectively.
    The optional raw bit uses exactly the already installed APD03 sensor, not a
    relevance bit, private target, recommended bank or hidden-world identity.
    Consequence must finish the resulting physical delayed-action window.
    """
    if type(raw_bit) is not int or raw_bit not in (0, 1):
        raise ValueError('Only an exact already-public raw fact0/1')
    trial = presence.use(adapter, raw_bit, family='balanced_z_left')
    return {
        'kind': 'APD04_candidate_source_request', 'version': VERSION,
        'physical_choice': trial['reader']['choice'], 'native_trial': trial,
        'fixed_source_or_action_conversion_is_not_defined_here': True,
        'passive_detail_requested': bool(detail),
        'source_expected_or_private_data_received': False,
    }


def finish(adapter, category, mode='real'):
    """One post-effect generic consequence; receives no action or answer."""
    return route.consequence(adapter, category, mode=mode)


def classify(adapter, value, detail=False):
    """Use inherited physical comparison; do not compute a category in Python."""
    if type(value) is not int or not 0 <= value <= 512:
        raise ValueError('One independently observed exact scalar0..512')
    trial = comparison.current(adapter, value, detail=detail)
    return {
        'kind': 'APD04_candidate_scalar_classification', 'version': VERSION,
        'physical_choice': trial['reader']['choice'], 'native_trial': trial,
        'target_category_or_reference_decoded_for_action': False,
        'scope': 'A prepared comparator using this life physical reference; '
                 'not a new learned classification rule merely by this call.',
    }


def balance(adapter, left, right, detail=False):
    """One Native aggregate+comparison; no Python sum, difference or sign.

    The two publicly observed loads remain independent in their fixed codec:
    left -> channel0; right -> channel1 as20-right. The old128-channel native
    tree combines them and the SAME life native comparison emits a direction.
    The other126 samples are explicitly prepared zero-material components.
    An environment may interpret the direction as moving one unit or holding;
    this module never calculates the useful move or an optimal transfer.
    """
    if any(type(value) is not int or not 0 <= value <= BALANCE_BIAS
           for value in (left, right)):
        raise ValueError('Each independently observed load lies in0..20')
    if perception.get(adapter).get('level') != BALANCE_COMPONENTS:
        raise ValueError('The inherited FI01 joint128 body is indispensable')
    components = [0] * BALANCE_COMPONENTS
    components[0] = left
    components[1] = BALANCE_BIAS - right
    trial = perception.frame(adapter, components, detailed=detail)
    return {
        'kind': 'APD04_candidate_native_balance', 'version': VERSION,
        'public_independent_loads': [left, right],
        'frozen_per_operand_bias': BALANCE_BIAS,
        'physical_choice': trial['reader']['choice'], 'native_trial': trial,
        'action_computed_from_observer_sum_difference_or_target': False,
        'scope': 'New reuse test of an inherited comparison relation with a '
                 'prepared independent-operand codec. No acquired EQUILIBRA '
                 'concept, useful action or transfer is established without '
                 'actual reserved environment effects and causal controls.',
    }
