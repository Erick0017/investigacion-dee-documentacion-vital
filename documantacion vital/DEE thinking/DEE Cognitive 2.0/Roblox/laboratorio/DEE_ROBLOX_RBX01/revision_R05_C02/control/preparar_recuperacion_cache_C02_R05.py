"""Pure cached-status observer. No Native requests or controls are submitted.

R04 could never accept an initially paused publication even when the already
resumed owner's later publications were running and fresh. R05 keeps that
initial observation and selects a fresh, unpaused baseline prospectively, then
observes the full 5/61-second window. Physical and idle invariants are constant
across initial observation, selected baseline, and every subsequent sample.
"""
import datetime,time
KEYS=('N','tick','RAW_sha256','clocks_sha256')
def observe(reader,is_alive,physical,minimum_seconds,*,maximum_seconds=75,
            clock=time.monotonic,sleep=time.sleep,utcnow=lambda:datetime.datetime.now(datetime.timezone.utc)):
    if minimum_seconds not in(5,61)or maximum_seconds!=75:raise ValueError('Fixed 5/61 second window and 75 second cap')
    start=clock();initial=before=after=None;baseline_at=None;samples=[];passed=False;reason='CACHE_NOT_READY'
    try:
        initial=reader();after=initial
        while True:
            elapsed=clock()-start
            if not is_alive():reason='OWNER_LAUNCHER_EXITED';break
            after=reader()
            equal=all(initial.get('physical',{}).get(k)==after.get('physical',{}).get(k)==physical.get(k)for k in KEYS)
            idle=initial.get('idle_ticks')==after.get('idle_ticks')
            flags=initial.get('C02_host_event_driven')is True and after.get('C02_host_event_driven')is True
            age=(utcnow()-datetime.datetime.fromisoformat(after['wall_utc'])).total_seconds()
            active=after.get('paused')is False and after.get('running')is True
            if not equal or not idle or not flags:reason='PHYSICAL_IDLE_OR_HOST_INVARIANT_CHANGED';break
            if after.get('running')is not True:reason='CACHED_OWNER_NOT_RUNNING';break
            if before is None and active and 0<=age<=15:
                before=after;baseline_at=clock()
            active_elapsed=0 if baseline_at is None else clock()-baseline_at
            progress=0 if before is None else after.get('host_elapsed_seconds',0)-before.get('host_elapsed_seconds',0)
            samples.append(dict(observed_seconds=elapsed,active_window_seconds=active_elapsed,
                                cache_wall_utc=after.get('wall_utc'),cache_age_seconds=age,
                                cache_progress_seconds=progress,physical_equal=equal,idle_equal=idle,
                                host_flags=flags,paused=after.get('paused'),running=after.get('running')))
            if before is not None and not active:reason='ACTIVE_WINDOW_PAUSED';break
            if active_elapsed>=minimum_seconds and progress>=minimum_seconds-1.5 and 0<=age<=15 and active:
                passed=True;reason='FRESH_RUNNING_BASELINE_AND_FULL_WINDOW';break
            if elapsed>=maximum_seconds:reason='BOUNDED75S_CACHE_WINDOW_NOT_MET';break
            sleep(min(.5,maximum_seconds-elapsed))
    except BaseException as error:reason='OBSERVATION_EXCEPTION_'+type(error).__name__
    return dict(schema='DEE.RBX01.C02.no_idle_cached_observation.R05',passed=passed,reason=reason,
                seconds=clock()-start,minimum_seconds=minimum_seconds,maximum_seconds=maximum_seconds,
                initial=initial,before=before,after=after,samples=samples,baseline_physical=physical,
                physical_equal=passed,Native_requests_sent=0,
                scope='Cached SQLite publications only; fresh baseline does not submit resume or material operations.')
