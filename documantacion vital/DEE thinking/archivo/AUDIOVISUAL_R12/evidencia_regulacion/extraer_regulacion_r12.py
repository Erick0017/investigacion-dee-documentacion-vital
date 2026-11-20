"""Extract existing CPC5/4.5 regulation records. No DEE import or evolution.

The copied dense arrays are historical audit fields, not restorable worlds.
Run with bundled CPython; source locations are derived from DEE thinking.
"""
from pathlib import Path
import array, gzip, hashlib, json, shutil, sys

OUT = Path(__file__).resolve().parent
THINK = OUT.parents[2]
PRODUCT = THINK / '4.5/DEE_thinking_4_5_0'
BASE = PRODUCT / 'validation/experimental_regulation_4_5_final6'
CASES = ('REG_PAIRED', 'REG_RESERVED_TRANSLATION', 'REG_UNPAIRED', 'REG_OPPOSITE')
N = 67

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def ref(p, pointer=None):
    p = Path(p).resolve()
    row = {'path': str(p), 'sha256': sha(p), 'bytes': p.stat().st_size}
    if pointer is not None:
        row['pointer'] = pointer
    return row

def exact(p, tick=None):
    keys = ('tick','site','raw','clock','state','s_reg','direction','semantic','raw_present','occupied')
    q = {k:p[k] for k in keys if k in p}
    q['raw'] = str(q['raw']); q['clock'] = str(q['clock'])
    q['tick'] = int(q.get('tick', tick))
    return q

def decode_array(folder, descriptor):
    p = folder / descriptor['path']
    packed = p.read_bytes(); raw = gzip.decompress(packed)
    assert hashlib.sha256(packed).hexdigest() == descriptor['sha256_compressed']
    assert hashlib.sha256(raw).hexdigest() == descriptor['sha256_uncompressed']
    assert len(raw) == descriptor['bytes'] == 8*N**3
    a = array.array('Q'); a.frombytes(raw)
    if sys.byteorder != 'little': a.byteswap()
    return a

def index(site):
    x,y,z = site
    return x*N*N+y*N+z

def copy_exact(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        assert sha(source) == sha(destination), 'Existing export differs; preserve it.'
    else:
        shutil.copy2(source, destination)
    assert sha(source) == sha(destination)

def run():
    result_path = OUT / 'CPC5_REGULACION_DATOS_EXACTOS.json'
    assert not result_path.exists(), 'Preserve prior exports; do not overwrite.'
    comparison_path = PRODUCT / 'validation/EXPERIMENTAL_REGULATION_DIFF_final6.json'
    comparison = load(comparison_path)
    comparison_cases = {c['case_id']:c for c in comparison['cases']}
    mode_source = PRODUCT / 'source/python/dee_thinking/experimental_regulation.py'
    if not mode_source.exists():
        mode_source = THINK / 'DEE Cognitive 2.0/motor/python313/site-packages/dee_thinking/experimental_regulation.py'
    module_provenance = mode_source.parent / 'data/CPC5_REGULATION_PROVENANCE.json'
    runner_path = PRODUCT / 'validation/tools/regulation_port.py'
    config_path = PRODUCT / 'validation/tools/regulation_port_config.json'
    known_fields = {}
    originals = {}
    for case in CASES:
        p = BASE/case/'RESULT.json'; data = load(p); originals[case] = data
        assert sha(p) == comparison_cases[case]['after_primary_sha256']
        for frame in data['frames']:
            for record in frame['forms'].values():
                fields = {k:record[k] for k in ('state','s_reg','direction','semantic')}
                raw = str(record['raw'])
                if raw in known_fields: assert known_fields[raw]['fields'] == fields
                else: known_fields[raw] = {'fields':fields,'source':ref(p, '/frames/'+str(data['frames'].index(frame))+'/forms')}
    arms = {}
    files = []
    for case in CASES:
        folder = BASE/case; src = folder/'RESULT.json'; data = originals[case]
        cfg = load(folder/'CONFIG.json'); translation = cfg['case']['translation']
        meeting = [(v+t)%N for v,t in zip((22,40,10),translation)]
        hub = next(f for f in data['frames']if int(f['tick'])==3)['forms']['nominal_regulator_segment']['site']
        compact_frames = []
        dense_context = []
        for fi, f in enumerate(data['frames']):
            tick = int(f['tick']); obs = {k:exact(v) for k,v in f['forms'].items()}
            row = {'tick':tick,'observations':obs,'points':list(obs.values()),'source':ref(src, '/frames/'+str(fi)+'/forms')}
            if 'raw' in f:
                aa = decode_array(folder,f['raw']); cc = decode_array(folder,f['clock'])
                # Verify the storage order against every explicitly decoded
                # record, including nonzero anchors: xyz, z varying fastest.
                assert all(aa[index(v['site'])]==int(v['raw']) and cc[index(v['site'])]==int(v['clock']) for v in f['forms'].values())
                for kind in ('raw','clock'):
                    source = folder/f[kind]['path']; dest = OUT/'primarios'/case/source.name
                    copy_exact(source,dest); files.append({'source':ref(source),'export_relative':str(dest.relative_to(OUT))})
                if tick in (292,293):
                    points=[]
                    for dx in (-1,0,1):
                        for dy in (-1,0,1):
                            for dz in (-2,-1,0,1,2):
                                site=[(meeting[0]+dx)%N,(meeting[1]+dy)%N,(meeting[2]+dz)%N];ii=index(site)
                                p={'tick':tick,'site':site,'raw':str(aa[ii]),'clock':str(cc[ii]),'linear_index':ii}
                                if p['raw'] in known_fields:
                                    p.update(known_fields[p['raw']]['fields']);p['field_decode_provenance']=known_fields[p['raw']]['source']
                                points.append(p)
                    dense_context.append({'tick':tick,'N':N,'center':meeting,'offset_domain':{'dx':[-1,1],'dy':[-1,1],'dz':[-2,2]},'coverage':'45 exact sampled sites, including RAW0; not the full dependency region of a v27 tick.','points':points,'raw_source':ref(folder/f['raw']['path']),'clock_source':ref(folder/f['clock']['path'])})
                row['dense_fields']={'raw':f['raw'],'clock':f['clock'],'source_folder':str(folder.resolve()),'linear_layout':'x*N*N+y*N+z; checked against all explicit observations at this frontier.'}
            compact_frames.append(row)
        entries=[]
        for call in data['calls']:
            if call['port'].startswith('native_regulator.'):
                dr=(-1,0,0) if call['port'].endswith('.cue') else (1,0,-1 if cfg['case']['mode']=='opposite'else 1)
                site=[(hub[i]-3*dr[i])%N for i in range(3)]
                entries.append({**call,'site':site,'direction':list(dr),'state':1,'semantic':1,'coordinate_provenance':'Fixed public interface recipe _interfaces; not an inferred path or an additional material observation.','source':ref(src,'/calls/'+str(data['calls'].index(call)))})
        captures = {bank:{role:exact(point)for role,point in pair.items()}for bank,pair in data['captures'].items()}
        qualified = {}
        for bank,pair in captures.items():
            rr,ff = pair['resource'],pair['function']
            resource_direction = [1,0,1] if bank=='N'else[1,0,0]
            rv = rr['state']>0 and rr['semantic']!=5 and rr['s_reg']==3 and rr['direction']==resource_direction
            fv = ff['state']>0 and ff['semantic']!=5 and ff['s_reg']==7 and ff['direction']==[0,1,0]
            calculated={'resource':rv,'function':fv,'external_utility':int(rv)+2*int(fv)}
            assert calculated == data['profiles'][bank]
            qualified[bank]={'observations':pair,'qualified_resource':rv,'qualified_function':fv,'resource_contract':{'state_positive':True,'semantic_not':5,'s_reg':3,'direction':resource_direction},'function_contract':{'state_positive':True,'semantic_not':5,'s_reg':7,'direction':[0,1,0]},'external_utility':calculated['external_utility'],'source':ref(src,'/captures/'+bank)}
        utility = sum(v['external_utility']for v in qualified.values())
        assert utility == (5 if cfg['case']['mode']=='paired' else 4)
        arm={'case_id':case,'mode':cfg['case']['mode'],'N':N,'translation':translation,'source':ref(src),'config':cfg['case'],'frames':compact_frames,'contact_contexts':dense_context,'entry_receipts':entries,'all_input_calls':data['calls'],'qualified_readers':qualified,'functional_observer':{'external_utility':utility,'formula':'sum_banks(int(resource_valid)+2*int(function_valid))','computed_after_trajectory':True,'not_a_raw_load_or_energy':True},'technical':data['technical'],'observed_ticks':[int(f['tick'])for f in data['frames']],'version_comparison':comparison_cases[case]}
        arms[case]=arm
        for name in ('RESULT.json','CONFIG.json'):
            source=folder/name;dest=OUT/'primarios'/case/name;copy_exact(source,dest);files.append({'source':ref(source),'export_relative':str(dest.relative_to(OUT))})
    code_sources=[mode_source,module_provenance,runner_path,config_path,comparison_path,PRODUCT/'evidence/CPC5_regulation/src/network.py',PRODUCT/'evidence/CPC5_regulation/src/regulation_forks.py']
    for p in code_sources:
        dest=OUT/'fuentes'/p.name;copy_exact(p,dest);files.append({'source':ref(p),'export_relative':str(dest.relative_to(OUT))})
    payload={'schema':'DEE.R12.CPC5.regulation.archival-extraction.1','new_Native_ticks':0,'no_DEE_imports':True,'cases':arms,'arms':list(arms),'N':N,'source_coverage':{'F2':{'source':ref(THINK/'4.5/DEE_thinking_4_5_0_Libro_Blanco_y_Manual_Tecnico.docx'),'coverage':'Partial directed reading: section67, XML body/table paragraph sequence1517..1525 and C23 entry2418..2421. Page74 reference not independently rendered in this extraction.'},'installed_experimental_module':'Complete text; no import or execution.','regulation_port_runner':'Complete text; no execution.','historical_network':'Directed regulate function437..572, especially learned_pulse476..492 and field sampling493..552; surrounding text read incidentally, not the whole source.','historical_regulation_forks':'Complete text; implementation only. Its original diagnostic outputs were not recovered here and are not claimed executed by this export.','primary_results':'All four4.5 RESULT.json files parsed complete, all23forms per case and all calls/readers; four4.0 RESULT hashes and preexisting differential identify the source-equivalence history. Dense4.5 five-frontier RAW/clocks exported and checked against their declared hashes, not evolved.'},'interpretation_limits':['Direction was acquired from actual zero-load cue/report experiences. The designer prepared geometry, interfaces, finite schedule and later resource opportunities.','This is neither U0 guard_mode nor six fixed interceptors; no new policy, autonomous timing, reinforcement-selected regulation, universal homeostasis or indefinitely renewable pulse is demonstrated.','T3→T290 is a declared jump between recorded frontiers. Nominal samples do not establish uninterrupted tracked lineage; do not interpolate missing history as observed physical motion.','At292 the paired pulse and adjacent opposing material are recorded; at293 their sites are empty. Controls have the adjacent material enter the meeting instead. Attribution is to the bounded apparatus and contrasts, not a general microscopic genealogy proof.','The5/4 values are external task utility from two prepared banks. Physical functional witness is load7 at Flat.function437 in paired/reserve and absence in unpaired/opposite.','Port4.5 comparisons are software equivalence witnesses preserving older positive/negative cases, not independent new learners or new scientific replications.','Dense RAW/clock exports do not include the full operative snapshot and must not be restored as a life. Original complete checkpoints remain at their source locations.'],'files':files,'extractor':ref(__file__)}
    result_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'output':str(result_path),'bytes':result_path.stat().st_size,'sha256':sha(result_path),'utilities':{k:a['functional_observer']['external_utility']for k,a in arms.items()},'new_Native_ticks':0},ensure_ascii=False),flush=True)

if __name__=='__main__':
    run()
