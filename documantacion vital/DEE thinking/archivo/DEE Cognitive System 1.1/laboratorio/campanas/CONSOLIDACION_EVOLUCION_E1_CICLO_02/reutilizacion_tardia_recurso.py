import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import recovery,ic_native_core as core,social_guard
source='C02_REC_033_SIN_PERDIDA'
cases=[('C02_LATE_160_CONSERVAR','keep'),('C02_LATE_161_DESVIAR','redirect'),('C02_LATE_162_SHAM','sham')]
atomic_json(EV/'RECURSO_TARDIO_PROTOCOLO_160.json',{
    'source':source,'source_tick':16887,'old_resource_launch':16589,'query_tick':16954,
    'new_generic_recovery_seeds':0,'existing_resource_cycles_before_query':5,
    'cases':cases,'intervention':'At16890 add Y0 to both predicted old resource sites, or equal-dose19z sham. This changes direction, not fields by editing and not indiscriminate deletion.',
    'criterion':'Ancestral prepared zero influence supports old content later through a fixed native encounter. Positive sign must have4later motor uses. No unique token identity inferred just from zero load or matching coordinate.',
    'assistance':'All old/original and alternative ports fixed before query. No post-query repair or new sign/reference/B teaching.'})
for name,mode in cases:
    fork(source,name)
    def test(a):
        initial=physical(a.world,occupation=True);assert a.tick==16887
        # Only fixes all parallel instrument ports. enabled=False inserts NO
        # new recovery seed; actual ancestral resources remain in the world.
        prep=recovery.preposition_social_access(a,name=name,enabled=False)
        q=recovery.query_social_access(a,name=name,query_tick=16954);rr=[];banks=prep['base_banks']
        for b in banks:
            target=core.move(b['target'],(b['sign'],0,-1),3)
            if mode!='keep':rr.append(core.arrive(a,name+'.existing_resource.'+str(b['sign']),core.move(target,(0,0,1),19)if mode=='sham'else target,(0,1,0),16890,0))
        frames=[]
        for t in(16889,16890,16891,16953,16954,16955,16956,16957):
            ic.advance(a,until=t,record=False)
            frames.append({'tick':t,'regions':[{'sign':b['sign'],'original':observe(a.world,b['target']),
                'meeting':observe(a.world,core.move(b['target'],(b['sign'],0,-1),3)),
                'context125':[observe(a.world,core.move(core.move(b['target'],(b['sign'],0,-1),3),(x,y,z)))for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)]if t in(16889,16890,16956,16957)else[]}for b in banks]})
            if t in(16889,16890,16957):a.save(EV/(name+'.T'+str(t)+'.deetsnap.gz'))
        external=ic.act_external(a,steps=4)
        return{'initial':initial,'mode':mode,'instrument_preparation_no_new_seed':prep,'common_query':q,'frames':frames,'external':external,
               'requests':core.receipts(a,rr+q['requests']),'ancestral_resource_primary':'C02_REC_033_SIN_PERDIDA.json',
               'final':physical(a.world,occupation=True),'not_claimed':'No unique material identity, learned time concept, new policy or unlimited resource regeneration.'}
    run(name,name,test,{'spec':'RECURSO_TARDIO_PROTOCOLO_160.json'})
