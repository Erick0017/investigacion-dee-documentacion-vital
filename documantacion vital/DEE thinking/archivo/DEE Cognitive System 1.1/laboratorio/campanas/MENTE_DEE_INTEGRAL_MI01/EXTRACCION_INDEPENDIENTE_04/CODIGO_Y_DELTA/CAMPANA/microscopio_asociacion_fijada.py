"""Nine-tick association window, fixed-prefix diagnostic copy, not a repair."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from controles_desde_prefijo_fijado import prefix,name
from capacidades.mente_integral_mi01 import externo_selector as motor,saved
from capacidades.integracion_situada_01 import ic_native_core as n
life='MI01_ASOCIACION_FIJADA_473';fork('E1_MI01_MAIN',life,checkpoint=prefix())
atomic_json(E/'MICROSCOPIO_ASOCIACION_PROTOCOLO_473.json',{'source_discovery':'471 first missing expected150 at25011 with only392occupied sites. Examine B25005->association25008, not the later dense final state.','scope':'Five external steps replayed from the whole frozen-prefix snapshot. Passive full-state samples in a selected short window, not restoring an in-flight diagnostic snapshot as a supported life.','new_learning_claimed':False,'MAIN_untouched':True})
def fn(a):
    g=saved(a);h=g['native_habitats'][name];f=h['direct_failure']['opportunities'][0];p=g['material_queries'][f['query_name']];B=p['B'];t0=p['source_tick'];events={};rows=[]
    for dt in range(-1,8):
        t=t0+dt;sites=[('B',B)]
        for sign in(-1,1):
            sites.extend([('flight_'+str(sign)+'_'+str(k),n.move(B,(sign,-1,0),k))for k in(1,2,3)])
        events[t]=sites
    original=a.run_until
    def record(t):
        for when in sorted(k for k in events if a.tick<k<=t):
            original(when);samples=[]
            for label,site in events[when]:
                context=[n.obs(a,[(site[0]+dx)%67,(site[1]+dy)%67,(site[2]+dz)%67])for dx in(-1,0,1)for dy in(-1,0,1)for dz in(-1,0,1)]
                samples.append({'label':label,'site':site,'native':n.obs(a,site),'context27':context})
            snap=E/(life+'.T'+str(when)+'.DIAGNOSTICO_NO_OPERATIVO.deetsnap.gz');a.save(snap);rows.append({'tick':when,'samples':samples,'physical':physical(a.world,occupation=True),'snapshot':str(snap.relative_to(R)),'sha256':sha(snap)})
        original(t)
    a.run_until=record
    try:v=motor.run(a,steps=5,mode='closed',feedback='cost',transition=True,habitat=name,motor_codec='native_body_roles')
    finally:a.run_until=original
    return{'external':v,'samples':rows,'final':physical(a.world,occupation=True),'coverage':'Local sampling plus full global snapshots. No unique packet identity inferred from equal payloads.'}
v=run(life,'MI01_473_ASOCIACION_MICRO',fn)['result'];print(json.dumps([{'tick':r['tick'],'occupied':r['physical']['occupied'],'B':r['samples'][0]['native'],'Pplus':next(s['native']for s in r['samples']if s['label']=='flight_1_3')}for r in v['samples']],ensure_ascii=False))
