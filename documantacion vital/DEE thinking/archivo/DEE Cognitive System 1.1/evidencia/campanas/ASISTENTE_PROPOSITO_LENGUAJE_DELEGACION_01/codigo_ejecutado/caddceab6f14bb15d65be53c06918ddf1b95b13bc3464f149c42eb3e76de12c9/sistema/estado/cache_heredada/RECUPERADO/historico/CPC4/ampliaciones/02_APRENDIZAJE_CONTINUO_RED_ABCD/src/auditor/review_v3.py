"""Reconstruct sampled V3 fields and explicitly preserve an alternative route.

No new trajectory, ablation or world preparation. Does not turn coincident
loads into unique ancestry; snapshots provide only the declared local windows.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from src.auditor.passive import neighborhood, record, digest


def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def put(p, x): p.write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    import dee_thinking as d
    folder = ROOT / 'resultados/red/confirmacion03'; config_path = folder / 'EXPERIMENT_CONFIG.json'
    config = read(config_path); rows = []
    for path in sorted(folder.glob('*/MEASUREMENTS.json')):
        x = read(path)
        row = {'id': x['case']['id'], 'case': x['case'], 'evidence': rel(path), 'sha256': sha(path),
            'diagnostic_control': x['diagnostic_control'], 'diagnostic_edits': x['diagnostic_edits'],
            'task_profile': x['task_profile'], 'D161': x['D_first'], 'D228': x['D_reused'],
            'relay291': x['native_turn'], 'B350': x['B_social_received'], 'B417': x['B_future_read'],
            'source_sha256': x['source_sha256'], 'scope': x['scope'],
            'receipt_statuses': [r['status'] for r in x['actual_protocol_receipts']]}
        trace = {t['tick']: t['samples'] for t in x['trace']}
        row['sampled_joint86'] = trace.get(86, {}).get('joint')
        row['sampled_D94'] = trace.get(94, {}).get('D')
        rows.append(row)
    alternative = []
    for identifier in ('FULL', 'C_UNPAIRED'):
        directory = ROOT / 'resultados/red/v3_discovery01' / identifier
        if not (directory / 'T416.deetsnap').exists(): continue
        a = d.OrganizationalWorld.load_snapshot(str(directory / 'T416.deetsnap'))
        b = d.OrganizationalWorld.load_snapshot(str(directory / 'T417.deetsnap'))
        before = digest(a); before_b = digest(b); context = neighborhood(a, (30, 32, 12))
        post = record(b.runtime.observe(d.Coordinate(30, 32, 12)))
        assert digest(a) == before and digest(b) == before_b
        proposals = context['directional_proposals_without_activity_prefilter']
        alternative.append({'id': identifier, 'pre_snapshot': rel(directory / 'T416.deetsnap'),
            'pre_sha256': sha(directory / 'T416.deetsnap'), 'post_snapshot': rel(directory / 'T417.deetsnap'),
            'post_sha256': sha(directory / 'T417.deetsnap'), 'pre_center': context['center'],
            'proposals': proposals, 'full_pre26': context['moore26'], 'post_B': post,
            'reconstructed_proposal_load_sum': sum(r['s_reg'] for r in proposals),
            'no_new_native_advance': True,
            'scope': 'Local proposal participation and observed post-state. Long-range ancestry between82 and350 is not uniquely established by a matching37 or89.'})
    result = {'utc': datetime.now(timezone.utc).isoformat(), 'mode': 'A_READ_ONLY_REANALYSIS_NO_NEW_PHYSICAL_TRAJECTORY',
        'configuration': rel(config_path), 'configuration_sha256': sha(config_path),
        'measured_confirmatory_cases_read': len(rows), 'cases': rows, 'alternative_local_window416_417': alternative,
        'scope': [
            'V3 makes C/D inputs orthogonal; it is a new preparation, not a relabeling of the V2 unpaired control.',
            'Four finite mobile functional regions share one Runtime; no claim of four indefinitely renewable basal organisms.',
            'D has sequential native outputs at161 and228 with different directions; the firstquery cancels x and the second restores it. The panel deliberately changes queryaxis, not a claim of invariant output.',
            'The role relay and timing are prepared physical couplings. Their use is native, but the relay is not a learned utility selector.',
            'C_UNPAIRED discovery still permits a B-only useful later output42 despite D social outputs21/26. This alternative remains measured evidence, not a failed control to discard.',
            'A task-level useful output can therefore survive omission of one intended path. Preserve intermediate states and selective Dcuts instead of claiming every successful output requires the whole proposed chain.',
            'Fresh translated reserves are separate worlds; continuations and diagnostic forks must not inflate the fresh-world count.'],
        'technical_modifications': [], 'new_NATIVE_runs': 0}
    put(ROOT / 'resultados/auditor/NETWORK_V3_SCOPE_REVIEW.json', result)
    print(json.dumps({'confirmatory_cases_read': len(rows), 'passive_local_windows': len(alternative)}))


if __name__ == '__main__': main()
