"""Append a real closed milestone to the one existing campaign record."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def main(a):
 proof=a.prueba.resolve(strict=True)
 if proof.parent!=(P/'control').resolve():raise ValueError('Only actual PI09 control proof')
 value=read(proof)
 if value.get('closed')is not True or value.get('error')is not None:raise ValueError('Closed unambiguous milestone required')
 record=P/'REGISTRO_CAMPANA.json';before=sha(record);v=read(record);entry={'phase':a.fase,'recorded_utc':datetime.now(timezone.utc).isoformat(),'proof':str(proof),'sha256':sha(proof),'life_id':value['life_id'],'initial_tick':value['initial_tick'],'final_tick':value['final_tick'],'new_Native_ticks':value['new_Native_ticks']}
 if any(x.get('proof')==str(proof)for x in v.get('closed_milestones',[])):raise FileExistsError('Milestone already recorded; never double-count')
 v.setdefault('closed_milestones',[]).append(entry);v['phase']=a.fase;v['latest_actual_global_selection']=read(C/'sistema/estado/ACTIVO.json');v['recorded_utc']=entry['recorded_utc']
 temp=record.with_name(record.name+'.PI09.pending')
 with temp.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
 if sha(record)!=before:raise ValueError('Concurrent campaign-record edit')
 os.replace(temp,record);print(json.dumps({'record':str(record),'milestone':entry,'budget_unchanged':True},ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--fase',required=True);p.add_argument('--prueba',type=Path,required=True);main(p.parse_args())
