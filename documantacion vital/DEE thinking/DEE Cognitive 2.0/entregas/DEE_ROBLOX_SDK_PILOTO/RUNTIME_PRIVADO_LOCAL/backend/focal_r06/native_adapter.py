"""Bridge-to-official-owner adapter. No Native import or owner creation.

Root supplies one already-started official diagnostic Owner. There is no
fallback participant. Repeated bridge operation IDs reconcile the same queue
entry; this class never manufactures replacement IDs or retries experience.
"""
import hashlib
import json

KINDS = {'decision': 'eci01-rbx01-decision',
         'query_sensor': 'eci01-rbx01-query-sensor',
         'function': 'eci01-rbx01-function',
         'feedback': 'eci01-rbx01-feedback'}


class NativeUnavailable(RuntimeError):
    pass


class NativeAdapter:
    identity = 'LIVE_NATIVE'

    def __init__(self, owner):
        if owner is None or not callable(getattr(owner, 'material', None)):
            raise NativeUnavailable('Root must supply one live official finite owner')
        self.owner = owner
        self.public_life_id = getattr(owner, 'life', None)

    def execute(self, kind, payload, context):
        if kind not in KINDS:
            raise ValueError('Closed Native phase kind')
        if set(context) != {'session_id', 'sequence', 'observation_id', 'operation_id', 'mode'}:
            raise ValueError('Exact Native correlation context')
        literal = {'modo': KINDS[kind], 'payload': payload, 'context': context}
        result = self.owner.material(context['operation_id'], literal,
                                     feedback='omit', actuator='closed')
        # Official persistent service returns outer before/after plus rows.
        rows = result.get('rows')
        if rows is None and isinstance(result.get('result'), dict):
            rows = result['result'].get('rows')
        if not isinstance(rows, list) or len(rows) != 1:
            raise NativeUnavailable('Native exact single-phase result absent; preserve same operation ID')
        value = rows[0]
        if not isinstance(value, dict) or value.get('version') != 'DEE.Roblox.SDK.focal.native.0.1.0':
            raise NativeUnavailable('Native phase version mismatch; preserve')
        # Full actual observations/receipts/traces are durably preserved by
        # the Native owner queue and RBX events journal. The web record keeps
        # their exact correlation/hash, within its independent16KiB ceiling.
        encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode('utf8')
        concise = {key: content for key, content in value.items() if key != 'evidence'}
        concise['evidence'] = {'native_request_id': context['operation_id'],
                               'native_phase_sha256': hashlib.sha256(encoded).hexdigest(),
                               'full_evidence': 'Official Native queue result and DEE_SDK_NATIVE_0_1_0/events.jsonl'}
        return concise


def create_adapter(config):
    if not isinstance(config, dict) or set(config) != {'owner'}:
        raise NativeUnavailable('Factory requires Root-injected official owner only')
    return NativeAdapter(config['owner'])
