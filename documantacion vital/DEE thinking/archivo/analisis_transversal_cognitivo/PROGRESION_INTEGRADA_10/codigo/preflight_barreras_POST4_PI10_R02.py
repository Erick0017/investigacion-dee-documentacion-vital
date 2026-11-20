"""Passive four-point cut/sham preflight from exact closed REAL2 POST4.

No Native imports. Report all inactive RAW fields in halo; do not silently
call an installed SEM4 stop empty. Straight prepared paths are declared
engineering predictions, not newly measured trajectories or sham passivity.
"""
from pathlib import Path
import gzip,hashlib,importlib.util,itertools,json,struct
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';PAIR=P/'pares/REAL2_4_T928627';OUT=P/'control/PREFLIGHT_CUT_SHAM_POST4_PI10_R02.json';ORIGIN=(24,12,12)
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 if OUT.exists():raise ValueError('Preserve prior preflight')
 mf=PAIR/'EXPORTACION_SERVICIO.json';v=json.loads(mf.read_text('utf8'));assert sha(mf.read_bytes())=='b0b993e4f3732b3c5f59c9af778d2272b6438978282406a11e5923b181e52f47'
 snap=PAIR/v['native_snapshot'];encoded=snap.read_bytes();assert sha(encoded)==v['snapshot_sha256']
 path=C/'reproducibilidad/observador_pasivo.py';sp=importlib.util.spec_from_file_location('PI10_POST4_safe_reader',path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);r=m.Reader(gzip.decompress(encoded)[:-8]);assert r.take(8)==b'DEETSNP1'and r.u32()==2
 n=r.u32();tick=r.u64();r.u8();r.u64();r.u64();r.text();total=r.u64();assert(n,tick,total)==(67,928627,67**3)
 raw=r.take(8*total);clocks=r.take(8*total);assert sha(raw)==v['physical']['RAW_sha256']and sha(clocks)==v['physical']['clocks_sha256']
 def at(d):return tuple((ORIGIN[k]+d[k])%67 for k in range(3))
 def observe(site):
  x,y,z=site;i=(x*n+y)*n+z;word=struct.unpack_from('<Q',raw,i*8)[0];ds=[(word>>s)&15 for s in(48,52,56)]
  return {'site':list(site),'raw':word,'clock':struct.unpack_from('<Q',clocks,i*8)[0],'state':word&0xffffffff,'s_reg':(word>>32)&65535,'semantic':word>>60,'direction':[d-16 if d&8 else d for d in ds]}
 offsets={'cut':[(-4,-1,-2),(4,-1,-2)],'sham':[(-4,2,-2),(4,2,-2)]};rows={}
 for name,ds in offsets.items():
  targets=[at(d)for d in ds];halo={tuple((s[k]+d[k])%67 for k in range(3))for s in targets for d in itertools.product((-1,0,1),repeat=3)}
  obs=[observe(s)for s in sorted(halo)];rows[name]={'targets':[observe(s)for s in targets],'all_target_RAW0':all(observe(s)['raw']==0 for s in targets),'halo_sites':len(obs),'halo_nonzero_RAW':[o for o in obs if o['raw']!=0]}
 # Only direct prepared inputs/reader-output rays; not a measured trajectory.
 query=[at((0,0,-3+t))for t in range(8)]
 supports=[at((-2+t,1,-2+t))for t in range(8)]+[at((2-t,4-t,0))for t in range(8)]
 outputs=[at((dx*t,t,z*t))for dx in(-1,0,1)for z in(-1,0)for t in range(4)]
 sham={at(d)for d in offsets['sham']};predicted=set(query+supports+outputs)
 out={'schema':'DEE.PI10.closed_POST4_fixed_cut_sham_preflight.R02','Native_imported':False,'new_ticks':0,'source_manifest':{'path':str(mf),'sha256':sha(mf.read_bytes())},'snapshot_sha256':sha(encoded),'physical':v['physical'],'origin':list(ORIGIN),'preflight':rows,
  'sham_direct_prepared_query_support_read_rays_intersection':[list(s)for s in sorted(sham&predicted)],
  'geometry_scope':'Fixed straight input rays and output dx=-1/0/+1,z=-1/0 to local step3 stops. This checks declared coordinates, not native whole-path ancestry, material sham inertness or all future interactions.',
  'timing_scope':'Both symmetric births are prescribed seed+2, after first central readq+4/efference seedq+7 and question-signature readq+8. They do not select a side from the observed answer. Future affected episodes still require actual receipt/read controls.',
  'inactive_field_scope':'Target RAW0 is required. Known SEM4 fields in a halo are reported and never cleared; all-halo-empty must not be claimed if any is listed.'}
 assert snap.read_bytes()==encoded
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'file':str(OUT),'sha256':sha(OUT.read_bytes()),'cut':rows['cut'],'sham':rows['sham'],'sham_direct_path_intersection':out['sham_direct_prepared_query_support_read_rays_intersection']}))
if __name__=='__main__':main()
