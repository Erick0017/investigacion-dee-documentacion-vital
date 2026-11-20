"""Recalculate recorded primary data. No engine import, no experiment execution.

Semantic levels remain claims authored in the original campaign. This program
does not award meanings, intelligence or generality from a technical PASS.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,csv,hashlib,json,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from codec import Reader,canonical,sha
from campos_guardados import array_bytes,stats
sys.stdout.reconfigure(encoding='utf8')
STAGES=[('resultados/vida_integral/EI_D01',0,884),('resultados/continuacion/E1_MAIN_884_1220',884,1220),
 ('front_relations/resultados/E1_MAIN_1220_1371',1220,1371),('front_relations/resultados/E1_MAIN_1371_1639',1371,1639),
 ('front_relations/resultados/E1_MAIN_1639_1907',1639,1907),('resultados/continuacion/E1_MAIN_K65_1907_2353',1907,2353),
 ('resultados/continuacion/E1_MAIN_TAIL_2353_2493',2353,2493)]
def compact(q):return{k:q[k]for k in('raw','clock','state','s_reg','semantic','direction','active','site')if k in q}if isinstance(q,dict)else None
def qualified(q,d,load=None):return bool(q and q.get('active')and q.get('semantic')==1 and q.get('direction')==d and(load is None or q.get('s_reg')==load))
def fmap(d):return{f['tick']:(i,f)for i,f in enumerate(d.get('frames',[]))}
def field(frame,path):
    q=frame.get('view',frame)
    try:
        for k in path.split('/'):q=q[int(k)]if isinstance(q,list)else q[k]
        return q
    except(KeyError,IndexError,TypeError):return None
def readings(x,path=''):
    if isinstance(x,dict):
        if 'raw'in x and 'clock'in x:yield path,x
        for k,v in x.items():yield from readings(v,path+'/'+str(k))
    elif isinstance(x,list):
        for i,v in enumerate(x):yield from readings(v,path+'/'+str(i))
def fingerprints(x):
    out=set()
    def walk(v):
        if isinstance(v,dict):
            if all(k in v for k in('tick','RAW_sha256','clocks_sha256')):out.add((v['tick'],v['RAW_sha256'],v['clocks_sha256']))
            for q in v.values():walk(q)
        elif isinstance(v,list):
            for q in v:walk(q)
    walk(x);return out

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();started=time.monotonic()
    if a.out.exists():raise FileExistsError('Use a new output directory; source files never overwritten')
    a.out.mkdir(parents=True);reader=Reader(a.root/'EVIDENCIA_PRIMARIA_ESENCIAL');lookup={};bysha=defaultdict(list)
    for r in reader.index['documents']:
        for o in r['origins']:
            lookup[(o.get('archive'),o.get('logical_path',o.get('member')))]=r['id'];bysha[o['sha256']].append(r['id'])
    C9='CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip';CORE='DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip'
    def doc(rel):return reader.get(lookup[(C9,'CPC9/'+rel)])
    def ref(rel,pointer=''):
        k=lookup[(C9,'CPC9/'+rel)];r=reader.lookup[k];o=next(o for o in r['origins']if o.get('archive')==C9 and o.get('member')=='CPC9/'+rel)
        return{'document':k,'original_member':o['member'],'original_sha256':o['sha256'],'pointer':pointer}
    def frame(d,t):return fmap(d)[t][1]
    result={'schema':'CPC9.essential.independent.primary.recalculation.v1','engine_imported':False,'campaign_repeated':False,
      'formulas':{'uint64':'0<=integer<2**64; no float accepted','state':'RAW & (2**32-1)','s_reg':'(RAW>>32)&65535','semantic':'(RAW>>60)&15','direction':'signed4-bit components at48,52,56',
      'qualified':'active AND semantic==1 AND direction==frozen_expected; load equality only when predeclared','rate':'sum(qualified)/number_of_requested_observations; all rejections/misses retained',
      'physical_equal':'tick and complete RAW/clocks SHA equality; not documentary metadata equality','occupation':'count((RAW & 0xffffffff)>0)','main_new_receipts':'set(current_ids)-set(previous_ids)'}}
    # Recount exact fields, including adverse and incomplete primary containers.
    exact=0;bad=[];mismatch=[];statuses=Counter();nprim=0
    for r in reader.index['documents']:
        if r['role']!='CPC9_PRIMARY':continue
        d=reader.get(r['id']);nprim+=1;statuses[str(d.get('status'))]+=1
        def scan(x,path):
            nonlocal exact
            if isinstance(x,dict):
                for k,v in x.items():
                    if k.lower()in('raw','clock'):
                        if(type(v)is int and 0<=v<2**64)or(isinstance(v,str)and v.isdecimal()and 0<=int(v)<2**64):exact+=1
                        else:bad.append({'id':r['id'],'pointer':path+'/'+k,'type':type(v).__name__})
                    else:scan(v,path+'/'+k)
                if all(k in x for k in('raw','state','s_reg','semantic','direction')):
                    v=int(x['raw']);dv=[((v>>s)&15)-16 if((v>>s)&15)>=8 else((v>>s)&15)for s in(48,52,56)]
                    if(v&0xffffffff)!=x['state']or(v>>32)&65535!=x['s_reg']or(v>>60)&15!=x['semantic']or dv!=x['direction']:mismatch.append({'id':r['id'],'pointer':path})
            elif isinstance(x,list):
                for i,v in enumerate(x):scan(v,path+'/'+str(i))
        scan(d,'')
    result['primary_coverage']={'containers':nprim,'statuses':dict(statuses),'uint64_exact_fields':exact,'invalid':bad,'unpacked_mismatch':mismatch}
    if bad or mismatch:raise ValueError('Invalid exact primary fields')
    print('Exact primary fields',exact,flush=True)
    # Reconstruct chain from measured frontiers, not the old continuity verdict.
    stages=[];trajectory=[];oldids=set();last=None;mainids=[]
    fields_dir=a.root/'EVIDENCIA_PRIMARIA_ESENCIAL/CAMPOS_COMPACTOS'
    if not fields_dir.exists():fields_dir=a.root/'EVIDENCIA_PRIMARIA_ESENCIAL/CAMPOS_COMPLETOS'
    saved=[];snapsha={}
    for f in sorted(fields_dir.glob('S*.json')):
        d=json.loads(f.read_bytes());raw=array_bytes(d,'RAW',f.parent);clocks=array_bytes(d,'CLOCKS',f.parent);actual=stats(raw)
        if sha(raw)!=d['physical']['RAW_sha256']or sha(clocks)!=d['physical']['clocks_sha256']or actual!=d['independently_recounted']:raise ValueError('Physical extraction changed')
        snapsha[d['source_snapshot']['member']]=d['source_snapshot']['sha256'];saved.append({'file':f.relative_to(a.root).as_posix(),'physical':d['physical'],'statistics_recounted':actual,'source':d['source_snapshot']})
    for phase,(folder,t0,t1)in enumerate(STAGES):
        rel=folder+'/MEDICIONES.json';d=doc(rel);initial=d.get('initial_physical',d.get('parent',{}).get('physical',d['frames'][0]['physical']))
        current={int(q['receipt']['id']):q['receipt']for q in d['requests']};new=set(current)-oldids
        parent=d.get('parent_snapshot_sha256',d.get('parent',{}).get('sha256'))
        prevsnapshot='CPC9/'+STAGES[phase-1][0]+'/T'+str(t0)+'.deetsnap.gz'if phase else None
        row={'phase':phase,'case_id':d['case_id'],'start':t0,'end':t1,'initial':initial,'final':d['final_physical'],'new_receipts':len(new),'new_statuses':dict(Counter(current[k]['status']for k in new)),
          'prior_ids_retained':oldids<=set(current),'previous_final_equal':initial==last if phase else None,'parent_declared':parent,'parent_saved_sha':snapsha.get(prevsnapshot),'parent_hash_matches_saved_original':parent==snapsha.get(prevsnapshot)if phase else None,'source':ref(rel)}
        if phase and not(row['previous_final_equal']and row['parent_hash_matches_saved_original']):raise ValueError('Physical continuity mismatch')
        if not row['prior_ids_retained']or d.get('MAIN_RAW_clock_edits'):raise ValueError('History changed or declared field edit')
        stages.append(row);oldids=set(current);last=d['final_physical'];mainids.append(ref(rel)['document'])
        for i,f in enumerate(d['frames']):
            view=f['view'];fm=f['physical'];nreads=sum(1 for _ in readings(view));tm=field(f,'two_memory/center');qty=field(f,'quantity/center');gate=field(f,'cpc9_query_loop/gate')
            trajectory.append({'phase':phase,'case_id':d['case_id'],'tick':f['tick'],'RAW_sha256':fm['RAW_sha256'],'clocks_sha256':fm['clocks_sha256'],'observed_records':nreads,
              'TM_raw':tm.get('raw')if tm else None,'TM_direction':tm.get('direction')if tm else None,'quantity_raw':qty.get('raw')if qty else None,'quantity_direction':qty.get('direction')if qty else None,
              'query_gate_raw':gate.get('raw')if gate else None,'query_gate_direction':gate.get('direction')if gate else None,
              'repertoire_attempts_in_frame':len(f.get('repertoire_queries',[])),'evidence_id':ref(rel)['document'],'json_pointer':'/frames/'+str(i),'original_sha256':ref(rel)['original_sha256']})
    result['continuity']={'stages':stages,'unique_receipts':len(oldids),'tick_span':sum(r['end']-r['start']for r in stages),'recorded_frames':len(trajectory),'scope':'Seven serialized phases, not seven independent lives. External empty interfaces are declared, not native growth.'}
    result['saved_physical_field_recounts']=saved
    # Opaque65 attempts: independently retain every query, including failures.
    cap=[];attempts=[]
    for folder in('E1_MAIN_K65_1907_2353','E1_CF_K65_NO_EVENT','E1_CF_K65_UNPAIRED'):
        rel='resultados/continuacion/'+folder+'/MEDICIONES.json';d=doc(rel);counts=defaultdict(lambda:[0,0]);first=[0,0];later=[0,0]
        for fi,f in enumerate(d['frames']):
            for qi,q in enumerate(f.get('repertoire_queries',[])):
                ok=qualified(q['physical'],q['expected_auditor_direction']);counts[f['tick']][0]+=int(ok);counts[f['tick']][1]+=1;target=first if q['query_index']==0 else later;target[0]+=int(ok);target[1]+=1
                attempts.append({'case':folder,'tick':f['tick'],'form':q['form'],'query_index':q['query_index'],'expected_auditor_direction':q['expected_auditor_direction'],'qualified':ok,'physical':q['physical'],'source':ref(rel,f'/frames/{fi}/repertoire_queries/{qi}')})
        # These are staggered bank sweeps, NOT65 simultaneous readings at a tick.
        # Each window uses the original four read times after all blocks exist.
        windows=[]
        for ticks in((2180,2193,2206,2219),(2247,2260,2273,2286),(2314,2327,2340,2353)):
            parts=[{'tick':t,'qualified':counts[t][0],'attempts':counts[t][1]}for t in ticks]
            members=[q for q in attempts if q['case']==folder and q['tick']in ticks]
            if len(members)!=65 or len({q['form']for q in members})!=65:raise ValueError('Staggered sweep repeats or omits forms')
            windows.append({'from_tick':ticks[0],'to_tick':ticks[-1],'qualified':sum(v['qualified']for v in parts),'attempts':sum(v['attempts']for v in parts),'distinct_forms':len({q['form']for q in members}),'parts':parts,'simultaneous':False})
        cap.append({'case':folder,'first_queries':first,'later_queries':later,'rounds':[{'tick':t,'qualified':v[0],'attempts':v[1]}for t,v in sorted(counts.items())],
          'complete_staggered_sweeps':windows,'source':ref(rel)})
    result['opaque65']=cap
    # New comparison objects and content-sensitive old operands.
    quantity=[]
    for folder in('E1_MAIN_884_1220','E1_CF_OFFPATH_884_1220'):
        rel='resultados/continuacion/'+folder+'/MEDICIONES.json';d=doc(rel);fs=fmap(d);pred=d['prediction_before_any_new_tick'];obs=[]
        for t,v in zip(pred['comparison_ticks'],pred['predicted_direction_X']):
            i,f=fs[t];q=field(f,'quantity/center');obs.append({'tick':t,'observed':compact(q),'predicted_auditor_direction':[v,0,0],'match':qualified(q,[v,0,0]),'reference_hub':compact(field(f,'quantity/reference_hub')),'source':ref(rel,f'/frames/{i}/view/quantity')})
        quantity.append({'case':folder,'predeclared_auditor_forecast':pred,'observations':obs,'matches':sum(x['match']for x in obs),'denominator':len(obs),'scope':'Prepared comparison law; acquired/revised physical reference. Forecast belongs to auditor, not native prospective prediction.'})
    result['quantity']=quantity
    memrel='resultados/auditoria/MEMORIAS_TARDIAS_2283_R1/MEDICIONES.json';memory=doc(memrel);result['late_memory']={'source':ref(memrel),'conditions':[]}
    for r in memory.get('rows',[]):
        q=r.get('post',r.get('actual2283',r.get('observation')))
        if q is None:
            for _,f in fmap(r).values():
                if f['tick']==2283:q=field(f,'two_memory/center')
        result['late_memory']['conditions'].append({'condition':r.get('condition'),'actual':q,'recorded_controls':{k:v for k,v in r.items()if k not in('frames','pre_Moore27','post_Moore27','local_neighborhoods')}})
    # Composition: use actual raw and subsequent local output, not a scalar sum verdict.
    comprel='resultados/auditoria/COMPOSICION_E1/MEDICIONES.json';d=doc(comprel);base=doc(STAGES[0][0]+'/MEDICIONES.json');q=field(frame(base,210),'joint/plus.changed/use_site')
    comp={'source':ref(comprel),'incoming':d['incoming'],'formed':d['actual_formed206'],'incoming_load_sum':sum(r['s_reg']for r in d['incoming']),'baseline_consequence210':q,'conditions':[]}
    for r in d['rows']:
        f=frame(r,210);actual=field(f,'joint/plus.changed/use_site');comp['conditions'].append({'condition':r['condition'],'pre_tick':r['pre_tick'],'new_raw':r['new_raw'],'victim':r['victim'],'clock_preserved':r['clock_preserved'],
          'consequence210':actual,'baseline_qualified_consequence_present':qualified(actual,[1,0,1],63),'parents_unchanged':r['parents_unchanged'],'full_original884_equal':r['full_original884_equal']})
    result['composition']=comp
    # Return, query-gate and regulation retain both polarities and residual outputs.
    returns=[]
    for r in reader.index['documents']:
        if r['role']!='CPC9_PRIMARY':continue
        origins=[o for o in r['origins']if o.get('archive')==C9];name=origins[0].get('member','')if origins else''
        if '/resultados/retorno/'not in name:continue
        d=reader.get(r['id']);cases=d.get('rows',[d])
        for c in cases:
            for t,fd in((216,'hub'),(221,'use_site'),(225,'delivery_site')):
                fs=fmap(c)
                if t in fs:
                    vals=field(fs[t][1],'return')or[]
                    returns.append({'case':d.get('case_id',name.split('/')[-2]),'condition':c.get('condition','MAIN_OR_AUX_CASE'),'tick':t,'field':fd,'banks':[{'bank':v.get('bank',v.get('id')),'physical':v.get(fd)}for v in vals],'document':r['id']})
    result['return_observations']=returns
    qr='resultados/consulta/QA_INTEGRAL_CAUSAL/MEDICIONES.json';d=doc(qr);query=[]
    for c in d['rows']:
        query.append({'condition':c['condition'],'gate210':field(frame(c,210),'cpc9_query_loop/gate'),'TM206':field(frame(c,206),'two_memory/center'),'full_final_equal':c['full_final_equal'],'receipts_equal':c['full_receipts_equal'],'parent_unchanged':c['parent_unchanged'],'source':ref(qr,'/rows')})
    result['query_causal']=query;reg=[]
    for name in('EI_D01','EI_C05_RCA_OFFPATH'):
        rel='resultados/vida_integral/'+name+'/MEDICIONES.json';d=doc(rel);q=field(frame(d,137),'cpc9_regulator/quantity/center');reg.append({'case':name,'response137':q,'configuration':d['configuration'],'source':ref(rel)})
    result['regulation_R1']=reg
    initial_checks=[];baseline_initial=doc(STAGES[0][0]+'/MEDICIONES.json')['frames'][0]['physical']
    for r in reader.index['documents']:
        if r['role']!='CPC9_PRIMARY':continue
        if not any(o.get('member','').startswith('CPC9/resultados/vida_integral/')for o in r['origins']):continue
        d=reader.get(r['id']);initial=d['frames'][0]['physical'];initial_checks.append({'case':d['case_id'],'initial_physical':initial,'same_initial_RAW_clocks_tick_as_EI_D01':initial==baseline_initial,'configuration':d['configuration'],'document':r['id']})
    result['integral_initial_state_controls']=initial_checks
    # Historical facts versus technical assertions. No original PASS is silently upgraded.
    proofid=next(r['id']for r in reader.index['documents']if any(o.get('member')=='PRUEBA_RECUPERACION_DESDE_CERO.json'and o.get('kind')=='ORIGINAL_EXTERNAL_FILE'for o in r['origins']));proof=reader.get(proofid)
    matrix=reader.get(lookup[(CORE,'DEE_COGNITIVE_CORE/documentacion/MATRIZ_CAPACIDADES.json')]);family=[]
    for k,v in proof['family_results'].items():
        originals=set();fresh=[]
        def seek(x,key=''):
            if isinstance(x,dict):
                for kk,vv in x.items():
                    if isinstance(vv,str)and len(vv)==64 and any(t in kk.lower()for t in('historical','original','primary'))and vv in bysha:originals.update(bysha[vv])
                    seek(vv,kk)
            elif isinstance(x,list):
                for y in x:seek(y,key)
        seek(v)
        for r in reader.index['documents']:
            if any(o.get('kind')=='COMPLETED_CLEAN_RUN_FILE'and o.get('family')==k for o in r['origins']):fresh.append(r['id'])
        family.append({'family':k,'recorded_status':v.get('status'),'proof_document':proofid,'proof_pointer':'/family_results/'+k,'original_primary_ids_identified':sorted(originals),'completed_replay_documents':fresh,'new_native_execution_by_this_audit':False,
          'verification_limit':'Recorded pass and included original/fresh data are separate. Investigator can inspect the data; no generic scientific-capability verdict is inferred from exit0.'})
    result['historical_families']=family;result['historical_rows']={'count':len(matrix['rows']),'classification_recount':dict(Counter(r['current_recovery_status']for r in matrix['rows'])),'pending_ids':[r['id']for r in matrix['rows']if r['current_recovery_status']=='D']}
    ns=doc('revision/NSM65_EVIDENCIAS.json');result['NSM_claims_recount']={'catalogue_entries':len(ns['entries']),'original_E1_levels':dict(Counter(e['E1_level']for e in ns['entries'])),'scope':'Counts original manual claims, not an automatic fresh adjudication of meanings; see ESTADO_REAL_NSM65.csv and scientific report.'}
    result['elapsed_seconds']=time.monotonic()-started
    (a.out/'CALCULOS_RECALCULADOS.json').write_bytes(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False).encode('utf8')+b'\n')
    (a.out/'CONSULTAS_65_COMPLETAS.json').write_bytes(canonical({'schema':'CPC9.audit.all_opaque65.query_records.v1','rows':attempts})+b'\n')
    (a.out/'TRAYECTORIA_DATOS.json').write_bytes(canonical(trajectory)+b'\n')
    print(json.dumps({'status':'PASS','primary_containers':nprim,'exact_fields':exact,'continuity_edges':len(stages)-1,'receipts':len(oldids),'opaque65':cap,'family_count':len(family),'pending_historical':len(result['historical_rows']['pending_ids']),'elapsed_seconds':result['elapsed_seconds']},ensure_ascii=False))
if __name__=='__main__':main()
