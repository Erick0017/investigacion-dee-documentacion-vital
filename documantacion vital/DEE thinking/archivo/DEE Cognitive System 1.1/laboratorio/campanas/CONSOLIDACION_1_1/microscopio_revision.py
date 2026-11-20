from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store,load_adapter
from app.native_tools import physical,observe,moore27,atomic_json,digest_file
from app.process_control import protect_current,current_resources
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();protect_current();a.out.mkdir(parents=True,exist_ok=False);store=Store();rows=[]
    for life in('R65_REVISION_11','R65_SHAM_11_R2'):
        history=[json.loads(x)for x in(store.life_dir(life)/'HISTORIA.jsonl').read_text(encoding='utf8').splitlines()];entry=next(x for x in history if x['operation']['kind']=='EXPERIENCE_revision-fisica');snap=next(p for p in(store.state/'checkpoints').glob(life+'.T792.*.gz')if digest_file(p)==entry['snapshot_sha256']);s=load_adapter('repertorio_fisico_4_5',snap);s.schedule_query(['L%02d'%i for i in range(2,33)],917,payload=5);hub=s.preparation.forms[0].hub;hub=[hub.x,hub.y,hub.z];shub=s.preparation.forms[5].hub;shub=[shub.x,shub.y,shub.z];frames=[]
        for t in(916,917,918,919,920,921,923):
            s.run_until(t);frames.append({'tick':t,'L01_Moore27':moore27(s.world,hub),'L01':observe(s.world,hub),'L06':observe(s.world,shub),'physical':physical(s.world)})
        actual_entry=next(x for x in history if x['operation']['kind']=='MATERIAL_QUERY'and x['tick']==920);actual_path=next(p for p in(store.state/'checkpoints').glob(life+'.T920.*.gz')if digest_file(p)==actual_entry['snapshot_sha256']);actual=load_adapter('repertorio_fisico_4_5',actual_path);ph=next(f['physical']for f in frames if f['tick']==920);actualph=physical(actual.world);rows.append({'life':life,'source_snapshot':snap.relative_to(ROOT).as_posix(),'source_sha256':digest_file(snap),'actual920_snapshot_sha256':digest_file(actual_path),'full920_replay_equal':ph==actualph,'frames':frames,'scope':'Exactreplayofqueuedpreparedteacherinputs and the actual31neighborformprobes. Offpathpublishedsham is at+10Zand can act onL06; do not assume it is globallyinert.'})
    atomic_json(a.out/'MICRO_REVISION.json',{'schema':'DCS1.1.revision.microscope.r1','cases':rows,'resources':current_resources(),'RAW_clock_edits':[]});print(json.dumps({'cases':len(rows),'all920equal':all(x['full920_replay_equal']for x in rows)}))
if __name__=='__main__':main()
