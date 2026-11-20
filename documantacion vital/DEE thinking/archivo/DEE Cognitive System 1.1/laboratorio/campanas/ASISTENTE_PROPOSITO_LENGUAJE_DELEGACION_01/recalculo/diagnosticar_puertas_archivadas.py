"""Read-only instrument-domain diagnosis; no Runtime or native import."""
import argparse,importlib.util,json
from pathlib import Path
sp=importlib.util.spec_from_file_location('apd_auditor',Path(__file__).with_name('recalcular_primarios_apd.py'))
audit=importlib.util.module_from_spec(sp);sp.loader.exec_module(audit);read=audit.read;walk=audit.walk
def main():
    p=argparse.ArgumentParser();p.add_argument('--primarios',type=Path,required=True);a=p.parse_args();rows=[]
    for path in sorted(a.primarios.glob('P[0-9][0-9]_*.json.gz')):
        primary=read(path);body=primary.get('result')
        if isinstance(body,dict)and'INSTRUMENTO'in body:body=body.get('result',body)
        for where,node in walk(body):
            r=node.get('reader',{})
            if isinstance(r,dict)and isinstance(r.get('observations'),list)and'choice'in r and len(r['observations'])!=6:
                rows.append({'primary':path.name,'where':where,'kind':node.get('kind'),'origin':r.get('origin'),
                    'sites':[o['site']for o in r['observations']],'choice':r['choice']})
    print(json.dumps(rows,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
