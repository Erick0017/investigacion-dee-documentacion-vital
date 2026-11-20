"""Finite serial contact cohort runner; each native trajectory supervised."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--prefix',required=True);p.add_argument('--only',default='');a=p.parse_args();data=json.loads(a.config.read_text(encoding='utf-8'));index=[]
    for c in data['cases']:
        if a.only and c['id'] not in a.only.split(','):continue
        out=ROOT/'resultados/semantica'/c['id'];argv=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'tools/supervisor.py'),'--name',a.prefix+'_'+c['id'].lower(),'--timeout','900','--',sys.executable,'-I','-B','-X','utf8',str(ROOT/'src/relaciones/ejecutar_contacto.py'),'--config',str(a.config),'--case',c['id'],'--out',str(out)]
        code=subprocess.run(argv,timeout=950).returncode;row={'id':c['id'],'worker_exit':code,'path':str(out/'MEASUREMENTS.json')}
        if (out/'MEASUREMENTS.json').is_file():
            m=json.loads((out/'MEASUREMENTS.json').read_text(encoding='utf-8'));row.update(status=m['status'],observed=m.get('observed'))
        index.append(row);(ROOT/'resultados/semantica'/('INDEX_'+a.prefix+'.json')).write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'completed':len(index),'errors':sum(x['worker_exit']!=0 for x in index)}))
if __name__=='__main__':main()
