"""R03 prospective actuator clearance over one closed exact R02 snapshot.

Pure standard-library snapshot reads. No engine, Runtime, SQLite or code edits.
"""
from pathlib import Path
import datetime, hashlib, importlib.abc, json, runpy


class BlockDEE(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split('.')[0]in{'dee_thinking','app','capacidades','_native','numpy'}:
            raise RuntimeError('No executable/DEE imports: '+fullname)
        return None


def sha(b):return hashlib.sha256(b).hexdigest()


def main():
    p7=Path(__file__).resolve().parents[1];atc=p7.parent
    out=p7/'control/PREFLIGHT_ACTUADOR57_PI07_R03_R01.json'
    if out.exists():raise FileExistsError(out)
    primary=p7/'ensayos/PI07_RESERVA_A_R02_EP11.json';pb=primary.read_bytes();p=json.loads(pb)
    if p['status']!='completed':raise ValueError('Closed completed primary required')
    outer=json.loads(p['result']);saved=outer['committed_snapshot']
    if saved['physical']['tick']!=834005:raise ValueError('Only declared pre-revision stable cut')
    snapshot=p7/'estados/candidato/sistema'/saved['snapshot'];before=snapshot.read_bytes()
    if sha(before)!='7c86a24b973958042ebee395dc06e3c85dbfce4f771737986dd0ed2aaaf38e83':
        raise ValueError('Unexpected exact stable source hash')
    sysmod=__import__('sys');sysmod.meta_path.insert(0,BlockDEE())
    parser=atc/'PROGRESION_INTEGRADA_05/codigo/contrastar_prefijos_C2C_PI05_pasivo.py'
    reader=runpy.run_path(str(parser),run_name='passive_only')
    public,raw,clocks,*_=reader['parse'](snapshot,sha(before))
    def obs(site):
        i=(site[0]*67+site[1])*67+site[2]
        return{'site':list(site),'clock':str(clocks[i]),**reader['decode'](int(raw[i]))}
    sites={'actor_message':(52,48,57),'message_reader':(53,48,57),
           'new_fixed_sink':(55,48,57),'old_actor_preserved':(52,48,51),
           'sensor_preserved':(52,48,47),'threat_source_preserved':(52,48,46),
           'conditional_old_before_contact':(52,48,55),'conditional_contact':(52,48,56),
           'old_FI_parent':(52,48,58)}
    named={k:obs(site)for k,site in sites.items()}
    halo=[obs((55+x,48+y,57+z))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]
    nonzero=[row for row in halo if int(row['RAW'])!=0]
    lane=[obs((52,48,z))for z in range(67)]
    row={'schema':'DEE.PI07.R03.fixed_actor57.passive_clearance.v1',
         'inspection_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'Native_ticks':0,'DEE_imports':0,'SQLite_opened':False,
         'primary':{'path':str(primary.resolve()),'sha256':sha(pb)},
         'snapshot':{'path':str(snapshot.resolve()),'bytes':len(before),'sha256':sha(before)},
         'physical':public['physical'],'pending_count':public['pending_count'],
         'named_sites':named,'sink_Moore_halo27_nonzero_RAW':nonzero,
         'lane52_48_all67_nonzero_RAW':[r for r in lane if int(r['RAW'])!=0],
         'new_sink_current_RAW0':int(named['new_fixed_sink']['RAW'])==0,
         'new_actor_current_RAW0':int(named['actor_message']['RAW'])==0,
         'reader_current_RAW0':int(named['message_reader']['RAW'])==0,
         'conditional_new_phase_prediction':{'sensor':'S=qsel-1 atz47, actual+Z only',
              'birth':'qsel+7=S+8, atz57 withold+Znominalz55',
              'contact':'S+9, z56 ifvacantandonlythesetwosources',
              'scope':'Prospective source-algebra prediction; not a measured Native contact or remedy.',
              'message':'same actor site+X; fixed reader53,48,57 atbirth+1; sink55,48,57 atbirth+3'},
         'preservation':'R01/R02 sources, oldactor51,oldkeys,banksandoriginalsnapshotsuntouched.',
         'current_clearance_not_future_guarantee':True,
         'parser_sha256':sha(parser.read_bytes()),'script_sha256':sha(Path(__file__).read_bytes())}
    after=snapshot.read_bytes()
    if sha(after)!=sha(before)or primary.read_bytes()!=pb:raise ValueError('Frozen source changed')
    row['source_unchanged_before_after']=True
    data=(json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    if len(data)>10000:raise ValueError('Proof size exceeds bounded10k')
    out.write_bytes(data)
    print(json.dumps({'proof':str(out),'bytes':len(data),'sha256':sha(data),
                      'new_sink_RAW0':row['new_sink_current_RAW0'],
                      'actor_RAW0':row['new_actor_current_RAW0'],
                      'reader_RAW0':row['reader_current_RAW0'],
                      'sink_halo_nonzero':nonzero,'Native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
