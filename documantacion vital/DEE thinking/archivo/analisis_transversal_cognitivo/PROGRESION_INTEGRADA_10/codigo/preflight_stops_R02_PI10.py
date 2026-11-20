"""Fixed R02 two-stop frozen-prefix preflight. No DEE/Native."""
from pathlib import Path
import gzip,hashlib,importlib.util,json,struct,types
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';PAIR=P/'pares/P0_COMUN_T922374';OUT=P/'control/PREFLIGHT_DOS_STOPS_R02_PI10.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 if OUT.exists():raise ValueError('Prior preflight preserved')
 mf=PAIR/'EXPORTACION_SERVICIO.json';v=json.loads(mf.read_text('utf8'));snap=PAIR/v['native_snapshot'];encoded=snap.read_bytes()
 assert sha(encoded)==v['snapshot_sha256']=='63940ed9c1573eb8660dbbf82ead8e7a58f7a87c691b2ac6069b388dd6582277'
 passive=load('PI10_R02_source_binary_reader',C/'reproducibilidad/observador_pasivo.py');r=passive.Reader(gzip.decompress(encoded)[:-8])
 assert r.take(8)==b'DEETSNP1'and r.u32()==2
 n=r.u32();tick=r.u64();r.u8();r.u64();r.u64();r.text();total=r.u64();assert(n,tick,total)==(67,922374,67**3)
 raw=r.take(8*total);clocks=r.take(8*total);assert sha(raw)==v['physical']['RAW_sha256']and sha(clocks)==v['physical']['clocks_sha256']
 def lookup(a,site):
  x,y,z=site;i=(x*n+y)*n+z;word=struct.unpack_from('<Q',raw,i*8)[0];ds=[(word>>s)&15 for s in(48,52,56)]
  return {'site':list(site),'tick':tick,'raw':word,'clock':struct.unpack_from('<Q',clocks,i*8)[0],'state':word&0xffffffff,'s_reg':(word>>32)&65535,'semantic':word>>60,'direction':[d-16 if d&8 else d for d in ds]}
 module_path=P/'codigo/pi10_consulta_adaptativa_R02.py';module=load('PI10_R02_fixed_stops_pure_actor',module_path);module.observe=lookup;check=module.stop_preflight(types.SimpleNamespace(tick=tick))
 assert check['eligible']and check['new_stops']==[[30,40,32],[32,40,32]]
 view=passive.snapshot_view(snap);parent=json.loads(view['metadata'][module.OLD_PI10_KEY]);assert parent['ready']is True and parent['admitted']is False and parent['ordinal']==0 and parent['rows']==[]
 out={'schema':'DEE.PI10.R02.frozen_two_postread_stop_preflight.R01','Native_imported':False,'new_ticks':0,'source_manifest':{'path':str(mf),'sha256':sha(mf.read_bytes())},'source_snapshot_sha256':sha(encoded),'physical':v['physical'],'actor_sha256':sha(module_path.read_bytes()),'preflight':check,'inherited_R01_key_sha256':sha(view['metadata'][module.OLD_PI10_KEY].encode('utf8')),'inherited_R01_ready_unadmitted_ordinal0':True,'old_sink36':lookup(None,(36,40,30)),'scope':'Frozen source only; no Native stop birth, no predicted safety/efficacy, no old state or clock edit.'}
 assert snap.read_bytes()==encoded
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'file':str(OUT),'sha256':sha(OUT.read_bytes()),'eligible':check['eligible'],'sites':check['checked_sites'],'actor_sha256':out['actor_sha256']}))
if __name__=='__main__':main()
