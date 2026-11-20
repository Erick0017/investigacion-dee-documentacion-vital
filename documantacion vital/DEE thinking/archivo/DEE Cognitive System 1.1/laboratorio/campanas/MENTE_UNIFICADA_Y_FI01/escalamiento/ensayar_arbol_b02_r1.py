"""Prospective finite raw-tree screen, paired complete MU_MAIN forks.

No component sum enters DEE. Fixed reader/query at datum-3 and query+6.
No clearing, resizing, transplanted memories, repaired admissions or host choice.
"""
from __future__ import annotations
import argparse,gc,gzip,hashlib,json,os,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from arbol_umbral_adquirido_b01 import internal_A_close,native_imports,memory_guard
from arbol_en_selector_b02 import plan,enqueue
LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema'
CUT='estado/checkpoints/MU_MAIN.T16634.ba61eac94a01.deetsnap.gz';EXPECTED='b6c02df2e804b167b85f9e8fd849e091227b81ccfd7a49e442f67156944c71ad'
E=(15,15,15)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,o):
    if p.exists():raise FileExistsError(p)
    p.parent.mkdir(parents=True,exist_ok=True);b=json.dumps(o,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
    if p.suffix=='.gz':
        with p.open('xb')as f:
            with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0)as z:z.write(b)
    else:p.write_bytes(b)
def execute(a,level,label,ni,sel,old_panel=False):
    d,encode,decode,Store,Adapter,now,physical,body,ep=ni;g=plan(level,E,67);start=a.tick
    pre=physical(a.world,occupation=True);pre_nonzero=[body.obs(a,p)for p in g['opened']if int(body.obs(a,p)['raw'])!=0]
    values=[0]*level
    if label in('single_first','single_no_query'):values[0]=2
    elif label=='single_last':values[-1]=2
    elif label=='all_two':values=[2]*level
    if label in('no_raw','query_only'):
        leaf=start+2;root=leaf-g['raw_relative_tick'];datum=root+36;requests=[]
        if label=='no_raw':
            for s in g['generic_sources']:requests.append(body.send(a,'FI01.B02.'+s['id'],s['site'],s['direction'],root+s['injection_tick_relative'],0))
    else:
        offered=enqueue(a,values,level=level,E=E);leaf=offered['leaf_tick'];root=offered['root_tick'];datum=offered['datum_tick'];requests=offered['requests']
    q=datum-3
    if label!='single_no_query':requests.extend(sel.query(a.world,q,5,'MU.selector'))
    # Observed coordinates are fixed BEFORE looking at any result.
    pts={'E':E,'D':g['datum_site'],'A':sel.at(E,(-1,-1,0)),'B':sel.at(E,(1,-1,0))}
    pts.update({n['id']:n['site']for n in g['nodes']})
    for s in g['generic_sources']:
        pts[s['id']+'.source']=s['site'];pts[s['id']+'.meeting']=[(s['site'][i]+s['direction'][i])%67 for i in range(3)]
    for x in(-1,0,1):pts['actuator'+str(x)]=sel.at(E,(2*x,2,0))
    schedule={leaf-1,leaf,leaf+1,datum-2,datum-1,datum,datum+1,q+6,q+8}
    schedule.update(root+n['join_tick_relative']+dt for n in g['nodes']for dt in(-1,0,1))
    schedule.update(root+s['injection_tick_relative']+dt for s in g['generic_sources']for dt in(0,1,2))
    rows=[];answer=None
    for t in sorted(schedule):
        if t<start:continue
        memory_guard();a.run_until(t);rows.append({'tick':a.tick,'fields':{k:body.obs(a,p)for k,p in pts.items()}})
        if t==q+6:answer=sel.read(a.world,E,67)
    refs_at_read=[body.obs(a,sel.at(E,p))for p in[(-1,-1,0),(1,-1,0)]]
    a.run_until(q+8+134);memory_guard();passive=physical(a.world,occupation=True)
    old=None
    if old_panel:
        from capacidades import mente_acumulativa_r02 as ma
        old=ma.session(a,situations=[{'contexto':c}for c in['alfa','beta','gamma','delta','epsilon','zeta']],directory=HERE/'NO_EXTERNAL_ACTIONS',detailed=False)
    return {'label':label,'level':level,'initial':pre,'raw_components':values,'input_count':0 if label in('no_raw','query_only')else level,
      'generic_zero_count':0 if label=='query_only'else len(g['generic_sources']),'geometry':g,'pre_nonzero_route_fields':pre_nonzero,
      'leaf_tick':leaf,'native_datum_tick':datum,'query_tick':q,'fixed_reader_tick':q+6,'reader':answer,'frames':rows,
      'requests':[{**r,'receipt':sel.exact_receipt(a.world.runtime.receipt(r['id']))}for r in requests],
      'references_after_reader_window':refs_at_read,'passive_after_2N':passive,'old_six_panel_after_2N':old,
      'final':physical(a.world,occupation=True),'peak_process_bytes':memory_guard(),
      'scope':'Native raw aggregation candidate plus this exact inherited acquired reference. No result is inferred solely from admitted ports or an auditor sum. Sparse0/2 boundary screen, notNsemantic concepts.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--level',type=int,choices=(8,16,32,64,128),required=True);ap.add_argument('--old-panel',action='store_true');args=ap.parse_args()
    authorization=internal_A_close(LAB/'CIERRE_INTERNO_A.json')
    if sha(SYSTEM/CUT)!=EXPECTED:raise ValueError('Wrong explicit complete A cut')
    os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    ni=native_imports();d,encode,decode,Store,Adapter,now,physical,body,ep=ni
    from capacidades import selector_acrecion_nativo as sel
    store=Store();original=sha(store.life_dir('MU_MAIN')/'VIDA.json');active=sha(SYSTEM/'estado/ACTIVO.json')
    out=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento'/('B02_TREE_R1_N'+str(args.level))
    labels=['zero','single_first','single_last','all_two','single_no_query','no_raw','query_only']
    dump(out/'PROTOCOLO.json',{'authorization':authorization,'before_native_ticks':now(),'source':CUT,'source_sha256':EXPECTED,
      'script_sha256':sha(__file__),'dependency_hashes':{p.name:sha(p)for p in[HERE/'arbol_en_selector_b02.py',HERE/'arbol_umbral_adquirido_b01.py',HERE/'preflight_arbol_crudo.py']},
      'level':args.level,'labels':labels,'old_panel_after_every_arm':args.old_panel,'reader':'Same3physical actuator sites atq+6, q=dataarrival−3','not_independent_replicas':True})
    summary=[]
    for label in labels:
        life='FI01_B02_TREE_R1_N'+str(args.level)+'_'+label
        if store.life_dir(life).exists():raise FileExistsError('Existing diagnostic branch protected: '+life)
        store.fork('MU_MAIN',life,kind='B02_RAW_TREE_PAIRED_DIAGNOSTIC',checkpoint=CUT);gc.collect();memory_guard()
        x=store.mutate(life,'B02_RAW_TREE_R1',lambda a:execute(a,args.level,label,ni,sel,args.old_panel),{'exact_source':EXPECTED,'level':args.level,'label':label,'source_revision':sha(__file__)})
        dump(out/(label+'.json.gz'),x)
        r=x['result'];row={'label':label,'life':life,'choice':r['reader']['choice'],'applied':sum(q['receipt']['status']=='applied'for q in r['requests']),
          'requested':len(r['requests']),'route_pre_nonzero':len(r['pre_nonzero_route_fields']),'end_tick':x['physical']['tick'],'snapshot_sha256':x['INSTRUMENTO']['snapshot_sha256'],
          'old_six_choices':[z['reader']['formed_native_command']for z in r['old_six_panel_after_2N']['rows']]if r['old_six_panel_after_2N']else None,'output_sha256':sha(out/(label+'.json.gz'))}
        summary.append(row);print(json.dumps(row),flush=True);del x;gc.collect();memory_guard()
    integrity={'parent_record_unchanged':original==sha(store.life_dir('MU_MAIN')/'VIDA.json'),'parent_snapshot_unchanged':EXPECTED==sha(SYSTEM/CUT),'active_unchanged':active==sha(SYSTEM/'estado/ACTIVO.json')}
    dump(out/'RESUMEN.json',{'arms':summary,'integrity':integrity,'finished_utc':now()})
    if not all(integrity.values()):raise AssertionError('Original identity changed externally; no protection certification')
if __name__=='__main__':main()
