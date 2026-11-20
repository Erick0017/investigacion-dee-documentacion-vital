"""Pure PI08 evidence helpers. No DEE, process, network or world access."""
from pathlib import Path, PurePosixPath
from collections import Counter
import hashlib
import json


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':')).encode('utf-8')


def safe_name(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ValueError('A simple portable relative path is required')
    p = PurePosixPath(value)
    if p.is_absolute() or any(x in ('', '.', '..') for x in p.parts):
        raise ValueError('Absolute/traversing evidence path')
    return p


def local(root, value):
    root = Path(root).resolve(strict=True)
    p = root.joinpath(*safe_name(value).parts)
    # Inspect lexical ancestors before resolve; a junction may otherwise vanish.
    for node in (p, *p.parents):
        st = node.lstat()
        if node.is_symlink() or getattr(st, 'st_file_attributes', 0) & 1024:
            raise ValueError('Linked/reparse evidence is not allowed')
        if node == root:
            break
    q = p.resolve(strict=True)
    if not q.is_relative_to(root) or not q.is_file():
        raise ValueError('Evidence escaped its root or is not a file')
    return q


def checked(root, entry):
    path = local(root, entry['file'])
    data = path.read_bytes()
    if type(entry.get('bytes')) is not int or len(data) != entry['bytes']:
        raise ValueError('Evidence size differs: ' + entry['file'])
    if digest(data) != entry.get('sha256'):
        raise ValueError('Evidence SHA differs: ' + entry['file'])
    return path, data


def read_json(data):
    return json.loads(data.decode('utf-8-sig'))


def pointer(value, text):
    """RFC6901 only; never eval, glob, executable expression or source path."""
    if text == '':
        return value
    if not isinstance(text, str) or not text.startswith('/'):
        raise ValueError('JSON pointer must be empty or start with /')
    for raw in text[1:].split('/'):
        part = raw.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def receipt_map(requests):
    """Direct, current-operation requests only; never walk cached metadata."""
    result = {}
    aliases = 0
    for request in requests:
        rid, receipt = request['id'], request['receipt']
        if type(rid) is not int or receipt.get('id') != rid:
            raise ValueError('Request/receipt Native ID disagreement')
        if rid in result:
            if canonical(result[rid]) != canonical(receipt):
                raise ValueError('Contradictory aliases of Native receipt ' + str(rid))
            aliases += 1
        result[rid] = receipt
    statuses = Counter(v['status'] for v in result.values())
    return result, {'unique_requested': len(result),
                    'applied': statuses['applied'],
                    'rejected': sum(n for s, n in statuses.items() if s.startswith('rejected')),
                    'pending_or_other': sum(n for s, n in statuses.items()
                                            if s != 'applied' and not s.startswith('rejected')),
                    'status_counts': dict(statuses), 'aliases_not_new_events': aliases}


def interval_union(intervals):
    """Tick advancements are half-open [before,after), not sample counts."""
    ordered = []
    for before, after in intervals:
        if type(before) is not int or type(after) is not int or not 0 <= before <= after:
            raise ValueError('Exact ordered nonnegative Native ticks required')
        ordered.append((before, after))
    merged = []
    for before, after in sorted(ordered):
        if merged and before <= merged[-1][1]:
            merged[-1][1] = max(after, merged[-1][1])
        else:
            merged.append([before, after])
    return {'merged_half_open_intervals': merged,
            'unique_recorded_tick_advancements': sum(b-a for a, b in merged),
            'raw_interval_sum': sum(b-a for a, b in ordered),
            'overlap_not_counted_twice': sum(b-a for a, b in ordered)-sum(b-a for a, b in merged)}


def body(primary):
    value = primary.get('result')
    if value is None:
        return None, []
    if isinstance(value, str):
        value = json.loads(value)
    envelope = value
    if isinstance(value, dict) and 'rows' not in value and isinstance(value.get('result'), dict):
        value = value['result']
    return envelope, value.get('rows', []) if isinstance(value, dict) else []


def actual_life(envelope, row, entry):
    candidates = []
    for value in (row.get('life_id'),
                  (envelope or {}).get('committed_snapshot', {}).get('life_id'),
                  entry.get('life_id')):
        if value is not None:
            if not isinstance(value, str) or not value:
                raise ValueError('Malformed actual life identity')
            candidates.append(value)
    if len(set(candidates)) > 1:
        raise ValueError('Primary, row and explicit index life disagree')
    return candidates[0] if candidates else None


def direct_requests(row, kind):
    if kind in ('regulation_episode', 'regulated_FI_access', 'association'):
        return row['requests']
    if kind == 'numeric':
        return row['native_operation']['native_trial']['requests']
    if kind == 'C2C':
        out = list(row['requests'])
        arithmetic = row.get('native_arithmetic')
        if arithmetic is not None:
            out += arithmetic['native_operation']['native_trial']['requests']
        second = row.get('second_native_use')
        if second is not None:
            out += second.get('requests', [])
        return out
    raise ValueError('No current direct-request contract for kind ' + kind)


def count_request_ledger(records):
    """IDs are scoped by actual world key, never globally across clones."""
    worlds = {}
    aliases = 0
    missing_scope = []
    for record in records:
        world = record.get('world_key')
        if not world:
            missing_scope.append(record['source'])
            continue
        current, stats = receipt_map(record['requests'])
        aliases += stats['aliases_not_new_events']
        target = worlds.setdefault(world, {})
        for rid, receipt in current.items():
            if rid in target:
                if canonical(target[rid]) != canonical(receipt):
                    raise ValueError('Same-world Native receipt contradicts an earlier row')
                aliases += 1
            target[rid] = receipt
    summary = {}
    total = Counter()
    for world, mapping in sorted(worlds.items()):
        statuses = Counter(r['status'] for r in mapping.values())
        total.update(statuses)
        summary[world] = {'unique_current_Native_requests': len(mapping),
                          'status_counts': dict(statuses),
                          'ids_sha256': digest(canonical(sorted(mapping)))}
    return {'worlds': summary, 'unique_current_Native_requests': sum(len(v) for v in worlds.values()),
            'status_counts': dict(total), 'aliases_not_new_events': aliases,
            'rows_missing_actual_world_scope_not_added': missing_scope,
            'scope': 'Only explicit current requests from recognized material contracts. '
                     'No recursive traversal of snapshots, cached arithmetic, old receipts or metadata; '
                     'common-prefix clones are not independent individuals.'}
