"""One minimal current-outcome integration before freezing confirmatory tests."""
import argparse,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.common import identity,put
from src.experiment import run_case
def main():
    p=argparse.ArgumentParser();p.add_argument('--wheel',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert not a.output.exists();start=time.monotonic();ident=identity(a.wheel)
    result=run_case({'id':'ACTUAL_SENSOR_A_DISCOVERY','type':'DISCOVERY','pairing':{'S1':'U','S2':'V'},'future_events':{'S1':'U','S2':'V'}},a.output)
    put(a.output/'IDENTITY.json',ident);put(a.output/'ELAPSED.json',{'seconds':time.monotonic()-start})
    print([(x['signal'],x['anticipation']['emission']['anticipated_class'],x['evaluation']['profile']) for x in result['uses']])
if __name__=='__main__':main()
