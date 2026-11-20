"""Read only selected archived records; no DEE import or physical evolution.

The single output is a bounded audiovisual source extract, not an operative
snapshot or another campaign register. Exact source hashes and JSON pointers
are preserved. No spatial interpolation or content decoding is performed.
"""
from pathlib import Path
import gzip, hashlib, json

R08=Path(__file__).resolve().parents[1]
THINK=R08.parents[1]
R05=THINK/'archivo/produccion_audiovisual_DEE_Cognitive_2_0_20261028/videos/R05'
OLD=THINK/'archivo/DEE Cognitive System 1.1/evidencia/campanas'
SOURCES={}

def load(path, pointer=''):
    path=Path(path).resolve(); b=path.read_bytes()
    h=hashlib.sha256(b).hexdigest()
    SOURCES[str(path)]={'sha256':h,'bytes':len(b),'read_scope':pointer or 'selected keys below'}
    obj=json.loads(gzip.decompress(b) if path.suffix=='.gz' else b)
    return obj,{'path':str(path),'sha256':h,'pointer':pointer}

def wrapped(path):
    obj,src=load(path,'/result/result')
    return obj,obj['result']['result'],src

def main():
    actual,sa=load(R05/'datos/evidencia_actual_R05.json')
    foundations,sf=load(R05/'datos/evidencia_fundamentos_R05.json')
    cases={}
    neutral=actual['S09_neutral']; nr=neutral['recorded_result']['rows'][0]
    cases['FI128_7_7']={'N':67,'life':neutral['life'],'source':{**sa,'pointer':'/S09_neutral'},
        'original_primary':{'path':neutral['source'],'sha256':neutral['sha256']},
        'data':nr,'representation':'Visualización de registros',
        'limits':['Early reader is prepared P0; zero is a qualified emission, NULL is missing output.',
                  'No autonomous choice of reader or learned recovery is inferred.']}
    probes={}
    for mode in ('on','off'):
        entry=actual['S09_probe_'+mode]
        dg=entry['recorded_result']['diagnostic']
        probes[mode]={'N':67,'life':entry['life'],'source':{**sa,'pointer':'/S09_probe_'+mode},
            'original_primary':{'path':entry['source'],'sha256':entry['sha256']},'data':dg}
    # Exact comparison of recorded ROI values at the same tick. No kernel is run.
    diffs=[]
    for a,b in zip(probes['on']['data']['frames'],probes['off']['data']['frames']):
        assert a['offset']==b['offset']
        aa={tuple(p['site']):p for p in a['ROI_nonzero_RAW']}
        bb={tuple(p['site']):p for p in b['ROI_nonzero_RAW']}
        changed=[]
        for site in sorted(aa.keys()|bb.keys()):
            pa=aa.get(site);pb=bb.get(site)
            if (pa or {}).get('raw','0')!=(pb or {}).get('raw','0'):
                changed.append({'site':list(site),'on':pa,'off':pb})
        diffs.append({'tick':probes['on']['data']['query_tick']+a['offset'],'q_offset':a['offset'],'differences':changed})
    cases['R04_QUERY']={'arms':probes,'recorded_ROI_differences':diffs,
        'representation':'Visualización de registros',
        'limits':['Common q+4 E vector is present in both arms; it is not exclusively query-created.',
                  'Three original q+6 actuator readings are NULL in both arms.',
                  'ROI sampling is not full causal lineage or a complete operative snapshot.']}
    cpc=THINK/'casos practicos/trabajo_codex/CPC9/runs'
    cp,sc=load(cpc/'RUN_20261019_165651/resultados/auditoria/COMPOSICION_E1/MEDICIONES.json')
    ess,se=load(cpc/'AUDITORIA_ESENCIAL_20261019_205807/paquete_01/CONTROLES_CAUSALES/COMPOSICION_Y_CORTE.json')
    cases['CPC9_COMPOSITION']={'N':67,'life':'EI_D01 / diagnostic copies',
        'source':sc,'selected_essential_source':se,'data':ess,'pre_Moore27':cp['pre_Moore27'],
        'parent_snapshot':cp['parent'],'parent_snapshot_sha256':cp['parent_sha256'],
        'comparison_selected_before_render':'cut_arrival_0',
        'representation':'Reconstrucción de etapas',
        'limits':['Only T205,T206,T210 stages are used; no invented intermediate trajectory.',
                  'Controls are external diagnostic interventions on copies; no autonomous cutting.']}
    social={}
    ib=OLD/'INTEGRACION_COGNITIVA_SITUADA_E1_01'
    for key,n in [('full','LATE_SOCIAL_OPPOSITE_166.json'),('cut','LATE_SOCIAL_CUT_OPPOSITE_166.json'),('sham','LATE_SOCIAL_SHAM_OPPOSITE_166.json'),('no_B','LATE_SOCIAL_NO_NEW_B_166.json')]:
        d,sp=load(ib/n,'/result');r=d['result']
        social[key]={'source':sp,'identity':r['external']['identity'],
            'plan':r['new_plan'],'progress':r['new_social_progress'],
            'first_external_rows':r['external']['rows'][:2],
            'all_external_summaries':[{'tick':q['tick'],'q_sin':q['q_sin'],'native_command':q['native_command'],
                 'executed_torque':q['executed_torque'],'social_reads':q.get('social_reads',[])}for q in r['external']['rows']]}
    cases['IC01_SOCIAL']={'N':67,'arms':social,'passive_sampled_frames':foundations['scenes']['S07_IC01']['passive_local_frames'],
        'passive_source':{**sf,'pointer':'/scenes/S07_IC01/passive_local_frames'},
        'representation':'Reconstrucción de etapas',
        'limits':['Private B input45 is not the received scalar7 or the later fixed motor command.',
                  'Cut is legal material SEM4 input at source-timed association sites; sham elsewhere.',
                  'Sparse retained observations do not establish a unique lineage across the delay.']}
    cyc={}
    for key,n in [('full','C02_GATE_050_RETORNO.json'),('omit','C02_GATE_051_SIN_RETORNO.json')]:
        d,s=load(OLD/'CONSOLIDACION_EVOLUCION_E1_CICLO_02'/n,'/data/result')
        cyc[key]={'source':s,'life':d['life'],'N':d['data']['physical']['N'],'data':d['data']['result']}
    cases['CYCLE02_RETURN']={'arms':cyc,'representation':'Reconstrucción de etapas',
        'limits':['Native reference and response are recorded; environment wear is a prepared consequence, not native metabolism.',
                  'Returns omitted in control; subsequent interactive futures can diverge.']}
    cases['CP02_EARLY']={'source':{**sf,'pointer':'/scenes/S10_CP02'},'data':foundations['scenes']['S10_CP02'],
        'N':47,'N_provenance':{'dimension':47,'source':'historico/CPC3/genealogia/CP02_B/EXPERIMENT_CONFIG.json',
            'blob_sha256':'312a78c5fb89c2f4ae9fe1252ac1c776caf8fdd4106cf048c3c8932d973c2d49',
            'store':str(cpc/'RUN_20261019_165651/core/DEE_COGNITIVE_CORE/mecanismos/RECUPERACION_POR_HASH.jsonl.gz'),
            'predictor_blob_sha256':'057ca2b25e4ca1045533a8ce6fabfb7e6f24b81f1feff8af4f51aa2246f0576b',
            'scope':'Frozen historical dimension47 and modulo47; M002 reproduces this preparation under4.5 with the recorded reserved origin22,20,24.'},
        'representation':'Reconstrucción de etapas',
        'limits':['Emission T37 and external outcome T70 are different records; T is not seconds.',
                  'An early signal is not a universal prediction guarantee.']}
    ep,er,es=wrapped(OLD/'ENTE_DEE_OPERATIVO_01/32_PROTO_MAIN_2.json.gz')
    cases['ENTE01_RETURN']={'source':es,'N':ep['result']['physical']['N'],'life':ep['result']['INSTRUMENTO']['life_id'],
        'data':er['rows'][0],'representation':'Reconstrucción de etapas',
        'limits':['External fixed environment is outside the kernel, not an industrial robot.',
                  'Codec transduces actual post-execution contact/posture, not a desired next decision.']}
    ente2={}
    eb=OLD/'ENTE_DEE_EVOLUCION_02'
    selected=['04_FUENTE_T.json.gz','05_FUENTE_U.json.gz','06_FUENTE_H.json.gz',
        '10_DESTINO_B_T.json.gz','11_DESTINO_B_U.json.gz','12_DESTINO_B_H.json.gz',
        '30T_CONTRARIA.json.gz','30U_CONTRARIA.json.gz']
    for n in selected:
        p,r,s=wrapped(eb/n);rows=r['rows']
        ente2[n]={'source':s,'life':p['result']['INSTRUMENTO']['life_id'],'N':p['result']['physical']['N'],
            'code_revision_sha256':p['code_revision_sha256'],'first':rows[0],
            'final_own':rows[-1]['after']['own'],'rows_count':len(rows),'job_completed_count':sum(bool(q['job_completed'])for q in rows),
            'all_outcomes':[{'reader':q['reader'],'row':q['row'],'observed_result':q['observed_result'],
                'consequence':q['consequence'],'job_completed':q['job_completed']}for q in rows]}
    assert[ente2[n]['job_completed_count']for n in selected[3:6]]==[6,4,3]
    assert[ente2[n]['job_completed_count']for n in selected[6:]]==[1,3]
    cases['ENTE02_TRANSFER']={'records':ente2,'representation':'Reconstrucción de etapas',
        'denominators':{'destination_workers':{'T':[6,6],'U':[4,6],'H':[3,6]},'inverse_rule':{'T':[1,3],'U':[3,3]}},
        'limits':['T/U/H source histories are real/omitted/decoupled consequence, respectively.',
                  'Do not substitute the separate four-row transaction experiment28T/U/H.',
                  'Transfer is between prepared isomorphic comparison contexts, not arbitrary tasks.']}
    agg,sg=load(R05/'datos/agregacion_FI01_R05.json','/aggregate128/pair')
    pair=agg['aggregate128']['pair']
    assert[(i,a,b)for i,(a,b)in enumerate(zip(pair['ref_sham_zero']['raw_components'],pair['ref_sham_two']['raw_components']))if a!=b]==[(0,0,2)]
    cases['FI01_128']={'source':sg,'original_source':agg['source'],'original_source_sha256':agg['source_sha256'],
        'pairs':pair,'counts':agg['aggregate128']['counts'],'representation':'Reconstrucción de etapas',
        'limits':['128 components are scheduled raw inputs, not128 meanings.',
                  'Only recorded field samples appear; no simultaneous128-particle claim or interpolated genealogy.']}
    entry=actual['S12_W11']; fac=entry['recorded_result']['native_factorial']
    cases['ECI02_COEXISTENCE']={'source':{**sa,'pointer':'/S12_W11'},'original_primary':{'path':entry['source'],'sha256':entry['sha256']},'data':fac,'N':67,
        'representation':'Visualización de registros','limits':['Both operations have prepared timing and readers; not spontaneous scheduling.']}
    ECI01=THINK/'archivo/analisis_transversal_cognitivo/ECI01'
    pp=ECI01/'estados/P_COPIA_CERRADA/sistema/estado/eci01_resultados/ECI01_D_FACTOR_7/DF_7.json.gz'
    dd,ss=load(pp);print('ECI01 shape',list(dd))
    # Preserve the bounded primary whole: it is small and its original schema is
    # intentionally not rewritten by this audiovisual extractor.
    cases['ECI01_INTERFERENCE']={'source':ss,'primary':dd,'N':67,'representation':'Visualización de registros',
        'limits':['Different parent and shared-interface test; do not attribute its rejection to ECI02J11.']}
    out={'schema':'DEE.R08.directed_visual_sources.R01','new_native_ticks':0,
        'scope':'Selected existing records for S06-S11; documentary extraction only; not an operative backup.',
        'sources':SOURCES,'cases':cases,
        'delegated':{'S06_P01':'escenas_centrales_r08.retention_panels','S11_P03_P04':'escenas_principal_r08.model'},
        'infrastructure':{'latest_actual_found':'R05','R06_R07':'Not located in directed audiovisual roots/known attachments; not a claim of global absence.',
           'renderer':'R05/renderer_r05.py and render_common.cjs','voice':'Kokoro ONNX em_alex in produccion_cientifica/voz/pydeps',
           'voice_timing_limit':'Model durations, not independentASR; oldR05 clause captions proportionally apportioned and not sufficient as R08independent alignment.',
           'ASR_bundled_find_spec':{'whisper':False,'faster_whisper':False,'whisperx':False,'vosk':False},
           'ffmpeg':'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe','ffprobe':'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'}}
    target=R08/'infraestructura/FUENTES_MECANISMOS_S06_S11_R08.json'
    target.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')),encoding='utf8')
    print(json.dumps({'output':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'cases':list(cases)},ensure_ascii=False))

if __name__=='__main__':main()
