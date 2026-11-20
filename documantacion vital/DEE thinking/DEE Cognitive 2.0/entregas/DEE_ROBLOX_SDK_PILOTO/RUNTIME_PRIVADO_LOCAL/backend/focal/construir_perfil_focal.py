"""Mechanical FOCAL6 overlay. Writes only backend/focal, never demo sources.

No DEE import, instance preparation, Native execution or Studio calls.
The phase mechanisms are copied literally; only namespace/supply6 is extended.
"""
from pathlib import Path
import ast
import hashlib
import json
import os

HERE = Path(__file__).resolve().parent
BACKEND = HERE.parent
ROOT = BACKEND.parent

def read(path): return Path(path).read_text('utf-8-sig')
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def once(text, old, new):
    if text.count(old) != 1: raise ValueError('Exact FOCAL source anchor: ' + old[:100])
    return text.replace(old, new)
def save(name, text):
    ast.parse(text); path = HERE / name
    if path.exists():
        if path.read_bytes() != text.encode('utf8'): raise FileExistsError('Preserve different FOCAL source ' + name)
    else:
        with path.open('x', encoding='utf8', newline='\n') as out: out.write(text)

def build():
    freeze_path = next((ROOT / 'configuracion' / n for n in ('FUENTES_RUNTIME_CONGELADAS_R03.json','FUENTES_RUNTIME_CONGELADAS_R02.json','FUENTES_RUNTIME_CONGELADAS.json') if (ROOT / 'configuracion' / n).exists()))
    frozen = json.loads(freeze_path.read_text('utf8'))
    before = {r['file']: digest(ROOT / r['file']) for r in frozen['members']}
    if before != {r['file']: r['sha256'] for r in frozen['members']}: raise RuntimeError('Demo freeze changed before FOCAL generation')
    common = read(BACKEND / 'sdk_common.py').replace('parents[1]', 'parents[2]')
    common = common.replace("NATIVE_VERSION = 'DEE.Roblox.SDK.native.0.1.0'", "NATIVE_VERSION = 'DEE.Roblox.SDK.focal.native.0.1.0'")
    common = once(common, "    return home, cfg\n", "    if cfg.get('profile') != 'FOCAL': raise ValueError('FOCAL profile only')\n    return home, cfg\n")
    common = common.replace("lease['additionalCycles'] <= 3", "lease['additionalCycles'] <= 6").replace("lease['additionalCycles'] <= 3", "lease['additionalCycles'] <= 6")
    common = common.replace("lease['additionalCycles'] <= 3", "lease['additionalCycles'] <= 6")
    common = common.replace("lease['startingCompletedCycles'] + lease['additionalCycles'] <= 3", "lease['startingCompletedCycles'] + lease['additionalCycles'] <= 6")
    common = once(common, '1 <= local <= 6', '1 <= local <= 12')
    save('common_focal.py', common)
    actor = read(ROOT / 'dependencias/sdk_bundle/rbx07_native_v3.py')
    actor = actor.replace('DEE.Roblox.SDK.native.0.1.0', 'DEE.Roblox.SDK.focal.native.0.1.0')
    actor = actor.replace('DEE.Cognitive.Roblox.SDK.native.0.1.0', 'DEE.Cognitive.Roblox.SDK.focal.native.0.1.0')
    actor = actor.replace('DEE.Cognitive.Roblox.SDK.CODE_SCOPE.0.1.0', 'DEE.Cognitive.Roblox.SDK.FOCAL.CODE_SCOPE.0.1.0')
    actor = actor.replace('DEE.Cognitive.Roblox.SDK.LEASE.0.1.0', 'DEE.Cognitive.Roblox.SDK.FOCAL.LEASE.0.1.0')
    actor = actor.replace('DEE_SDK_NATIVE_0_1_0', 'DEE_SDK_FOCAL_NATIVE_0_1_0')
    actor = once(actor, "role_limits = {'pilot': 3}", "role_limits = {'focal': 6}")
    actor = once(actor, "0 < lease['cumulativeCycleCap'] <= 3", "0 < lease['cumulativeCycleCap'] <= 6")
    save('rbx07_native_v3.py', actor)
    identity = read(ROOT / 'dependencias/sdk_bundle/rbx07_identity_v3.py').replace('DEE.Roblox.SDK.identity.0.1.0', 'DEE.Roblox.SDK.focal.identity.0.1.0')
    save('rbx07_identity_v3.py', identity)
    save('rbx07_funciones_v3.py', read(ROOT / 'dependencias/sdk_bundle/rbx07_funciones_v3.py'))
    owner = read(BACKEND / 'sdk_owner.py')
    owner = once(owner, 'REVISION_ROOT = Path(__file__).resolve().parents[1]', 'REVISION_ROOT = Path(__file__).resolve().parents[2]')
    owner = once(owner, "REVISION_ROOT / 'backend/ledger_sdk.py'", "REVISION_ROOT / 'backend/focal/ledger_focal.py'")
    save('sdk_owner_focal.py', owner)
    adapter = read(BACKEND / 'native_adapter.py').replace('DEE.Roblox.SDK.native.0.1.0', 'DEE.Roblox.SDK.focal.native.0.1.0').replace('DEE_SDK_NATIVE_0_1_0', 'DEE_SDK_FOCAL_NATIVE_0_1_0')
    save('native_adapter_focal.py', adapter)
    factory = read(BACKEND / 'native_factory.py').replace('from sdk_common import ', 'from common_focal import ')
    factory = factory.replace("'sdk_owner.py'", "'sdk_owner_focal.py'").replace("'native_adapter.py'", "'native_adapter_focal.py'")
    factory = once(factory, 'def create_session(home, cfg, window):\n', "def create_session(home, cfg, window):\n    if cfg.get('profile') != 'FOCAL': raise ValueError('FOCAL_ONLY_BEFORE_NATIVE')\n")
    save('native_factory_focal_R02.py', factory)
    service = read(BACKEND / 'servicio_sdk.py').replace('from sdk_common import ', 'from common_focal import ')
    service = service.replace('from native_factory import create_session', 'from native_factory_focal_R02 import create_session')
    service = once(service, "'runtimeVersion': '0.1.0',", "'runtimeVersion': '0.1.0', 'profile': 'FOCAL',")
    service = once(service, "'profile': 'FOCAL',", "'profile': 'FOCAL', 'focalCondition': self.cfg['focalCondition'],")
    save('servicio_focal_R03.py', service)
    lease = read(BACKEND / 'preparacion/renovar_lease_sdk.py')
    lease = lease.replace("'DEE.Cognitive.Roblox.SDK.LEASE.0.1.0'", "'DEE.Cognitive.Roblox.SDK.FOCAL.LEASE.0.1.0'")
    lease = lease.replace("'DEE.Cognitive.Roblox.SDK.native.0.1.0'", "'DEE.Cognitive.Roblox.SDK.focal.native.0.1.0'")
    lease = once(lease, "Path(__file__).with_name('preparar_instancia_par28_sdk.py')", "Path(runtime) / 'backend/preparacion/preparar_instancia_par28_sdk.py'")
    lease = once(lease, "Path(runtime) / 'backend/sdk_common.py'", "Path(runtime) / 'backend/focal/common_focal.py'")
    lease = lease.replace("lease['startingCompletedCycles'] < 3", "lease['startingCompletedCycles'] < 6")
    lease = lease.replace("lease['additionalCycles'] <= 3", "lease['additionalCycles'] <= 6")
    lease = lease.replace("lease['startingCompletedCycles'] + lease['additionalCycles'] <= 3", "lease['startingCompletedCycles'] + lease['additionalCycles'] <= 6")
    lease = once(lease, "def _closed(fs, common, home, cfg, c):\n", "def _closed(fs, common, home, cfg, c):\n    need(cfg.get('profile') == 'FOCAL' and cfg.get('focalCondition') in ('OSCILANTE','CONTROL') and c.get('profile') == 'FOCAL', 'FOCAL_PROFILE_REQUIRED_BEFORE_NATIVE')\n    pin = c.get('focalOverlay', {})\n    need(pin.get('condition') == cfg['focalCondition'] and pin.get('sourceManifest') == 'backend/focal/PERFIL_FOCAL_CONGELADO.json', 'EXACT_FOCAL_CONTEXT')\n    root = home.parents[2]\n    manifest = root / 'backend/focal/PERFIL_FOCAL_CONGELADO.json'\n    need(fs.hash_file(manifest) == pin.get('sourceManifestSha256'), 'FOCAL_CODE_MANIFEST_CHANGED')\n    need(fs.read(manifest)['nativeSources'] == pin.get('nativeSources'), 'EXACT_FOCAL_NATIVE_SOURCE_SET')\n    for name, expected in pin['nativeSources'].items():\n        need(Path(name).name == name and fs.hash_file(home / 'sistema/capacidades' / name) == expected, 'FOCAL_CODE_CHANGED_BEFORE_NATIVE:' + name)\n")
    save('lease_focal_R02.py', lease)
    publication = read(BACKEND / 'publicar_lease.py').replace('from sdk_common import ', 'from common_focal import ')
    publication = publication.replace('from ledger_sdk import TickLedger', 'from ledger_focal import TickLedger')
    publication = once(publication, "cfg['lifeId'], 3, role='pilot'", "cfg['lifeId'], 6, role='focal'")
    save('publicar_focal.py', publication)
    start = read(BACKEND / 'iniciar_sesion.py').replace('from sdk_common import ', 'from common_focal import ')
    start = once(start, "Path(__file__).parent / 'preparacion/renovar_lease_sdk.py'", "Path(__file__).parent / 'lease_focal_R02.py'")
    start = start.replace('1 <= cycles <= 3', '1 <= cycles <= 6').replace("world['cycles'] + cycles > 3", "world['cycles'] + cycles > 6")
    start = once(start, "    if type(minutes) is not int", "    if validation_campaign is not True: raise ValueError('FOCAL requires the current finite validation campaign')\n    if type(minutes) is not int")
    start = start.replace("from publicar_lease import finalize_lease_tx", "from publicar_focal import finalize_lease_tx")
    start = once(start, "Path(__file__).with_name('servicio_sdk.py')", "Path(__file__).with_name('servicio_focal_R03.py')")
    start = once(start, "default=1)", "default=6)")
    start = once(start, "p.add_argument('--no-serve', action='store_true');", "p.add_argument('--port', type=int, default=8896); p.add_argument('--no-serve', action='store_true');")
    start = once(start, "'--instance', a.instance, '--mode'", "'--port', str(a.port), '--instance', a.instance, '--mode'")
    save('iniciar_focal_R03.py', start)
    # Scientific phase mechanisms must remain identical ASTs, not just labels.
    old = ast.parse(read(ROOT / 'dependencias/sdk_bundle/rbx07_native_v3.py')); new = ast.parse(actor)
    mechanisms = ('first','second','function','feedback','BoundedTime')
    for name in mechanisms:
        a = next(x for x in old.body if getattr(x,'name',None) == name)
        b = next(x for x in new.body if getattr(x,'name',None) == name)
        if ast.dump(a, include_attributes=False) != ast.dump(b, include_attributes=False): raise RuntimeError('Mechanism changed:' + name)
    after = {r['file']: digest(ROOT / r['file']) for r in frozen['members']}
    if before != after: raise RuntimeError('Frozen demo source changed')
    sources = {n: digest(HERE / n) for n in ('rbx07_native_v3.py','rbx07_identity_v3.py','rbx07_funciones_v3.py')}
    output = {'schema': 'DEE.Roblox.SDK.FOCAL6.0.1.0', 'profile': 'FOCAL', 'maxCycles': 6,
              'maxLocalSequence': 12, 'nativeSources': sources, 'demoFreezeUnchanged': True,
              'mechanismsAstEqual': list(mechanisms), 'NativeExecuted': False}
    path = HERE / 'PERFIL_FOCAL_CONGELADO.json'
    if path.exists():
        if json.loads(path.read_text('utf8')) != output: raise FileExistsError('Different FOCAL freeze')
    else: path.write_text(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2)+'\n',encoding='utf8')
    return output

if __name__ == '__main__': print(json.dumps(build(), ensure_ascii=False, sort_keys=True))
