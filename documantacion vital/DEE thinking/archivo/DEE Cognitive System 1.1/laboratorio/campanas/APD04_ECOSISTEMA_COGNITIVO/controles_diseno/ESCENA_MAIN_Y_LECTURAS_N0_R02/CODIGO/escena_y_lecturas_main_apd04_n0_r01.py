"""Archive-only synchronized storyboard and exact inherited/new reader extension.

Reuses Delivery's already-exported22-reader panel; no second panel extraction.
No Native import/tick. MAIN and its later CONTINUABLE fork are distinct tracks.
Only existing uint64 reader witnesses are displayed, not invented3D footage.
"""
from pathlib import Path
import argparse,csv,gzip,hashlib,importlib.util,json,shutil
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
EV=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
OUT=HERE/'ESCENA_MAIN_Y_LECTURAS_N0_R02'
LOGS=['MAIN_PILOTO_R02','MAIN_PREPARACION_R03','MAIN_ADQUISICION_R01','CONTINUABLE_OPERATIVO_R01']
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
def dump(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(canonical(v))
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def walk(v,p='$'):
    yield p,v
    if isinstance(v,dict):
        for k,x in v.items():
            if k in('result','result_json')and isinstance(x,str):
                try:x=json.loads(x)
                except json.JSONDecodeError:pass
            yield from walk(x,p+'.'+k)
    elif isinstance(v,list):
        for i,x in enumerate(v):yield from walk(x,p+'['+str(i)+']')
def raw(n):
    v=int(n)
    if not 0<=v<2**64:raise ValueError('Exact RAW uint64 required')
    return {'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':(v>>60)&15,
        'direction':[((v>>k)&15)-(16 if((v>>k)&15)>=8 else 0)for k in(48,52,56)]}
def gate_map(family):
    old=[((33,33,33),[(1,0,0),(0,1,0),(1,1,0),(-1,1,0),(1,-1,0),(-1,-1,0),(-1,0,0),(0,-1,0)]),
        ((47,47,47),[(-1,0,0),(0,-1,0),(1,0,0),(0,1,0)]),((47,17,47),[(1,0,0),(0,1,0)]),((47,7,47),[(-1,0,0),(0,-1,0)])]
    if family=='MA12':old=[(old[0][0],old[0][1][:6])]
    if family=='LEX36':old=old+[((47,7,47),[(1,0,0),(1,1,0)])]
    result={}
    for o,dirs in old:
        for d in dirs:
            for sign in(-1,1):result[tuple((o[i]+4*d[i]+(sign if i==2 else 0))%67 for i in range(3))]=sign
    return result
def lexical(node):
    kind=node.get('kind')
    if kind=='query'and'context_signal'in node:family='MA12';name=node['context_signal']
    elif kind=='APD03_common_lexical_query':family='LEX32';name=node['form']
    elif kind=='APD04_common36_lexical_query':family='LEX36';name=node['form']
    else:return None
    reader=node['reader'];g=gate_map(family);panel=reader['panel']
    if len(panel)!=len(g)or{tuple(o['site'])for o in panel}!=set(g):raise ValueError('Exact declared reader geometry differs')
    cs=[]
    for o in panel:
        d=raw(o['raw']);sign=g[tuple(o['site'])]
        if d['state']and d['semantic']==1 and d['direction']==[0,0,sign]:cs.append({'sign':sign,'observation':o})
    sign=cs[0]['sign']if len(cs)==1 else None
    return {'family':family,'name':name,'read_tick':node['read_tick'],'input_tick':node['input_tick'],'end_tick':node['end_tick'],
        'RAW_sign':sign,'reported_formed_native_command':reader['formed_native_command'],'candidate_count':len(cs),
        'candidates':cs,'observations':panel,'agrees':sign==reader['formed_native_command'],
        'reader_uses_target_or_token':reader.get('reader_uses_target_or_token',reader.get('reader_uses_token_target_or_expected_sign'))}
def witness_rows(scene_id,role,observations):
    rows=[]
    for o in observations:
        d=raw(o['raw']);s=o['site'];di=d['direction']
        rows.append({'scene_id':scene_id,'role':role,'tick':o.get('tick'),'x':s[0],'y':s[1],'z':s[2],
            'RAW_uint64_text':str(o['raw']),'clock_uint64_text':str(o['clock']),'state':d['state'],'s_reg':d['s_reg'],
            'semantic':d['semantic'],'direction_x':di[0],'direction_y':di[1],'direction_z':di[2]})
    return rows
def source_rows(base,index):
    result={}
    for src in index['logs']:
        z=(base/src['export']).read_bytes()
        if sha(z)!=src['export_sha256']:raise ValueError('Compressed original log bytes differ')
        b=gzip.decompress(z)
        if sha(b)!=src['original_sha256']:raise ValueError('Exact original log bytes differ')
        result[src['group']]=(src,[json.loads(x)for x in b.splitlines()])
    return result
def recalc(base):
    index=json.loads((base/'INDICE.json').read_bytes());logs=source_rows(base,index)
    helper=module('archived_workshop_exact_decoder',base/'CODIGO/compactar_recalcular_taller_n0.py')
    delivery=module('existing_Delivery_panel_recalculator',base/'CODIGO/extraer_panel_heredado_apd04_n0_r01.py')
    inherited=delivery.recalculate(base/'PANEL_HEREDADO_REUTILIZADO')
    readings=[];scene=[];witness=[];checks=[];seen=set();op_seen=set()
    for item in index['selected_existing_result_lines']:
        z=(base/item['export']).read_bytes();b=gzip.decompress(z)
        checks.append({'check':'selected_original_line_exact_bytes','ok':sha(z)==item['export_sha256']and sha(b)==item['line_sha256'],'request_id':item['request_id']})
    for group,(src,events)in logs.items():
        life='APD04_CONTINUABLE_R01'if group.startswith('CONTINUABLE')else'APD04_MAIN'
        for line_no,event in enumerate(events,1):
            request=event.get('requested_id','');rowprefix=group+':L'+str(line_no)
            for loc,n in walk(event):
                if not isinstance(n,dict):continue
                q=lexical(n)
                if group=='CONTINUABLE_OPERATIVO_R01'and n.get('kind')in('APD04_candidate_scalar_classification','APD04_candidate_native_balance'):
                    t=n['native_trial'];reader=t['reader'];sign=helper.choice(reader,'primitive');cs=[]
                    for o in reader['observations']:
                        d=raw(o['raw']);x=(o['site'][0]-15)//2;z=(o['site'][2]-15)//2
                        if d['state']and d['semantic']==1 and d['direction']==[x,1,z]:cs.append({'sign':x,'observation':o})
                    q={'family':'NUM6','name':n['kind'],'read_tick':t['read_tick'],'input_tick':t.get('query_tick'),
                        'end_tick':t.get('end_tick',t.get('after',{}).get('tick',t['read_tick'])),'RAW_sign':sign,
                        'reported_native_reader_choice':reader['choice'],'reported_physical_choice':n['physical_choice'],
                        'candidate_count':len(cs),'candidates':cs,'observations':reader['observations'],
                        'agrees':sign==reader['choice']and sign==n['physical_choice'],'value':t.get('raw_sensor_value'),'loads':n.get('public_independent_loads'),
                        'reader_uses_target_or_token':False}
                if q is not None and group in('MAIN_ADQUISICION_R01','CONTINUABLE_OPERATIVO_R01'):
                    key=(life,q['family'],q['name'],q['read_tick'])
                    if key not in seen:
                        seen.add(key);sid='read_'+str(len(readings)).zfill(3)
                        q.update(scene_id=sid,life=life,group=group,request_id=request,original_log=src['original'],original_log_sha256=src['original_sha256'],line_1based=line_no,locator=loc,
                            within_prepared_workshop_pipeline=loc.endswith('.word'))
                        readings.append(q);checks.append({'check':'native_reader_output_from_RAW_at_exact_geometry'if q['family']=='NUM6'else'formed_native_command_from_RAW_at_exact_geometry','ok':q['agrees'],'scene_id':sid})
                        witness.extend(witness_rows(sid,q['family'],q['observations']))
                        scene.append({'scene_id':sid,'track':life,'event_kind':'material_query','tick':q['read_tick'],'tick_end':q['end_tick'],
                            'request_id':request,'name':q['name'],'output_sign':q['RAW_sign'],'action':'CALIBRATION_QUERY_NO_ACTUATOR'if q['family']=='NUM6'else'ASSISTED_QUERY','useful':None,
                            'failure':'unformed'if q['candidate_count']==0 else'ambiguous'if q['candidate_count']>1 else'',
                            'assistance':'Operator supplies raw scalar/independent loads to fixed codec and Native comparison; no environmental actuator in calibration.'if q['family']=='NUM6'else'Operator selects query/context and fixed phase/resources/reader; content emitted by Native history. Material query, not passive observation.',
                            'original_log':src['original'],'original_sha256':src['original_sha256'],'line_1based':line_no,'locator':loc,
                            'details':{'reader_family':q['family'],'candidate_count':q['candidate_count']}})
                if not {'selection','public_before','committed_effect'}<=set(n):continue
                selector=n['selection'];reader=selector.get('reader',selector.get('native_trial',{}).get('reader',{}));tick=reader.get('tick')
                key=(life,n['episode'],tick)
                if life!='APD04_MAIN'or tick is None or not 604825<=tick<=639374 or key in op_seen:continue
                op_seen.add(key);sign=helper.choice(reader,'selection');action={-1:'USE',0:'INSPECT',1:'INSPECT'}.get(sign)
                checks.append({'check':'MAIN_prefix_physical_action_from_RAW','ok':action==n['physical_action'],'episode':n['episode']})
                sid='main_episode_'+str(n['episode']).zfill(3);effect=n['committed_effect'];primitive=n.get('native_operation');po=[];ps=None;pt=None
                if primitive:
                    pr=primitive['native_trial']['reader'];po=pr['observations'];ps=helper.choice(pr,'primitive');pt=pr.get('tick')
                    checks.append({'check':'MAIN_prefix_numeric_output_from_RAW','ok':ps==primitive['physical_choice'],'episode':n['episode']})
                word=n.get('word');lr=lexical(word)if isinstance(word,dict)else None
                if lr is not None:checks.append({'check':'MAIN_prefix_tool_output_from_RAW','ok':lr['agrees'],'episode':n['episode']})
                witness.extend(witness_rows(sid,'selector',reader['observations']));witness.extend(witness_rows(sid,'numerical_primitive',po))
                if lr:witness.extend(witness_rows(sid,'tool_word',lr['observations']))
                scene.append({'scene_id':sid,'track':life,'event_kind':'workshop_opportunity','tick':tick,'tick_end':pt or tick,'request_id':request,
                    'name':n['public_before']['word'],'output_sign':sign,'action':action,'useful':effect.get('useful'),
                    'failure':effect.get('reason','')if not effect.get('useful')else'',
                    'assistance':'P0 circular source order, two-bit sensor, task-word map, primitive codec, actuator and binary post-effect return. Native emits INSPECT/USE, lexical tool sign and numerical output when formed. Cache is environmental, not Native numeric memory.',
                    'original_log':src['original'],'original_sha256':src['original_sha256'],'line_1based':line_no,'locator':loc,
                    'details':{'episode':n['episode'],'public_before':n['public_before'],'native_tool_sign':None if lr is None else lr['RAW_sign'],
                        'native_numeric_sign':ps,'numeric_read_tick':pt,'effect':effect,'feedback':n.get('feedback'),'audit_after_effect':n.get('auditor_only_after_effect')}})
    scene.sort(key=lambda r:(r['track'],r['tick'],r['scene_id']))
    panel=[q for q in readings if q['request_id']=='apd04main_old_panel_r01']
    checks.append({'check':'reuse_existing_panel22_same_signs','ok':len(panel)==22 and all(any(q['name']==r['name']and q['RAW_sign']==r['RAW_sign']and(q['family']=='MA12')==(r['family']=='memories')for q in panel)for r in inherited['rows'])})
    return {'schema':'APD04.scene_and_extended_readers.N0.R02','new_native_ticks':0,'readings':readings,'scene':scene,'RAW_witness_rows':witness,
        'checks':checks,'check_count':len(checks),'issues':[c for c in checks if not c['ok']],
        'inherited_panel_counts':{'MA12':sum(q['family']=='MA12'for q in panel),'LEX32':sum(q['family']=='LEX32'for q in panel)},
        'reading_scope_counts':{'reused_material_panel':len(panel),'new_standalone_after_panel_source':sum(q['request_id']!='apd04main_old_panel_r01'and not q['within_prepared_workshop_pipeline']for q in readings),
            'nested_workshop_word_uses':sum(q['within_prepared_workshop_pipeline']for q in readings),'independent_learners_from_rows':0},
        'scope':'MAIN prefix604825→639374 only for integrated workshop scene. CONTINUABLE is a distinct child track. No AUX knowledge, adverse future, proposed observer, pending R04/reserve or unrecorded spatial frames are added.'}
def csv_write(path,rows):
    with path.open('x',encoding='utf-8-sig',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    with path.open(encoding='utf-8-sig',newline='')as f:back=list(csv.DictReader(f))
    if back!=[{k:''if v is None else str(v)for k,v in r.items()}for r in rows]:raise ValueError('Analytical CSV exact roundtrip failed')
def export():
    if OUT.exists():raise FileExistsError('Preserve the existing scene export')
    OUT.mkdir();index={'logs':[],'selected_existing_result_lines':[],'new_native_ticks':0,'omissions':['Complete Native/SQLite/bridge states remain local; this is not a continuity backup.','No dense3D frames exist in this export; RAW witnesses cover declared reader sites only.','No reserve or later R04 result is included before its real closure.']}
    for group in LOGS:
        p=EV/group/'TRAYECTORIA/EVENTOS.jsonl';b=p.read_bytes();z=gzip.compress(b,compresslevel=9,mtime=0);q=OUT/'PRIMARIOS'/(group+'_EVENTOS.jsonl.gz');q.parent.mkdir(exist_ok=True);q.write_bytes(z)
        if gzip.decompress(z)!=b:raise ValueError('Lossless original log export failed')
        index['logs'].append({'group':group,'original':p.relative_to(ROOT).as_posix(),'original_sha256':sha(b),'original_bytes':len(b),'export':q.relative_to(OUT).as_posix(),'export_sha256':sha(z)})
        for i,line in enumerate(b.splitlines(keepends=True)):
            e=json.loads(line);rid=e.get('requested_id','')
            selected=e.get('kind')=='scheduled_material_result'and(rid.startswith(('apd04main_first_r01_','apd04main_retained_r01_','apd04continuable_operation_r01_')))
            if selected:
                q=OUT/'LECTURAS_STANDALONE'/(rid+'.jsonl.gz');q.parent.mkdir(exist_ok=True);gz=gzip.compress(line,compresslevel=9,mtime=0);q.write_bytes(gz)
                index['selected_existing_result_lines'].append({'request_id':rid,'group':group,'line_1based':i+1,'line_sha256':sha(line),'line_bytes':len(line),'export':q.relative_to(OUT).as_posix(),'export_sha256':sha(gz),'exact_original_line_not_reserialized':True})
        if p.read_bytes()!=b:raise ValueError('Closed log changed during read')
    original_panel=EV/'PANEL_HEREDADO_RAW_N0_R01'
    for p in original_panel.iterdir():
        if p.is_file():q=OUT/'PANEL_HEREDADO_REUTILIZADO'/p.name;q.parent.mkdir(exist_ok=True);shutil.copy2(p,q)
    index['reused_existing_panel']={'original_directory':original_panel.relative_to(ROOT).as_posix(),
        'index_sha256':sha((original_panel/'INDICE_LINEA_ORIGINAL.json').read_bytes()),'not_reextracted':True}
    code=[Path(__file__),HERE/'compactar_recalcular_taller_n0.py',ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/cierre/extraer_panel_heredado_apd04_n0_r01.py']
    for p in code:q=OUT/'CODIGO'/p.name;q.parent.mkdir(exist_ok=True);shutil.copy2(p,q)
    dump(OUT/'INDICE.json',index);result=recalc(OUT);dump(OUT/'RECALCULO_Y_GUION.json',result)
    # A flat event table and a linked exact-uint64 observation table synchronize
    # byscene_id. No target-bearing data is fed to any participant.
    event_rows=[{k:v for k,v in row.items()if k!='details'}for row in result['scene']]
    csv_write(OUT/'ESCENA_EVENTOS.csv',event_rows);csv_write(OUT/'TESTIGOS_RAW.csv',result['RAW_witness_rows'])
    dump(OUT/'VERIFICACION_TABLAS.json',{'exact_roundtrip':True,'event_rows':len(event_rows),'RAW_rows':len(result['RAW_witness_rows']),
        'RAW_and_clocks_are_exact_text_not_float':True,'missing_emission_is_blank_with_explicit_failure_not_zero':True})
    manifest=[{'file':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in sorted(OUT.rglob('*'))if p.is_file()]
    dump(OUT/'MANIFIESTO.json',{'members':manifest,'self_hash_excluded':True})
    print(json.dumps({'output':str(OUT),'readers':len(result['readings']),'checks':result['check_count'],'issues':len(result['issues']),
        'scene_events':len(result['scene']),'RAW_witness_rows':len(result['RAW_witness_rows']),'files':len(manifest)+1,'bytes':sum(r['bytes']for r in manifest),'new_native_ticks':0},ensure_ascii=False))
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--export',action='store_true');g.add_argument('--recalc',type=Path);a=ap.parse_args()
    if a.export:export()
    else:
        r=recalc(a.recalc);print(json.dumps({'readers':len(r['readings']),'checks':r['check_count'],'issues':r['issues'],'new_native_ticks':0},ensure_ascii=False))
