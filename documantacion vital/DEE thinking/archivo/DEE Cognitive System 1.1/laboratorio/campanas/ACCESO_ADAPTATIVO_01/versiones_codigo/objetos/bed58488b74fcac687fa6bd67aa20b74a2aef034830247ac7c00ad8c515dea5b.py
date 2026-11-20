"""One native tick from an existing recorded prestate, diagnostic copies only.

No diagnostic future is imported into MAIN. RAW edits below are explicit
counterfactual instruments, not autonomous or admissible life actions.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path[:0]=[str(a.system),str(a.system.parent/'laboratorio/campanas/PAISAJE_CAUSAL_01')]
import dee_thinking as d
from dee_thinking.persistence import materialized_snapshot
from app.native_tools import physical,observe
from app.process_control import protect_current
from instrumentos_pc01 import witness,receipts,frame,sha,native_digest
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);source=a.system.parent/'evidencia/campanas/ACCESO_ADAPTATIVO_01/TRAZA_RETENCION_B_39/baseline/ANTES_DESVIO.native.gz'
with materialized_snapshot(source)as(path,storage):original=d.Runtime.load_snapshot(str(path))
target=[27,11,11];incoming=[27,11,12];w=SimpleNamespace(runtime=original);old=observe(w,target);edits=[]
if a.case!='none':
    edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*(incoming if a.case=='remove_incoming'else[40,24,24]if a.case=='sham_empty'else target));edit.raw=int(old['raw'])&~0xffffffff if a.case=='zero_state_only'else 0;edit.label='AA01_DIAGNOSTIC42_'+a.case;edits=[edit]
copy=original.diagnostic_fork(edits,True)if edits else original.fork();wc=SimpleNamespace(runtime=copy);data={'case':a.case,'scope':'One-tick native counterfactual, no owner-host continuation and no promotion into MAIN. Not a cognitive action.','source_sha256':sha(source),'source_code_sha256':sha(__file__),'storage':storage,'edited_sites':[{'site':[q.coordinate.x,q.coordinate.y,q.coordinate.z],'raw':str(q.raw),'clock':'UNCHANGED'}for q in edits],'pre':physical(wc),'pre_context':witness(wc,target),'pre_frame':frame(wc),'pre_receipts':receipts(copy)};copy.advance(1);data['post']=physical(wc);data['destination']=observe(wc,target);data['former_incoming_site']=observe(wc,incoming);data['post_frame']=frame(wc);data['post_receipts']=receipts(copy);data['original_unadvanced']=int(original.current_tick)==45028;(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'case':a.case,'destination':data['destination'],'original_unadvanced':data['original_unadvanced']}))
