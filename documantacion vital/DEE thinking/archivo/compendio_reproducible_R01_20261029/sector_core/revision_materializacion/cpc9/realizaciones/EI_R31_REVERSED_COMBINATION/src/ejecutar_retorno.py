"""Execute a new one-Runtime trajectory; evaluate only after observations."""
from pathlib import Path
import argparse,hashlib,json,sys,time,traceback
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src')]
from retorno_social import ReturnSession
from integracion.relational_pair import physical,move


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.pending')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # A short-lived external reader can prevent Windows replacement. Two
    # bounded retries affect only telemetry publication, never native state.
    for attempt in range(3):
        try:
            temp.replace(path)
            break
        except PermissionError:
            if attempt==2:raise
            time.sleep((0.05,0.20)[attempt])


def minimal_view(s):
    v=s.view()
    return {'tick':s.tick,'physical':physical(s.world),
            'quantity':{k:v['quantity'].get(k)for k in ('center','reference','object','reference_hub')},
            'magnitude_transfer':v['magnitude_transfer'],'joint':v['joint'],
            'common_join':v['common_join'],'contact_social':v['contact_social'],
            'return':s.return_view()}


def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--source',type=int,default=31)
    p.add_argument('--first-object',type=int,default=18);p.add_argument('--form',default='paired')
    p.add_argument('--no-query',action='store_true');p.add_argument('--out',required=True,type=Path)
    p.add_argument('--until',type=int,default=616);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    r={'schema':'CPC9.return.measurements.v1','case_id':a.case,'config':vars(a)|{'out':str(a.out)},
       'preparations':0,'frames':[],'decisive_local':[],'snapshots':[],
       'MAIN_RAW_clock_edits':[],'source_hashes':{},'status':'RUNNING'}
    for path in [ROOT/'src/retorno_social.py',Path(__file__),*sorted((ROOT/'base_validada/cpc8/src').rglob('*.py'))]:
        r['source_hashes'][str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    try:
        s=ReturnSession.create(identifier=a.case)
        r.update(preparations=1,geometry=s.geometry)
        s.curriculum(magnitude_value=a.source,magnitude_objects=(a.first_object,45,31),back_form=a.form,back_query=not a.no_query)
        ticks={0,3,70,73,80,89,137,143,146,147,148,149,150,165,170,204,206,210,214,215,216,217,220,221,222,225,268,271,281,338,340,348,405,411,415,428,472,478,487,539,549,554,559,563,616}
        for tick in sorted(t for t in ticks if t<=a.until):
            s.run_until(tick)
            r['frames'].append(minimal_view(s))
            if tick in (146,147,148,149,215,216,220,221):
                for bank in s.geometry['cpc9_return']['banks']:
                    site=bank['hub']if tick<220 else bank['use_site']
                    r['decisive_local'].append({'tick':tick,'bank':bank['id'],'site':site,
                        'Moore27':[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
            if tick in (0,148,149,216,549,616):
                snap=a.out/f'T{tick}.deetsnap.gz';storage=s.save(snap)
                r['snapshots'].append({'path':snap.name,'storage':storage,'physical':physical(s.world)})
            r.update(last_complete_tick=tick,requests=s.receipts(),elapsed_seconds=time.monotonic()-started)
            write(a.out/'MEDICIONES.json',r)
        r.update(status='MEASURED',final_physical=physical(s.world),receipt_statuses=dict(Counter(x['receipt']['status']for x in s.receipts())))
    except BaseException as error:
        r.update(status='TECHNICAL_ERROR',error=repr(error),traceback=traceback.format_exc());raise
    finally:write(a.out/'MEDICIONES.json',r)
    print(json.dumps({'case':a.case,'status':r['status'],'tick':s.tick,
                     'return_frames':[{ 'tick':x['tick'],'return':x['return']}for x in r['frames']if x['tick']in(149,216,221,225)],
                     'seconds':time.monotonic()-started},ensure_ascii=False))


if __name__=='__main__':main()
