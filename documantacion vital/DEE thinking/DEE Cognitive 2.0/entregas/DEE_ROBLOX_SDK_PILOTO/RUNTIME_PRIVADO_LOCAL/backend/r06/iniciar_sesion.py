"""Explicit NEW/CONTINUE session with finite current UTC lease.

Plan is stdlib/closed-read only. --execute-real-native performs an official
zero-tick administrative lease under512MiB, then starts the loopback service.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
import uuid
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sdk_common import RUNTIME, atomic, budget, canonical, closed_native, instance_home, read, sha, validate_pair

def load_lease_module():
    path = Path(__file__).parent / 'preparacion/renovar_lease_sdk.py'
    spec = importlib.util.spec_from_file_location('_sdk_closed_lease', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def make_lease(instance_id, *, minutes, cycles, mode, validation_campaign=False):
    if type(minutes) is not int or not 45 <= minutes <= 360 or type(cycles) is not int or not 1 <= cycles <= 3:
        raise ValueError('Finite session: minutes45..360, cycles1..3')
    home, cfg = instance_home(instance_id)
    if (home / 'SDK_SERVICE.lock').exists(): raise RuntimeError('Existing service preserved; do not reopen')
    proof = closed_native(home, cfg)
    paired = (home / 'SDK_PAIR.json').exists()
    if mode == 'start' and (paired or cfg['localSequence'] != 0): raise ValueError('START cannot reuse an advanced instance; choose continue')
    if mode == 'continue' and not paired: raise ValueError('CONTINUE requires actual closed SDK_PAIR')
    if mode == 'continue': validate_pair(home, cfg, proof)
    value = read(RUNTIME / 'estado_demo/LEDGER_SDK_R06.json')
    if value['intents']: raise RuntimeError('Preserved material intent; no administrative lease')
    world = value['worlds'].get(cfg['lifeId'], {'cycles': 0, 'consumed': 0, 'reserved': 0})
    if world['reserved'] or world['cycles'] + cycles > 3: raise ValueError('This demonstration life has a finite cumulative3episode profile; use NEW explicitly for another life')
    now = int(time.time()); finish = now + minutes * 60; last = finish - 1800
    campaign_sha = None
    if validation_campaign:
        campaign = budget(); finish = min(finish, campaign['hardFinishUtcEpoch']); last = min(last, campaign['lastNewUtcEpoch'])
        campaign_sha = sha(RUNTIME / 'configuracion/VENTANA_R06.json')
    if last <= now + 300: raise RuntimeError('Insufficient prospective admission/close margin')
    lease = {'schema': 'DEE.Roblox.SDK.operational_lease.0.1.0', 'leaseId': 'SDK_LEASE_' + uuid.uuid4().hex[:16].upper(),
             'instanceId': instance_id, 'lifeId': cfg['lifeId'], 'sessionId': cfg['sessionId'],
             'startUtcEpoch': now, 'lastNewUtcEpoch': last, 'hardFinishUtcEpoch': finish,
             'additionalCycles': cycles, 'startingCompletedCycles': world['cycles'], 'startingConsumedTicks': world['consumed'],
             'cumulativeCycleCap': world['cycles'] + cycles, 'validationCampaign': validation_campaign,
             'validationCampaignSha256': campaign_sha}
    return home, cfg, lease

def apply_child(tx, plan_sha):
    # This branch runs in the private official CP313 process, never HTTP thread.
    p = read(Path(tx) / 'PLAN.json'); home = RUNTIME / p['home']
    sys.path[:0] = [str(home / 'sistema'), str(home / 'sistema/app')]
    from app import process_control as pc
    resources = pc.protect_current(output=Path(tx) / 'RECURSOS_LEASE.json', memory_limit=536870912)
    if resources.get('job_memory_limit') != 536870912: raise RuntimeError('Effective512MiB administrative job required')
    from publicar_lease import finalize_lease_tx
    result = load_lease_module().apply(Path(tx), plan_sha, runtime=RUNTIME,
               execute_root_only=True, finalize=finalize_lease_tx)
    print(canonical(result), flush=True)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=('start','continue','apply-child'))
    p.add_argument('--instance'); p.add_argument('--minutes', type=int, default=120); p.add_argument('--cycles', type=int, default=1)
    p.add_argument('--validation-campaign', action='store_true'); p.add_argument('--execute-real-native', action='store_true')
    p.add_argument('--no-serve', action='store_true'); p.add_argument('--tx'); p.add_argument('--plan-sha256')
    a = p.parse_args()
    if a.mode == 'apply-child':
        if not a.execute_real_native: p.error('Explicit administrative execution flag')
        apply_child(a.tx, a.plan_sha256); return
    if not a.instance: p.error('--instance required')
    home, cfg, lease = make_lease(a.instance, minutes=a.minutes, cycles=a.cycles, mode=a.mode, validation_campaign=a.validation_campaign)
    # Stage backups/plan is itself non-Native and preserves prior proofs.
    staged = load_lease_module().stage(home, lease, runtime=RUNTIME, execute_root_only=True)
    print(canonical({'status': 'STAGED_ONLY', 'mode': a.mode, 'lease': lease, 'transaction': staged}), flush=True)
    if not a.execute_real_native: return
    tx = staged.get('txPath', staged.get('transaction')); plan_sha = staged['planSha256']
    python = RUNTIME / 'dependencias/producto/motor/python313/python.exe'
    command = [str(python), '-I', '-B', str(Path(__file__)), 'apply-child', '--tx', tx,
               '--plan-sha256', plan_sha, '--execute-real-native']
    completed = subprocess.run(command, cwd=RUNTIME, timeout=min(1800, max(1, lease['hardFinishUtcEpoch'] - time.time())))
    if completed.returncode != 0: raise RuntimeError('Administrative lease failed; preserve transaction, no owner/retry')
    if not a.no_serve:
        command = [str(python), '-I', '-B', str(Path(__file__).with_name('servicio_sdk.py')),
                   '--instance', a.instance, '--mode', 'new' if a.mode == 'start' else 'continue', '--start-real-native']
        service = subprocess.run(command, cwd=RUNTIME)
        raise SystemExit(service.returncode)

if __name__ == '__main__': main()
