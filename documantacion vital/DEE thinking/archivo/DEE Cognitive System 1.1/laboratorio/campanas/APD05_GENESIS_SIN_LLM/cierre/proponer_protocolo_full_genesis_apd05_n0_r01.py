"""Produce an unapproved Full GUI protocol from an explicitly selected cut.

No application, updater, Native, browser or Word is opened. Root must inspect
the actual prior knowledge, RAW decoder/criteria and freeze a new closed file.
"""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--selection', required=True, help='Root-relative selection that will be in the Full')
    p.add_argument('--personal-life', required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--prior-clasifica-sign', type=int, choices=(-1, 1), required=True)
    p.add_argument('--new-clasifica-sign', type=int, choices=(-1, 1), required=True)
    p.add_argument('--port', type=int, default=8875)
    a = p.parse_args()
    root = a.root.resolve(strict=True)
    path = (root / a.selection).resolve(strict=True)
    if not path.is_relative_to(root) or a.out.exists():
        raise ValueError('Explicit in-root selection and fresh proposal required')
    selection = json.loads(path.read_text(encoding='utf-8-sig'))
    if selection.get('status') != 'CLOSED_SELECTED_FOR_USE':
        raise ValueError('A selected complete cut is required even for this proposal')
    if a.prior_clasifica_sign == a.new_clasifica_sign:
        raise ValueError('The proposed revision must be distinct; declare reinforcement separately instead')
    pending = 'apd05_full_gui_pending_r01'
    def action(ident, command, value=None, limit=300, expected='completed', **extra):
        return {'id': ident, 'kind': 'action', 'action': command, 'value': value,
                'timeout_seconds': limit, 'expected_job_status': expected, **extra}
    def frame(ident):
        return {'id': ident, 'kind': 'frame', 'timeout_seconds': 30}
    phases = [
        {'id': 'OPEN_REVISION_RECORD_PENDING', 'startup_timeout_seconds': 90,
         'steps': [
             action('first_open_whole_personal', 'abrir', limit=300),
             frame('initial_paused_coherent_frame'),
             action('unknown_form_no_native_submission', 'ejecutar', {'texto': 'palabra quasar'},
                    expected='error', expect_no_transport_row=True, limit=30),
             action('invalid_syntax_no_native_submission', 'ejecutar', {'texto': 'suma [4,]'},
                    expected='error', expect_no_transport_row=True, limit=30),
             action('start_recording', 'grabar', limit=30),
             action('explicit_live', 'vivir', limit=150),
             action('prior_clasifica', 'ejecutar', {'texto': 'palabra clasifica', 'id': 'apd05_full_gui_prior_class_r01'}),
             action('old_luma_before_revision', 'ejecutar', {'texto': 'palabra luma', 'id': 'apd05_full_gui_old_luma_a_r01'}),
             action('prepared_numeric_use', 'ejecutar', {'texto': 'usar suma 4 5', 'id': 'apd05_full_gui_numeric_r01'}),
             action('old_nara_before_revision', 'ejecutar', {'texto': 'palabra nara', 'id': 'apd05_full_gui_old_nara_a_r01'}),
             action('explicit_finite_association_revision', 'ensenar',
                    {'forma': 'clasifica', 'senal': a.new_clasifica_sign, 'revision': True}),
             action('use_revised_association', 'ejecutar', {'texto': 'palabra clasifica', 'id': 'apd05_full_gui_revised_class_r01'}),
             action('retention_old_luma', 'ejecutar', {'texto': 'palabra luma', 'id': 'apd05_full_gui_old_luma_b_r01'}),
             action('retention_old_nara', 'ejecutar', {'texto': 'palabra nara', 'id': 'apd05_full_gui_old_nara_b_r01'}),
             frame('coherent_frame_after_use'),
             action('pause_before_pending', 'pausar', limit=150),
             action('close_recording', 'grabar', limit=30),
             action('export_context_not_restorable_mind', 'exportar', limit=30),
             {'id': 'real_browser_visual_and_archived_replay', 'kind': 'browser_checkpoint',
              'timeout_seconds': 90,
              'scope': 'PASSIVE_FULL_BROWSER: identify life/tick, rotate/zoom, filter/slice and coordinate selection, then load the closed gzip recording and verify archived replay labels; no material buttons or new task.'},
             action('submit_exact_pending_once_while_paused', 'ejecutar',
                    {'texto': 'palabra clasifica', 'id': pending}, limit=300),
             {'id': 'pending_id_preserved_before_stop', 'kind': 'wait_pending', 'timeout_seconds': 30},
             action('save_with_pending', 'guardar', limit=150),
             action('stop_first_owner', 'detener', limit=150)]},
        {'id': 'REOPEN_SAME_PENDING_AND_RETENTION', 'startup_timeout_seconds': 90,
         'steps': [
             action('reopen_same_personal_pointer', 'abrir', limit=180),
             {'id': 'same_pending_id_after_reopen', 'kind': 'wait_pending', 'timeout_seconds': 30},
             frame('reopened_paused_coherent_frame'),
             action('resume_same_world', 'vivir', limit=150),
             {'id': 'reconcile_same_id_read_only_until_terminal', 'kind': 'wait_result',
              'timeout_seconds': 300, 'expected_transport_status': 'completed'},
             action('retention_revised_association_after_reopen', 'ejecutar',
                    {'texto': 'palabra clasifica', 'id': 'apd05_full_gui_after_reopen_class_r01'}),
             action('retention_old_luma_after_reopen', 'ejecutar',
                    {'texto': 'palabra luma', 'id': 'apd05_full_gui_after_reopen_luma_r01'}),
             action('retention_old_nara_after_reopen', 'ejecutar',
                    {'texto': 'palabra nara', 'id': 'apd05_full_gui_after_reopen_nara_r01'}),
             frame('final_live_coherent_frame'),
             action('pause_final', 'pausar', limit=150),
             action('save_final', 'guardar', limit=150),
             action('export_final_context', 'exportar', limit=30),
             action('stop_final_owner', 'detener', limit=150)]}
    ]
    value = {'schema': 'APD05.exact_full_gui.prospective_protocol.R01',
             'status': 'DRAFT_REQUIRES_ROOT_FREEZE_AND_GUI_STABILIZATION',
             'personal_life': a.personal_life, 'N': 67,
             'expected_selection_file': path.relative_to(root).as_posix(),
             'expected_selection_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
             'source_snapshot_sha256': selection['source_snapshot_sha256'],
             'source_pair_manifest_sha256': selection['paired_export_manifest_sha256'],
             'source_life': selection['source_life'], 'source_tick': selection['source_tick'],
             'pending_transport_id': pending, 'pending_terminal_status': 'completed',
             'port': a.port, 'tree_memory_limit_bytes': 1073741824,
             'total_wall_limit_seconds': 900, 'phases': phases,
             'prospective_auditor_criteria_not_sent_to_actor': {
                 'prior_clasifica_sign': a.prior_clasifica_sign,
                 'revised_clasifica_sign': a.new_clasifica_sign,
                 'old_nara_sign': -1,
                 'old_luma_sign': 1,
                 'numeric_requested_operands': [4, 5], 'nominal_sum': 9,
                 'native_tool_attribution_requires_strict_RAW_and_route': True,
                 'same_world_and_single_complete_import': True,
                 'Native_decoder_and_old_knowledge_must_be_confirmed_by_Root_before_freeze': True},
             'scope': 'Exact Full real GUI/API and same-life continuity. Browser checkpoint is separately acknowledged by Root. The driver does not calculate actor answers; archived RAW interpretation remains independent.',
             'not_an_execution': True, 'new_native_ticks': 0}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'proposal': str(a.out), 'sha256': hashlib.sha256(a.out.read_bytes()).hexdigest(),
                      'status': value['status'], 'new_native_ticks': 0, 'GUI_or_Full_started': False}))


if __name__ == '__main__':
    main()
