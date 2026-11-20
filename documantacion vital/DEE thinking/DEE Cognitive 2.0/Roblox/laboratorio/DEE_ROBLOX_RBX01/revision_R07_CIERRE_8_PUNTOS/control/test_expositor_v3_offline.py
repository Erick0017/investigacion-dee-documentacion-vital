"""Offline metadata-only tests for the closed-cut expositor. No Native/DB/process calls."""
from pathlib import Path
import copy,importlib.util,json
ROOT=Path(__file__).resolve().parent
CAMPAIGN=ROOT.parent
def main():
    spec=importlib.util.spec_from_file_location('_expositor_v3_test',ROOT/'exponer_reanudacion_estado_local_v3.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    d=ROOT/'FIXTURES_EXPOSITOR_V3_R01'
    if d.exists():raise ValueError('Preserve prior offline fixtures')
    d.mkdir()
    life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_TEST_METADATA_ONLY'
    def closed(a,b,cycle):
        return{'offline_fixture':True,'schema':'DEE.RBX01.R07.integrated.result.R01',
            'identity':{'life':life,'session':'OFFLINE_FIXTURE_NO_WORLD','participant':'LIVE_NATIVE'},
            'source_tick':a,'final_tick':b,'new_Native_ticks':b-a,'owner_closed':True,
            'new_opportunities_completed':1,'global_completed':cycle,'rows':[{'cycle':cycle}],
            'world_sha256':'a'*64,'world_checkpoint':'OFFLINE_FIXTURE_NO_WORLD.json'}
    a,b=closed(991187,991200,29),closed(991200,991220,30)
    pair={'offline_fixture':True,'schema':'DEE.RBX.IntegralV3.ClosedPair.R01',
        'boundary':{'life_id':life,'native_tick':991220,'world_sha256':'a'*64,'next_opportunity':31},
        'members':[{'file':'WORLD_CHECKPOINT.json'},{'file':'CIERRE_CONCILIADO.json'}],
        'source_all_file_hashes_before_after_equal':True,'material_reopen_tested':False}
    def write(name,value):
        p=d/name;p.write_text(json.dumps(value),encoding='utf8');return p
    pa,pb,pp=write('FICTIONAL_A.json',a),write('FICTIONAL_B.json',b),write('FICTIONAL_PAIR.json',pair)
    report=m.expose([pa,pb],pp,life,True)
    assert report['status']=='OFFLINE_FIXTURE_ONLY'and report['last_supplied_closed_tick']==991220
    assert report['new_rows_in_supplied_blocks']==2 and report['SQLite_opened_by_this_tool']is False
    checks=['valid_explicit_closed_chain']
    def rejects(label,aa,bb,qq,allow=True):
        x=write('CASE_'+label+'_A.json',aa);y=write('CASE_'+label+'_B.json',bb);z=write('CASE_'+label+'_PAIR.json',qq)
        try:m.expose([x,y],z,life,allow)
        except ValueError:checks.append(label);return
        raise AssertionError('Expected rejection:'+label)
    bad=copy.deepcopy(a);bad['owner_closed']=False;rejects('unclosed_owner',bad,b,pair)
    bad=copy.deepcopy(pair);bad['boundary']['native_tick']+=1;rejects('different_pair_tick',a,b,bad)
    bad=copy.deepcopy(b);bad['identity']['life']='OTHER_LIFE';rejects('different_life',a,bad,pair)
    bad=copy.deepcopy(b);bad['source_tick']+=1;bad['new_Native_ticks']-=1;rejects('discontinuous_physical_prefix',a,bad,pair)
    bad=copy.deepcopy(b);bad['rows'][0]['cycle']=29;bad['global_completed']=29;rejects('repeated_prefix_not_new_experience',a,bad,pair)
    rejects('fixture_cannot_masquerade_real_closure',a,b,pair,False)
    result={'schema':'DEE.R07.expositor.offline_test.v1','tests':len(checks),'passed':len(checks),'checks':checks,
        'fixtures_are_not_states':True,'Native_calls':0,'DB_opens':0,'process_inspections':0,'originals_changed':False}
    (d/'RESULTADO_FIXTURES.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result))
if __name__=='__main__':main()
