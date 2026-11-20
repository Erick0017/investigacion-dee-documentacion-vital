"""Auditor-only one-site insertion reconstructs the real input guard transition."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from core.entity import Entity,write_gate,observation,add,xyz,atomic_json
import dee_thinking as d
def main(root):
    path=root/'checkpoints/continuidad/BA_FULL/FIRST_READ.deetsnap';e=Entity.load(path);e._advance_to(163);spec=e.world.view('body').spec;inlet=d.Coordinate(*add(xyz(spec.a),(0,-1,0)));old=e.world.runtime.observe(inlet)
    assert old.record.state==0,'Frozen event was not present in the expected reference'
    baseline=e.world.fork();x=d.ResearchStateEdit();x.coordinate=inlet;x.raw=d.pack_record(1,0,0,0,-1,1);x.label='AUDITOR_ONLY_REAL_EVENT_RECONSTRUCTION';edited=e.world.diagnostic_fork([x],True)
    before={'baseline':write_gate(baseline.runtime,spec.a,True),'inserted_event':write_gate(edited.runtime,spec.a,True),'event_before':observation(old),'event_after':observation(edited.runtime.observe(inlet)),'clock_unchanged':edited.runtime.observe(inlet).clock==old.clock,'a_untouched':edited.runtime.observe(spec.a).raw==baseline.runtime.observe(spec.a).raw,'b_untouched':edited.runtime.observe(spec.b).raw==baseline.runtime.observe(spec.b).raw}
    baseline.advance();edited.advance();e._input('A',163,{'kind':'ACTUAL_PROTOCOL_RECEIPT_CONTROL'})
    def digest(w):
        from array import array
        import hashlib
        return {'tick':w.runtime.current_tick,'raw':hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest(),'clock':hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest()}
    b=digest(baseline);z=digest(edited);a=digest(e.world);historical_full=Entity.load(root/'checkpoints/continuidad/BA_FULL/T164.deetsnap');historical_no=Entity.load(root/'checkpoints/continuidad/BA_NO_NEW/T164.deetsnap')
    checks={'diagnostic_insertion_matches_actual_channel':z==a,'actual_matches_saved_FULL_cut':a==digest(historical_full.world),'no_event_matches_saved_NO_NEW_cut':b==digest(historical_no.world),'edit_excludes_A_B_and_clocks':before['a_untouched'] and before['b_untouched'] and before['clock_unchanged'],'ordinary_condition_before':before['baseline']['ordinary_increment_condition'],'ordinary_condition_after_insertion_false':not before['inserted_event']['ordinary_increment_condition']}
    out={'modality':'DIAGNOSTIC_FORK_AUDITOR_ONLY_NO_MERGE','reference_snapshot':str(path.relative_to(root)).replace('\\','/'),'tick':163,'edit':{'site':xyz(inlet),'fields':['RAW'],'old':old.raw,'new':x.raw,'s_reg':0,'direction':[0,0,-1],'state':1,'semantic':1,'new_ports':0},'gate':before,'after':{'baseline_A':observation(baseline.runtime.observe(spec.a)),'input_A':observation(edited.runtime.observe(spec.a)),'baseline_B':observation(baseline.runtime.observe(spec.b)),'input_B':observation(edited.runtime.observe(spec.b))},'digests':{'no_input':b,'diagnostic_inserted':z,'real_channel':a},'checks':checks,'inference_scope':'conditional inhibitory input effect at this state/phase; not a universal monotone learning rule; no edited state returned to MAIN'}
    atomic_json(root/'experimentos/continuidad/CAUSAL_GATE.json',out);print(json.dumps({'checks':checks,'baseline_gate':before['baseline'],'with_input_gate':before['inserted_event']},ensure_ascii=True));assert all(checks.values())
if __name__=='__main__':main(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT)
