"""Read-only targeted R08 primary-life extraction; zero Native calls."""
from pathlib import Path
from collections import Counter
import gzip,hashlib,importlib.util,json,sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT.parent
THINKING=ARCHIVE.parent
BASE=ARCHIVE/'analisis_transversal_cognitivo/ECI02/CONSOLIDACION_OPERATIVA'
OUT=ROOT/'evidencia_principal'
OBSERVER=ARCHIVE/'analisis_transversal_cognitivo/ECI01/codigo/base_cognitive_R01/sistema/capacidades/observador_causal_retrospectivo_01.py'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def find_reader(row):
    if 'reader' in row:return row
    if isinstance(row.get('result'),dict):
        for child in row['result'].get('rows',[]):
            found=find_reader(child)
            if found:return found
    return None

def main():
    OUT.mkdir(exist_ok=True)
    dest=OUT/'PRINCIPAL_R08_DATOS_EXACTOS.json.gz'
    if dest.exists():raise FileExistsError('Keep prior extraction bytes')
    index=read(BASE/'datos/PRIMARIOS_OUTBOX_CIERRE_R01.json')
    proof=read(BASE/'datos/PRUEBA_CONSOLIDACION_RECUPERADA_R02.json')
    adoption=read(BASE/'datos/ADOPCION_OPERATIVA_PUBLICADA_R02.json')
    rows={};sources={}
    for item in index['rows']:
        path=Path(item['source'])
        if not path.is_file():path=BASE/item['member']
        assert sha(path)==item['sha256']
        source=read(path);sources[item['label']]={**item,'resolved_source':str(path),'bytes_verified':True}
        if item['label'] not in ('LEX_luma','MA_PRE','LUMA_POST','MA_POST'):continue
        row=source['result']['rows'][0];physical=find_reader(row);assert physical is not None
        reader=physical['reader'];candidates=reader['candidates']
        assert not reader['ambiguous'] and len(candidates)==1
        sign=reader['formed_native_command']
        rows[item['label']]={'N':67,'tick':physical['read_tick'],'output':sign,
             'points':reader['panel'],'reader_sites':[r['site'] for r in candidates],
             'input_tick':physical['input_tick'],'input_receipts':physical['requests'],
             'input_site':physical['requests'][0]['site'],'reader_contract':reader,
             'source':sources[item['label']],'source_pointer':'/result/rows/0'+('/result/rows/0' if physical is not row else ''),
             'preparation':'Operation and context are operator-selected. No new teaching in this panel.',
             'lineage_scope':'Actual panel in ECI02_CIERRE_CANDIDATA_01; its reached T727225 state was published under the principal identity.'}
    assert rows['LEX_luma']['output']==rows['LUMA_POST']['output']==1
    assert rows['MA_PRE']['output']==rows['MA_POST']['output']==-1
    spec=importlib.util.spec_from_file_location('_r08_stdlib_snapshot_parser',OBSERVER)
    obs=importlib.util.module_from_spec(spec);spec.loader.exec_module(obs)
    check=BASE/'estados/LAB/sistema'
    snapshots={};loaded={}
    for name in ('before','after'):
        item=proof['reopen_passive_comparison'][name]
        path=check/item['snapshot'];assert sha(path)==item['sha256']
        snap=obs.Snapshot(path,verify_checksum=True);loaded[name]=snap
        snapshots[name]={'source_path':str(path),'source_sha256':sha(path),'summary':snap.summary(),
             'N':snap.N,'tick':snap.tick,'points':[snap.observation(obs.coord(i,snap.N)) for i,v in enumerate(snap.raw) if v],
             'protocol_hashes':{k:hashlib.sha256(json.dumps(getattr(snap,k),sort_keys=True,separators=(',',':')).encode()).hexdigest()
                 for k in ('channels','pending','receipts','next_event_id','next_sequence','phase')}}
    equal={k:getattr(loaded['before'],k)==getattr(loaded['after'],k)
           for k in ('N','tick','raw','clocks','channels','pending','receipts','next_event_id','next_sequence','phase')}
    assert all(equal.values())
    active=adoption['actual_active'];p=THINKING/'DEE Cognitive 2.0/sistema'/active['snapshot']
    assert sha(p)==active['snapshot_sha256']
    published=obs.Snapshot(p,verify_checksum=True)
    assert published.tick==727225 and published.raw==loaded['after'].raw and published.clocks==loaded['after'].clocks
    selected={'source_path':str(p),'source_sha256':sha(p),'summary':published.summary(),
         'N':published.N,'tick':published.tick,'life':'ECI02_OPERATIVA_PRINCIPAL_01',
         'points':[published.observation(obs.coord(i,published.N)) for i,v in enumerate(published.raw) if v],
         'adoption_source':str(BASE/'datos/ADOPCION_OPERATIVA_PUBLICADA_R02.json'),
         'adoption_sha256':sha(BASE/'datos/ADOPCION_OPERATIVA_PUBLICADA_R02.json'),
         'published_RAW_clock_equal_reached_candidate':True}
    data={'schema':'DEE.R08.principal.direct_read.v1','new_Native_ticks':0,
          'sources':sources,'reader_panels':rows,'save_restore_snapshots':snapshots,
          'recomputed_save_restore_equality':equal,'selected_principal':selected,
          'panel_recount':read(OUT/'RECALCULO_PANEL_PRINCIPAL_R08.json'),
          'limitations':['Fourteen original outbox files checked; only four relevant reader panels exported.',
              'Empty per-tick traces stay empty: the images show measured endpoints, not invented motion.',
              'The functional panel is in the exact source trajectory later published as principal; adoption itself taught nothing.',
              'Documentary identity metadata changes on publication; physical equality is not asserted for arbitrary unrelated lives.']}
    b=(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n').encode()
    dest.write_bytes(gzip.compress(b,mtime=0))
    print(json.dumps({'output':str(dest),'bytes':dest.stat().st_size,'sha256':sha(dest),'readers':{k:r['output'] for k,r in rows.items()},'save_restore':equal,'Native':0}))

if __name__=='__main__':main()
