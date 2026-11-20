"""Extract trajectory metrics from already recalculated CLOSED OSC members.

No experiment replay/recalculation, Native, SQLite, network or live runtime.
Only three manifest-pinned closed members and the referenced protocol are read.
"""
from pathlib import Path
import argparse
import hashlib
import json

def need(ok,message):
    if not ok:raise ValueError(message)
def sha(b):return hashlib.sha256(b).hexdigest()

def extract(package,historical_protocol,output_prefix):
    package=Path(package).resolve(strict=True);mp=package/'MANIFIESTO.json';mb=mp.read_bytes();manifest=json.loads(mb)
    members={r['archive']:r for r in manifest['files']}
    def member(name,jsonl=False):
        r=members[name];p=package/name
        need(p.resolve(strict=True).is_relative_to(package) and not p.is_symlink(),'CLOSED_MEMBER_CONTAINMENT')
        b=p.read_bytes();need(len(b)==r['bytes'] and sha(b)==r['sha256'],'CLOSED_MEMBER_HASH')
        return ([json.loads(x) for x in b.decode('utf-8-sig').splitlines() if x.strip()] if jsonl else json.loads(b))
    facts=member('HECHOS_RECALCULADOS.json');journal=member('PRIMARIOS/NATIVE/events.jsonl',True)
    experiment=member('PROTOCOLO/PROTOCOLO_PROSPECTIVO.json')
    hp=Path(historical_protocol).resolve(strict=True);hb=hp.read_bytes();history=json.loads(hb)
    need(sha(hb)==experiment['protocolHistoricalSourceSha256'],'EXACT_PROSPECTIVE_HISTORICAL_PROTOCOL')
    need(facts['condition']=='OSCILANTE' and facts['actualCompletedCycles']==6 and facts['issues']==[],
         'ONLY_THE_CONFIRMED_CLOSED_OSC_SIX')
    final_receipts={};intent=None
    for row in journal:
        if row.get('kind')=='PHASE_INTENT':intent=row
        elif row.get('kind')=='PHASE_COMPLETED':
            if intent['mode']=='eci01-rbx01-feedback':
                final_receipts[intent['context']['operation_id']]={r['id']:r for r in row['result']['evidence']['requests']}
            intent=None
    rows=[];stock=facts['stock']['initial'];zones=[];run=0;longest=0
    for c in facts['cycles']:
        q1=next(a for a in c['actions'] if a['kind']=='decision')
        q2=next(a for a in c['actions'] if a['kind']=='query_sensor')
        body=q2['bodyResult'];panel=c['paidPanel'];datum=q2['nativeEvidence']['datum_request']
        receipt=final_receipts[c['feedbackOperationId']][datum['id']]
        need(receipt['receipt']['status']=='applied' and c['NativeQ2DatumApplied'] is True,'Q2_ACTUAL_APPLIED_RECEIPT')
        before=stock;stock-=c['costs']['permissionSpent']
        success=body['outcome']=='MOVED' and body['motor']['status']=='ARRIVED'
        a,b=body['originStation'],body['selectedTarget'];loop=success and (a,b) in((2,3),(3,2))
        run=run+1 if loop else 0;longest=max(longest,run)
        if not zones:zones.append(a)
        need(zones[-1]==a,'OBSERVED_TRAJECTORY_DISCONTINUITY');zones.append(b)
        rows.append({'cycle':c['cycle'],'partition':c['partition'],'from':a,'to':b,'selectedPort':body['selectedPort'],
            'nativeQ1Action':q1['nativeAction'],'nativeQ2Action':q2['nativeAction'],'successfulMove':success,'loop2to3or3to2':loop,
            'nativeTicks':c['nativeTicks'],'panel':panel['sample'],'panelStation':panel['station'],
            'paidASKApplied':c['paidASKApplied'],'datumOmitted':c['datumOmitted'],'nativeRawPrice':c['nativeRawPrice'],
            'nativeDatumApplied':c['NativeQ2DatumApplied'],'datumRequest':datum,'datumFinalReceipt':receipt['receipt'],
            'charges':{'queryPaidAtQ1':q1['costs']['querySpent'],'queryPaidAtQ2':q2['costs']['querySpent'],
                       'tollPaidAtQ2':q2['costs']['tollSpent'],'total':c['costs']['permissionSpent']},
            'stock':{'before':before,'afterASK':before-q1['costs']['permissionSpent'],'afterCycle':stock},
            'freePassUsed':body['passage']['freePassUsed'],'rechargeAt':body['passage'].get('rechargeAt'),
            'actualPhysicalFailed':c['actualPhysicalFailed'],'appliedGenericFailed':c['appliedGenericFailed'],
            'genericReturnPulses':c['genericReturnPulses'],
            'operationIds':{'decision':q1['operationId'],'query_sensor':q2['operationId'],'feedback':c['feedbackOperationId']}})
    need(stock==facts['stock']['final'],'CLOSED_STOCK_EXTRACTION_MISMATCH')
    successful=[r for r in rows if r['successfulMove']];loops=[r for r in successful if r['loop2to3or3to2']]
    departures=[r for r in successful if r['from'] in(2,3) and r['to'] not in(2,3)]
    need(not departures,'THIS_OSC_SNIPPET_EXPECTS_NO_VERIFIED_DEPARTURE;_REVIEW_NEW_DATA_WITHOUT_RETUNING')
    replenished=[]
    for event in facts['environment']['replenished']:
        exposures=[r['cycle'] for r in rows if r['panelStation']==event['station'] and
            r['panel']['epoch']>=event['epoch'] and r['panel']['price'+str(event['port'])]==0 and r['nativeDatumApplied']]
        replenished.append(dict(event,subsequentActuallyQueriedCycles=exposures))
    depleted=[]
    for r in rows:
        if r['panel']['price0']==2 or r['panel']['price1']==2:
            depleted.append({'cycle':r['cycle'],'station':r['panelStation'],'portPrices':[r['panel']['price0'],r['panel']['price1']],
                'nativeSignal':r['nativeRawPrice'],'datumRequestId':r['datumRequest']['id'],
                'receiptStatus':r['datumFinalReceipt']['status'],'remainingOpportunitiesInFixedHorizon':6-r['cycle']})
    metrics={'schema':'DEE.SDK.Focal.OSC.closed_trajectory_metrics.R06','mode':'EXTRACTION_FROM_EXISTING_RECALCULATED_FACTS',
        'instanceId':facts['instanceId'],'lifeId':facts['lifeId'],'sessionId':facts['sessionId'],
        'sourcePrefixAndScopeBornTick':facts['sourceTick'],'finalNativeTick':facts['finalNativeTick'],'newNativeTicks':facts['newNativeTicks'],
        'actualCompletedOpportunities':6,'zones':zones,'transitions':rows,
        'repetition':{'prospectiveRule':history['prospectiveMetrics']['repetition'],'numeratorLoopSuccessfulMoves':len(loops),
            'denominatorAllSuccessfulMoves':len(successful),'fraction':len(loops)/len(successful),
            'longestConsecutiveLoopSuccessfulMoves':longest,'loopMoveCycles':[r['cycle'] for r in loops]},
        'sustainedExit':{'prospectiveRule':history['prospectiveMetrics']['sustainedExit'],
            'firstVerifiedDeparture':None,'departureCount':0,'criterionDemonstrated':False,
            'status':'NO_VERIFIED_DEPARTURE_IN_OBSERVED_FIXED_WINDOW','fixedHorizon':6,
            'limit':'No departure was observed; no post-departure two-arrival window exists. Do not infer future behaviour.'},
        'freeAndPaidPasses':{'free':sum(r['freePassUsed'] for r in rows),'paid':sum(r['charges']['tollPaidAtQ2']>0 for r in rows)},
        'costs':facts['costs'],'stock':facts['stock'],'NativeInputs':facts['NativeInputs'],
        'actuallyExposedDepletedPanels':depleted,'replenishmentEventsAndObservedExposure':replenished,
        'signalZeroVsNoQuery':'Cycles4/5 have paid panel signal0 and an applied Native datum. NoQuery would be omitted datum with signal-1.',
        'tollNotGenericFailure':{'tollCycles':[r['cycle'] for r in rows if r['charges']['tollPaidAtQ2']>0],
            'allActualPhysicalFailedFalse':all(r['actualPhysicalFailed'] is False for r in rows),
            'allAppliedGenericFailedFalse':all(r['appliedGenericFailed'] is False for r in rows)},
        'provenance':{'exportManifestSha256':sha(mb),'factsMember':members['HECHOS_RECALCULADOS.json'],
            'journalMember':members['PRIMARIOS/NATIVE/events.jsonl'],'prospectiveHistoricalProtocolSha256':sha(hb)},
        'limits':['n=1 paired descendant; CONTROL not read here.','No policy-learning inference or new Native execution.',
            'Late depleted sample at cycle5 leaves one further opportunity, not two; do not shorten the sustained-exit rule.'],
        'NativeExecuted':False,'SQLiteOpened':False,'experimentRecalculatedAgain':False}
    md=['## OSC cerrado: trayectoria y exposición observadas','',
        f"Fuente/ScopeBorn **T{facts['sourceTick']}**, cierre **T{facts['finalNativeTick']}**, +{facts['newNativeTicks']} ticks; seis oportunidades. Estado y IDs completos en el JSON adjunto.",'',
        '**Zonas:** '+' → '.join(map(str,zones))+'. Fracción de movimientos exitosos 2↔3: **5/6 (83,33 %)**; racha consecutiva máxima **5 movimientos** (ciclos2–6). El denominador es6 movimientos exitosos, no5 pares de ensayos ni6consultas.','',
        '| Ciclo | Tránsito | Acción Q2 | Panel pagado (p0,p1; señal) | Peaje | Stock después | Datum/recibo |','|---:|---|---|---|---:|---:|---|']
    for r in rows:
        p=r['panel'];md.append(f"| {r['cycle']} | {r['from']}→{r['to']} | {r['nativeQ2Action']} | {p['price0']},{p['price1']}; {r['nativeRawPrice']} | {r['charges']['tollPaidAtQ2']} | {r['stock']['afterCycle']} | {r['datumRequest']['id']} / {r['datumFinalReceipt']['status']} |")
    md+=['', '**Consulta y coste:**6ASK pagados y6datos Q2 aplicados;0 omisiones. La consulta cuesta1 en Q1 y no se cobra de nuevo en Q2. Cuatro pasos libres y dos con peaje2 (ciclos4/5): coste6+4=10, stock164→154;78 inputs Native aplicados/0 rechazados.', '',
        '**Exposición:** los paneles agotados de ciclos4/5 se consultaron realmente (señal0, no NoQuery). Hubo tres eventos ambientales de reposición: estación0/puerto1/época4, estación3/puerto1/época5 y estación2/puerto1/época6. Sólo la reposición de estación3 fue consultada de nuevo en esta ventana, en ciclo6 con señal1 y datum aplicado. No se cuentan las otras dos como exposición Native.', '',
        '**Salida sostenida:** no se observó ninguna salida de {2,3} a otra estación. Por tanto no se demostró el criterio de dos llegadas posteriores fuera; no se sustituye por un cambio aislado ni se extrapola más allá del horizonte6. La nueva muestra agotada de estación2 en ciclo5 deja sólo una oportunidad posterior: no permite exigir/evaluar dos futuras llegadas tras ella.', '',
        '**Retorno:** peaje no equivale a fallo genérico. En ambos pasos pagados constan actualPhysicalFailed=false y appliedGenericFailed=false; se conservan los dos pulsos de retorno por ciclo. No se infiere aprendizaje de política. n=1; CONTROL sigue fuera de este resumen.', '']
    prefix=Path(output_prefix).absolute();need(prefix.parent.is_dir(),'EXISTING_OUTPUT_PARENT')
    jp=prefix.with_suffix('.json');mpath=prefix.with_suffix('.md');need(not jp.exists() and not mpath.exists(),'NEW_METRIC_ARTIFACTS_ONLY')
    jp.write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    mpath.write_text('\n'.join(md),encoding='utf8',newline='\n')
    return {'json':str(jp),'jsonSha256':sha(jp.read_bytes()),'markdown':str(mpath),'markdownSha256':sha(mpath.read_bytes()),
            'NativeExecuted':False,'experimentRecalculatedAgain':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package',type=Path,required=True)
    p.add_argument('--historical-protocol',type=Path,required=True);p.add_argument('--output-prefix',type=Path,required=True)
    a=p.parse_args();print(json.dumps(extract(a.package,a.historical_protocol,a.output_prefix),ensure_ascii=False))
