"""FS-only fix of prospective World restore audit; Native/body unchanged."""
from pathlib import Path
import ast,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def save(p,text):
    ast.parse(text)
    with p.open('x',encoding='utf8')as f:f.write(text)
    return {'file':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
s=(ROOT/'control/world_comprimido_v3.py').read_text('utf8')
s=s.replace("run_integrated_v3.py','_r07_original_world_base'", "run_integrated_v3_R02.py','_r07_original_world_base_R02'")
marker='class CompressedWorld(BASE.LegacyWorld):'
helper='''def verify_restore_events(source,restored,identity):
    old=source['events'];new=restored['events']
    if new[:len(old)]!=old:raise RuntimeError('Historical World events altered during restore; no Native')
    added=new[len(old):];kinds=[row.get('kind')for row in added]
    mandatory=['MOTOR_PREPARED','R07_MOTOR_ENVIRONMENT_PREPARATION','R07_TECHNICAL_IDENTITY']
    if kinds not in (mandatory,['R07_COMMON_NAVIGATION_GEOMETRY']+mandatory):
        raise RuntimeError('Restore added an undeclared event/action; no Native')
    for row in added:
        data=row.get('data',{});kind=row['kind']
        if kind=='R07_COMMON_NAVIGATION_GEOMETRY':
            if type(data.get('oldDecorativeCollidersDisabled'))is not int or not 0<=data['oldDecorativeCollidersDisabled']<=10000:
                raise RuntimeError('Bounded declared decorative collider preparation required')
        elif kind=='MOTOR_PREPARED':
            if data.get('kind')!='HUMANOID_PATHFINDING' or data.get('semantic_destination_selected_by_motor')is not False:
                raise RuntimeError('Motor preparation cannot select a semantic destination')
            pivot=data.get('preservedPivot')
            if not isinstance(pivot,list)or len(pivot)!=12 or any(type(x)not in(int,float)for x in pivot):
                raise RuntimeError('Exact prepared motor pivot required')
            if any(abs(x-y)>1e-5 for x,y in zip(pivot,source['body_pose'])):
                raise RuntimeError('Prepared motor changed the inherited body pivot')
        elif kind=='R07_MOTOR_ENVIRONMENT_PREPARATION':
            if data.get('native_ticks_advanced')!=0 or data.get('semanticPolicy')is not False or data.get('floorAndObstaclesPrepared')is not True:
                raise RuntimeError('Only declared zero-Native motor/environment preparation allowed')
        elif kind=='R07_TECHNICAL_IDENTITY':
            if data.get('current')!=identity or data.get('Native_memory_edited')is not False or data.get('products_preserved')is not True:
                raise RuntimeError('Exact technical identity/preserved products required')
    return kinds

'''
s=s.replace(marker,helper+marker)
start=s.index("        old_events=before['events'];new_events=after['events']")
end=s.index("        before['events']=[];after['events']=[]",start)
s=s[:start]+"        appended_preparation=verify_restore_events(state,restored,identity)\n"+s[end:]
s=s.replace("excluded_auditor_event='one appended R07_TECHNICAL_IDENTITY; old event prefix checked exactly'", "excluded_auditor_event='exact declared motor preparation and one identity event; old prefix checked byte-meaning exactly', appended_preparation_events=appended_preparation")
rows=[save(ROOT/'control/world_comprimido_v3_R02.py',s)]
s=(ROOT/'control/run_integrated_v3.py').read_text('utf8').replace('world_comprimido_v3.py','world_comprimido_v3_R02.py')
s=s.replace("session=a.session or 'R07_MAIN_'+uuid.uuid4().hex[:20]", "session=a.session or (state['S']['sessionId'] if state['native_life_id']==life and state['world_id']=='RBX01_CIERRE8_R07' else 'R07_MAIN_'+uuid.uuid4().hex[:20])")
rows.append(save(ROOT/'control/run_integrated_v3_R02.py',s))
with(ROOT/'control/CORRECCION_RESTAURACION_MOTOR_V3_R02.json').open('x',encoding='utf8')as f:
    json.dump({'Native_calls':0,'MCP_calls':0,'source_R01_preserved':True,'changes':['exact prepared motor event ABI, historical prefix unchanged','default same-life R07 reopen keeps source sessionID'],'files':rows},f,ensure_ascii=False,indent=2)
print(json.dumps(rows))
