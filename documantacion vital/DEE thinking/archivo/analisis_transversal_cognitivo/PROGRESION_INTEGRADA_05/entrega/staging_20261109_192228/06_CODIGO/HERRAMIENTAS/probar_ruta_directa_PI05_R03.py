"""Pure mock direct-RP source contract; fake bytes are NOT Native snapshots."""
from pathlib import Path
import copy,hashlib,importlib.util,json,types
P=Path(__file__).resolve().parents[1];SRC=P/'codigo/incorporar_PI05.py';OUT=P/'control/INCORPORADOR_RUTA_DIRECTA_PI05_R03_PURO.json'
def need(x,s):
 if not x:raise AssertionError(s)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True),encoding='utf8')
def refused(fn):
 try:fn()
 except ValueError:return True
 raise AssertionError('Expected exact direct path refusal absent')
if __name__=='__main__':
 need(not OUT.exists(),'No overwrite');root=P/'control/INCORPORADOR_RUTA_DIRECTA_MOCK_R03';need(not root.exists(),'Fresh mock only');root.mkdir()
 sp=importlib.util.spec_from_file_location('pi05_direct_contract',SRC);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 m.P=root/'campaign';m.C=root/'product';m.RP=m.C/'reproducibilidad';m.CS=m.P/'source_system';m.P.mkdir();m.CS.mkdir();(m.RP/'materiales').mkdir(parents=True)
 tick=999999;pair=m.RP/'materiales'/('PI03_PI05_FINAL_GUARD_T'+str(tick));pair.mkdir();fake=b'MOCK_NOT_NATIVE_SNAPSHOT';(pair/'VIDA.deetsnap.gz').write_bytes(fake)
 source_snap=m.CS/'fake_snapshot.bin';source_snap.write_bytes(fake);physical={'N':67,'tick':tick,'RAW_sha256':'1'*64,'clocks_sha256':'2'*64}
 card={'life_id':m.SOURCE_LIFE,'physical':physical,'snapshot':'fake_snapshot.bin','snapshot_sha256':sha(source_snap)};write(m.CS/'estado/vidas'/m.SOURCE_LIFE/'VIDA.json',card)
 manifest={'life_id':m.SOURCE_LIFE,'queue_journal_required':True,'physical':physical,'native_snapshot':'VIDA.deetsnap.gz','snapshot_sha256':sha(pair/'VIDA.deetsnap.gz'),'members':[{'file':'VIDA.deetsnap.gz','bytes':len(fake),'sha256':sha(pair/'VIDA.deetsnap.gz')}]};write(pair/'EXPORTACION_SERVICIO.json',manifest)
 proof=pair.parent/(pair.name+'_PRESERVACION.json');value={'schema':'DEE.PI05.direct_stable_closed_paired_preservation.R03','direct_stable_RP_export':True,'source_files_all_unchanged':True,'Native_executed':False,'new_ticks':0,'destination':str(pair),'source_system':str(m.CS),'life_id':m.SOURCE_LIFE,'source_tick':tick,'snapshot_sha256':card['snapshot_sha256'],'manifest_sha256':sha(pair/'EXPORTACION_SERVICIO.json')};write(proof,value)
 d={'desired_cut':{'N':67,'tick':tick,'snapshot_sha256':card['snapshot_sha256']},'pair':{'directory':str(pair),'manifest_sha256':sha(pair/'EXPORTACION_SERVICIO.json')},'direct_preservation':{'path':str(proof),'sha256':sha(proof)},'stable_pair_relative_to_product':pair.relative_to(m.C).as_posix()}
 m.validate_genealogy=lambda d,c:{'all_genealogy_is_mock':True};parser=types.SimpleNamespace(snapshot_view=lambda p:{'physical':physical},compare_native=lambda a,b,allow_service=False:{'mock_only':True,'new_ticks':0})
 result=m.source_state(d,parser);stable,check=m.stable_pair(d);need(result[1]==stable==pair,'Same exact source/stable path, no duplicate')
 bad=copy.deepcopy(d);bad.pop('direct_preservation');r={'missing_direct_or_relocation':refused(lambda:m.source_state(bad,parser))}
 altered=dict(value,destination=str(pair.parent/'DIFFERENT'));write(proof,altered);bad=copy.deepcopy(d);bad['direct_preservation']['sha256']=sha(proof);r['changed_destination']=refused(lambda:m.source_state(bad,parser));write(proof,value)
 other=pair.parent/'OTHER_PAIR';other.mkdir();bad=copy.deepcopy(d);bad['stable_pair_relative_to_product']=other.relative_to(m.C).as_posix();r['different_stable_copy']=refused(lambda:m.stable_pair(bad))
 record={'schema':'DEE.PI05.incorporator.direct_stable_route.pure_contracts.v1','Native_ticks':0,'DEE_imports':0,'all_source_pair_and_physical_objects_are_mocks':True,'actual_product_RP_or_S5_writes':False,'incorporator_sha256':sha(SRC),'same_source_stable_path_verified':str(pair),'stable_member_hash_checks_mock':check,'refusals':r,'Native_import_or_promotion_executed':False};write(OUT,record);print(json.dumps({'proof':str(OUT),'sha256':sha(OUT),'Native_ticks':0,'all_refusals':all(r.values())}))
