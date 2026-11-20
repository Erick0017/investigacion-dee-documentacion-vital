"""New query experiments. All scoring happens after the native trajectory."""
from pathlib import Path
import argparse,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src')]
from consulta_adquirida import QuerySession,move
from ejecutar_retorno import write
from integracion.relational_pair import physical
def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--local',default='unknown');p.add_argument('--remote',default='known')
    p.add_argument('--delay',type=int,default=0);p.add_argument('--remote-load',type=int,default=11);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    s=QuerySession.create();s.curriculum(a.local,a.remote,a.delay,remote_load=a.remote_load)
    r={'schema':'CPC9.query.measurements.v1','case_id':a.case,'configuration':vars(a)|{'out':str(a.out)},'geometry':s.geometry,
       'preparations':1,'MAIN_RAW_clock_edits':[],'frames':[],'windows':[],'snapshots':[],'source_sha256':hashlib.sha256((ROOT/'src/consulta_adquirida.py').read_bytes()).hexdigest()}
    ticks={0,3,14,67,69,70,73,75,76,77,78,79,80,81,82,83,84,85,91,92,93,107,108,109,113,114,115,133,134,135,136,137,138,142,143,144,201,203,204,209,210,211,268,270,271,276,277,278,300}
    for tick in sorted({0}|{t+a.delay for t in ticks if t}):
        s.run_until(tick);r['frames'].append(s.view())
        relative=tick-a.delay
        if relative in(69,70,75,76,80,81,83,84,133,134,135,136,137,142,143,203,204,209,210):
            r['windows'].append({'tick':tick,'Moore27':{name:[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]for name,site in(('local',s.geometry['origin']),('gate',s.geometry['gate']),('B',s.geometry['B']))}})
        if relative in(0,136,137,210,300):
            path=a.out/f'T{tick}.deetsnap.gz';storage=s.save(path);r['snapshots'].append({'path':path.name,'storage':storage,'physical':physical(s.world)})
        r.update(last_complete_tick=tick,requests=s.receipts());write(a.out/'MEDICIONES.json',r)
    r.update(status='MEASURED',final_physical=physical(s.world),elapsed_seconds=time.monotonic()-start)
    write(a.out/'MEDICIONES.json',r)
    print(json.dumps({'case':a.case,'gates':[{'tick':f['tick'],'active':f['gate']['active'],'s_reg':f['gate']['s_reg'],'direction':f['gate']['direction']}for f in r['frames']if f['tick']-a.delay in(76,143,210,277)]},ensure_ascii=False))
if __name__=='__main__':main()
