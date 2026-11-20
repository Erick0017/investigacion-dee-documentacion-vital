"""Passive source inspection and stdlib fake tests; NEVER imports DEE."""
from pathlib import Path
import array, ast, datetime, gzip, hashlib, importlib.util, json, struct, sys
from types import SimpleNamespace

P = Path(__file__).resolve().parents[1]
C = P.parents[2] / 'DEE Cognitive 2.0'
CAP = C / 'sistema/capacidades'


def sha(b): return hashlib.sha256(b).hexdigest()
def write(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')


def selected_ast(path, names, env):
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    body = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    if {n.name for n in body} != set(names): raise ValueError('Missing pure parser/function')
    exec(compile(ast.Module(body=body, type_ignores=[]), str(path), 'exec'), env)
    return env


def main():
    sys.dont_write_bytecode = True
    code = P / 'codigo/pi06_organizacion_R01.py'
    spec = importlib.util.spec_from_file_location('PI06_pure', code)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    if any(n == 'dee_thinking' or n.startswith('dee_thinking.') for n in sys.modules):
        raise RuntimeError('Pure test must not import DEE')
    source = C / 'sistema/estado/checkpoints/ECI02_PI03_REPRO_PI04_PI05_MAIN_01.T824911.9732f690faa1.deetsnap.gz'
    expected = 'af74c8f47e43ed3b2395a338a23a6cbd42f105ec2cff4daac15b7a4d45e90832'
    parser = P.parent / 'PROGRESION_INTEGRADA_05/codigo/contrastar_prefijos_C2C_PI05_pasivo.py'
    env = selected_ast(parser, ['Reader', 'decode', 'parse'],
                       {'array': array, 'gzip': gzip, 'struct': struct, 'sys': sys,
                        'sha': sha, 'json': json})
    parsed = env['parse'](source, expected)
    summary, raws, clocks, channels = parsed[:4]
    geometry = selected_ast(CAP / 'percepcion_cruda_fi01.py', ['geometry'],
        {'N': 67, 'E': (15,15,15), 'S': (14,15,16), 'VERSION': 'FI01.B05.operational_candidate.R1',
         'FACTORS': {8:[4],16:[4,2],32:[4,4],64:[4,4,2],128:[4,4,4]}})['geometry'](128)
    sites = []
    for name, site in m.SITES.items():
        index = (site[0]*67+site[1])*67+site[2]
        bindings = []
        for channel_name, encoded in channels:
            row = struct.unpack('<iiiIiiiBBB', bytes.fromhex(encoded))
            if list(row[:3]) == site:
                bindings.append({'name':channel_name,'site':list(row[:3]),'state':row[3],
                    'direction':list(row[4:7]),'semantic':row[7],
                    'allow_experience':bool(row[8]),'allow_probe':bool(row[9])})
        sites.append({'name':name, 'site':site, 'clock':int(clocks[index]),
                      **env['decode'](raws[index]), 'existing_interfaces':bindings,
                      'in_prepared_FI_corridor':site in geometry['opened']})
    if any(int(x['RAW']) != 0 for x in sites): raise ValueError('Proposed source is not RAW-empty')
    if any(name.startswith('PI06.') for name, _ in channels): raise ValueError('PI06 source already used')
    checks = []
    def ok(name, result):
        if not result: raise AssertionError(name)
        checks.append({'check':name,'passed':True})
    def refused(row):
        try:m.validate_literal(row)
        except (ValueError, TypeError):return True
        return False
    for condition in m.CONDITIONS:
        row = {'modo':m.FIPLUS,'condicion':condition,'izquierda':14,'derecha':3,'captura':'normal'}
        ok('literal '+condition, m.validate_literal(row)==row)
    ok('bool operand rejected', refused({'modo':m.FIPLUS,'condicion':'intacto','izquierda':True,'derecha':3,'captura':'normal'}))
    ok('answer field rejected', refused({'modo':m.FIPLUS,'condicion':'izq0','izquierda':14,'derecha':3,'captura':'normal','expected':1}))
    ok('arbitrary condition rejected', refused({'modo':m.FIPLUS,'condicion':'new','izquierda':14,'derecha':3,'captura':'normal'}))
    ok('fragmentation not exposed', refused({'modo':m.FIPLUS,'condicion':'intacto','izquierda':14,'derecha':3,'captura':'fragmentar'}))
    for count in (1,2,10,11,66,67,68,2000):
        ticks, anchors = m.evolution_ticks(100,count)
        ok('bounded evolution '+str(count), ticks[0]==100 and ticks[-1]==100+count and
           len(ticks)<=42 and anchors=={100,100+count} and len(anchors)<=3 and
           set(range(100,100+min(count,10)+1))<=set(ticks))
    ok('evolution zero rejected', refused({'modo':m.EVOLUTION,'ticks':0,'captura':'normal'}))
    ok('evolution cap rejected', refused({'modo':m.EVOLUTION,'ticks':2001,'captura':'normal'}))
    def identity(life, dimension=67, profile='fisica_directa'):
        runtime=SimpleNamespace(dimension=dimension,snapshot_metadata_entries=[(m.SYSTEM_KEY,json.dumps({'life_id':life,'profile':profile}))])
        return SimpleNamespace(world=SimpleNamespace(runtime=runtime))
    ok('diagnostic identity',m._identity(identity('ECI02_PI03_REPRO_PI04_PI05_PI06_TEST_01'))['profile']=='fisica_directa')
    for life in ('ECI02_PI03_REPRO_PI04_PI05_MAIN_01','ECI02_PI03_MAIN','ECI02_PI03_REPRO_PI06_TEST_01'):
        try:m._identity(identity(life)); good=False
        except ValueError:good=True
        ok('non-PI06 identity rejected '+life, good)
    # Import the exact external recorder implementation (stdlib-only) and
    # exercise its scheduler wrapper with a FAKE, not a Native Runtime.
    observer_spec=importlib.util.spec_from_file_location('PI06_pure_observer',CAP/'observador_global_PI05_R01.py')
    observer=importlib.util.module_from_spec(observer_spec);observer_spec.loader.exec_module(observer)
    class Fake:
        tick=100
        world=object()
        calls=[]
        def run_until(self,target):
            if target<self.tick:raise ValueError('rewind')
            self.calls.append([self.tick,target]);self.tick=target
    fake=Fake(); ticks,anchors=m.evolution_ticks(100,2000)
    wrapper=observer.CapturingAdapter(fake,ticks=ticks,recorder=None)
    wrapper.run_until(2100)
    ok('fake official adapter reaches horizon',fake.tick==2100 and wrapper.boundaries==ticks)
    ok('fake instrumentation schedules no new input',not hasattr(fake,'submit'))
    # Existing interface reuse is tested without constructing/importing Native.
    site=m.SITES['izq']
    channel=SimpleNamespace(injection_site=SimpleNamespace(x=site[0],y=site[1],z=site[2]),
        direction=SimpleNamespace(dx=0,dy=0,dz=1),state=1,semantic=1,allow_experience=True,allow_probe=False)
    fake_world=SimpleNamespace(interfaces=[SimpleNamespace(name='PI06.test',channel=channel)])
    ok('same physical channel reused without Native factory',m._declare(SimpleNamespace(world=fake_world),'PI06.test',site) is False)
    channel.state=0
    try:m._declare(SimpleNamespace(world=fake_world),'PI06.test',site); good=False
    except ValueError:good=True
    ok('mismatched immutable source rejected',good)
    req={'id':1,'receipt':{'status':'applied'}}
    counts=m._counts([req,req],1)
    ok('receipt alias deduplicated',counts['unique_requested']==1 and counts['applied']==1)
    dependencies={name:sha((CAP/name).read_bytes()) for name in (
        'pi05_transito_causal_R01.py','PROTOCOLO_PI05_TRANSITO_R01.json',
        'observador_global_PI05_R01.py','acceso_eci01.py','percepcion_cruda_fi01.py')}
    proof={'schema':'DEE.PI06.organization.passive_preflight_and_pure_tests.R01',
        'inspected_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source_snapshot':summary['snapshot'],'source_physical':summary['physical'],
        'sites':sites,'geometry_source_sha256':dependencies['percepcion_cruda_fi01.py'],
        'geometry_raw_relative_tick':geometry['raw_relative_tick'],
        'parent_geometry_nodes':[x for x in geometry['nodes'] if x['site'] in ([52,48,58],[19,53,25])],
        'pure_checks':checks,'pure_checks_passed':len(checks),'Native_executed':False,
        'Native_ticks':0,'physical_admission_not_yet_tested':True,
        'trajectory_prediction_not_native_lineage':True,'source_files_modified':False,
        'module':{'path':str(code),'sha256':sha(code.read_bytes())}}
    proofpath=P/'control/ORGANIZACION_PI06_PREFLIGHT_Y_PRUEBAS_PURAS_R01.json'
    write(proofpath,proof)
    protocol={'schema':'DEE.PI06.organization.protocol.R01','status':'SEALED','N':67,
        'sites':m.SITES,'birth':{'state':1,'semantic':1,'direction':[0,0,1],
            'delay_from_input_tick':4,'offset_from_query_tick':-50},
        'conditions':{k:None if v is None else {'site_key':v[0],'payload':v[1]} for k,v in m.CONDITIONS.items()},
        'dependencies_sha256':dependencies,
        'source_snapshot':summary['snapshot'],'source_physical':summary['physical'],
        'passive_preflight':{'file':proofpath.name,'sha256':sha(proofpath.read_bytes())},
        'unchanged_readers':{'early_offset_from_q':4,'old_offset_from_q':6},
        'evolution_capture':{'maximum_ticks':2000,'first_offsets_inclusive':[0,10],
            'cadence_ticks':67,'last_frame':True,'anchor_rule':'first and last only','max_anchors':2,'max_frames':42,
            'max_compressed_bytes':67108864},
        'predictions':{'izq':'A legal +Z carrier may occupy the left aggregation parent before the four incoming contributions, changing their encounter. Whether it is admitted and impairs FI is empirical.',
                       'der':'Prepared right-side comparison; inherited PI05 guard may interact after recirculation. No new SEM4.',
                       'sham':'Off-path equal material dose and birth phase; absence of effect remains empirical.'},
        'limitations':['Preflight RAW0 is observed only at the frozen parent; future occupied-site rejection must be retained without clearing or retiming.',
            'One transient carrier is not physiological harm, pain, learned regulation or repair.',
            'Evolution preserves all existing pending inputs and anatomy; spontaneous recovery must be distinguished from age, phase and exhaustion in paired controls.']}
    write(P/'codigo/PROTOCOLO_PI06_ORGANIZACION_R01.json',protocol)
    print(json.dumps({'pure_checks_passed':len(checks),'sites':sites,'Native_executed':False,
        'protocol_sha256':sha((P/'codigo/PROTOCOLO_PI06_ORGANIZACION_R01.json').read_bytes()),
        'module_sha256':sha(code.read_bytes())},ensure_ascii=False))


if __name__=='__main__':main()
