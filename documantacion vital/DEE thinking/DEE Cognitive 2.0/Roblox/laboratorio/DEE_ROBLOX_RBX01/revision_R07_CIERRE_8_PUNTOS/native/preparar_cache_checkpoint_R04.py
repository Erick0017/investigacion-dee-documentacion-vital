"""Prepare a source-only metadata batch prototype. No active module is edited."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'native/MAIN/sistema/app/cache_fuentes_C02.py'
OUTPUT=ROOT/'native/prototipos/cache_fuentes_C02_R04.py'
EXTENSION=r'''

# R04 prototype: fresh metadata once per immutable-source path in ONE checkpoint.
# Operational state, Native data, artifacts and identity projections are untouched.
import contextlib as _contextlib
import threading as _threading
_PATH_STAT_R04 = Path.stat
_PATH_RESOLVE_R04 = Path.resolve
_PATH_LSTAT_R04 = Path.lstat

def _source_fingerprint_R04(value):
    return (value.st_dev, value.st_ino, value.st_mode, value.st_size,
            value.st_mtime_ns, value.st_ctime_ns,
            getattr(value, 'st_file_attributes', 0))

@_contextlib.contextmanager
def _checkpoint_pass_R04(self):
    if not self.active:
        raise RuntimeError('An open deny-write immutable-source cache is required')
    if getattr(self, '_checkpoint_pass_active_R04', False):
        raise RuntimeError('One nonnested checkpoint metadata pass per owner')
    if (Path.stat is not _PATH_STAT_R04 or Path.resolve is not _PATH_RESOLVE_R04 or
            Path.lstat is not _PATH_LSTAT_R04):
        raise RuntimeError('No other Path metadata interposer may be active')
    self._checkpoint_pass_active_R04 = True
    thread = _threading.get_ident()
    stat_cache, resolve_cache, first_stamp, used_paths = {}, {}, {}, {}
    counts = {'stat_hits': 0, 'stat_misses': 0, 'resolve_hits': 0,
              'resolve_misses': 0, 'fresh_rechecks': 0}
    def admitted(path):
        # Only the bytes already locked and admitted by the ORIGINAL whitelist.
        return self.entries.get(key(path)) if _threading.get_ident() == thread else None
    def remember(path):
        k = key(path)
        if k not in first_stamp:
            value = _PATH_STAT_R04(path, follow_symlinks=False)
            if stat.S_ISLNK(value.st_mode) or getattr(value, 'st_file_attributes', 0) & 1024:
                raise RuntimeError('Immutable source path became linked/reparse')
            first_stamp[k] = _source_fingerprint_R04(value)
            used_paths[k] = Path(path)
        return k
    def cached_stat(path, *, follow_symlinks=True):
        if admitted(path) is None:
            return _PATH_STAT_R04(path, follow_symlinks=follow_symlinks)
        k = remember(path); token = (k, bool(follow_symlinks))
        if token in stat_cache:
            counts['stat_hits'] += 1
            return stat_cache[token]
        counts['stat_misses'] += 1
        value = _PATH_STAT_R04(path, follow_symlinks=follow_symlinks)
        if _source_fingerprint_R04(value) != first_stamp[k]:
            raise RuntimeError('Immutable source changed during fresh metadata read')
        stat_cache[token] = value
        return value
    def cached_lstat(path):
        return cached_stat(path, follow_symlinks=False)
    def cached_resolve(path, strict=False):
        item = admitted(path)
        if item is None:
            return _PATH_RESOLVE_R04(path, strict=strict)
        k = remember(path); token = (k, bool(strict))
        if token in resolve_cache:
            counts['resolve_hits'] += 1
            return resolve_cache[token]
        counts['resolve_misses'] += 1
        resolved = _PATH_RESOLVE_R04(path, strict=strict)
        if key(resolved) != key(item[0]):
            raise RuntimeError('Immutable source resolution changed')
        resolve_cache[token] = resolved
        return resolved
    Path.stat, Path.lstat, Path.resolve = cached_stat, cached_lstat, cached_resolve
    body_error = None
    try:
        yield counts
    except BaseException as error:
        body_error = error
        raise
    finally:
        Path.stat, Path.lstat, Path.resolve = _PATH_STAT_R04, _PATH_LSTAT_R04, _PATH_RESOLVE_R04
        try:
            # Fresh physical metadata/resolution fence, still holding deny-write leases.
            for k, path in used_paths.items():
                current = _PATH_STAT_R04(path, follow_symlinks=False)
                resolved = _PATH_RESOLVE_R04(path, strict=True)
                counts['fresh_rechecks'] += 1
                if (_source_fingerprint_R04(current) != first_stamp[k] or
                        key(resolved) != key(self.entries[k][0])):
                    raise RuntimeError('Immutable source changed within checkpoint pass: ' + str(path))
        except BaseException as check_error:
            if body_error is not None:
                check_error.add_note('The validator also failed: ' + repr(body_error))
            raise
        finally:
            self._checkpoint_pass_active_R04 = False
            self.checkpoint_metadata_passes_R04 = getattr(self, 'checkpoint_metadata_passes_R04', [])
            self.checkpoint_metadata_passes_R04.append(dict(counts, unique_sources=len(used_paths)))
            stat_cache.clear(); resolve_cache.clear(); first_stamp.clear(); used_paths.clear()

ImmutableSourceCache.checkpoint_pass = _checkpoint_pass_R04
'''

def main():
    original=SOURCE.read_bytes();source_sha=hashlib.sha256(original).hexdigest()
    if OUTPUT.exists():raise ValueError('Fresh prototype path required')
    source=original.decode('utf-8-sig')+EXTENSION
    compile(source,str(OUTPUT),'exec');OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(source,encoding='utf-8',newline='\n')
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=source_sha:raise ValueError('Active original changed')
    record={'schema':'DEE.R07.P06.immutable_metadata_pass.prototype.R04','source':str(SOURCE),
      'source_sha256_before_after':source_sha,'prototype':str(OUTPUT),
      'prototype_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
      'status':'PROTOTYPE_NOT_INSTALLED_NOT_NATIVE_EXECUTED',
      'scope':'Memoize stat/lstat/resolve only for originally whitelisted deny-write leased source paths, only within one checkpoint; fresh first observation and fresh final fence.',
      'not_cached':['estado','Native files','operational artifacts','metadata aliases','operational_dependencies payload','anything outside original source whitelist'],
      'required_before_activation':'Root compares complete operational_dependencies payload old/new on same closed prefix, no Native ticks; versioned installation only after validation.'}
    proof=OUTPUT.with_name('PROTOTIPO_CACHE_CHECKPOINT_R04.json');proof.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
