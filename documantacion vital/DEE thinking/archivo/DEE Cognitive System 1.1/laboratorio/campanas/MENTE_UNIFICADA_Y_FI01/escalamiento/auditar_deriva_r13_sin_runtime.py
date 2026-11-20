"""Targeted existing-record/snapshot field extraction; ZERO native imports.

Snapshot RAW/clock offsets are accepted only if their complete hashes match
the physical witnesses already recorded by the original owner. No evolution,
past reconstruction, interface continuation or kernel reimplementation occurs.
"""
from pathlib import Path
import gzip,hashlib,itertools,json,struct
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parents[2]
EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/servicio'
SOURCE=EV/'SERVICIO_60MIN_FINAL_R11/REGISTROS_TRANSPORTE.json.gz'
WANTED=('fi60_00412','fi60_00413','fi60_00421','fi60_00422','fi60_00457','fi60_00458')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fields(raw):
    raw=int(raw);v=[(raw>>k)&15 for k in(48,52,56)]
    return {'raw':str(raw),'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,'semantic':(raw>>60)&15,
      'direction':[q-16 if q>=8 else q for q in v]}
def saved_world(snapshot):
    path=ROOT/'sistema'/snapshot['snapshot'];expected=snapshot['physical'];blob=path.read_bytes()
    if hashlib.sha256(blob).hexdigest()!=snapshot['snapshot_sha256']:raise ValueError('Complete snapshot changed')
    data=gzip.decompress(blob)
    if data[:8]!=b'DEETSNP1':raise ValueError('Not expected saved-world format')
    version,N=struct.unpack_from('<II',data,8);tick=struct.unpack_from('<Q',data,16)[0]
    if version!=2 or N!=67:raise ValueError('Only this verified v2/N67 snapshot is examined')
    length=struct.unpack_from('<I',data,41)[0];count_offset=45+length;count=struct.unpack_from('<Q',data,count_offset)[0]
    if count!=N**3:raise ValueError('RAW entry count mismatch')
    offset=count_offset+8;raw=data[offset:offset+8*count];clocks=data[offset+8*count:offset+16*count]
    if hashlib.sha256(raw).hexdigest()!=expected['RAW_sha256']or hashlib.sha256(clocks).hexdigest()!=expected['clocks_sha256']:raise ValueError('Physical witness mismatch; no guessed field extraction')
    def obs(p):
        k=((p[0]*N)+p[1])*N+p[2];out=fields(struct.unpack_from('<Q',raw,8*k)[0]);out.update(site=list(p),tick=tick,clock=str(struct.unpack_from('<Q',clocks,8*k)[0]));return out
    pts={'A':(14,14,15),'B':(16,14,15),'E':(15,15,15),'S':(14,15,16),'C':(12,17,18),
      'central_diagonal_first_step':(15,16,14),'central_axial_first_step':(15,16,15),'central_diagonal_gate':(15,17,13)}
    roi=[obs(tuple((15+v[i])%N for i in range(3)))for v in itertools.product(range(-3,4),repeat=3)]
    return {'source':path.relative_to(ROOT).as_posix(),'source_sha256':digest(path),'snapshot_bytes':len(blob),
      'version':version,'N':N,'tick':tick,'field_count':count,'RAW_sha256':expected['RAW_sha256'],'clocks_sha256':expected['clocks_sha256'],
      'complete_field_hashes_matched':True,'fields':{k:obs(p)for k,p in pts.items()},'roi_radius3':roi,
      'scope':'Read-only saved-field extraction. Whole RAW/clocks hashes verified, but interfaces/queues after these fields are not decoded here; the original full file is preserved.'}
def main():
    records=json.loads(gzip.decompress(SOURCE.read_bytes()));out=[];crossings=[]
    for entry in records:
        if not entry.get('result')or not entry.get('id','').startswith('fi60_'):continue
        value=json.loads(entry['result']);payload=json.loads(entry['payload']);rows=value.get('result',{}).get('rows',[])
        if not rows:continue
        row=rows[0];mode=(payload.get('situaciones')or[{}])[0].get('modo');before=value['before_tick'];after=value['after_tick']
        refs=value['result'].get('final',{}).get('references',[])
        if any(before<=q*391<after for q in range(before//391,(after//391)+1)):
            crossings.append({'request':entry['id'],'mode':mode,'payload':payload,'before':before,'after':after,
              'writing_phase_candidates':[q*391 for q in range(before//391,(after//391)+1)if before<=q*391<after],
              'references_after':refs,'query_tick':row.get('query_tick'),'input_tick':row.get('input_tick'),
              'datum_inputs':[r for r in row.get('requests',[])if r.get('channel')=='MU.current.datum']})
        if entry['id']not in WANTED:continue
        requests=row.get('requests',[]);stats={'requested':len(requests),'applied':sum(r['receipt']['status']=='applied'for r in requests),
          'rejected':sum(str(r['receipt']['status']).startswith('rejected')for r in requests)}
        raw=row.get('raw_components');nonzero=[{'index':i,'value':v}for i,v in enumerate(raw)if v]if raw is not None else None
        out.append({'request':entry['id'],'payload':payload,'before_tick':before,'after_tick':after,
          'committed_snapshot':value['committed_snapshot'],'saved_world_fields':saved_world(value['committed_snapshot']),
          'query_tick':row.get('query_tick'),'read_tick':row.get('read_tick'),'input_tick':row.get('input_tick'),'datum_tick':row.get('datum_tick'),
          'nonzero_raw_components':nonzero,'raw_sensor_value':row.get('raw_sensor_value'),
          'reader':row.get('reader'),'references_pre':row.get('references_pre'),'references_after':refs,
          'frames':row.get('frames',[]),'requests':requests,'admission_counts':stats,
          'scalar_detail_gap':'No per-tick frames recorded'if mode=='dato'and not row.get('frames')else None})
    target=EV/'ANALISIS_DIRIGIDO_DERIVA_R13_B.json'
    if target.exists():raise FileExistsError(target)
    report={'native_imports':False,'Runtimes_created_or_loaded':0,'native_ticks':0,'source':SOURCE.relative_to(ROOT).as_posix(),
      'source_sha256':digest(SOURCE),'script_sha256':digest(Path(__file__)),'cases':out,'existing_phase_crossings':crossings,
      'known_gaps':['No exact complete before62548snapshot found; nearest previous request commit is62525.',
        'Scalarfi60_00413has no per-tickframes; current data is29, not13.',
        'Direction0,+1,-1in the failed raw frames and the active SEM4 first-step support are observed/inherited facts. Their sufficiency as a causal explanation needs a counterfactual, not a renamed reader.',
        'No age-only future matched to62525exists in these selected records; temporal coincidence does not isolate age versus datum/query interaction.']}
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'out':str(target),'sha256':digest(target),'cases':len(out),'existing_crossing_rows':len(crossings),'native_ticks':0}))
if __name__=='__main__':main()
