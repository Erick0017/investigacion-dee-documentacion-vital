"""Non-native orchestrator; each independent trajectory gets a supervised process."""
import argparse,json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--prefix',required=True)
    p.add_argument('--only',default='')
    a=p.parse_args();data=json.loads(a.config.read_text(encoding='utf-8'));index=[]
    for case in data['cases']:
        if a.only and case['id'] not in a.only.split(','):continue
        target=ROOT/'resultados/semantica'/case['id']
        cmd=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'tools/supervisor.py'),'--name',a.prefix+'_'+case['id'].lower(),
            '--timeout','900','--',sys.executable,'-I','-B','-X','utf8',str(ROOT/'src/comunicacion/ejecutar_social.py'),
            '--config',str(a.config),'--case',case['id'],'--out',str(target)]
        if 'parent' in case:cmd+=['--parent',str(ROOT/'resultados/semantica'/case['parent']),'--diagnostic',case['diagnostic']]
        code=subprocess.run(cmd,timeout=950).returncode
        record={'id':case['id'],'worker_exit_code':code,'path':str(target/'MEASUREMENTS.json')}
        if (target/'MEASUREMENTS.json').is_file():
            m=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf-8'));record.update(status=m['status'],counts=m.get('observed_counts'))
        index.append(record)
        out=ROOT/'resultados/semantica'/('INDEX_'+a.prefix+'.json');out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'completed':len(index),'errors':sum(x['worker_exit_code']!=0 for x in index)}))
if __name__=='__main__':main()
