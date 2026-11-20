"""Closed U0 spatial context extraction: data only, zero DEE imports/ticks."""
from __future__ import annotations

import argparse
from array import array
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
THINK = HERE.parents[3]
ROOT = THINK / '4.5/DEE_thinking_4_5_0/validation/cpc_ports_4_5_final6/IR_P01_GUARDED_M1'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def meta(path, pointer=''):
    p = Path(path)
    b = p.read_bytes()
    return dict(path=str(p), bytes=len(b), sha256=sha(b), pointer=pointer)


def fields(raw):
    def signed(at):
        value = (raw >> at) & 15
        return value - 16 if value & 8 else value
    return dict(raw=str(raw), state=raw & 0xffffffff,
                s_reg=(raw >> 32) & 65535,
                direction=[signed(k) for k in (48, 52, 56)],
                semantic=(raw >> 60) & 15)


def observations(obj, pointer=''):
    if isinstance(obj, dict):
        if all(k in obj for k in ('site', 'raw', 'clock')):
            p = dict(obj)
            p['raw'], p['clock'] = str(p['raw']), str(p['clock'])
            p['source_pointer'] = pointer
            for k, value in fields(int(p['raw'])).items():
                if k in p and p[k] != value:
                    raise ValueError((pointer, k, p[k], value))
            return [p]
        return [p for k, v in obj.items() for p in observations(v, pointer + '/' + str(k))]
    if isinstance(obj, list):
        return [p for i, v in enumerate(obj) for p in observations(v, pointer + '/' + str(i))]
    return []


def buffer(desc, n):
    p = ROOT / desc['path']
    encoded = p.read_bytes()
    decoded = gzip.decompress(encoded)
    assert sha(encoded) == desc['sha256_compressed'], p
    assert sha(decoded) == desc['sha256_uncompressed'], p
    assert len(decoded) == desc['bytes'] == n ** 3 * 8, p
    values = array('Q')
    values.frombytes(decoded)
    if sys.byteorder != 'little':
        values.byteswap()
    return values, dict(source=meta(p), descriptor=desc)


def within(site, center, half=3):
    return all(abs(a - b) <= half for a, b in zip(site, center))


def main(replace=False):
    src, cfgsrc = ROOT / 'RESULT.json', ROOT / 'CONFIG.json'
    result = json.loads(src.read_text(encoding='utf-8-sig'))
    config = json.loads(cfgsrc.read_text(encoding='utf-8-sig'))
    assert result['case_id'] == 'IR_P01_GUARDED_M1'
    n, geometry = config['geometry']['N'], config['geometry']
    assert n == 67 and result['library'] == '4.5.0'
    requested = [0, 19, 69, 72, 75, 139, 142, 335, 338, 402, 405, 469, 472]
    supplementary = [3, 5, 11, 15, 70]
    centers = {
        'L03_reader_and_revision_hub': geometry['sites']['form.L03'],
        'right_native_question': geometry['sites']['question.right.different'],
        'right_comparison': geometry['sites']['comparison.right'],
        'right_minus_name': geometry['sites']['name.right.minus'],
        'right_own_bank': geometry['sites']['bank.right'],
        'native_use_minus': geometry['sites']['action.minus'],
    }
    frames, buffer_sources = [], []
    for i, f in enumerate(result['frames']):
        tick = int(f['tick'])
        if tick not in requested + supplementary:
            continue
        exact = observations(f, f'/frames/{i}')
        unique = {}
        for p in exact:
            key = tuple(p['site'])
            if key in unique:
                assert (unique[key]['raw'], unique[key]['clock']) == (p['raw'], p['clock'])
            unique[key] = p
        exact = list(unique.values())
        complete = 'raw' in f and 'clock' in f
        reads_verified = 0
        desc = None
        if complete:
            raw, rawsrc = buffer(f['raw'], n)
            clocks, clocksrc = buffer(f['clock'], n)
            desc = dict(raw=rawsrc, clock=clocksrc)
            buffer_sources += [rawsrc['source'], clocksrc['source']]
            for p in exact:
                x, y, z = p['site']
                index = (x * n + y) * n + z
                assert (str(raw[index]), str(clocks[index])) == (p['raw'], p['clock'])
                reads_verified += 1
            nonzero = []
            for index, value in enumerate(raw):
                if value:
                    x, rem = divmod(index, n * n)
                    y, z = divmod(rem, n)
                    nonzero.append(dict(tick=tick, site=[x, y, z],
                                        clock=str(clocks[index]), **fields(value),
                                        source_pointer=f'/frames/{i}/raw',
                                        buffer_linear_index=index))
        else:
            nonzero = [p for p in exact if int(p['raw']) != 0]
        regions = {}
        for name, center in centers.items():
            regions[name] = dict(
                center=center, half_extent_cells=3,
                bounds=[[max(0, v - 3) for v in center], [min(n - 1, v + 3) for v in center]],
                nonzero_points=[p for p in nonzero if within(p['site'], center)],
                explicitly_observed_zero_points=[p for p in exact if int(p['raw']) == 0 and within(p['site'], center)],
                exhaustive_nonzero_in_ROI=complete,
                role='Editorial ROI around a documented apparatus position; not a localized memory claim')
        frames.append(dict(
            tick=tick, N=n, source_pointer=f'/frames/{i}',
            source_class='complete_RAW_and_clock_buffers' if complete else 'sparse_documented_field_reads',
            complete_buffers=complete, buffers=desc,
            all_nonzero_points=nonzero,
            nonzero_state0_count=sum(p['state'] == 0 for p in nonzero),
            original_field_reads=exact, original_reads_verified_against_full_buffers=reads_verified,
            regions=regions,
            coverage=('All nonzero RAW including state0; every clock is preserved in original complete buffer.' if complete else
                      'Only recorded field sites. No spatial absence or lack of context is inferred outside them.'),
            stage_transition='Editorial cut only; no matter-position interpolation across missing physical ticks'))
    data = dict(
        schema='DEE.audiovisual5min.U0_spatial_context.v1',
        created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        new_DEE_ticks=0, DEE_imports=False, simulations_or_replays=False,
        life=result['case_id'], profile=geometry['kind'], N=n,
        condition=config['case'], sources=[meta(src), meta(cfgsrc)],
        extractor=meta(__file__),
        requested_ticks=requested, supplementary_same_record_ticks=supplementary,
        available_ticks=[f['tick'] for f in frames],
        complete_buffer_ticks=[f['tick'] for f in frames if f['complete_buffers']],
        frames=frames,
        prepared_interfaces_separate_from_matter=dict(
            source=meta(cfgsrc, '/geometry'),
            scope='Documented preparation roles and input/reader opportunities, not newly observed particles.',
            sites=geometry['sites'], names=geometry['names'],
            action_inputs=geometry['action_inputs'], actions=geometry['actions'],
            need=geometry['need'], banks=geometry['banks'],
            interface_names=result['final_operative']['channels'],
            L03_signal_input_site=None,
            L03_signal_input_site_limit='RESULT/CONFIG record L03.signal and reader hub but do not document its input position here; no coordinate is invented.',
            visual_rule='Interfaces may be outlines/annotations, never fabricated RAW cells.'),
        qualified_readings=result['readouts'],
        relevant_calls=[q for q in result['calls'] if q['port'].startswith('L03.') or
                        q['port'].startswith('own.') or q['port'].startswith('need.actual.')],
        buffer_sources=buffer_sources,
        attribution=['ROI selection is an external visualization choice.',
                     'A historical physical difference is not automatically a memory site or new learning.',
                     'Questions, actions, names and L03 revision are in the SAME archived U0 record, not combined divergent lives.',
                     'Other opposite-history and matching-current controls remain separately identified in ESCENAS_04_06_09.json.',
                     'No absent sparse context is filled, no new history is reconstructed.'])
    out = HERE / 'CONTEXTOS_U0_3D.json'
    if out.exists() and not replace:
        raise FileExistsError(out)
    temporary = out.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    temporary.replace(out)
    print(json.dumps(dict(path=str(out), bytes=out.stat().st_size, sha256=sha(out.read_bytes()),
                          frames=len(frames), full_buffer_ticks=data['complete_buffer_ticks'],
                          nonzero_by_tick={str(f['tick']): len(f['all_nonzero_points']) for f in frames},
                          ROI_nonzero_counts={str(f['tick']): {k: len(v['nonzero_points']) for k, v in f['regions'].items()} for f in frames},
                          new_DEE_ticks=0), ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--replace', action='store_true')
    main(parser.parse_args().replace)
