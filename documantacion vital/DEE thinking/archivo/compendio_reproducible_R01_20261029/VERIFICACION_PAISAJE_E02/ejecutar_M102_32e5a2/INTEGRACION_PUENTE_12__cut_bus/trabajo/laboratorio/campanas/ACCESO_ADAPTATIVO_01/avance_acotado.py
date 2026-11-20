"""Cooperative owner-level checkpoint before an owned worker time limit.

Elapsed host time may stop an experiment, never choose its physical response.
The resulting prefix is PARTIAL, not an incorrect cognitive answer.
"""
import time
class BudgetWindowStop(RuntimeError):pass
def install(adapter,out,*,seconds=220,chunk=4):
    original=adapter.run_until;started=time.perf_counter();samples=[]
    def run(target):
        while adapter.tick<target:
            original(min(target,adapter.tick+chunk))
            if time.perf_counter()-started>seconds:
                record={'tick':adapter.tick,'requested_target':target,'elapsed_seconds':time.perf_counter()-started,'reason':'Cooperative worker budget; no physical response selected','state':adapter.save(out/'LIMITE_COOPERATIVO_ESTADO_COMPLETO.deetsnap.gz')};samples.append(record);raise BudgetWindowStop('Cooperative time window ended at tick '+str(adapter.tick))
        return None
    adapter.run_until=run
    return {'original':original,'events':samples,'chunk':chunk,'seconds':seconds}
