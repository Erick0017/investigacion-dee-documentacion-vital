"""Zero-tick projections of complete saved states; never imports the DEE engine."""
import argparse,gzip,hashlib,importlib.util,json
from pathlib import Path

def load(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def emit(p,v):
    if p.exists():raise FileExistsError(str(p))
    b=(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
    p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def sha(b):return hashlib.sha256(b).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in('system','delta','o2','out'):ap.add_argument('--'+key,type=Path,required=True)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    parser=a.system/'capacidades/observador_causal_retrospectivo_01.py'
    spec=importlib.util.spec_from_file_location('APD_PASSIVE_PARSER',parser)
    ob=importlib.util.module_from_spec(spec);spec.loader.exec_module(ob)
    projections=[]
    for arm in('real','omit','sham'):
        path=a.o2/arm/'OP2_ANTES_COMPLETO.deetsnap.gz';s=ob.Snapshot(path)
        row={'arm':arm,'snapshot_locator':str(path.resolve()),'summary':s.summary(),
             'N':s.N,'tick':s.tick,'RAW_sha256':sha(ob.pbytes(s.raw)),
             'clocks_sha256':sha(ob.pbytes(s.clocks)),
             'clock_default':str(s.tick),
             'rows':[[i,str(v),str(s.clocks[i])]for i,v in enumerate(s.raw)if v],
             'clock_exceptions':[[i,str(v)]for i,v in enumerate(s.clocks)if v!=s.tick],
             'channels':s.channels,'pending':s.pending,'receipts':s.receipts,
             'execution':{'paused':s.paused,'next_event_id':s.next_event_id,
                          'next_sequence':s.next_sequence,'phase':s.phase,
                          'backend':s.backend,'threads':s.threads},
             'metadata_value_sha256':{k:sha(v.encode('utf8'))for k,v in s.metadata.items()}}
        projections.append(row);del s
    emit(a.out/'PRE_TERCERA_ACCION_RAW_CLOCK_COMPLETO.json.gz',
         {'schema':'APD01.O2.prethird.complete_field_projection.v1','native_ticks':0,
          'parser_sha256':sha(parser.read_bytes()),'cases':projections,
          'scope':'Full RAW/clocks, interfaces, pending events, receipts and execution counters exported. Metadata values represented by per-key hashes only; no claim of whole-state causal identity or unique material lineage.'})
    summary=load(a.delta/'RESULTADOS.json');cases=[]
    for h in summary['histories']:
        identity=h['id'];doc=load(a.delta/identity/'05_RESULTADO_COMPLETO.json.gz')['result']
        reqs=list(doc['lesson']['requests'])
        for use in doc['uses']:reqs.extend(use['requests'])
        for old in doc['old_six']:reqs.extend(old['result']['requests'])
        path=a.system/h['final']['snapshot'];s=ob.Snapshot(path)
        if s.encoded_sha256!=h['final']['snapshot_sha256']:raise ValueError('Final snapshot changed')
        lookup={r['id']:r for r in s.receipts};rows=[]
        for r in reqs:
            if r['id']not in lookup:raise ValueError('Missing final receipt')
            rows.append({'id':r['id'],'captured_status':r['receipt']['status'],
                         'captured_receipt':r['receipt'],'final_receipt':lookup[r['id']]})
        cases.append({'id':identity,'snapshot_locator':str(path.resolve()),
                      'snapshot_sha256':s.encoded_sha256,'tick':s.tick,'pending':s.pending,
                      'final_receipts_of_requested_events':rows});del s
    emit(a.out/'DELTA_RECIBOS_FINALES_COMPLETOS.json.gz',
         {'schema':'APD01.affine.final_receipts.read_only.v1','native_ticks':0,
          'parser_sha256':sha(parser.read_bytes()),'event_status_codes':
          {'SCHEDULED':1,'APPLIED':2,'REJECTED_LATE':3,'REJECTED_INVALID':4,
           'REJECTED_OCCUPIED':5,'REJECTED_CONFLICT':6,'REJECTED_QUEUE_FULL':7},
          'cases':cases,'scope':'Receipt snapshots captured earlier remain untouched. Final native serializer receipts resolve later applications without converting scheduled records into earlier applied records.'})
    print(json.dumps({'native_ticks':0,'projected_complete_fields':len(projections),
                      'final_receipts':sum(len(c['final_receipts_of_requested_events'])for c in cases)}))

if __name__=='__main__':main()
