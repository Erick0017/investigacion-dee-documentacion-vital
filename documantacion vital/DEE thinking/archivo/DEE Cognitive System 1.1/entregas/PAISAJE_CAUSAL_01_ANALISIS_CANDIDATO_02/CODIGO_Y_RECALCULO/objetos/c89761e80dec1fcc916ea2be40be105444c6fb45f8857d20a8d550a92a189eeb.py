"""Explicit one-tick research-state edits on native diagnostic copies only.

NOT a continuation of a normal E1session, NOT an autonomous cleaning action.
Clocks, all other fields and the complete pending queue are preserved.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
import dee_thinking as d
from dee_thinking.persistence import materialized_snapshot
from app.native_tools import physical,observe
from app.process_control import protect_current
from instrumentos_pc01 import native_digest,witness,receipts,sha
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);source=a.system.parent/'evidencia/campanas/PAISAJE_CAUSAL_01/ACCESO_TRAYECTO_LIBRE_19/trace_events/PRE_SNAPSHOT_NATIVE_DIAGNOSTIC_ONLY.deetsnap.gz'
with materialized_snapshot(source)as(p,proof):original=d.Runtime.load_snapshot(str(p))
base=original.fork();edits=[]
for label,site in(('free',[60,0,21]),('counter',[59,1,20])):
    if a.case in('remove_'+label,'remove_both'):
        edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.raw=0;edit.label='PC01.DIAGNOSTIC_ONLY_REMOVE_'+label;edits.append(edit)
if a.case=='sham_empty':
    edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(59,10,20);edit.raw=0;edit.label='PC01.DIAGNOSTIC_SHAM_ALREADY_RAW_ZERO';edits.append(edit)
copy=original.diagnostic_fork(edits,True)if edits else original.fork();wb=SimpleNamespace(runtime=base);wc=SimpleNamespace(runtime=copy)
def diffs(a,b):
    ar=a.raw_copy();br=b.raw_copy();ac=a.clock_copy();bc=b.clock_copy()
    return{'RAW_different_sites':sum(x!=y for x,y in zip(ar,br)),'clock_different_sites':sum(x!=y for x,y in zip(ac,bc))}
data={'case':a.case,'identity':'PC01_NATIVE_DIAGNOSTIC22_'+a.case,'source':str(source),'source_sha256':sha(source),'source_native_storage':proof,'scope':'Complete nativeRTdiagnosticcopyforone-tickcausaltest, not advertisedasnormalE1sessionwiththepausedPythonprotocol','source_sha256_code':sha(__file__),'pre_base':physical(wb),'pre_copy':physical(wc),'pre_differences':diffs(base,copy),'pre_context':witness(wc,[59,1,20],3),'edits':[{'site':[int(e.coordinate.x),int(e.coordinate.y),int(e.coordinate.z)],'raw':'0','clock':'UNCHANGED','label':e.label}for e in edits]}
base.advance(1);copy.advance(1);data['post_base']=physical(wb);data['post_copy']=physical(wc);data['post_differences']=diffs(base,copy);data['post_free_destination']=observe(wc,[59,1,20]);data['post_receipts_equal']=receipts(base)==receipts(copy)
for rt in(base,copy):
    for key in('dee_thinking.diagnostic_fork','dee_thinking.diagnostic_edit_count'):rt.erase_snapshot_metadata(key)
data['post_all_native_except_only_diagnostic_labels_equal']=native_digest(base)==native_digest(copy);data['original_pre_unchanged']=int(original.current_tick)==26165
(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:data[k]for k in('case','pre_differences','post_differences','post_free_destination','post_receipts_equal','post_all_native_except_only_diagnostic_labels_equal')}))
