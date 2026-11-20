"""Prospective PI10 read-window instrument on a fresh complete P0 clone.

No DEE import, owner, world, file or process is created on import. The original
R01 actor and physical inputs remain literal. Explicit diagnostic CALIBRATE
temporarily segments supplied-owner advancement to observe fixed windows;
it never reinterprets a stationary RAW as a valid motor or repairs a response.
Only Root may execute it, after closing the original calibration owners.
"""
from pathlib import Path
import hashlib, json, os

VERSION='DEE.PI10.prospective_read_windows_instrument.R02'
PREPARE='eci01-pi10-preparar';ADMIT='eci01-pi10-admitir';EPISODE='eci01-pi10-episodio';CALIBRATE='eci01-pi10-calibrar';STATE='eci01-pi10-estado'
MODES={PREPARE,ADMIT,EPISODE,CALIBRATE,STATE}
_BUSY=False
def body():
    from capacidades import pi10_consulta_adaptativa_R01 as literal
    return literal
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(data):return hashlib.sha256(data).hexdigest()
def at(site,d):return tuple((site[k]+d[k])%67 for k in range(3))
def validate_literal(row):return body().validate_literal(row)
def validate(a,row):
    b=body();b.validate(a,row)
    if row['modo']==CALIBRATE:
        p,_,c=b.protocol(a,True)
        need(p.get('diagnostic_windows_only')is True and c['role']=='calibration','Fresh explicitly diagnostic protocol/scope only; never evaluation')
        need(c.get('force_query')is True or c.get('force_query')is False,'Forced engineering calibration declared separately')
def points(protocol):
    preview=(30,40,30);origin=tuple(protocol['query_origin']);old=tuple(protocol['old_origin'])
    device={at(preview,(x,y,z))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)}
    device|={(30,40,29),(29,40,30),(33,40,30),(34,40,30),(36,40,30)}
    result={}
    for label,where in(('q1_TC',origin),('q2_TC',old)):
        local={at(where,(x,y,z))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)}
        local|={at(where,(x,-1,-2))for x in range(-5,6)}
        local|={at(where,d)for d in((0,0,-3),(-2,1,-2),(2,4,0),(-1,0,1),(0,-1,-3),(0,0,-2))}
        result[label]=sorted(local)
    result['device']=sorted(device)
    return result
def diagnostic_episode(a,directory):
    global _BUSY
    validate(a,{'modo':CALIBRATE});need(not _BUSY,'One diagnostic instrument per process; never overlap owners')
    b=body();p,protocol_sha,c=b.protocol(a,True);m=b._get(a);ordinal=m['ordinal'];h,g,d,exact,_=b.native();i=b.identity(a)
    refs1=g.bank_observations(a,d,exact,tuple(p['query_origin']));refs2=g.bank_observations(a,d,exact,tuple(p['old_origin']))
    cal=g.two_selector_calendar(int(a.tick),refs1['reference_clocks'][0],refs2['reference_clocks'][0])
    windows={name:list(range(cal[name]['query_tick']-3,cal[name]['query_tick']+9))for name in('first','second')}
    tick_set=set(windows['first'])|set(windows['second']);need(min(tick_set)>int(a.tick),'All diagnostic windows must be future; no rewind')
    groups=points(p);frames=[];captured=set();folder=b.home(directory,i['life_id']);need(folder.is_dir(),'P0/admission artifact home required')
    path=folder/('ventanas_%04d_R02.json'%ordinal);need(not path.exists(),'Prior diagnostic witness preserved; never repeat same opportunity')
    from capacidades import pi07_regulacion_R01 as old
    original_adapter=old.SafeAdapter
    def capture(tick):
        need(int(a.tick)==tick,'Exact actual instrument tick')
        frames.append({'tick':tick,'phase67':tick%67,'phase391':tick%391,'phase782':tick%782,
          'relative_to_q1':tick-cal['first']['query_tick'],'relative_to_q2':tick-cal['second']['query_tick'],
          'regions':{name:[exact(a.world.runtime.observe(d.Coordinate(*site)))for site in sites]for name,sites in groups.items()}})
        captured.add(tick)
    class WindowAdapter(original_adapter):
        def run_until(self,end):
            end=int(end)
            for tick in sorted(t for t in tick_set-captured if int(self.a.tick)<t<=end):
                super().run_until(tick);capture(tick)
            return super().run_until(end)
    error=None;result=None;_BUSY=True
    try:
        old.SafeAdapter=WindowAdapter
        result=b.episode(a,directory,calibration=True)
    except BaseException as e:
        error={'type':type(e).__name__,'reason':str(e)}
        raise
    finally:
        old.SafeAdapter=original_adapter;_BUSY=False
        report={'schema':VERSION,'life_id':i['life_id'],'ordinal':ordinal,'protocol_sha256':protocol_sha,
          'operator_calibration':True,'forced_query':c['force_query'],'fixed_calendar':cal,'fixed_window_ticks':windows,
          'fixed_sites':{k:[list(v)for v in sites]for k,sites in groups.items()},'actual_frames':frames,'expected_frame_count':len(tick_set),'captured_frame_count':len(frames),
          'actual_final_tick':int(a.tick),'error':error,'new_material_inputs_from_instrument':0,
          'read_method':'Native runtime.observe only; no additional material query or probe',
          'advance_segmentation_changed':True,'host_safety_check_frequency_changed':True,
          'passivity_scope':'Observation method is read-only within existing contract, but no universal observer neutrality is inferred. Compare actual final physical/causal state with an uninstrumented matched run if claimed.',
          'interpretation':'Stationary SEM1 remains NULL under R01 reader. Windows are diagnostic evidence and do not select a favourable decoder or update any learned state from Python.'}
        data=(json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf8')
        with path.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
    return {**result,'diagnostic_window_witness':{'file':path.name,'bytes':len(data),'sha256':sha(data)},'diagnostic_instrument':VERSION,'not_evaluation_or_learned_initiative':True}
def dispatch(a,row,*,actuator='closed',directory=None):
    validate(a,row)
    if row['modo']==CALIBRATE:
        need(actuator=='closed'and directory is not None,'Existing owned diagnostic artifact home and closed actuator only')
        return diagnostic_episode(a,directory)
    return body().dispatch(a,row,actuator=actuator,directory=directory)
def uncertain(a):return body().uncertain(a)
def operational_dependencies(a,directory):return body().operational_dependencies(a,directory)
def code_files():return (Path(__file__),*body().code_files())
