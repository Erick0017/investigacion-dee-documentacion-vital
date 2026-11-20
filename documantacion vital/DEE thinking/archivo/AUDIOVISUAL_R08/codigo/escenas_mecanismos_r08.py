"""S06-S11: projections of selected existing records, never DEE execution.

Discrete stages are source observations. Progress selects an editorial hold
or cut; it never moves a material cell or fills a missing physical record.
"""
from pathlib import Path
from functools import lru_cache
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'infraestructura/FUENTES_MECANISMOS_S06_S11_R08.json'
A='Visualización de registros'
B='Reconstrucción de etapas'
C='Esquema explicativo'

@lru_cache(maxsize=1)
def data():
    return json.loads(DATA.read_text(encoding='utf8'))

@lru_cache(maxsize=1)
def source_hash():return hashlib.sha256(DATA.read_bytes()).hexdigest()

def point(p,role='site'):
    q=dict(p)
    if 'coordinate'in q:q['site']=q.pop('coordinate')
    if 'RAW'in q:q['raw']=str(q.pop('RAW'))
    q['raw']=str(q['raw']);q['clock']=str(q['clock']);q['role']=role
    return q

def collect(obj):
    """Only observed records with exact sites and RAW; no request→RAW codec."""
    if isinstance(obj,dict):
        if ('site'in obj or'coordinate'in obj)and('raw'in obj or'RAW'in obj):
            return [point(obj)]
        return [p for v in obj.values()for p in collect(v)]
    if isinstance(obj,list):return [p for v in obj for p in collect(v)]
    return []

def unique(points):
    rows={}
    for p in points:
        key=tuple(p['site'])
        if key in rows and(rows[key]['raw'],rows[key]['clock'])!=(p['raw'],p['clock']):
            raise ValueError('Conflicting observations must not share a displayed stage')
        rows[key]=p
    return list(rows.values())

def frame_at(frames,tick):
    return next(f for f in frames if f.get('tick',-1)==tick)

def select(values,progress):return values[min(len(values)-1,max(0,int(progress*len(values))))]

def signed(value):
    if value is None:return None
    # ASCII minus is present in the selected local font; U+2212 is not.
    return '+'if value>0 else'-'if value<0 else'0'

def panel(points,label,N,tick,source,reader_sites=(),output=None,evidence=None):
    p={'N':N,'tick':tick,'points':unique(points),'label':label,'source':source}
    if reader_sites:p['reader_sites']=[list(q)for q in reader_sites]
    if output is not None:
        if not evidence:raise ValueError('A displayed output needs its qualified source reader')
        p['output_text']=str(output);p['reader_evidence']=evidence
    return p

def model_base(title,panels,evidence_type,case,pointer,stage_jump=False,**kw):
    return {'title':title,'panels':panels,'evidence_type':evidence_type,
        'source_data_hash':source_hash(),'source':{'path':str(DATA),'sha256':source_hash(),'pointer':'/cases/'+case+pointer},
        'stage_jump':stage_jump,'no_new_DEE_execution':True,**kw}

def pfield(p,source_pointer,offset=(110,0)):
    return {'site':list(p['site']),'text':str(p['s_reg']),'source_field':source_pointer,'offset':list(offset)}

def s06(shot,progress):
    if shot=='S06_P01':
        from escenas_centrales_r08 import retention_panels
        name='nara'if progress<.5 else'MA'
        p=json.loads(json.dumps(retention_panels()[name]))
        p['label']='OTRA ASOCIACIÓN UTILIZADA'if name=='nara'else'MEMORIA RECUPERADA'
        if name=='nara'and progress>=.12:
            p['bounds']=[[46.6,2.6,45.5],[47.4,3.4,48.5]]
        out=model_base('CONTINUACIÓN REVISADA', [p],A,'FI128_7_7','',stage_jump=progress>=.5,bounds=p['bounds'])
        out['source']=p['source'];out['case_id']='ECI02_L_MINUS; separate from current principal'
        return out
    if shot=='S06_P02':
        x=data()['cases']['FI128_7_7'];r=x['data'];trial=r['original_result']['native_trial'];q=r['query_tick']
        if progress<.48:
            f=frame_at(trial['frames'],r['early_tick']);pts=collect(f['fields'])
            pp=panel(pts,'LECTURA TEMPRANA: 0',67,r['early_tick'],x['source'],[[15,15,15]],signed(r['early_physical_choice']),
                {'pointer':'/S09_neutral/recorded_result/rows/0/early_observation','observation':r['early_observation'],'qualified_choice':r['early_physical_choice']})
        else:
            reader=trial.get('reader')or trial.get('actuator_reader')
            # Original FI reader is recorded under the original native trial.
            if reader is None:
                reader=r['original_result'].get('reader')
            if reader is None:
                reader={'tick':q+6,'choice':r['old_q6_choice'],'observations':[]}
            f=frame_at(trial['frames'],q+6);pts=collect(f['fields'])+collect(reader.get('observations',[]))
            pp=panel(pts,'LECTURA POSTERIOR: SIN RESULTADO',67,q+6,x['source'],
                [p['site']for p in reader.get('observations',[])])
            pp['reader_evidence']={'original_result':reader,'old_q6_choice':r['old_q6_choice'],'NULL_is_not_zero':True}
        return model_base('OTRO EXPERIMENTO',[pp],A,'FI128_7_7','/data',stage_jump=progress>=.48,
            bounds=[[13.4,13.4,14.2],[16.6,17.6,16.8]])
    if shot in('S06_P03','S06_P04'):
        x=data()['cases']['R04_QUERY'];offset=1
        if shot=='S06_P03'and progress>.7:offset=4
        drow=next(r for r in x['recorded_ROI_differences']if r['q_offset']==offset)
        changed=[r['site']for r in drow['differences']]
        out=[]
        for mode,label in [('on','CON CONSULTA'),('off','SIN CONSULTA')]:
            arm=x['arms'][mode];dg=arm['data'];fr=next(f for f in dg['frames']if f['offset']==offset)
            pts=collect(fr['ROI_nonzero_RAW'])
            # A missing item is RAW0 only where an explicit point records it.
            pts=unique(pts+collect(fr['explicit_points_including_RAW0']))
            for p in pts:
                if p['site']in changed:p['role']='difference'
            pp=panel(pts,label,67,dg['query_tick']+offset,arm['source'],[[25,13,53]])
            pp['difference_sites']=changed
            pp['query_was_supplied']=mode=='on';pp['data_window']='ROI only; no full lineage'
            out.append(pp)
        title='OTRO EXPERIMENTO'if shot=='S06_P03'else'UNA CONSULTA CAMBIA EL ESTADO'
        if offset==4:title='UNA SEÑAL ESTÁ EN AMBOS CASOS'
        return model_base(title,out,A,'R04_QUERY','/recorded_ROI_differences',stage_jump=offset==4,
            bounds=[[22,10,51],[28,16,55]])
    raise KeyError(shot)

def s07(shot,progress):
    x=data()['cases']['CPC9_COMPOSITION'];r=x['data'];src=x['selected_essential_source'];N=x['N']
    cut=next(c for c in r['conditions']if c['condition']=='cut_arrival_0')
    if shot=='S07_P01':
        pp=panel([point(p,'input')for p in r['incoming']],'',N,205,src)
        pp['value_labels']=[pfield(p,'/incoming/'+str(i)+'/s_reg',(230,60)if i==0 else(-230,-60))for i,p in enumerate(r['incoming'])]
        pp['direction_sites']=[p['site']for p in r['incoming']]
        pp['camera_azimuth_degrees']=45
        return model_base('DOS CONTRIBUCIONES',[pp],B,'CPC9_COMPOSITION','/data/incoming',bounds=[[18.5,6.5,12.5],[20.5,8.5,14.5]])
    if shot=='S07_P02':
        formed=r['formed'];pp=panel([point(formed,'difference')],'',N,206,src)
        pp['value_labels']=[pfield(formed,'/formed/s_reg',(220,0))];pp['direction_sites']=[formed['site']]
        pp['camera_azimuth_degrees']=45
        return model_base('PRODUCTO DEL ENCUENTRO',[pp],B,'CPC9_COMPOSITION','/data/formed',stage_jump=True,bounds=[[19.2,7.2,13.2],[20.8,8.8,14.8]])
    if shot=='S07_P03':
        out=r['baseline_consequence210'];pp=panel([point(out,'reader')],'',N,210,src,[out['site']],str(out['s_reg']),{'qualified_observation':out,'pointer':'/baseline_consequence210'})
        pp['direction_sites']=[out['site']]
        return model_base('EL RESULTADO SE UTILIZA DESPUÉS',[pp],B,'CPC9_COMPOSITION','/data/baseline_consequence210',stage_jump=True,bounds=[[23.2,11.2,17.2],[24.8,12.8,18.8]])
    if shot=='S07_P04':
        # Exactly one preselected cut, selected before rendering the comparison.
        full=r['baseline_consequence210'];missing=cut['consequence210']
        ps=[]
        for p,label in[(full,'CON AMBOS APORTES'),(missing,'FALTA UN APORTE')]:
            pp=panel([point(p,'reader')],label,N,210,src,[p['site']],str(p['s_reg']),{'record':p,'cut':None if p is full else'cut_arrival_0'})
            pp['direction_sites']=[p['site']];pp['camera_azimuth_degrees']=45;ps.append(pp)
        return model_base('CAMBIA LA CONSECUENCIA',ps,B,'CPC9_COMPOSITION','/data/conditions/0',stage_jump=True,bounds=[[23.2,11.2,17.2],[24.8,12.8,18.8]],
            control='cut_arrival_0; parent clock preserved; sham agrees with baseline')
    raise KeyError(shot)

def social_points(arm,index=1):
    row=arm['first_external_rows'][index]
    return collect(row['social_reads'])

def s08(shot,progress):
    x=data()['cases']['IC01_SOCIAL'];full=x['arms']['full'];src=full['source'];plan=full['progress']['plan']
    if shot=='S08_P01':
        pp=panel([point(full['progress']['source'],'input')],'ORIGEN',67,16562,src,[[21,59,40]])
        if progress>.55:
            f=x['passive_sampled_frames'][0]
            pp=panel(collect(f['observations']),'RECEPTOR',67,f['tick'],x['passive_source'],[[20,59,40]])
        return model_base('OTRO PARTICIPANTE',[pp],B,'IC01_SOCIAL','/arms/full/progress',stage_jump=progress>.55,
            bounds=[[18,57,38],[23,61,42]])
    if shot=='S08_P02':
        if progress<.38:
            # Retained ROI samples16566/16567 have no observed point in this
            # viewport. Do not fill the gap or imitate a tracked carrier.
            # Hold the recorded association stage, then cut to recorded use.
            f=frame_at(x['passive_sampled_frames'],16563)
            pp=panel(collect(f['observations']),'MENSAJE',67,f['tick'],x['passive_source'])
            bounds=[[18,57,38],[23,61,42]]
        else:
            row=full['first_external_rows'][1]
            qualified=next(p for p in row['social_reads']if p['qualified'])
            pp=panel(social_points(full),'RESPUESTA POSTERIOR',67,row['tick'],src,[[31,59,29]],signed(qualified['prepared_gain1_command']),
                {'social_reads':row['social_reads'],'prepared_motor_command':row['native_command'],'pointer':'/result/external/rows/1'})
            bounds=[[30.1,58.1,28.1],[31.9,59.9,29.9]]
        return model_base('EL MENSAJE SE UTILIZA DESPUÉS',[pp],B,'IC01_SOCIAL','/arms/full',stage_jump=progress>=.38,bounds=bounds,
            editorial_stage_ticks=[16563,16619],
            temporal_coverage='Two recorded stages held with a declared cut; intermediate empty ROI samples are not turned into a trajectory.')
    if shot=='S08_P03':
        ps=[]
        for key,label in[('full','MENSAJE RECIBIDO'),('cut','MENSAJE INTERRUMPIDO')]:
            arm=x['arms'][key];row=arm['first_external_rows'][1]
            pp=panel(social_points(arm),label,67,row['tick'],arm['source'],[[31,59,29]],str(row['native_command']),
                {'fixed_wiring':row['external_motor_wiring'],'physical_social_readings':row['social_reads'],
                 'physical_quantity':row['native'],'actual_command_field':'native_command','executed_torque':row['executed_torque']})
            pp['prepared_output_transduction']='quantity_gain1_plus_social_gain1; external fixed actuator wiring'
            pp['direction_sites']=[[31,59,29]]
            ps.append(pp)
        return model_base('CAMBIA LA ACTUACIÓN POSTERIOR',ps,B,'IC01_SOCIAL','/arms',stage_jump=True,bounds=[[30.1,58.1,28.1],[31.9,59.9,29.9]])
    raise KeyError(shot)

def witness_points(frame,groups=('own','contacts','A')):
    return unique([p for name in groups for p in collect(frame.get(name,{}))])

def s09(shot,progress):
    if shot=='S09_P01':
        x=data()['cases']['CYCLE02_RETURN'];ps=[]
        phase=0 if progress<.28 else 1
        response=progress>.66
        for key,label in[('full','CONSECUENCIA RECIBIDA'),('omit','RETORNO OMITIDO')]:
            arm=x['arms'][key];row=arm['data']['rows'][phase]
            pts=collect(row['native_pre']) if not response else[point(row['native_response'],'reader')]
            tick=row['native_pre']['reference']['tick']if not response else row['tick']
            pp=panel(pts,label,67,tick,arm['source'],[[50,35,35]],
                signed(row['native_action'])if response else None,
                {'actual_native_response':row['native_response'],'fixed_transduction_native_action':row['native_action'],'valid':row['valid']}if response else None)
            if not response:pp['value_labels']=[pfield(row['native_pre']['reference'],'/data/result/rows/'+str(phase)+'/native_pre/reference/s_reg',(-160,-90))]
            pp['actual_return_request']=arm['data']['rows'][0]['requests'][3:]
            ps.append(pp)
        return model_base('LA CONSECUENCIA CAMBIA EL USO POSTERIOR',ps,B,'CYCLE02_RETURN','/arms',stage_jump=phase==1,bounds=[[48.3,34.3,34.3],[51.7,35.7,35.7]])
    if shot=='S09_P02':
        x=data()['cases']['CP02_EARLY'];case=x['data']['cases'][0];em=case['emission'];oc=case['outcome']
        if progress<.57:
            f=em.get('panel_after',em['panel_before']);pts=collect(f['observations'])
            pts=[p for p in pts if p['site'] in([21,20,24],[23,20,24],[22,20,24])]
            out=point(em['physical_output'],'reader');pts=[p for p in pts if p['site']!=out['site']]+[out]
            pp=panel(pts,'SEÑAL ANTERIOR',47,37,x['source'],[[22,20,24]],signed(em['physical_output']['direction'][0]),{'decoder':em['decoder'],'prediction_set':em['prediction_set'],'emission':em['physical_output']})
        else:
            pts=[p for p in collect(oc['panel']['observations'])if p['site']in([21,20,24],[23,20,24],[22,20,24])]
            pp=panel(pts,'ACONTECIMIENTO POSTERIOR',47,70,x['source'])
            pp['external_outcome_record']=oc['outcome'];pp['do_not_render_external_event_as_inferred_native_cell']=True
        return model_base('OTRO EXPERIMENTO',[pp],B,'CP02_EARLY','/data/cases/0',stage_jump=progress>=.57,bounds=[[20.2,19.2,23.2],[23.8,20.8,24.8]])
    if shot in('S09_P03','S09_P04'):
        x=data()['cases']['ENTE01_RETURN'];r=x['data'];u=r['reader']['source_tick']
        if shot=='S09_P03':
            f=frame_at(r['frames'],u);pp=panel(witness_points(f),'SALIDA DE DEE',26,u,x['source'],[[6,13,13]],signed(r['reader']['command']),r['reader'])
            out=model_base('OTRO EXPERIMENTO',[pp],'Etapas y esquema','ENTE01_RETURN','/data',bounds=[[4.3,12.3,12.3],[7.7,15.7,15.7]])
            out['scheme']={'kind':'external_service','label':'ENLACE PREPARADO'}
            out['external_event']={'stage':'action','reader':r['reader'],'command':r['executed_external_command'],
                'effect':r['observed_result'],'consequence':r['consequence'],'source':x['source']}
            if progress>.55:
                out['title']='ACCIÓN EN SERVICIO EXTERNO';out['panels'][0]['label']='SALIDA DE DEE'
                out['scheme']['label']='CONTACTO REGISTRADO'
                out['panels'][0].pop('output_text',None)
            return out
        f=frame_at(r['frames'],u+4)
        pp=panel(witness_points(f),'NUEVA ENTRADA ADMITIDA',26,u+4,x['source'])
        req=next(q for q in r['requests']if q['id']==r['consequence']['tactile_request_id'])
        pp['input_site']=req['site'];pp['input_receipts']=[req]
        # No RAW was sampled at the injection site on96565. The dashed input
        # marker denotes the admitted request; it is not a fabricated particle.
        out=model_base('CONSECUENCIA Y NUEVA EXPERIENCIA',[pp],'Etapas y esquema','ENTE01_RETURN','/data/consequence',stage_jump=True,bounds=[[4.3,9.3,12.3],[7.7,15.7,15.7]])
        out['scheme']={'kind':'external_service','label':'RETORNO ADMITIDO'}
        out['external_event']={'stage':'return','effect':r['observed_result'],'admitted_request':req,'consequence':r['consequence'],'source':x['source']}
        return out
    raise KeyError(shot)

def destination_panel(rec,label,which='read'):
    r=rec['first'];src=rec['source'];tick=r['plan']['decision_deadline']
    f=frame_at(r['frames'],tick)
    pp=panel(witness_points(f),label,rec['N'],tick,src,[[p,13,13]for p in(5,6,7)],signed(r['formed_native_command']),r['reader'])
    pp['after_action_consequence']=r['consequence'];pp['actual_service']=r['local_service']
    pp['reader_source_tick']=r['reader']['source_tick']
    return pp

def s10(shot,progress):
    x=data()['cases']['ENTE02_TRANSFER'];rs=x['records']
    if shot=='S10_P01':
        rec=rs['04_FUENTE_T.json.gz'];r=rec['first']
        pts=collect(r['before']['own'])if progress<.45 else collect(rec['final_own'])
        tick=r['before']['tick']if progress<.45 else rec['final_own'][0]['tick']
        if progress>=.45:
            # Highlight the recorded support which also differs from the
            # same-age omitted-return source control. No scalar is invented.
            for p in pts:
                if p['site']==[7,15,15]:p['role']='difference'
        pp=panel(pts,'ANTES DE LA EXPERIENCIA'if progress<.45 else'ESTADO TRAS LA EXPERIENCIA',26,tick,rec['source'])
        pp['matched_omission_control_at_same_final_tick']=rs['05_FUENTE_U.json.gz']['final_own']
        return model_base('EXPERIENCIA PREVIA',[pp],B,'ENTE02_TRANSFER','/records/04_FUENTE_T.json.gz',stage_jump=progress>=.45,bounds=[[4.3,14.3,14.3],[7.7,15.7,15.7]])
    if shot in('S10_P02','S10_P03'):
        t=rs['10_DESTINO_B_T.json.gz'];u=rs['11_DESTINO_B_U.json.gz']
        ps=[destination_panel(t,'CON EXPERIENCIA'),destination_panel(u,'CONTROL')]
        title='ACTUACIÓN ANTES DEL RETORNO'if shot=='S10_P02'else'CONSECUENCIAS DIFERENTES'
        out=model_base(title,ps,B,'ENTE02_TRANSFER','/records',bounds=[[4.3,12.3,12.3],[7.7,15.7,15.7]])
        if shot=='S10_P02'and progress>.72:
            # Return belongs to the control's actual first rejection. Its
            # time is later than BOTH original commands, never before them.
            for rec,pp in zip((t,u),ps):
                rr=rec['first'];rt=rr['consequence']['material_input_tick']
                later=frame_at(rr['frames'],125500)
                pp['points']=witness_points(later);pp['tick']=125500
                pp.pop('output_text',None)
                if rt is not None:
                    req=next(q for q in rr['requests']if q['id']==rr['consequence']['tactile_request_id'])
                    pp['input_site']=req['site'];pp['input_receipts']=[req]
            out['title']='DESPUÉS LLEGA LA CONSECUENCIA';out['stage_jump']=True
        if shot=='S10_P03':
            out['utility_records']=[t['first']['observed_result'],u['first']['observed_result']]
            for rec,pp,base in zip((t,u),ps,('CON EXPERIENCIA','CONTROL')):
                pp['label']=base+(': COMPLETA'if rec['first']['observed_result']['job_completed']else': NO COMPLETA')
        return out
    if shot=='S10_P04':
        t=rs['30T_CONTRARIA.json.gz'];u=rs['30U_CONTRARIA.json.gz']
        ps=[destination_panel(t,'CON EXPERIENCIA'),destination_panel(u,'CONTROL')]
        for rec,pp,base in zip((t,u),ps,('CON EXPERIENCIA','CONTROL')):
            pp['label']=base+(': COMPLETA'if rec['first']['observed_result']['job_completed']else': NO COMPLETA')
        return model_base('OTRA REGLA: CAMBIA LA UTILIDAD',ps,B,'ENTE02_TRANSFER','/records/30T_CONTRARIA.json.gz',stage_jump=True,
            bounds=[[4.3,12.3,12.3],[7.7,15.7,15.7]],utility_records=[t['first']['observed_result'],u['first']['observed_result']],
            counts_are_contextual_not_general=x['denominators'])
    raise KeyError(shot)

def s11(shot,progress):
    if shot in('S11_P03','S11_P04'):
        from escenas_principal_r08 import model as central
        return central('S11',shot,progress)
    if shot=='S11_P01':
        x=data()['cases']['FI01_128'];pairs=x['pairs'];ps=[]
        stage=0 if progress<.44 else 1 if progress<.77 else 2
        for key,label in[('ref_sham_zero','128 CONTRIBUCIONES'),('ref_sham_two','CAMBIA UNA ENTRADA')]:
            r=pairs[key];tick=(16643,16699,16702)[stage]
            f=frame_at(r['frames'],tick)
            if stage==0:
                fields={k:v for k,v in f['fields'].items()if k.startswith('left.root.0')and len(k.split('.'))<=4}
                pts=collect(fields);rsites=[[48,54,54]];bounds=[[46.9,52.9,52.9],[49.1,55.1,55.1]]
            else:
                fields={k:v for k,v in f['fields'].items()if k in('A','B','E','D','actuator-1','actuator0','actuator1')}
                pts=collect(fields);rsites=[r['geometry']['datum_site']]if stage==1 else[p['site']for p in r['reader']['observations']]
                bounds=[[13.2,13.2,14.2],[16.8,16.8,16.8]]if stage==1 else[[12.4,14.4,12.4],[17.6,17.6,15.6]]
            if stage==2:pts=unique(pts+collect(r['reader']['observations']))
            pp=panel(pts,label,67,tick,x['source'],rsites,signed(r['reader']['choice'])if stage==2 else None,r['reader']if stage==2 else None)
            if stage==1:pp['value_labels']=[pfield(f['fields']['D'],'/aggregate128/pair/'+key+'/frames/22/fields/D/s_reg',(125,0))]
            if stage==0:pp['value_labels']=[pfield(f['fields']['left.root.0.0'],'/aggregate128/pair/'+key+'/frames/2/fields/left.root.0.0/s_reg',(120,-40))]
            pp['raw_components_fixed_128']=r['raw_components'];pp['actual_leaf_tick']=r['leaf_tick']
            ps.append(pp)
        return model_base('UNA CONTRIBUCIÓN CAMBIA EL RESULTADO',ps,B,'FI01_128','/pairs',stage_jump=stage>0,bounds=bounds)
    if shot=='S11_P02':
        if progress<.68:
            x=data()['cases']['ECI02_COEXISTENCE'];r=x['data'];ma=progress<.34
            if ma:
                reader=r['MA02_common_reader_at_q4'];pts=collect(reader['panel']);tick=r['query_tick']+4
                pp=panel(pts,'MEMORIA',67,tick,x['source'],[c['site']for c in reader['candidates']],signed(reader['formed_native_command']),reader)
                # One recorded MA region, not the union with distant FI sites.
                bounds=[[36.2,32.2,31.2],[37.8,33.8,34.8]]
                pp['camera_roll_degrees']=90
                pp['direction_sites']=[[37,33,34]]
            else:
                reader=r['original_FI_MU_reader_at_q6'];pts=collect(reader['observations']);tick=reader['tick']
                pp=panel(pts,'COMPARACIÓN',67,tick,x['source'],[p['site']for p in reader['observations']],signed(reader['choice']),reader)
                # Close-up of the unique qualified candidate. All six frozen
                # reader observations remain in reader_evidence, unchanged.
                qualified=reader['candidates'][0]['observation']
                site=qualified['site'];bounds=[[v-.8 for v in site],[v+.8 for v in site]]
                pp['direction_sites']=[site]
                pp['camera_azimuth_degrees']=45
            pp['editorial_view']='Sequential close-up within the same J11 shared physical window; no movement interpolation.'
            return model_base('MEMORIA Y COMPARACIÓN',[pp],A,'ECI02_COEXISTENCE','/data',stage_jump=not ma,bounds=bounds,
                physical_interval_overlap=r['physical_interval_overlap'])
        x=data()['cases']['ECI01_INTERFERENCE'];r=x['primary']['overlap'];reader=r['original_FI_MU_reader_at_q6']
        fr=next(f for f in r['frames']if f['offset']==6)
        pts=collect(fr['capture']['points'])+collect(reader['observations'])
        pp=panel(pts,'SIN RESULTADO',67,reader['tick'],x['source'],[p['site']for p in reader['observations']])
        pp['rejections']=r['request_statuses'];pp['reader_evidence']=reader
        pp['editorial_view']='A close-up of one explicitly sampled empty reader site; NULL is qualified from all six frozen observations, not inferred from this crop.'
        pp['camera_azimuth_degrees']=45
        return model_base('OTRO ENSAYO: INTERFERENCIA',[pp],A,'ECI01_INTERFERENCE','/primary/overlap',stage_jump=True,bounds=[[12.2,16.2,12.2],[13.8,17.8,13.8]])
    raise KeyError(shot)

def model(scene_id,shot_id,progress):
    if not 0<=progress<=1:raise ValueError('Editorial progress must lie within this shot')
    result={'S06':s06,'S07':s07,'S08':s08,'S09':s09,'S10':s10,'S11':s11}[scene_id](shot_id,progress)
    # A deliberate ROI crop cannot project off-screen cells over captions.
    # Selection changes only the investigator's view, never source positions.
    bounds=result.get('bounds')
    if bounds:
        lo,hi=bounds
        inside=lambda s:all(a<=v<=b for v,a,b in zip(s,lo,hi))
        for p in result.get('panels',[]):
            original=len(p['points']);p['points']=[v for v in p['points']if inside(v['site'])]
            if not p['points']:raise ValueError('ROI contains no observed points')
            for key in('reader_sites','input_sites','difference_sites','direction_sites','teaching_sites'):
                if key in p:p[key]=[s for s in p[key]if inside(s)]
            p['observed_points_outside_editorial_ROI']=original-len(p['points'])
        result['crop_notice']=True
    result['source_file_sha256']=source_hash()
    subset={'scene':scene_id,'shot':shot_id,'panels':result.get('panels',[]),'source':result.get('source'),
            'external_event':result.get('external_event'),'bounds':result.get('bounds'),'scheme':result.get('scheme')}
    result['source_data_hash']=hashlib.sha256(json.dumps(subset,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return result

