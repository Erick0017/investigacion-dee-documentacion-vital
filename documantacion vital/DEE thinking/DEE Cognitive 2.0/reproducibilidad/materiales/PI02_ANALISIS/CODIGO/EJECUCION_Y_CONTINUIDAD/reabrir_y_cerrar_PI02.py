"""Actual separate-process continuation of the same complete R04 main."""
from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from servicio_ensayo import Owner,P,SYSTEM
LIFE='ECI02_PI02_MAIN';proof=P/'control/REAPERTURA_Y_CONTINUACION_PI02.json';pairfile=P/'control/PAR_FINAL_PI02.json'
if proof.exists()or pairfile.exists()or(P/'ensayos/PI02_REOPEN_STATE0.json').exists():raise ValueError('An attempted reopening already exists; reconcile, never repeat')
ret=json.loads((P/'ensayos/RESUMEN_RETENCION_PI02.json').read_text(encoding='utf-8-sig'))
before=json.loads((SYSTEM/'estado/vidas'/LIFE/'VIDA.json').read_text(encoding='utf-8'));physical=before['physical']
rows=[]
with Owner(LIFE,'PI02_REOPEN_FINAL')as owner:
    initial=owner.initial['physical']
    if any(initial[k]!=physical[k]for k in('N','tick','RAW_sha256','clocks_sha256')):raise ValueError('Actual restoration differs from the last physical checkpoint')
    for suffix,literal in [('STATE0',{'modo':'eci01-pi02-habitat-estado'}),('WORK13',{'modo':'eci01-pi02-habitat-trabajo','izquierda':13,'derecha':5,'aviso':True,'perturbacion':True,'adelanto':128}),('WORK7',{'modo':'eci01-pi02-habitat-trabajo','izquierda':7,'derecha':16,'aviso':True,'perturbacion':True,'adelanto':195}),('ENABLE',{'modo':'eci01-pi02-reactivar-habitat'}),('TIME',{'modo':'eci01-pi02-tiempo','ticks':1800}),('STATE1',{'modo':'eci01-pi02-habitat-estado'})]:
        r=owner.material('PI02_REOPEN_'+suffix,literal);rows.append({'id':'PI02_REOPEN_'+suffix,'result':r})
        if suffix in('STATE0','WORK13','WORK7','ENABLE')and(r['after_tick']!=r['before_tick']or r['before_tick']!=physical['tick']):raise ValueError('A declared0tick preparation advanced Native time; preserve actual future')
    exported=owner.control('exportar');value=json.loads(exported['result'])
    if value['before_tick']!=value['after_tick']:raise ValueError('Export unexpectedly advanced Native')
    pairfile.write_text(json.dumps({'source_life':LIFE,'source_tick':value['after_tick'],'pair':value['paired_export'],'transport_receipt':exported},ensure_ascii=False,indent=2),encoding='utf-8')
after=json.loads((SYSTEM/'estado/vidas'/LIFE/'VIDA.json').read_text(encoding='utf-8'))
log=SYSTEM/'estado/servicios_locales'/LIFE/'PI02_WORKBENCH_R04/eventos.jsonl';events=[json.loads(s)for s in log.read_text(encoding='utf-8').splitlines()]
opps=[s for s in events if s['kind']=='OPPORTUNITY_COMPLETED'and s['episode']>=12]
result={'schema':'PI02.actual.separate_process.continuation.v1','life_id':LIFE,'before':physical,'initial_reopened_physical':initial,'physical_unchanged_at_reopen':True,'operational_state_validated_by_existing_owner':True,'new_Native_ticks':after['physical']['tick']-physical['tick'],'after':after['physical'],'rows':rows,'new_opportunities':opps,'new_resources':sum(bool(x['effect'].get('useful'))for x in opps),'full_pair_descriptor':str(pairfile),'journal':str(log),'journal_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'no_Native_reset_or_content_reteaching':True,'owner_closed':True,'conservation_panel_is_previous_cut_not_repeated_at_final':ret,'scope':'Operator adds2external work opportunities and enables the same fixed bridge. Native retains its actual acquired state; its physical outputs control the device/work. This is not another complete12use panel at the final cut.'}
proof.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'life':LIFE,'before_tick':physical['tick'],'final_tick':after['physical']['tick'],'new_opportunities':len(opps),'new_resources':result['new_resources'],'pair':str(pairfile)},ensure_ascii=False))
