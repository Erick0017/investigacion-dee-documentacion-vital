"""Freeze one exogenous bounded material fixture; no seed search or Native."""
from pathlib import Path
import array,datetime,gzip,hashlib,json,random,struct,sys
P=Path(__file__).resolve().parents[1];S=P/'estados/candidato/sistema'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    sourceproof=P/'control/DIFERENCIA_TERMINAL_IZQ_NONE_PI06_R01.json'
    source=json.loads(sourceproof.read_text(encoding='utf8'))['sources']['izq']
    snapshot=S/source['snapshot'];encoded=snapshot.read_bytes()
    if sha(encoded)!=source['snapshot_sha256']:raise ValueError('Exact whole formed-source snapshot only')
    # Read only fixed header and allRAW for preflight; do not claim metadata or
    # full operational-state validation from this partial binary extraction.
    b=gzip.decompress(encoded);i=0
    def take(n):
        nonlocal i
        result=b[i:i+n];i+=n
        if len(result)!=n:raise ValueError('Truncated snapshot')
        return result
    def u32():return struct.unpack('<I',take(4))[0]
    def u64():return struct.unpack('<Q',take(8))[0]
    if take(8)!=b'DEETSNP1'or u32()!=2:raise ValueError('Frozen snapshot v2 only')
    n=u32();tick=u64();take(1);u64();u64();take(u32());count=u64()
    if n!=67 or tick!=826449 or count!=n**3:raise ValueError('N67 formed source826449 required')
    raw=array.array('Q');raw.frombytes(take(count*8))
    if sys.byteorder!='little':raw.byteswap()
    directions=[[x,y,z]for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)if(x,y,z)!=(0,0,0)]
    rng=random.Random(61001);births=[];selected=[]
    # The exact RNG stream and lexicographic order are declared. A direction
    # draw occurs only after an acceptedBernoulli draw; no separate hiddenseed.
    for x in range(33,38):
        for y in range(33,38):
            for z in range(33,38):
                if rng.random()>=0.4:continue
                direction=directions[rng.randrange(len(directions))]
                site=[x,y,z];value=int(raw[(x*n+y)*n+z]);sequence=len(births)
                births.append({'sequence':sequence,'channel':'PI06.environment.R03.cloud.%02d'%sequence,
                    'site':site,'direction':direction,'payload':7,'state':1,'semantic':1,
                    'delay_from_start':2,'snapshot_RAW_before':str(value)})
                selected.append(site)
    if not 1<=len(births)<=64:raise ValueError('Frozen seed exceeds finite birthbudget; do not resample')
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    fixture={'schema':'DEE.PI06.exogenous_material_fixture.R03','status':'SEALED_BEFORE_NATIVE',
        'registered_utc':stamp,'seed':61001,'random_generator':'Pythonstdlib random.Random(61001), integer seedv2',
        'algorithm':'Lexicographic x,y,z over33..37inclusive. Draw rng.random()<0.4. For each selectedsite draw rng.randrange(26) into lexicographic nonzeroMooredirections. No seedsearch, no deletion of inconvenient choices.',
        'box_center':[35,35,35],'box_side':5,'Bernoulli_probability':0.4,'direction_alphabet':directions,
        'birth_count':len(births),'births':births,'birth_tick':826451,
        'source':source,'source_snapshot_bytes':len(encoded),
        'preflight_selected_nonzero_RAW_sites':[r for r in births if int(r['snapshot_RAW_before'])!=0],
        'preflight_does_not_change_fixture':True,'new_Native_ticks':0,'Native_executed':False}
    fixturepath=P/'codigo/FIXTURE_PI06_AMBIENTE_R03_R02.json';write(fixturepath,fixture)
    protocol={'schema':'DEE.PI06.general_material_environment.protocol.R03','status':'SEALED_BEFORE_NATIVE',
        'registered_utc':stamp,'source':source,'N':67,'source_tick':826449,
        'fixture':{'file':fixturepath.name,'sha256':sha(fixturepath.read_bytes()),'birth_count':len(births)},
        'arms':['nube','control'],'entry_mode':{'modo':'eci01-pi06-ambiente','condicion':'nube|control','captura':'global|normal'},
        'birth_contract':{'state':1,'semantic':1,'payload':7,'delay_ticks':2,'SEM4_allowed':False,
            'inputs_per_arm':{'nube':len(births),'control':0},'fixed_source_order':True},
        'characterization':{'ticks':268,'new_corrective_actions':0,
            'capture_offsets':[0,1,2,3,4,5,6,7,8,9,10,67,134,201,268],
            'anchor_offsets':[0,268],'max_frames':15,'max_anchors':2},
        'safety':{'sample_every_ticks':67,'maximum_observed_RAW_nonzero_support':3000,
            'host_stop_only':True,'preserve_reached_future':True,
            'not_a_mathematical_between_samples_bound':True},
        'functional_followup':[{'mode':'old_fixed_FI_intact','public_operands':[14,3],'capture':'normal'},
            {'mode':'unforced_evolution','ticks':271,'capture':'global'},
            {'mode':'old_fixed_FI_intact','public_operands':[14,3],'capture':'normal'}],
        'age_budget_max_per_arm':955,'expected_age_if_original_FI198':935,
        'host_boundary':'The host fixes seed, geometry, sources, clock and two common questions. It does not select a response, send target-aware correction, add a guard after failure, clear a carrier or feed the expectedanswer.',
        'admission':'No occupiedsource is removed or moved. All fixed requests and any rejection remain evidence. If future admission is incomplete, stop under the existing runner without retry or overwriting.',
        'null_policy':'A fixed-reader NULL is retained separately from zero; a completed numerical/NULL outcome does not choose a new operation.',
        'scientific_scores':['NewSEM values, geometriccomponents and materialpersistence are descriptive.',
            'Changes of FI availability versus the no-supply arm must use the same actual ages, queryticks and originalreaders.',
            'A transient cloud can produce only agitation, relaxation or no usefuleffect; none of these is automatically regulation, learning or intelligence.',
            'The cloud and control share the oldformedsource containing the left+Zzero. They do not start from the official principal or erase thathistory.'],
        'Root_execution_gate':'Root must verify remaining bytes/worldslots/ticks/deadline before anyR03Native. Preparation alone is not execution.',
        'Native_executed_by_this_tool':False,'new_Native_ticks':0}
    protocolpath=P/'codigo/PROTOCOLO_PI06_AMBIENTE_R03_R02.json';write(protocolpath,protocol)
    print(json.dumps({'fixture':fixturepath.name,'fixture_sha256':sha(fixturepath.read_bytes()),
        'protocol':protocolpath.name,'protocol_sha256':sha(protocolpath.read_bytes()),'birth_count':len(births),
        'occupied_selected_sites':len(fixture['preflight_selected_nonzero_RAW_sites']),
        'Native_executed':False},ensure_ascii=False))
if __name__=='__main__':main()
