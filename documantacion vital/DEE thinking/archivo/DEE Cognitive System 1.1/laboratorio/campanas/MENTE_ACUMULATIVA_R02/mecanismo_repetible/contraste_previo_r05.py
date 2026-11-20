"""Zero-new-tick comparison of existing complete R04/R05 snapshots.
Identifies the pre-query effect of the three prepared closure sites. The new
contact path has not been used at these cuts, so cannot explain this contrast.
"""
import gzip,hashlib,json
from pathlib import Path
from dee_thinking.persistence import load_world_snapshot,decode_metadata
from dee_thinking.consolidated import exact_receipt,exact_observation
from dee_thinking import _native as d
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];EV=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA_R02/mecanismo_repetible';N=67
def load(name):
    p=EV/name;w,_=load_world_snapshot(p);return w,{'name':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'tick':int(w.runtime.current_tick)}
def rr(w):
    v=w.runtime.receipts;return[exact_receipt(x)for x in(v()if callable(v)else v)]
def comparison(oldname,newname,oldkey,newkey):
    a,ai=load(oldname);b,bi=load(newname);ar=a.runtime.raw_copy();br=b.runtime.raw_copy();ac=a.runtime.clock_copy();bc=b.runtime.clock_copy();diff=[]
    for i,(x,y,c,e)in enumerate(zip(ar,br,ac,bc)):
        if x!=y or c!=e:
            p=(i//(N*N),(i//N)%N,i%N);diff.append({'site':p,'old':exact_observation(a.runtime.observe(d.Coordinate(*p))),'new':exact_observation(b.runtime.observe(d.Coordinate(*p)))})
    am=decode_metadata(dict(a.runtime.snapshot_metadata_entries)[oldkey]);bm=decode_metadata(dict(b.runtime.snapshot_metadata_entries)[newkey]);receipts_equal=rr(a)==rr(b)
    return{'old':ai,'new':bi,'different_sites':diff,'RAW_differences':sum(x!=y for x,y in zip(ar,br)),'clock_differences':sum(x!=y for x,y in zip(ac,bc)),'physical_inputs_metadata_equal':am['requests']==bm['requests'],'runtime_receipts_equal':receipts_equal,'old_receipts':rr(a),'new_receipts':rr(b),'old_interface_count':len(a.interfaces),'new_interface_count':len(b.interfaces),'old_protocol_count':len(a.protocols),'new_protocol_count':len(b.protocols)}
def main():
    dest=EV/'MA02_R05_PREQUERY_CONTRAST.json.gz'
    if dest.exists():raise FileExistsError(dest)
    pairs=[comparison('MA02_P1_R04_GUARDED.T0.deetsnap.gz','MA02_P1_R05_GUARDED.T0.deetsnap.gz','MA02.P1.CYCLE.v1','MA02.P1.R05.v1'),comparison('MA02_P1_R04_GUARDED.T129.before_activation.deetsnap.gz','MA02_P1_R05_GUARDED.T129.deetsnap.gz','MA02.P1.CYCLE.v1','MA02.P1.R05.v1')]
    r={'schema':'MA02.R05.prequery_state_contrast.1','identifier':'MA02_R05_PREQUERY_CONTRAST','new_ticks':0,'comparisons':pairs,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Physical arrays, declared material inputs and actual receipts checked. Documentary identifiers/metadata intentionally differ. Before any action or rejection, only three prepared active closure sites differ atT0; the downstream pre-query difference is not a consequence-learning result.'}
    dest.write_bytes(gzip.compress(json.dumps(r,ensure_ascii=False,sort_keys=True).encode(),mtime=0));print(json.dumps({'comparisons':[{'oldtick':p['old']['tick'],'newtick':p['new']['tick'],'rawdiff':p['RAW_differences'],'clockdiff':p['clock_differences'],'inputs':p['physical_inputs_metadata_equal'],'receipts':p['runtime_receipts_equal']}for p in pairs]}))
if __name__=='__main__':main()
