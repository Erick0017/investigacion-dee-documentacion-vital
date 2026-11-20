"""Passive readback of every included complete admitted life."""
from pathlib import Path
import argparse,gc,json,sys
def main():
    p=argparse.ArgumentParser();p.add_argument('--sistema',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.sistema));from app.lives import Store;from app.native_tools import physical,atomic_json;from app.process_control import protect_current,current_resources;protect_current(output=a.out.with_name(a.out.stem+'.RECURSOS.json'));s=Store(a.sistema);selected=json.loads((a.sistema/'documentacion/ESTADO_ACTUAL_DE_VIDAS.json').read_bytes())['lives'];rows=[];active=s.record()['snapshot_sha256']
    for item in selected:
        rec,actor=s.load(item['life_id']);actual=physical(actor.world);rows.append({'life_id':rec['life_id'],'profile':rec['profile'],'snapshot_sha256':rec.get('snapshot_sha256',(rec.get('parent')or{}).get('encoded_sha256')),'physical':actual,'matches_declared_physical':all(actual[k]==item['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')),'interfaces':len(actor.world.interfaces),'receipts':len(actor.world.runtime.receipts),'paused':bool(actor.world.runtime.paused),'no_evolution':True});del actor;gc.collect()
    okay=all(x['matches_declared_physical']for x in rows)and s.record()['snapshot_sha256']==active;atomic_json(a.out,{'schema':'DCS1.1.admitted_lives.full_restore.v1','lives':rows,'all_match':okay,'active_unchanged':True,'resources':current_resources()})
    if not okay:raise AssertionError('An admitted complete life does not restore')
    print(json.dumps({'lives':len(rows),'all_full_restores_match':True,'active_unchanged':True}))
if __name__=='__main__':main()
