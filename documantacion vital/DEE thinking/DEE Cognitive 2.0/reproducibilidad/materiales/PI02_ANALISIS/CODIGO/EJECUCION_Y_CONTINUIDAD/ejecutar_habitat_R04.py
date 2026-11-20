"""Finite supervised workbench exposure. Root only, exact IDs, no policy."""
from pathlib import Path
import argparse,json,hashlib,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from servicio_ensayo import Owner,P,SYSTEM,append
p=argparse.ArgumentParser();p.add_argument('--vida',required=True);p.add_argument('--tag',required=True);p.add_argument('--serie',choices=['development','reserved'],required=True);p.add_argument('--historia',choices=['paired','unpaired','no_training','report_only'],required=True);p.add_argument('--brazo',choices=['real','warning_cut','actuator_null','valence_omit'],required=True);p.add_argument('--ticks',type=int,required=True);args=p.parse_args()
if not 1<=args.ticks<=12000:raise ValueError('Finite physical horizon only')
summary=P/'ensayos'/('RESUMEN_'+args.tag+'.json')
if summary.exists()or(P/'ensayos'/(args.tag+'_ADMIT.json')).exists():raise ValueError('Already attempted exposure; inspect existing exact record, never retry')
rows=[]
with Owner(args.vida,args.tag)as owner:
    for suffix,literal in [('ADMIT',{'modo':'eci01-pi02-habitat-preparar','serie':args.serie,'historia':args.historia,'brazo':args.brazo}),('TIME',{'modo':'eci01-pi02-tiempo','ticks':args.ticks}),('STATUS',{'modo':'eci01-pi02-habitat-estado'})]:
        result=owner.material(args.tag+'_'+suffix,literal);rows.append({'id':args.tag+'_'+suffix,'result':result})
log=SYSTEM/'estado/servicios_persistentes'/args.vida/'trabajo'/'PI02_WORKBENCH_R04/eventos.jsonl'
# Find the owner's declared work directory without guessing a second state.
if not log.is_file():
    found=list((SYSTEM/'estado').glob('**/'+args.vida+'/PI02_WORKBENCH_R04/eventos.jsonl'))
    if len(found)!=1:raise ValueError('Exact workbench journal locator not resolved: '+str(found))
    log=found[0]
events=[json.loads(x)for x in log.read_text(encoding='utf-8').splitlines()]
record={'life':args.vida,'series':args.serie,'history':args.historia,'arm':args.brazo,'ticks':args.ticks,'requests':rows,'journal':str(log),'journal_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'opportunities':[x for x in events if x['kind']=='OPPORTUNITY_COMPLETED'],'device_commands':[x for x in events if x['kind']=='DEVICE_COMMAND'],'warning_signatures':[x for x in events if x['kind']=='LEARNED_WARNING_SIGNATURE'],'scope':'Same continuous Native world; external clock/phase/decoders/device supplied, no individual action command or expected sign fed.'}
summary.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'summary':str(summary),'completed':len(record['opportunities']),'resources':[x['resources_total']for x in record['opportunities']][-1:],'CLOSE':len(record['warning_signatures'])}))
