"""Bounded cached-status observation. No material owner/query operation.

Waits for an actually advanced, recent, unpaused cache rather than requiring a
particular publish to land at exactly5seconds. Physical/idle invariants are never
relaxed. Returns before/after observations even on failure for durable recording.
"""
import datetime,time
KEYS=('N','tick','RAW_sha256','clocks_sha256')
def observe(reader,is_alive,physical,minimum_seconds,*,maximum_seconds=75,
            clock=time.monotonic,sleep=time.sleep,utcnow=lambda:datetime.datetime.now(datetime.timezone.utc)):
    if minimum_seconds not in(5,61)or maximum_seconds!=75:raise ValueError('Prospective5/61second minimum and75second cap required')
    t0=clock();before=None;after=None;samples=[];reason='CACHE_NOT_READY';passed=False
    try:
        before=reader();after=before
        while True:
            elapsed=clock()-t0
            if not is_alive():reason='OWNER_LAUNCHER_EXITED';break
            after=reader()
            physical_equal=all(before.get('physical',{}).get(k)==after.get('physical',{}).get(k)==physical.get(k)for k in KEYS)
            idle_equal=before.get('idle_ticks')==after.get('idle_ticks')
            flags=before.get('C02_host_event_driven')is True and after.get('C02_host_event_driven')is True
            cache_wall=datetime.datetime.fromisoformat(after['wall_utc'])
            cache_age=(utcnow()-cache_wall).total_seconds()
            cache_progress=after.get('host_elapsed_seconds',0)-before.get('host_elapsed_seconds',0)
            active=before.get('paused')is False and after.get('paused')is False and before.get('running')is True and after.get('running')is True
            samples.append({'observed_seconds':elapsed,'cache_wall_utc':after.get('wall_utc'),
                            'cache_age_seconds':cache_age,'cache_progress_seconds':cache_progress,
                            'physical_equal':physical_equal,'idle_equal':idle_equal,'host_flags':flags,
                            'paused':after.get('paused'),'running':after.get('running')})
            if not physical_equal or not idle_equal or not flags:reason='PHYSICAL_IDLE_OR_HOST_INVARIANT_CHANGED';break
            if after.get('running')is not True:reason='CACHED_OWNER_NOT_RUNNING';break
            if elapsed>=minimum_seconds and cache_progress>=minimum_seconds-1.5 and 0<=cache_age<=15 and active:
                reason='ACTUAL_RECENT_UNPAUSED_CACHE_ADVANCED';passed=True;break
            if elapsed>=maximum_seconds:reason='BOUNDED75S_CACHE_PROGRESS_OR_FRESHNESS_NOT_MET';break
            sleep(min(.5,maximum_seconds-elapsed))
    except BaseException as error:
        reason='OBSERVATION_EXCEPTION_'+type(error).__name__
    return {'schema':'DEE.RBX01.C02.no_idle_cached_observation.R04','passed':passed,'reason':reason,
            'seconds':clock()-t0,'minimum_seconds':minimum_seconds,'maximum_seconds':maximum_seconds,
            'before':before,'after':after,'samples':samples,'baseline_physical':physical,
            'physical_equal':passed,'Native_requests_sent':0,
            'scope':'Cached SQLite status only; no Native state request, control or material query submitted.'}
