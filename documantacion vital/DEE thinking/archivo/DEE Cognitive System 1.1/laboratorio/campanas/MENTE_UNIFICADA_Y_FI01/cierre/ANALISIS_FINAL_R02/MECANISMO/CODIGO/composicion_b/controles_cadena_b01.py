"""Fixed causal composition controls; exact own forks, never advance MAIN."""
import argparse,gc,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema'
sys.path.insert(0,str(LAB/'transferencia_b'))
import frontend_b01_r2 as f
OUT=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/composicion_b'
PRE='estado/checkpoints/MU_MAIN.T17025.f4cff8ab1cec.deetsnap.gz'
PRESHA='20954a87458a93a3d8544cbc012550b51a1e71b2b12f14e008f20a57a81834ec'
PENDING='estado/checkpoints/MU_MAIN.T31832.e5cdd4e78b56.deetsnap.gz'
PENDSHA='3a7cf0052e36d48a825658e6b8ded6ac614af30ada9bb81e174ec72184614f10'

def protocol(ni):
    p=OUT/'PROTOCOLO.json';code=f.digest(__file__)
    if p.exists():
        old=json.loads(p.read_text(encoding='utf-8'))
        if old['code_sha256']!=code:raise ValueError('Frozen control source changed; no overwrite')
        return
    f.dump(p,{'schema':'MUFI01.B.composition_controls.R1','before_first_control_tick':ni[5](),'code_sha256':code,
      'native_module_sha256':f.digest(SYSTEM/'capacidades/mente_unificada_01.py'),'frontend_helper_sha256':f.digest(f.__file__),
      'prefix':{'snapshot':PRE,'sha256':PRESHA,'tick':17025},'prepared_pending':{'snapshot':PENDING,'sha256':PENDSHA,'tick':31832},
      'U':'Exact pre19fork, no replacement lessons. Passive to31673; then raw11/29/13/32, no return. Then gamma[21,4] chain begin; save; new process finish with actual pending artifact. Preserve failure/pending.',
      'noDatum':'Exact pendingSHA32 fork; same query3generic, datum omitted; fixed6readerq+6; nativechoice→actual transaction worker, no feedback.',
      'sham':'Exact pendingSHA32 fork; datum32 legaldir0 at(14,15,23)insteadS, same query andfixed6reader; actual worker, nofeedback.',
      'prediction_not_actor_input':'U inheritsD−1 and should fail second operation for preparedcompressedfile. noDatum/sham32 shouldemit−, same workerasSHAprepare, soverifyfail. No targets, law orprepared_by supplied as native inputs.',
      'protected':'No MAIN mutation or reset, no RAW/clocks edits, no alternate reader selection; all failures remain in saved own continuations.'})

def first_u(a,ni):
    from capacidades import mente_unificada_01 as mu
    a.run_until(31673);f.memory_guard()
    m=mu.get(a);rows=[]
    for v in(11,29,13,32):
        r=mu.current(a,v,detail=True);m['queries']+=1;m['episodes']+=1;mu.save(a,m);rows.append(r)
    begun=mu.session(a,situations=[{'modo':'cadena-iniciar','contexto':'gamma','valores':[21,4]}],directory=OUT/'U_worker',feedback='omit',detailed=True)
    return {'raw_uses':rows,'chain_begin':begun,'actual_pending':mu.get(a).get('external_pending'),'no_new_reference_teaching':True}

def diagnostic(a,kind,ni):
    from capacidades import mente_unificada_01 as mu
    m=mu.get(a);before_pending=m.get('external_pending')
    if not before_pending:raise ValueError('Original complete pending transaction required')
    r=f.trial(a,kind,None if kind=='noDatum'else 32,ni,True,f.S if kind=='noDatum'else(14,15,23))
    values=m['cascade_pending']['values']
    r['external']=mu.job(a,r,{'valores':values,'dominio':'transaccion'},OUT/(kind+'_worker'),m,feedback='omit')
    m['queries']+=1;m['episodes']+=1;mu.save(a,m)
    return {'kind':kind,'native_and_action':r,'pending_before':before_pending,'pending_after':mu.get(a).get('external_pending'),
      'fixed_protocol_no_correct_answer_input':True,'physical':ni[6](a.world,occupation=True)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fase',choices=('U1','U2','noDatum','sham'),required=True);args=ap.parse_args()
    authorization,ni=f.bootstrap();protocol(ni);store=ni[3]();f.memory_guard()
    from capacidades import mente_unificada_01 as mu
    kind=args.fase;life='FI01_BCOMP_'+('U'if kind.startswith('U')else kind)
    if kind!='U2':
        snapshot,sha=(PRE,PRESHA)if kind=='U1'else(PENDING,PENDSHA)
        if f.digest(SYSTEM/snapshot)!=sha:raise ValueError('Original complete control snapshot hash mismatch')
        if store.life_dir(life).exists():raise FileExistsError(life)
        store.fork('MU_MAIN',life,kind='B_COMPOSITION_CAUSAL_CONTROL',checkpoint=snapshot);gc.collect();f.memory_guard()
    if kind=='U1':callback=lambda a:first_u(a,ni)
    elif kind=='U2':callback=lambda a:mu.session(a,situations=[{'modo':'cadena-finalizar'}],directory=OUT/'U_worker_continued_process',feedback='omit',detailed=True)
    else:callback=lambda a:diagnostic(a,kind,ni)
    result=store.mutate(life,'B_COMPOSITION_CONTROL_'+kind,callback,{'authorization':authorization,'code_sha256':f.digest(__file__),'phase':kind})
    f.dump(OUT/(kind+'.json.gz'),result)
    print(json.dumps({'phase':kind,'life':life,'tick':result['physical']['tick'],'snapshot_sha256':result['INSTRUMENTO']['snapshot_sha256'],'primary_sha256':f.digest(OUT/(kind+'.json.gz'))}))
if __name__=='__main__':main()
