"""CPC9 fresh integrated preparation; fixed controls and independent outputs."""
from pathlib import Path
import argparse,hashlib,json,sys,time,traceback
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src')]
from cpc9_integrado import CPC9Session
from integracion.relational_pair import physical,move
from ejecutar_retorno import write

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--out',required=True,type=Path)
    p.add_argument('--count',choices=['both','A','B','none','off'],default='both')
    p.add_argument('--count-form',default='paired');p.add_argument('--regulation',choices=['plus','minus','offpath','off'],default='plus')
    p.add_argument('--source',type=int,default=31);p.add_argument('--object',type=int,default=18)
    p.add_argument('--back-form',default='paired');p.add_argument('--until',type=int,default=616)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    config=vars(a)|{'out':str(a.out)}
    result={'schema':'CPC9.integrated.measurements.v1','case_id':a.case,'configuration':config,'preparations':0,
            'frames':[],'snapshots':[],'MAIN_RAW_clock_edits':[],'status':'RUNNING','sources':{}}
    sources=[*sorted((ROOT/'src').glob('*.py')),ROOT/'front_semantics/src/count_access.py',*sorted((ROOT/'base_validada/cpc8/src').rglob('*.py'))]
    for path in sources:result['sources'][str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    try:
        contacts=('A','B')if a.count=='both'else()if a.count in('none','off')else(a.count,)
        session=CPC9Session.create(identifier=a.case,enable_count=a.count!='off',enable_regulation=a.regulation!='off',
              regulation_medium=-1 if a.regulation=='minus' else 1,regulation_route='offpath'if a.regulation=='offpath'else'onpath',count_contacts=contacts)
        result.update(preparations=1,geometry=session.geometry)
        session.curriculum(magnitude_value=a.source,magnitude_objects=(a.object,45,31),back_form=a.back_form,count_form=a.count_form)
        ticks={0,2,4,5,9,10,11,24,31,53,54,69,70,73,77,78,79,80,86,89,91,94,100,114,136,137,143,146,147,148,149,165,170,171,204,206,210,214,215,216,220,221,225,268,271,281,338,340,344,348,405,411,415,417,428,472,478,484,487,500,539,549,554,559,563,616}
        for tick in sorted(t for t in ticks if t<=a.until):
            session.run_until(tick);v=session.view()
            result['frames'].append({'tick':tick,'physical':physical(session.world),'view':v})
            if tick in(0,94,148,216,549,616):
                path=a.out/f'T{tick}.deetsnap.gz';storage=session.save(path)
                result['snapshots'].append({'path':path.name,'physical':physical(session.world),'storage':storage})
            result.update(last_complete_tick=tick,elapsed_seconds=time.monotonic()-start,requests=session.receipts())
            write(a.out/'MEDICIONES.json',result)
        result.update(status='MEASURED',final_physical=physical(session.world),receipt_statuses=dict(Counter(x['receipt']['status']for x in session.receipts())))
    except BaseException as error:
        result.update(status='TECHNICAL_ERROR',error=repr(error),traceback=traceback.format_exc());raise
    finally:write(a.out/'MEDICIONES.json',result)
    print(json.dumps({'case':a.case,'status':result['status'],'tick':session.tick,'resources':session.geometry['resources'],
                      'seconds':time.monotonic()-start},ensure_ascii=False))
if __name__=='__main__':main()
