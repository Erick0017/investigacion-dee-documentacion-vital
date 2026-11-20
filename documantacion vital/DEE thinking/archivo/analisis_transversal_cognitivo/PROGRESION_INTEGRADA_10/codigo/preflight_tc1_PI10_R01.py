"""Passive binary parser and finite engineering origin preflight; no DEE."""
from pathlib import Path
from datetime import datetime,timezone
import gzip,hashlib,importlib.util,json,struct
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0'
PAIR=P/'pares/PRINCIPAL_D_T922371';MF=PAIR/'EXPORTACION_SERVICIO.json';OUT=P/'control/PREFLIGHT_ORIGENES_TC1_PI10_R01.json'
ORIGINS=[(8,12,12),(24,12,12),(40,12,12),(54,12,12),(8,24,24),(24,24,24),(40,24,24),(54,24,24)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
need=lambda ok,why: None if ok else (_ for _ in()).throw(ValueError(why))
need(not OUT.exists(),'Prior preflight preserved')
mf=json.loads(MF.read_text('utf-8-sig'));snap=PAIR/mf['native_snapshot'];need(sha(snap)==mf['snapshot_sha256']=='72743ad2fc708e41c2529af8f7192fe1087184562e4cd094f469384faedcd331','Exact complete current source only')
passive=load('PI10_preserved_binary_reader',C/'reproducibilidad/observador_pasivo.py')
encoded=snap.read_bytes();b=gzip.decompress(encoded)if encoded[:2]==b'\x1f\x8b'else encoded;r=passive.Reader(b[:-8])
need(r.take(8)==b'DEETSNP1'and r.u32()==2,'DEETSNP1/v2 required')
n=r.u32();tick=r.u64();r.u8();r.u64();r.u64();phase=r.text();total=r.u64();need(n==67 and tick==922371 and total==n**3,'Exact main physical cut required')
raw=r.take(8*total);clocks=r.take(8*total)
need(hashlib.sha256(raw).hexdigest()==mf['physical']['RAW_sha256']and hashlib.sha256(clocks).hexdigest()==mf['physical']['clocks_sha256'],'Exact RAW+clock identity')
def signed4(v):return v-16 if v&8 else v
def lookup(site):
 x,y,z=site;i=(x*n+y)*n+z;v=struct.unpack_from('<Q',raw,8*i)[0];clock=struct.unpack_from('<Q',clocks,8*i)[0]
 return {'site':list(site),'raw':v,'clock':clock,'state':v&0xffffffff,'s_reg':(v>>32)&0xffff,
   'direction':[signed4((v>>s)&15)for s in(48,52,56)],'semantic':(v>>60)&15}
tcfile=C/'sistema/capacidades/pi03_credito_generico_R01_BORRADOR.py';geofile=H/'pi10_dos_trazas_legales_R01.py'
tc=load('PI10_preserved_pure_TC_geometry',tcfile);geometry=load('PI10_new_pure_q1_geometry',geofile)
old=[lookup(geometry.at(geometry.OLD_ORIGIN,d))for d in((-1,-1,0),(1,-1,0))]
rows=[]
for index,origin in enumerate(ORIGINS):
 check=geometry.passive_preflight(tc,origin,lookup)
 clocks1=check['reference_clocks'];clocks2=[q['clock']for q in old]
 check['declared_engineering_order']=index
 check['old_q2_reference_observations']=old
 check['old_q2_A_minus_B']=int(old[0]['s_reg'])-int(old[1]['s_reg'])
 check['old_q2_phase_equal']=clocks2[0]%782==clocks2[1]%782
 check['clock_offset_new_minus_old']=clocks1[0]-clocks2[0]
 check['predicted_calendar_from_exact_frozen_clocks']=geometry.two_selector_calendar(tick,clocks1[0],clocks2[0])
 rows.append(check)
value={'schema':'DEE.PI10.static_exact_prefix_origin_preflight.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),'Native_imported':False,'Native_executed':False,'new_ticks':0,
 'source_manifest':{'path':str(MF),'sha256':sha(MF)},'source_snapshot':{'path':str(snap),'sha256':sha(snap)},
 'physical':mf['physical'],'clock_and_raw_decode_source':'kernel_v27.cpp99–124 and139; x-major ((x*N)+y)*N+z, signed4 directions',
 'parser_scope':'Gzip CRC and exact source SHA/RAW/clocks; not a fresh Native run or FNV recalculation',
 'engineering_origin_order_declared_before_any_installation':[list(p)for p in ORIGINS],
 'helper_sources':[{'path':str(p),'sha256':sha(p)}for p in(tcfile,geofile)],'rows':rows,
 'first_eligible_origin':next((x['origin']for x in rows if x['eligible']and x['old_q2_phase_equal']),None),
 'conclusion_scope':'Whole RAW current-state clearance, local halo and periodic eligibility row, not measured future isolation or learned useful capacity.'}
OUT.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'file':str(OUT),'sha256':sha(OUT),'rows':[{'origin':x['origin'],'eligible':x['eligible'],'clocks':x['reference_clocks'],'old_clock':old[0]['clock'],'old_delta':x['old_q2_A_minus_B'],'q2_minus_q1':x['predicted_calendar_from_exact_frozen_clocks']['q2_minus_q1']}for x in rows],'first_eligible_origin':value['first_eligible_origin'],'Native_executed':False}))
