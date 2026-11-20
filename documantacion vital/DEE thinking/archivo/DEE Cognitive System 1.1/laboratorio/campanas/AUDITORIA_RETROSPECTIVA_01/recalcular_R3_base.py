"""Retrospective calculations only: no engine import, restored life or new tick.

Input is the exported exact-primary bundle, not historical directories. Results
are arithmetic and equality facts, never an automatic cognitive verdict.
"""
from pathlib import Path
from collections import Counter
import argparse,json,tarfile,gzip,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from leer_estado import Snapshot,organization,compare,frame_arrays,fields,coord,index,sha,walk,load_json,pbytes

def run(base):
    ev=base/'EVIDENCIA_CAUSAL';ix=load_json(ev/'INDICE_PRIMARIOS.json');archive=ev/ix['archive']
    assert sha(archive.read_bytes())==ix['archive_sha256']
    with tarfile.open(archive,'r:xz')as t:objects={m.name:t.extractfile(m).read()for m in t.getmembers()if m.isfile()}
    records={};snapshots={};errors=[];count=Counter();coverage=[]
    for e in ix['entries']:
        b=objects[e['member']];assert sha(b)==e['sha256']and len(b)==e['original_bytes'];count['original_objects_verified']+=1
        if e['role']=='snapshot':
            s=Snapshot(e['member'],data=b);snapshots[e['id']]=s;count['complete_snapshots_parsed']+=1
        elif e['role']=='primary':
            d=json.loads(gzip.decompress(b)if e['member'].endswith('.gz')else b);records[e['id']]=d;count['primary_records_read']+=1
            for loc,q in walk(d):
                if all(k in q for k in('raw','site','clock','tick','state'))and isinstance(q['raw'],(int,str)):
                    v=int(q['raw']);assert 0<=v<2**64 and 0<=int(q['clock'])<2**64
                    calculated=fields(v)
                    for k in('state','s_reg','semantic','direction'):
                        if k in q and calculated[k]!=q[k]:errors.append([e['id'],loc,k,q[k],calculated[k]])
                    count['exact_observations_checked']+=1
                if all(k in q for k in('N','rows','clock_exceptions','RAW_sha256','clocks_sha256')):
                    if q['clock_exceptions']is None:count['incomplete_field_frames_not_used_for_equality']+=1
                    else:frame_arrays(q);count['whole_sparse_frames_verified']+=1
            coverage.append({'id':e['id'],'source_sha256':e['sha256'],'case':d.get('case',d.get('case_id')),'role':'existing_experiment_NOT_new_replication'})
    result={'schema':'DCS1.1.RETROSPECTIVE.calculations.v1','new_native_ticks':0,'counts':dict(count),'field_decode_errors':errors,'coverage':coverage}
    assert not errors

    # Complete saved owner files retain a journal; that journal is NOT silently
    # treated as a participant memory or dropped from an equality certificate.
    a=snapshots['S13/wall11'];b=snapshots['S13/wall17'];oa=organization(a);ob=organization(b)
    oa_no_journal={k:v for k,v in oa.items()if k!='operations'};ob_no_journal={k:v for k,v in ob.items()if k!='operations'}
    natural={}
    for case in ['wall11','wall17','no_wall11','no_wall17','sham11','sham17','no_history','wall11_relearn','wall17_relearn']:
        d=records['AA/PERDIDA_Y_REAPRENDIZAJE_13/'+case];row=d['read'];f=fields(int(row['raw']));decoded='opaqueA'if f['state']==1 and f['semantic']==1 and f['direction']==[1,1,0]and f['s_reg']==16 else'opaqueB'if f['state']==1 and f['semantic']==1 and f['direction']==[1,1,0]and f['s_reg']==22 else None
        assert decoded==d['decoded']
        natural[case]={'read':row,'decoded_recalculated':decoded,'native_digest_reported_before_owner_serialization':d['native_after6_excluding_only_documental_life'],'relearned_read':d.get('relearned_read'),'relearned_decoded':d.get('relearned_decoded')}
    result['AA13']={'saved_file_comparison':compare(a,b),'owner_equal_except_operations_journal':oa_no_journal==ob_no_journal,'journal11':oa['operations'],'journal17':ob['operations'],'common_pending':a.pending,'cases':natural,'boundary':'RAW, clocks, channels, pending writes, receipts and execution agree. Owner recipe/protocols/decoders/trace also agree. Files do NOT agree: life IDs and instrument operation journals differ. The common future is the recorded generic query; no target-readout from those journals is permitted.'}

    # Existing one-tick diagnostic contrasts: recompute all cells, not just port.
    base42=records['AA/CAUSAL_DESTINO_42/none'];br,bc=frame_arrays(base42['post_frame']);beforeR,beforeC=frame_arrays(base42['pre_frame']);rows42={}
    for case in ['none','remove_incoming','empty_destination','zero_state_only','sham_empty']:
        d=records['AA/CAUSAL_DESTINO_42/'+case];r,c=frame_arrays(d['post_frame']);pr,pc=frame_arrays(d['pre_frame'])
        delta=[i for i,(v,w)in enumerate(zip(br,r))if v!=w]
        rows42[case]={'pre_RAW_differences':sum(v!=w for v,w in zip(beforeR,pr)),'pre_clock_differences':sum(v!=w for v,w in zip(beforeC,pc)),'post_RAW_differences':len(delta),'post_clock_differences':sum(v!=w for v,w in zip(bc,c)),'post_differences':[{'site':coord(i,67),'baseline':fields(br[i]),'counterfactual':fields(r[i])}for i in delta],'receipts_equal':d['post_receipts']==base42['post_receipts'],'destination':d['destination']}
    result['AA42']={'contrasts':rows42,'pre_snapshot_pending':snapshots['S39/ANTES_DESVIO.native.gz'].pending,'post_native_pending':snapshots['S39/DESPUES_DESVIO.native.gz'].pending,'scope':'Original diagnostic copies, not a repaired life; deleting the incoming contribution yields the same entire physical poststate. No whole-history erasure claim.'}

    # Content contrasts before and after the habitual-reader failure.
    pairs={}
    for group in ['USO_INMEDIATO_RECUPERADO_46','REDUNDANCIA_Y_ACCESO_40']:
        a=records['AA/'+group+'/plus'];b=records['AA/'+group+'/minus'];rows=[]
        for fa,fb in zip(a['frames'],b['frames']):
            ra,ca=frame_arrays(fa['frame']);rb,cb=frame_arrays(fb['frame']);di=[i for i,(x,y)in enumerate(zip(ra,rb))if x!=y]
            rows.append({'tick':fa['frame']['tick'],'frame_label':fa.get('label',fa.get('tag')),'RAW_different_sites':len(di),'clock_different_sites':sum(x!=y for x,y in zip(ca,cb)),'differences':[{'site':coord(i,67),'plus':fields(ra[i]),'minus':fields(rb[i])}for i in di]})
        pairs[group]={'first_old_reader_plus':a['historical_source_read'],'first_old_reader_minus':b['historical_source_read'],'no_later_content_plus':a['later_content_teacher_inputs'],'no_later_content_minus':b['later_content_teacher_inputs'],'frames':rows}
    readyA=snapshots['READY/AA01_ACCESO_LISTO_plus'];readyB=snapshots['READY/AA01_ACCESO_LISTO_minus'];pairs['learned_ready_files']=compare(readyA,readyB);pairs['learned_ready_files']['pending_writes']=readyA.pending
    result['CONTENT_CONTRASTS']=pairs

    # Recalculate opaque-code outputs from raw fields, not expected-content IDs.
    access=[]
    for key,d in records.items():
        if not key.startswith(('AA/USO_INMEDIATO_RECUPERADO_46/','AA/CONTROLES_USO_INMEDIATO_47/','AA/REDUNDANCIA_Y_ACCESO_40/','AA/CONTROLES_REDUNDANCIA_40/')):continue
        stages=[]
        for v in d.get('stages',[]):
            stage=v['stage'];ans=v['answer'];native=ans['ENTE'];codes=set()
            for name,row in native.get('memories',{}).items():
                if stage!='access':continue
                q=fields(int(row['raw']))
                if q['state']==1 and q['semantic']==1 and q['direction']in([1,int(name),-1],[1,int(name),1]):codes.add('Z-'if q['direction'][2]<0 else'Z+')
            for name,row in native.get('B',{}).items():
                q=fields(int(row['raw']));r,z=map(int,name.split(','))
                immediate=ans['INSTRUMENTO'].get('recipient_mode')=='immediate_yz'
                expected=[1,r,z]if stage=='received'and immediate else[0,r,z]if stage=='use'and immediate else[0,0,z]if stage in('transformed','use')else[1,1,z]if stage=='social'else[1,0,z]
                if q['state']==1 and q['semantic']==1 and q['direction']==expected:codes.add('Z-'if z<0 else'Z+')
            calc=sorted(codes)
            if calc!=ans['CONTENT_CODES']:raise AssertionError((key,v['block'],stage,calc,ans['CONTENT_CODES']))
            stages.append({'block':v['block'],'stage':stage,'tick':ans['INSTRUMENTO']['tick'],'codes_from_RAW':calc,'policy':native['policy']})
        access.append({'id':key,'life':d['life'],'stages':stages,'old_reader':d['historical_source_read'],'later_content_inputs':d['later_content_teacher_inputs'],'prepared_redundancy':d['prepared_redundancy'],'final_tick':d['post']['tick'],'old_panels':d.get('panels')})
    result['RECOVERY_AND_CONTROLS']=access

    # P2 is a scientific interpretation of these local causal contrasts, not a
    # label awarded by this program.
    policies=[]
    for key,d in records.items():
        if key.startswith(('AA/ACCESO_LOCAL_SEPARADO_33/','AA/CONTROLES_Y_RESERVAS_33/')):
            policies.append({'id':key,'first':d.get('policy_first'),'second':d.get('policy_second'),'contexts':d.get('external_contexts'),'new_content_inputs':d.get('new_content_inputs'),'B_recall':d.get('B_recall'),'B_use':d.get('B_use'),'panel':d.get('panel'),'last_tick':d.get('post',{}).get('tick')})
    result['POLICY_HISTORY_CONTRASTS']=policies

    pc22=[]
    for key,d in records.items():
        if key.startswith('PC/COALESCENCIA_DIAGNOSTICA_22/'):
            pc22.append({'id':key,'pre_differences':d['pre_differences'],'post_differences':d['post_differences'],'native_equality_reported_in_original_diagnostic':d['post_all_native_except_only_diagnostic_labels_equal'],'post_receipts_equal':d['post_receipts_equal'],'post_destination':d['post_free_destination'],'scope':'Rechecked stored original records, not a new tick or new post-snapshot reconstruction'})
    result['PC22']=pc22
    reader=[]
    for key,d in records.items():
        if key.startswith(('PC/LECTOR_POST_TRANSFORMACION_41/','PC/RESERVA_LECTOR_TRANSFORMADO_42/','PC/CONTEXTO_UTIL_MIXTO_44/')):
            reader.append({'id':key,'transformed':d.get('transformed'),'reader':d.get('reader'),'words':d.get('SPANISH_DECODED'),'action':d.get('action'),'action_observed':d.get('NATIVE_ACTION_OBSERVED'),'result_recorded':d.get('commit',{}).get('result'),'scope':'Prepared reader and single functional polarity; not automatic general reconstruction'})
    result['PC_TRANSFORMED_ACCESS']=reader

    # CPC9: physical-form decoder is frozen, does not award NSM meanings.
    k65={}
    for name in ['E1_MAIN_K65_1907_2353','E1_CF_K65_NO_EVENT','E1_CF_K65_UNPAIRED']:
        d=records['CPC9/'+name];rows=[]
        for f in d['frames']:
            for q in f.get('repertoire_queries',[]):
                r=fields(int(q['physical']['raw']));valid=r['state']>0 and r['semantic']==1 and r['direction']==q['expected_auditor_direction'];rows.append({'tick':f['tick'],'form':q['form'],'correct':valid,'query_index':q['query_index']})
        windows=[]
        for lo,hi in [(2180,2219),(2247,2286),(2314,2353)]:
            r=[q for q in rows if lo<=q['tick']<=hi];assert len(r)==65 and len({q['form']for q in r})==65
            windows.append({'from':lo,'to':hi,'correct':sum(q['correct']for q in r),'attempted':len(r)})
        s=snapshots['K65/'+name+'/T2353']
        k65[name]={'windows':windows,'first_block_reads':{'correct':sum(q['correct']for q in rows if q['query_index']==0),'attempted':sum(q['query_index']==0 for q in rows)},'queries_total':len(rows),'physical_T2353':s.summary(),'max_s_reg':max((x>>32)&65535 for x in s.raw)}
    tails={}
    for name in ['E1_MAIN_TAIL_2353_2493','E1_TAIL_NO_NEW']:
        d=records['CPC9/'+name];unique={q['receipt']['id']:q['receipt']for q in d['requests']if q['receipt']['requested_tick']>=2353}
        tails[name]={'new_distinct_requests':len(unique),'statuses':dict(Counter(q['status']for q in unique.values())),'final_physical':d['final_physical']}
    growth=records['CPC9/CRECIMIENTO_OCUPACION'];result['CPC9']={'K65':k65,'tails':tails,'same_tail_physical':tails['E1_MAIN_TAIL_2353_2493']['final_physical']==tails['E1_TAIL_NO_NEW']['final_physical'],'growth_existing_profile':growth['profile'],'local_birth':growth['first_birth'],'existing_cut_and_sham':growth['rows']}

    x5=load_json(ev/'EXPLORACION_X5.json');full=load_json(ev/'CAMPOS_X5.json')
    for f in full:frame_arrays(f)
    ei=records['CPC9/EI_D01'];aligned=[q for q in ei['requests']if q.get('port')=='remote_contact.renew.left.free']
    at477=next(q for q in ei['frames']if q['tick']==477)
    observed477=[{'path':loc,'observation':q}for loc,q in walk(at477['view'])if q.get('site')==[31,11,11]]
    result['X5']={'observed_ancestor_checkpoint_count':len(x5['snapshots']),'matching_observations':sum(q['match_X5']for q in x5['snapshots']),'unique_ticks':sorted({q['tick']for q in x5['snapshots']}),'source_candidate_input':aligned,'first_direct_477_records':observed477,'phase_aligned_inputs_in_surviving_owner_journal':x5.get('candidate_phase_aligned_inputs'),'full_field_extractions_verified':len(full),'caveat':'Historical input and discontinuous phase-consistent checkpoints do not prove uninterrupted unique ancestry to T45028. No full toroidal lineage or useful earlier function is inferred solely from matching load/position.'}
    result['existing_lives']=load_json(ev/'ESTADOS_PROTEGIDOS.json')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--paquete',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();r=run(a.paquete);a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'counts':r['counts'],'errors':len(r['field_decode_errors']),'new_native_ticks':0,'result':str(a.salida)},ensure_ascii=False))
