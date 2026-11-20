"""Small installed4.5 physical correspondence example, not semantic dialogue."""
from pathlib import Path
from array import array
import argparse,hashlib,json
from dee_thinking.consolidated import RepertoireSession
def physical(s):
 r=s.world.runtime;return{'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 s=RepertoireSession.create(count=2,identifier='CORE_EXAMPLE_FRESH');initial=physical(s)
 # Declared external paired teaching, not a participant lookup table.
 s.acquire_block({'L01':1,'L02':-1},0);first=s.query(['L01','L02'],67)
 snapshot=a.out/'CONTINUIDAD.deetsnap.gz';s.save(snapshot,compress=True)
 other=RepertoireSession.load(snapshot);before_equal=physical(s)==physical(other)
 next_a=s.query(['L01','L02'],134);next_b=other.query(['L01','L02'],134)
 result={'instrument':'DEE thinking4.5.0','meaning_scope':'Two opaque form/direction correspondences only','initial_prepared_not_target_trained':initial,'ENTE_first':first,'ENTE_after_restore':next_b,'restored_physical_before_equal':before_equal,'continued_physical_equal':physical(s)==physical(other),'new_query_observations_equal':next_a==next_b,'final':physical(s),'INSTRUMENTO':'Two real paired exposures; same finite query cadence and no host RAW/clock edits'}
 (a.out/'OBSERVACIONES.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result,ensure_ascii=False))
 assert before_equal and result['continued_physical_equal']and result['new_query_observations_equal']
if __name__=='__main__':main()
