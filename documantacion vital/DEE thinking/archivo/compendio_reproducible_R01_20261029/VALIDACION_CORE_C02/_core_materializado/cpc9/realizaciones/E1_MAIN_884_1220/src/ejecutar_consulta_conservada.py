"""Observe conserved query inhibition and causal social reference acquisition."""
from pathlib import Path
import argparse,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src')]
from consulta_conservada import PreservedQuerySession
from consulta_adquirida import move
from ejecutar_retorno import write
from integracion.relational_pair import physical
def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--local',default='unknown');p.add_argument('--remote',default='known')
    p.add_argument('--delay',type=int,default=0);p.add_argument('--remote-load',type=int,default=11);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False);started=time.monotonic();s=PreservedQuerySession.create();s.curriculum(a.local,a.remote,a.delay,remote_load=a.remote_load)
    r={'schema':'CPC9.query.preserved.measurements.v2','case_id':a.case,'configuration':vars(a)|{'out':str(a.out)},'geometry':s.geometry,
       'preparations':1,'MAIN_RAW_clock_edits':[],'frames':[],'windows':[],'snapshots':[],'source_sha256':hashlib.sha256((ROOT/'src/consulta_conservada.py').read_bytes()).hexdigest()}
    ticks={0,3,13,66,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,103,104,105,108,109,110,111,133,134,135,136,137,138,139,141,142,143,202,203,204,205,206,208,209,210,269,270,271,273,275,276,277,337,338,340,342,343,344,404,405,407,409,410,411,430}
    for tick in sorted({0}|{x+a.delay for x in ticks if x}):
        s.run_until(tick);r['frames'].append(s.view())
        relative=tick-a.delay
        if relative in(69,70,74,75,79,80,81,82,135,136,137,138,141,142,203,204,208,209,270,271,275,276):
            centers={'center':s.geometry['center'],'local':s.geometry['origin'],'gate':s.geometry['gate'],'B':s.geometry['B']}
            r['windows'].append({'tick':tick,'Moore27':{name:[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]for name,q in centers.items()}})
        if relative in(0,136,137,209,430):
            path=a.out/f'T{tick}.deetsnap.gz';storage=s.save(path);r['snapshots'].append({'path':path.name,'storage':storage,'physical':physical(s.world)})
        r.update(last_complete_tick=tick,requests=s.receipts());write(a.out/'MEDICIONES.json',r)
    r.update(status='MEASURED',final_physical=physical(s.world),elapsed_seconds=time.monotonic()-started);write(a.out/'MEDICIONES.json',r)
    print(json.dumps({'case':a.case,'gates':[{'tick':f['tick'],'active':f['gate']['active'],'load':f['gate']['s_reg'],'direction':f['gate']['direction']}for f in r['frames']if f['tick']-a.delay in s.geometry['question_ticks']]},ensure_ascii=False))
if __name__=='__main__':main()
