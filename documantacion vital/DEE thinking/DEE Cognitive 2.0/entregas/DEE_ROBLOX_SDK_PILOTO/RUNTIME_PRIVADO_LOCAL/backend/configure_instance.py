"""Generate diagnostic paths and finite scopes; no Native runtime imports."""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sdk_common import RUNTIME, SCHEMA, atomic, budget, read, sha

def create_scopes(home, cfg, runtime=RUNTIME):
    home = Path(home); runtime = Path(runtime)
    window = budget(runtime, now=0); source = runtime / 'dependencias/SDK_SOURCES.json'
    pinned = read(source); system = home / 'sistema'
    lease = cfg.get('operationalLease', {'schema': 'DEE.Roblox.SDK.operational_lease.0.1.0',
        'leaseId': 'UNSTARTED_PREPARATION_ONLY', 'instanceId': cfg['instanceId'], 'lifeId': cfg['lifeId'], 'sessionId': cfg['sessionId'],
        'startUtcEpoch': window['startUtcEpoch'], 'lastNewUtcEpoch': window['lastNewUtcEpoch'], 'hardFinishUtcEpoch': window['hardFinishUtcEpoch'],
        'additionalCycles': 3, 'startingCompletedCycles': 0, 'startingConsumedTicks': 0, 'cumulativeCycleCap': 3,
        'validationCampaign': True, 'validationCampaignSha256': sha(runtime / 'configuracion/VENTANA_CONGELADA.json')})
    c = {'schema': 'DEE.RBX01.fixed_native_scope.INTEGRAL.V3.R01', 'life_id': cfg['lifeId'],
         'role': 'pilot', 'max_cycles': 3, 'max_ticks_per_cycle': 4096, 'max_total_ticks': 12288,
         'max_raw_support': 10000, 'monitor_tick_block': 16, 'max_permission_stock': 200,
         'source_tick': 991187, 'source_snapshot_sha256': 'b3163197548980355c45c6ffd57d2785b3a5e75cf71d8de3afb6b6ffdd4722d1',
         'native_cutoff_utc_epoch': lease['hardFinishUtcEpoch'],
         'last_new_cycle_utc_epoch': lease['lastNewUtcEpoch'], 'operational_lease': lease, 'sealed': True,
         'sensor_codec': 'products_v1', 'q2_sensor_codec': 'price_tag_v1', 'q2_sensor_arm': 'local_tag',
         'parent_completed_opportunities': 28, 'code_scope_manifest_sha256': sha(source),
         'feedback_arm': 'real', 'teacher_mode': 'omitted', 'sources_sha256': pinned['nativeSources'],
         'input_codec': {'Q1': 'unchanged products_v1', 'Q2': 'one legal datum pulse rawPrice0..2+3*fixed localTag0..5; constant_tag2 control; omission staysNone'}}
    atomic(system / 'capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json', c)
    app = system / 'app'
    host_names = ('servicio_eventos_v3.py', 'cache_fuentes_C02.py')
    inherited = ('servicio_persistente.py', 'mundo_genesis_apd05.py', 'cola_local.py', 'lives.py', 'process_control.py')
    h = {'schema': 'DEE.RBX01.INTEGRAL.V3.host_scope.v1', 'sealed': True,
         'system': '.', 'life': cfg['lifeId'], 'event_driven': True, 'single_initial_resume': True,
         'native_cutoff_utc_epoch': lease['hardFinishUtcEpoch'], 'immutable_source_cache': True,
         'host_sources_sha256': {n: sha(app / n) for n in host_names},
         'inherited_sources_sha256': {n: sha(app / n) for n in inherited},
         'new_native_ticks_when_idle': 0, 'threads': 1}
    atomic(app / 'HOST_INTEGRAL_V3.json', h)
    return {'scopeSha256': sha(system / 'capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json'),
            'hostScopeSha256': sha(app / 'HOST_INTEGRAL_V3.json'), 'newNativeTicks': 0}
