"""Prospective finite raw-tree screen, paired complete MU_MAIN forks.

No component sum enters DEE. Fixed reader/query at datum-3 and query+6.
No clearing, resizing, transplanted memories, repaired admissions or host choice.
"""
from __future__ import annotations
import argparse,gc,gzip,hashlib,json,os,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from arbol_umbral_adquirido_b01 import internal_A_close,native_imports,memory_guard
from arbol_en_selector_b05 import plan,enqueue
import importlib.util
FRONT_SOURCE=HERE.parent/'transferencia_b/frontend_b01_r2.py'
_spec=importlib.util.spec_from_file_location('fixed_transient_frontend_B05',FRONT_SOURCE)
front=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(front)
LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema'
CUT='estado/checkpoints/MU_MAIN.T16634.ba61eac94a01.deetsnap.gz';EXPECTED='b6c02df2e804b167b85f9e8fd849e091227b81ccfd7a49e442f67156944c71ad'
E=(15,15,15)
def prepare_frontend(a,ni):
    r=front.prepare(a,ni);body=ni[7];d=ni[0];p=(15,14,15);o=body.obs(a,p);inert=int(d.pack_record(0,0,0,0,0,4));rs=[]
    if int(o['raw'])!=inert:
        if int(o['raw'])!=0:raise ValueError('Extra S spill stop intersects nonzero RAW; never erase the context')
        name='FI01.B05.S.spill_stop';c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*p);c.direction=d.Direction(0,0,0);c.state=0;c.semantic=4;c.allow_experience=True;c.allow_probe=False
        i=d.InterfaceSpec();i.name=name;i.channel=c;a.world.declare_interface(i);t=a.tick+2;v=a.world.submit(name,0,t);rs=[{'id':int(v.id),'port':name,'payload':0,'tick':t,'site':list(p)}];a.run_until(t+1)
    from capacidades import selector_acrecion_nativo as sel
    out=[sel.receipt(a.world,q)for q in rs]
    if any(q['receipt']['status']!='applied'for q in out):raise ValueError('Extra spill stop was rejected, preserve reached state')
    return {'common_frontend':r,'extra_spill_stop':{'site':p,'before':o,'after':body.obs(a,p),'requests':out},'classification':'Declared P0 external receptor/actuator termination, not learned content.'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,o):
    if p.exists():raise FileExistsError(p)
    p.parent.mkdir(parents=True,exist_ok=True);b=json.dumps(o,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
    if p.suffix=='.gz':
        with p.open('xb')as f:
            with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0)as z:z.write(b)
    else:p.write_bytes(b)
def execute(a,level,label,ni,sel,old_panel=False,intervention=None):
    d,encode,decode,Store,Adapter,now,physical,body,ep=ni;g=plan(level,E,67);start=a.tick
    pre=physical(a.world,occupation=True);pre_nonzero=[body.obs(a,p)for p in g['opened']if int(body.obs(a,p)['raw'])!=0]
    values=[0]*level
    if label in('single_first','single_no_query'):values[0]=2
    elif label=='single_last':values[-1]=2
    elif label=='all_two':values=[2]*level
    if label in('no_raw','query_only'):
        leaf=start+2;root=leaf-g['raw_relative_tick'];datum=root+g['datum_relative_tick'];requests=[]
        if label=='no_raw':
            for s in g['generic_sources']:requests.append(body.send(a,'FI01.B05.'+s['id'],s['site'],s['direction'],root+s['injection_tick_relative'],0))
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
    rows=[];answer=None;edits=[]
    for t in sorted(schedule):
        if t<start:continue
        memory_guard();a.run_until(t)
        if intervention and t==root+(36 if intervention['site']=='C'else 38):
            site=g['remote_aggregate_site']if intervention['site']=='C'else g['datum_site'];before=body.obs(a,site)
            record={'kind':'EXTERNAL_DIAGNOSTIC_ONLY','site':site,'tick':a.tick,'pre':before,'mode':intervention['mode'],'performed':False}
            if before['state']>0:
                pre_file=Path(intervention['directory'])/(intervention['case']+'.pre_'+intervention['site']+'.T'+str(a.tick)+'.deetsnap.gz');a.save(pre_file)
                edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.clock=int(before['clock']);edit.label='Fixed diagnostic s_reg removal or exact RAW sham; never a native action or recovery'
                edit.raw=int(before['raw'])if intervention['mode']=='sham'else int(d.pack_record(before['state'],0,*before['direction'],before['semantic']))
                raw_pre=physical(a.world);a.world=a.world.diagnostic_fork([edit],True);raw_post=physical(a.world)
                record.update(performed=True,post=body.obs(a,site),before_physical=raw_pre,after_physical=raw_post,pre_snapshot={'path':str(pre_file),'sha256':sha(pre_file)})
            edits.append(record)
        rows.append({'tick':a.tick,'fields':{k:body.obs(a,p)for k,p in pts.items()}})
        if t==q+6:answer=front.reader(a,ni)
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
      'diagnostic_edits':edits,'final':physical(a.world,occupation=True),'peak_process_bytes':memory_guard(),
      'scope':'Native raw aggregation candidate plus this exact inherited acquired reference. No result is inferred solely from admitted ports or an auditor sum. Sparse0/2 boundary screen, notNsemantic concepts.'}
UCUT='estado/checkpoints/MU_SELECTOR_RETURN_U.T16066.039da88eadde.deetsnap.gz'
UEXPECTED='9471100a4cec341c40d9b3f03e402032d1cd3319937dd4347af6792f79bff5de'
CASES=[('history_U_zero','MU_SELECTOR_RETURN_U','zero',None,None),('history_U_two','MU_SELECTOR_RETURN_U','single_first',None,None),
 ('equal_refs_zero','MU_MAIN','zero','equal',None),('equal_refs_two','MU_MAIN','single_first','equal',None),
 ('ref_sham_zero','MU_MAIN','zero','sham',None),('ref_sham_two','MU_MAIN','single_first','sham',None),
 ('cut_C_two','MU_MAIN','single_first',None,('C','cut')),('sham_C_two','MU_MAIN','single_first',None,('C','sham')),
 ('cut_S_two','MU_MAIN','single_first',None,('S','cut')),('sham_S_two','MU_MAIN','single_first',None,('S','sham'))]
def initial_edit(a,mode,ni):
    d,encode,decode,Store,Adapter,now,physical,body,ep=ni;A=(14,14,15);B=(16,14,15);o=body.obs(a,A);b=body.obs(a,B)
    ed=d.ResearchStateEdit();ed.coordinate=d.Coordinate(*A);ed.clock=int(o['clock']);ed.label='External diagnostic only: equalize one acquired scalar or exact RAW sham'
    ed.raw=int(o['raw'])if mode=='sham'else int(d.pack_record(o['state'],b['s_reg'],*o['direction'],o['semantic']))
    pre=physical(a.world);a.world=a.world.diagnostic_fork([ed],True)
    return {'classification':'EXTERNAL_DIAGNOSTIC_NOT_NEW_LEARNING','mode':mode,'A_before':o,'B_before':b,'A_after':body.obs(a,A),'before':pre,'after':physical(a.world)}
def main():
    authorization=internal_A_close(LAB/'CIERRE_INTERNO_A.json')
    if sha(SYSTEM/CUT)!=EXPECTED or sha(SYSTEM/UCUT)!=UEXPECTED:raise ValueError('Wrong explicit complete history source')
    os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    ni=native_imports();d,encode,decode,Store,Adapter,now,physical,body,ep=ni
    from capacidades import selector_acrecion_nativo as sel
    store=Store();original=sha(store.life_dir('MU_MAIN')/'VIDA.json');active=sha(SYSTEM/'estado/ACTIVO.json')
    out=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento/B05_CONTROLS_R3_N128'
    dump(out/'PROTOCOLO.json',{'authorization':authorization,'before_native_ticks':now(),'source':CUT,'source_sha256':EXPECTED,
      'script_sha256':sha(__file__),'dependency_hashes':{p.name:sha(p)for p in[FRONT_SOURCE,HERE/'arbol_en_selector_b05.py',HERE/'arbol_en_selector_b02.py',HERE/'arbol_umbral_adquirido_b01.py',HERE/'preflight_arbol_crudo.py']},
      'other_history_source':UCUT,'other_history_sha256':UEXPECTED,'align_U_to_tick':16634,
      'level':128,'cases':CASES,'old_panel_after_every_arm':True,'reader':'Same six fixed classes atq+6, no plane choice','not_independent_replicas':True,
      'diagnostic_scope':'Equalization/cuts are external edits only in copies, never learning or actions. Native U differs in real past and has other full-state differences; exact one-field diagnostic plus sham complements, not replaces, that history contrast.',
      'formed_content_cut':'At predetermined Croot+36 or Sroot+38, preserve state/semantic/direction/clock, set s_reg0. Sham preserves entire RAW. No selection by eventual response.'})
    summary=[]
    for label,source,frame_label,ref_mode,later in CASES:
        life='FI01_B05_CONTROL_R3_'+label
        if store.life_dir(life).exists():raise FileExistsError('Existing diagnostic branch protected: '+life)
        store.fork(source,life,kind='B05_HISTORY_OR_CAUSAL_CONTROL',checkpoint=UCUT if source!='MU_MAIN'else CUT);gc.collect();memory_guard()
        if source!='MU_MAIN':
            def age(a):
                before=physical(a.world);a.run_until(16634);memory_guard();return {'before':before,'after':physical(a.world),'scope':'Same owner/protocol advancement without new probes or reference copy'}
            aligned=store.mutate(life,'B05_AGE_ALIGNMENT_ONLY',age,{'original_U_sha256':UEXPECTED});dump(out/(label+'_AGE.json.gz'),aligned);del aligned;gc.collect()
        prep=store.mutate(life,'B05_TRANSIENT_FRONTEND_P0',lambda a:prepare_frontend(a,ni),{'source_revision':sha(__file__),'common_frontend_sha256':sha(FRONT_SOURCE)})
        dump(out/(label+'_PREP.json.gz'),prep);del prep;gc.collect();memory_guard()
        def trial(a):
            edited=initial_edit(a,ref_mode,ni)if ref_mode else None
            iv={'site':later[0],'mode':later[1],'directory':str(out),'case':label}if later else None
            result=execute(a,128,frame_label,ni,sel,True,iv);result['initial_reference_diagnostic']=edited;result['case_label']=label;return result
        x=store.mutate(life,'B05_RAW_TREE_CAUSAL_R3',trial,{'exact_source':UEXPECTED if source!='MU_MAIN'else EXPECTED,'level':128,'case':label,'source_revision':sha(__file__)})
        dump(out/(label+'.json.gz'),x)
        r=x['result'];row={'label':label,'life':life,'choice':r['reader']['choice'],'applied':sum(q['receipt']['status']=='applied'for q in r['requests']),
          'requested':len(r['requests']),'route_pre_nonzero':len(r['pre_nonzero_route_fields']),'end_tick':x['physical']['tick'],'snapshot_sha256':x['INSTRUMENTO']['snapshot_sha256'],
          'old_six_choices':[z['reader']['formed_native_command']for z in r['old_six_panel_after_2N']['rows']]if r['old_six_panel_after_2N']else None,'output_sha256':sha(out/(label+'.json.gz'))}
        summary.append(row);print(json.dumps(row),flush=True);del x;gc.collect();memory_guard()
    integrity={'parent_snapshot_unchanged':EXPECTED==sha(SYSTEM/CUT),'other_history_snapshot_unchanged':UEXPECTED==sha(SYSTEM/UCUT),'active_unchanged':active==sha(SYSTEM/'estado/ACTIVO.json')}
    dump(out/'RESUMEN.json',{'arms':summary,'integrity':integrity,'mutable_MAIN_record_changed_elsewhere':original!=sha(store.life_dir('MU_MAIN')/'VIDA.json'),
      'guard_scope':'Checks immutable specified source snapshots, not the mutable source-life pointer legitimately advanced by another owner. No source world is written by this script.', 'finished_utc':now()})
    if not all(integrity.values()):raise AssertionError('Original identity changed externally; no protection certification')
if __name__=='__main__':main()
