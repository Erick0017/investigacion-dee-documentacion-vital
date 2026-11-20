"""FS publication after a separately guarded official zero-tick lease commit."""
from pathlib import Path
import copy
import time
from common_focal import RUNTIME, atomic, canonical, digest, read, sha

def finalize_lease_tx(home, lease, newNativeProof, ledgerOldSHA, txPath):
    """Callback used only after Native commit/deep/physical verification succeeds.

    A partial publication keeps the transaction marker. It is not retried
    automatically and cannot admit a second owner.
    """
    from ledger_focal import TickLedger
    home = Path(home); txPath = Path(txPath)
    cfg = read(home / 'INSTANCE.json')
    if (lease['instanceId'], lease['lifeId'], lease['sessionId']) != (cfg['instanceId'], cfg['lifeId'], cfg['sessionId']):
        raise ValueError('Exact existing identity required')
    if newNativeProof['nativeTick'] != cfg['nativeTick'] or newNativeProof['lifeId'] != cfg['lifeId']:
        raise ValueError('Zero-tick administrative publication only')
    ledger = TickLedger(RUNTIME / 'estado_demo/LEDGER_SDK.json', cfg['lifeId'], 6, role='focal')
    ledger.register_lease(lease, expected_sha256=ledgerOldSHA)
    scopepath = home / 'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json'
    scope = read(scopepath)
    scope['native_cutoff_utc_epoch'] = lease['hardFinishUtcEpoch']
    scope['last_new_cycle_utc_epoch'] = lease['lastNewUtcEpoch']
    scope['operational_lease'] = lease
    atomic(scopepath, scope)
    hostpath = home / 'sistema/app/HOST_INTEGRAL_V3.json'
    host = read(hostpath); host['native_cutoff_utc_epoch'] = lease['hardFinishUtcEpoch']; atomic(hostpath, host)
    cfg['operationalLease'] = lease; atomic(home / 'INSTANCE.json', cfg)
    pairpath = home / 'SDK_PAIR.json'; pair_updated = False
    if pairpath.exists():
        pair = read(pairpath)
        if pair['sessionId'] != cfg['sessionId'] or pair['localSequence'] != cfg['localSequence'] or digest(pair['snapshot']) != pair['snapshotSha256']:
            raise ValueError('Original paired Agent/World must remain literal')
        old = copy.deepcopy(pair)
        atomic(txPath / 'SDK_PAIR_ANTES_PUBLICAR.json', old, new=True)
        proof = {**pair['backendProof'], **newNativeProof,
                 'backendWriterClosed': True, 'bridgeQuiescent': True,
                 'sessionId': cfg['sessionId'], 'localSequence': cfg['localSequence'],
                 'leaseAdministrativeTransition': {'leaseId': lease['leaseId'], 'newNativeTicks': 0,
                     'previousPairSha256': sha(txPath / 'SDK_PAIR_ANTES_PUBLICAR.json'),
                     'worldSnapshotSha256Unchanged': pair['snapshotSha256']}}
        proof.pop('proofSha256', None); proof['proofSha256'] = digest(proof)
        pair['native'] = newNativeProof; pair['backendProof'] = proof
        pair['leaseAdministrativeTransition'] = proof['leaseAdministrativeTransition']
        if canonical(pair['snapshot']) != canonical(old['snapshot']): raise RuntimeError('World changed during administrative lease')
        atomic(pairpath, pair); pair_updated = True
    result = {'schema': 'DEE.Roblox.SDK.lease_publication.0.1.0', 'leaseId': lease['leaseId'],
              'newNativeTicks': 0, 'ledgerSha256': sha(RUNTIME / 'estado_demo/LEDGER_SDK.json'),
              'scopeSha256': sha(scopepath), 'hostScopeSha256': sha(hostpath),
              'instanceSha256': sha(home / 'INSTANCE.json'), 'pairedWorldUpdated': pair_updated,
              'worldLiteralUnchanged': True, 'notLearnedAutonomousRecovery': True}
    atomic(txPath / 'PUBLICACION_FS.json', result, new=True)
    return result
