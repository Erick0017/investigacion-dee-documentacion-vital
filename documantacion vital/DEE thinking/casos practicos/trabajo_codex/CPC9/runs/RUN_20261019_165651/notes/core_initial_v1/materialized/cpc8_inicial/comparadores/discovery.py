"""Small disclosed K8 discovery only; freezes reserved configuration before runs."""
from pathlib import Path
import hashlib,json,random,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from models import ReplayMLP

BASE=Path(__file__).resolve().parent
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    if (BASE/"FROZEN_CONFIG.json").exists():raise FileExistsError("Discovery/config already frozen")
    rng=random.Random(816042);labels=[rng.choice((-1,1)) for _ in range(8)];rows=[]
    for updates in (64,256):
        t=time.perf_counter();m=ReplayMLP(count=65,seed=816043,updates=updates)
        for i,y in enumerate(labels):m.experience(i,y)
        before=[m.query(i)["value"] for i in range(8)]
        revised=labels[:];revised[0]*=-1;m.experience(0,revised[0])
        after=[m.query(i)["value"] for i in range(8)]
        rows.append({"updates":updates,"labels":labels,"before":before,"after":after,"new_labels":revised,
          "errors_before":sum(a!=b for a,b in zip(before,labels)),"errors_after":sum(a!=b for a,b in zip(after,revised)),
          "wall_seconds":time.perf_counter()-t,"replay_presentations":m.replay_presentations})
    write(BASE/"DISCOVERY_K8.json",{"scope":"Discovery; not reserved worlds","candidates":rows,
      "choice":"256 finite presentations/event chosen in advance for retention margin, if K8 both stages have zero errors. Not tuned on reserved K65."})
    chosen=rows[-1]
    if chosen["errors_before"] or chosen["errors_after"]:raise AssertionError("K8 discovery prerequisite not met; keep attempts")
    config={"schema":1,"scope":"Opaque formID -> observed directional class, NOT 65 semantic meanings",
      "count":65,"dimension":131,"native_backend":"LAZY","native_threads":1,"reserved_seeds":[402817,591307],
      "blocks":[{"start":0,"stop":8,"experience_tick":0,"panel_tick":131},
        {"start":8,"stop":16,"experience_tick":262,"panel_tick":393},
        {"start":16,"stop":32,"experience_tick":524,"panel_tick":655},
        {"start":32,"stop":65,"experience_tick":786,"panel_tick":917}],
      "revision":{"form":0,"tick":1048,"panel_tick":1179,"method":"symmetric_counterflow"},
      "restored_panel_tick":1310,"query_payload":5,"mlp":{"hidden":24,"updates":256,"learning_rate":.08},
      "criterion":{"acquisition":"first physical/algorithmic response for newly experienced forms equals latest observed direction",
        "retention":"response for previously acquired forms after later experience, without re-teaching that form",
        "revision":"same form receives opposite current observation; revised form and unchanged forms assessed separately",
        "missing":"None/rejected/uncovered remains distinct from wrong numeric prediction",
        "denominator":"queries, with per-world/seed results; ticks are not independent samples"},
      "information_policy":"Participants receive only past/current explicit experience(form,observation) and query(form); evaluator labels never passed to query.",
      "inequivalence":["DEE queries are physical consumable inputs and advance ticks; conventional query forward passes do not change stored knowledge.",
        "DEE geometry and revision route are prepared; MLP architecture/optimizer/replay and dictionary update are prepared algorithms.",
        "DEE has 2 physical training inputs/observation and 4 for revision; conventional event is one example and replay has separately counted cost.",
        "No comparison of universal intelligence or energy efficiency; process memory and portable state size are different quantities."],
      "source_hashes":{p.name:sha(p) for p in (BASE/"models.py",BASE/"discovery.py",BASE/"run_comparison.py")}}
    write(BASE/"FROZEN_CONFIG.json",config)
    print(json.dumps({"discovery":rows,"frozen_config_sha256":sha(BASE/"FROZEN_CONFIG.json")}))
if __name__=="__main__":main()
