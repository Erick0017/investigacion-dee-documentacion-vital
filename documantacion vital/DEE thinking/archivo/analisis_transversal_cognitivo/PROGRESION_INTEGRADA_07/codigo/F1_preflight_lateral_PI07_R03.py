"""Read a Root-selected immutable actual checkpoint; no future-cut invention."""
from pathlib import Path
import argparse,datetime,hashlib,importlib.abc,json,runpy,sys


class NoDEE(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split('.')[0]in{'dee_thinking','app','capacidades','_native','numpy'}:
            raise RuntimeError('No executable imports: '+fullname)
        return None


def sha(b):return hashlib.sha256(b).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--primario',type=Path,required=True)
    ap.add_argument('--tick',type=int,required=True);ap.add_argument('--salida',type=Path,required=True)
    args=ap.parse_args();p7=Path(__file__).resolve().parents[1]
    primary=args.primario.resolve(strict=True);out=args.salida.resolve()
    if not primary.is_relative_to(p7/'ensayos')or not out.is_relative_to(p7/'control'):
        raise ValueError('Only actual PI07 primary and new PI07 control destination')
    if out.exists():raise FileExistsError(out)
    pb=primary.read_bytes();p=json.loads(pb)
    if p.get('status')!='completed':raise ValueError('Actual completed primary required')
    outer=json.loads(p['result'])if isinstance(p['result'],str)else p['result']
    c=outer['committed_snapshot']
    if c['life_id']!='ECI02_PI03_REPRO_PI04_PI05_PI07_CAND_01'or c['physical']['tick']!=args.tick:
        raise ValueError('Declared candidate lineage and actual saved cut mismatch')
    system=p7/'estados/candidato/sistema';snapshot=(system/c['snapshot']).resolve(strict=True)
    if not snapshot.is_relative_to(system.resolve()):raise ValueError('Snapshot escape')
    b=snapshot.read_bytes()
    if sha(b)!=c['snapshot_sha256']:raise ValueError('Exact actual checkpoint hash mismatch')
    sys.meta_path.insert(0,NoDEE())
    source=p7.parent/'PROGRESION_INTEGRADA_05/codigo/contrastar_prefijos_C2C_PI05_pasivo.py'
    module=runpy.run_path(str(source),run_name='pure_frozen_parser')
    public,raw,clock,*_=module['parse'](snapshot,sha(b))
    if public['physical']['tick']!=args.tick:raise ValueError('Physical snapshot tick mismatch')
    def obs(site):
        i=(site[0]*67+site[1])*67+site[2]
        return{'site':list(site),'clock':str(clock[i]),**module['decode'](int(raw[i]))}
    sites={'fixed_lateral_actor_and_message':(53,48,56),'message_reader_Bplus1':(54,48,56),
      'new_sink':(56,48,56),'conditional_contact':(52,48,56),
      'old_new_cue_at_birth_if_uninterrupted':(52,48,55),'possible_old_residue':(52,48,57),
      'FI_parent':(52,48,58),'sensor':(52,48,47),'environment_source':(52,48,46)}
    named={key:obs(site)for key,site in sites.items()}
    def halo(center):
        return[obs((center[0]+x,center[1]+y,center[2]+z))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]
    sinkhalo=halo(sites['new_sink']);actorhalo=halo(sites['fixed_lateral_actor_and_message'])
    lane=[obs((52,48,z))for z in range(67)]
    result={'schema':'DEE.PI07.final_lateral_R03.actual_frozen_preflight.v1',
      'inspection_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'Native_ticks':0,'DEE_imports':0,'SQLite_opened':False,
      'primary':{'path':str(primary),'sha256':sha(pb)},
      'snapshot':{'path':str(snapshot),'bytes':len(b),'sha256':sha(b)},
      'physical':public['physical'],'pending_count':public['pending_count'],
      'named_sites':named,
      'sink_halo27_nonzero_RAW':[x for x in sinkhalo if int(x['RAW'])!=0],
      'actor_halo27_nonzero_RAW':[x for x in actorhalo if int(x['RAW'])!=0],
      'lane52_48_all67_nonzero_RAW':[x for x in lane if int(x['RAW'])!=0],
      'new_sink_and_halo_RAW0':all(int(x['RAW'])==0 for x in sinkhalo),
      'actor_RAW0_now':int(named['fixed_lateral_actor_and_message']['RAW'])==0,
      'reader_RAW0_now':int(named['message_reader_Bplus1']['RAW'])==0,
      'scope':'Actual immutable checkpoint selected by Root, not an instant observation of a live owner. Current RAW clearance is not future admission or functional efficacy. No kernel/life/product edit; new sink only through a later legal Native P0 operation if admitted.',
      'source_parser_sha256':sha(source.read_bytes()),'script_sha256':sha(Path(__file__).read_bytes())}
    if snapshot.read_bytes()!=b or primary.read_bytes()!=pb:raise ValueError('Frozen source changed')
    result['source_unchanged_before_after']=True
    encoded=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    if len(encoded)>12000:raise ValueError('Bounded proof exceeds12k')
    out.write_bytes(encoded)
    print(json.dumps({'proof':str(out),'bytes':len(encoded),'sha256':sha(encoded),
      'sink_and_halo_RAW0':result['new_sink_and_halo_RAW0'],
      'actor_RAW0':result['actor_RAW0_now'],'reader_RAW0':result['reader_RAW0_now'],
      'actual_tick':args.tick,'Native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
