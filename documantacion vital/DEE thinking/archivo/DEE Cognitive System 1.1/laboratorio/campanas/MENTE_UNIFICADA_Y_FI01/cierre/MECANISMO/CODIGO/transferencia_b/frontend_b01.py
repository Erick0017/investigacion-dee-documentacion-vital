"""Frozen B-transfer frontend: transient current datum, not a host comparator.

Exact fork of the closed A cut. All supplementary stops are admitted through
legal inactive SEM4 inputs. No RAW edit/clear, no target-aware reader.
"""
from __future__ import annotations
import argparse,gc,gzip,hashlib,json,os,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema'
sys.path.insert(0,str(LAB/'escalamiento'))
from arbol_umbral_adquirido_b01 import internal_A_close,native_imports,memory_guard
OUT=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/transferencia_b'
CUT='estado/checkpoints/MU_MAIN.T16634.ba61eac94a01.deetsnap.gz'
EXPECTED='b6c02df2e804b167b85f9e8fd849e091227b81ccfd7a49e442f67156944c71ad'
E=(15,15,15);S=(14,15,16);N=67
STOPS=[(E[0]+3*x,E[1]+3,E[2]+3*z)for x in(-1,0,1)for z in(0,-1)]

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,o):
    if p.exists():raise FileExistsError(p)
    p.parent.mkdir(parents=True,exist_ok=True)
    data=json.dumps(o,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
    if p.suffix=='.gz':
        with p.open('xb')as f:
            with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0)as z:z.write(data)
    else:p.write_bytes(data)

def reader(a,ni):
    body=ni[8];observations=[];candidates=[]
    for x in(-1,0,1):
        for z in(0,-1):
            o=body.obs(a,(E[0]+2*x,E[1]+2,E[2]+2*z));observations.append(o)
            if o['state']>0 and o['semantic']==1 and o['direction']==[x,1,z]:candidates.append({'choice':x,'observation':o})
    return {'tick':a.tick,'observations':observations,'candidates':candidates,'choice':candidates[0]['choice']if len(candidates)==1 else None,
      'information':'Six fixed spatial/directional classes; no datum, target, history or selected plane is an argument.'}

def prepare(a,ni):
    body=ni[8]
    from dee_thinking import _native as d
    inert=int(d.pack_record(0,0,0,0,0,4));before=[body.obs(a,p)for p in STOPS];rs=[];t=a.tick+2
    for j,o in enumerate(before):
        if o['raw']==inert:continue
        if o['raw']!=0:raise ValueError('Stop is not vacant RAW or existing identical inactive SEM4; no overwrite: '+repr(o))
        name='FI01.BT.S.stop.'+str(j);c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*STOPS[j]);c.direction=d.Direction(0,0,0);c.state=0;c.semantic=4;c.allow_experience=True;c.allow_probe=False
        i=d.InterfaceSpec();i.name=name;i.channel=c;a.world.declare_interface(i);r=a.world.submit(name,0,t)
        rs.append({'id':int(r.id),'port':name,'payload':0,'tick':t,'site':list(STOPS[j])})
    a.run_until(t+1);memory_guard()
    from capacidades import selector_acrecion_nativo as sel
    receipts=[sel.receipt(a.world,r)for r in rs]
    if any(r['receipt']['status']!='applied'for r in receipts):raise ValueError('P0 stop admission incomplete; retain reached state, do not retry')
    return {'before':before,'after':[body.obs(a,p)for p in STOPS],'requests':receipts,'S':body.obs(a,S),'classification':'External P0 frontend, not acquired information.'}

def trial(a,label,value,ni,query=True,site=S):
    body=ni[8];physical=ni[7]
    from capacidades import selector_acrecion_nativo as sel
    q=a.tick+8;pre=physical(a.world,occupation=True);rs=[]
    datum_pre=body.obs(a,site)
    if value is not None:rs.append(body.send(a,'FI01.BT.S.datum',site,(0,0,0),q+3,value))
    if query:rs.extend(sel.query(a.world,q,5,'MU.selector'))
    points={sel.at(E,(x,y,z))for x in range(-3,4)for y in range(-3,5)for z in range(-4,4)};points.add(tuple(site))
    rows=[];answer=None
    for t in range(q-1,q+9):
        memory_guard();a.run_until(t);rows.append({'tick':a.tick,'sites':[body.obs(a,p)for p in sorted(points)]})
        if t==q+6:answer=reader(a,ni)
    return {'label':label,'value':value,'site':list(site),'query':query,'query_tick':q,'reader':answer,'before':pre,'datum_pre':datum_pre,
      'frames':rows,'requests':[sel.receipt(a.world,r)for r in rs],'after':physical(a.world,occupation=True),'datum_after':body.obs(a,site),
      'references':[body.obs(a,p)for p in[(14,14,15),(16,14,15)]],
      'scope':'Fixed raw-value transduction and native gradient choice. No externally calculated comparison or selected response enters DEE.'}

def bootstrap():
    authorization=internal_A_close(LAB/'CIERRE_INTERNO_A.json')
    if digest(SYSTEM/CUT)!=EXPECTED:raise ValueError('Frozen complete source snapshot changed')
    os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    return authorization,native_imports()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--calibrate',action='store_true');args=ap.parse_args()
    if not args.calibrate:raise ValueError('Only frozen initial calibration is authorized by this revision')
    authorization,ni=bootstrap();Store=ni[3];now=ni[5];store=Store();code=digest(__file__)
    dump(OUT/'B01_PROTOCOLO_CALIBRACION.json',{'revision':'BT.S1','before_first_tick':now(),'authorization':authorization,'code_sha256':code,
      'parent':'MU_MAIN','checkpoint':CUT,'checkpoint_sha256':EXPECTED,'prepared_stops':[list(p)for p in STOPS],'datum_site':list(S),
      'fixed_protocol':'query5 plus two generic zero supports atq; raw datum direction0 atq+3; six fixed actuator classes atq+6; endq+8. All native admissions count.',
      'ordered_same_life_values':[0,2,0,2],'controls':['noDatum','noQuery2','sham2'],'criterion_before_reserve':'Same calibration life produces alternating physical signs minus/plus without datum overwrite; S returns RAW0 after every use. T/U/H only proceed if fulfilled.',
      'not_claimed':'Not learned scalar threshold yet, no control policy or abstraction; exact-prefix diagnostic forks, not independent histories.'})
    rows=[]
    for label in('repeat','noDatum','noQuery2','sham2'):
        life='FI01_BT_S1_'+label
        if store.life_dir(life).exists():raise FileExistsError(life)
        fork=store.fork('MU_MAIN',life,kind='B_TRANSFER_TRANSIENT_FRONTEND',checkpoint=CUT);gc.collect();memory_guard()
        prep=store.mutate(life,'BT_S1_P0_FRONTEND',lambda a:prepare(a,ni),{'revision_sha256':code});dump(OUT/('B01_'+label+'_PREP.json.gz'),prep)
        specs=[('repeat'+str(j),v,True,S)for j,v in enumerate([0,2,0,2])]if label=='repeat'else[(label,None if label=='noDatum'else 2,label!='noQuery2',(14,15,23)if label=='sham2'else S)]
        result=store.mutate(life,'BT_S1_FIRST_USE_CALIBRATION',lambda a:{'trials':[trial(a,*[n,v,ni,b,p])for n,v,b,p in specs]}, {'revision_sha256':code,'fixed_specs':specs})
        dump(OUT/('B01_'+label+'_USES.json.gz'),result)
        row={'life':life,'choices':[r['reader']['choice']for r in result['result']['trials']],'S_final_raws':[r['datum_after']['raw']for r in result['result']['trials']],
          'tick':result['physical']['tick'],'snapshot_sha256':result['INSTRUMENTO']['snapshot_sha256']};rows.append(row);print(json.dumps(row),flush=True)
        del prep,result;gc.collect();memory_guard()
    dump(OUT/'B01_RESUMEN_CALIBRACION.json',{'rows':rows,'source_snapshot_unchanged':digest(SYSTEM/CUT)==EXPECTED,'peak_RSS':memory_guard()})
if __name__=='__main__':main()
