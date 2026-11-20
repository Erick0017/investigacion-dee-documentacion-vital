"""MI02 constructors and dispatch through the existing Store, not a new manager."""
from datetime import datetime,timezone
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from app.lives import WorldAdapter,validate_id
KEY='DEE.Cognitive.System.1.1.MI02.T0.preparation.v1'

def create(store,life,variant):
    validate_id(life)
    if store.life_dir(life).exists():raise FileExistsError('Identity exists; explicit continue or exact fork required')
    if variant=='retorno-r8':
        from capacidades.geometria_distribuida_mi02 import return_recipe
        recipe,g=return_recipe()
    elif variant=='unificada-r6':
        from capacidades.geometria_distribuida_mi02_r6 import unified_recipe
        recipe,g=unified_recipe()
    else:raise ValueError('Unknown admitted MI02 constructor')
    a=WorldAdapter(d.OrganizationalWorld.create(recipe));a.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'variant':variant,'geometry':g,'new_untrained_T0':True,'no_learned_snapshot_imported':True}))
    rec={'schema':'DCS1.1.life.v1','life_id':life,'world_id':life,'profile':'fisica_directa','branch':'NEW_PREPARATION_T0','parent':None,'created_utc':datetime.now(timezone.utc).isoformat(),'architecture_id':'MI02.'+variant,'knowledge':'Prepared anatomy only; empty objective content fields until explicit later experiences.','memberships':[{'id':life+'.A','role':'Native local-history selection and action region'},{'id':life+'.B','role':'Private-information participant, only for unified variant'}]}
    with store.writer(life):return store.commit(rec,a,{'kind':'MI02_CONSTRUCT_UNTRAINED_T0','variant':variant,'no_trained_transplant':True})

def acquire(a,own,private):
    m=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in m or a.tick!=0:raise ValueError('Only the explicit untrained T0 constructor may be acquired here; never reprepare a lived state')
    p=decode_metadata(m[KEY])
    if p['variant']=='retorno-r8':
        from capacidades.arquitectura_distribuida_mi02_r8 import prepare
        return prepare(a,center=p['geometry']['center'],values=own)
    from capacidades.integracion_distribuida_mi02_r6 import acquire as training
    return training(a,geometry=p['geometry'],own=own,private=private)

def shared(a):
    from capacidades.integracion_distribuida_mi02_r6 import saved
    return saved(a)is not None

def live(a,availability,mode):
    if shared(a):
        import importlib
        from capacidades.integracion_distribuida_mi02_r6 import saved
        schema=saved(a)['schema'];modules={'MI02.unified.r1':'integracion_distribuida_mi02','MI02.unified.r2':'integracion_distribuida_mi02_r2','MI02.unified.r3':'integracion_distribuida_mi02_r3','MI02.unified.r4':'integracion_distribuida_mi02_r4','MI02.unified.r5':'integracion_distribuida_mi02_r5','MI02.unified.r6':'integracion_distribuida_mi02_r6'}
        if schema not in modules:raise ValueError('Unknown lived protocol; never select another one by its result')
        fn=importlib.import_module('capacidades.'+modules[schema]).live
        return fn(a,availability=availability,mode=mode,trace=False)
    from capacidades.arquitectura_distribuida_mi02_r8 import live as fn
    return fn(a,availability=availability,mode=mode,trace=False)

def state(a):
    if shared(a):
        from capacidades.integracion_distribuida_mi02_r6 import state as fn
        return fn(a)
    from capacidades.arquitectura_distribuida_mi02_r8 import inspect
    return inspect(a)
