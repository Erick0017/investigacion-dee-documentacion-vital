"""Prospective single R3 phase-protection pair, reusing the R15 real history.

World-only diagnostic, not a new life, service or promotion. Explicit P0 flag
changes the common input schedule only; fixed native six-class reader unchanged.
Must be executed only after Root approves the exact installed R3 source hashes.
"""
from __future__ import annotations
import argparse,gc,hashlib,importlib.util,json,os,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from arbol_umbral_adquirido_b01 import internal_A_close,native_imports,memory_guard
from ensayar_arbol_b05_r1 import dump,sha
LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema'
EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01'
R15=EV/'servicio/AUTOPSIA_FASE_R15';OUT=EV/'servicio/PROTECCION_FASE_R16'
SOURCE=SYSTEM/'estado/checkpoints/MU_MAIN.T62525.25da49a2c759.deetsnap.gz'
SOURCE_SHA='686e22bcb58d5e32368fe4af6e58cc848209fbda3afb5ffc09606ea64da8f8eb'
BASE=R15/'snapshots/real_62564_POST.deetsnap.gz'
SHAM=(14,15,23);SHAM_NAME='FI01.R15.sham.scalar29';E=(15,15,15)
LABELS=['unprotected_age_matched','protected_R3']
CONTEXTS=['alfa','beta','gamma','delta','epsilon','zeta']

def observer():
    q=SYSTEM/'capacidades/observador_causal_retrospectivo_01.py';sp=importlib.util.spec_from_file_location('pure_R16_observer',q)
    m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--approved-source-hashes',type=Path,required=True);args=ap.parse_args()
    if OUT.exists():raise FileExistsError('No implicit repeat of R16')
    auth=internal_A_close(LAB/'CIERRE_INTERNO_A.json');approved=json.loads(args.approved_source_hashes.read_text(encoding='utf8'))
    if approved.get('native_R16_authorized')is not True:raise ValueError('Exact source Root approval required before Runtime')
    for name,h in approved['sha256'].items():
        if sha(SYSTEM/'capacidades'/name)!=h:raise ValueError('Approved source changed: '+name)
    if sha(SOURCE)!=SOURCE_SHA:raise ValueError('Wrong original complete prefix')
    r15=json.loads((R15/'RESUMEN.json').read_text(encoding='utf8'))
    old=next(x for x in r15['arms']if x['arm']=='real');baseline_expected=next(s['sha256']for s in old['snapshots']if s['tag']=='62564_POST')
    if sha(BASE)!=baseline_expected:raise ValueError('Wrong closed R15 real snapshot')
    ob=observer()
    for p in(SOURCE,BASE):
        s=ob.Snapshot(p)
        if s.pending or ob.organization(s)['protocols']:raise ValueError('Complete source has unfinished physical protocol')
    vector=[0]*128;vector[0]=19;vector[2]=2
    protocol={'schema':'FI01.R16.phase_protection.paired.v1','authorization':auth,'root_approval':approved,
      'source':str(SOURCE),'source_sha256':SOURCE_SHA,'baseline_reused':str(BASE),'baseline_sha256':baseline_expected,
      'reused_history':'R15 real413 already executed; baseline advances only6 passive ticks to match the protected final62570.',
      'code_sha256':sha(__file__),'same_sham_interface':{'name':SHAM_NAME,'site':list(SHAM),'state':1,'semantic':1,'direction':[0,0,0]},
      'schedule':{'protected_begin':62548,'requested_query':62556,'expected_effective_query':62562,'scalar_value':29,'matched_end':62570,'passive_end':62704},
      'phase_rule':'floor((q-2)/391)==floor((q+8)/391); smallest nonnegative common shift, independent of payload/RAW/results.',
      'common_raw_vector':vector,'common_raw_begin':62704,'common_old_panel':CONTEXTS,
      'frozen_reader':'All six existing MU.current direction classes at q+6 in both arms, unchanged.',
      'assistance':'Researcher explicitly enables prepared P0 scheduling; not learned choice, new content, recovery initiative or P2/R2.',
      'not_independent_learners':True,'no_Main_Store_SQLite_or_workers':True}
    dump(OUT/'PROTOCOLO.json',protocol)
    for name in approved['sha256']:
        target=OUT/'codigo_congelado'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((SYSTEM/'capacidades'/name).read_bytes())
    os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    ni=native_imports();d,encode,decode,Store,Adapter,now,physical,body,ep=ni
    from dee_thinking.persistence import load_world_snapshot
    from capacidades import mente_unificada_01 as mu,percepcion_cruda_fi01 as raw,mente_acumulativa_r02 as ma
    all_summaries=[]
    for label in LABELS:
        memory_guard();w,_=load_world_snapshot(BASE if label=='unprotected_age_matched'else SOURCE);a=Adapter(w);del w
        saves=[]
        def save(tag):
            path=OUT/'snapshots'/(label+'_'+tag+'.deetsnap.gz');path.parent.mkdir(parents=True,exist_ok=True);a.save(path)
            saves.append({'tag':tag,'tick':a.tick,'path':str(path),'sha256':sha(path)})
        if label=='protected_R3':
            raw.declare(a,SHAM_NAME,SHAM,(0,0,0));flag=mu.protect_phase(a)
            a.run_until(62548);save('62548_BEFORE')
            current=mu.current(a,29,detail=True)
            if current['query_tick']!=62562 or a.tick!=62570:raise ValueError('Prospective frozen schedule differs; preserve reached state, do not retune')
        else:
            flag={'not_enabled':True,'R15_original_query_tick':62556,'history_not_replayed':True};current={'reused_R15_record':str(R15/'real.json.gz'),'reused_R15_sha256':sha(R15/'real.json.gz')}
            a.run_until(62570)
        save('62570_MATCHED');matched=physical(a.world,occupation=True)
        refs_matched=[mu.observation(a,p)for p in((14,14,15),(16,14,15))]
        a.run_until(62704);memory_guard();save('62704_PASSIVE')
        common=raw.frame(a,vector,detailed=True);memory_guard();save('AFTER_COMMON_RAW128')
        panel=ma.session(a,situations=[{'contexto':c}for c in CONTEXTS],directory=OUT/'NO_EXTERNAL_ACTIONS',detailed=False)
        memory_guard();save('AFTER_OLD_SIX')
        result={'label':label,'prepared_phase_flag':flag,'scalar_or_reused_history':current,'matched':matched,'refs_matched':refs_matched,
          'common_raw128':common,'old_six_panel':panel,'final':physical(a.world,occupation=True),'snapshots':saves,'peak_bytes':memory_guard(),
          'scope':'One dependent pair; prepared P0 temporal assistance only. No learner is restored to erase its own future or supplied a target.'}
        dump(OUT/(label+'.json.gz'),result)
        all_summaries.append({'label':label,'matched':matched,'refs_matched':refs_matched,'raw_choice':common['reader']['choice'],
          'raw_query_tick':common['query_tick'],'raw_read_tick':common['read_tick'],'raw_requests':len(common['requests']),
          'old_six_commands':[r['reader']['formed_native_command']for r in panel['rows']],'final':result['final'],'snapshots':saves})
        print(json.dumps(all_summaries[-1]),flush=True)
        del a,result,current,common,panel;gc.collect();memory_guard()
    dump(OUT/'RESUMEN.json',{'protocol_sha256':sha(OUT/'PROTOCOLO.json'),'rows':all_summaries,'source_unchanged':sha(SOURCE)==SOURCE_SHA,'baseline_unchanged':sha(BASE)==baseline_expected})
    # Retrospective full comparisons, no more native ticks.
    comparisons={};agendas={}
    for row in all_summaries:
        for ss in row['snapshots']:
            s=ob.Snapshot(ss['path']);owner=ob.organization(s)
            agendas[row['label']+'_'+ss['tag']]={'summary':s.summary(),'pending':s.pending,'channels':s.channels,'receipts':s.receipts,'next_event_id':s.next_event_id,'next_sequence':s.next_sequence,'owner_protocols':owner['protocols'],'owner_interfaces':owner['recipe']['interfaces']}
    for tag in('62570_MATCHED','62704_PASSIVE','AFTER_COMMON_RAW128','AFTER_OLD_SIX'):
        x=next(s['path']for s in all_summaries[0]['snapshots']if s['tag']==tag);y=next(s['path']for s in all_summaries[1]['snapshots']if s['tag']==tag)
        comparisons[tag]=ob.compare(ob.Snapshot(x),ob.Snapshot(y),sample_limit=400)
    dump(OUT/'AGENDAS.json.gz',agendas);dump(OUT/'COMPARACIONES_COMPLETAS.json.gz',comparisons)
    print(json.dumps({'out':str(OUT),'closed':True,'native_worlds_released':True}),flush=True)

if __name__=='__main__':main()
