"""Export two CLOSED goal/FIFO windows; never reads the live SQLite journal."""
import argparse,collections,gzip,hashlib,importlib.util,json,shutil,sqlite3,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];S=ROOT/'sistema'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);data=(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
    with p.open('xb')as f:f.write(gzip.compress(data,mtime=0)if p.suffix=='.gz'else data)
def copy(p,d):d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
    p=argparse.ArgumentParser();p.add_argument('--primera',type=Path,required=True);p.add_argument('--segunda',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);a=p.parse_args()
    if a.stage.exists():raise FileExistsError('Preserve previous export')
    windows=[a.primera.resolve(),a.segunda.resolve()]
    if any(not(f/'RESUMEN.json').is_file()for f in windows):raise ValueError('Both windows must have stopped and saved their closed primaries')
    a.stage.mkdir(parents=True);ev=a.stage/'EVIDENCIA';ev.mkdir();states={};context={'windows':[],'state_witnesses':{},'artifacts':{},'omitted_full_native':[]}
    observer=module('passive_goal_snapshot',S/'capacidades/observador_causal_retrospectivo_01.py')
    def native_witness(source,expected):
        digest=sha(source)
        if digest!=expected:raise ValueError('Named immutable complete snapshot bytes mismatch')
        if digest in states:return states[digest]
        sn=observer.Snapshot(source,verify_checksum=True);raw=sn.raw;clocks=sn.clocks;default=int(clocks[0])
        relative='ESTADOS/'+digest[:24]+'.json.gz'
        witness={'schema':'APD02.exact_snapshot_causal_fields.v1','source_sha256':digest,'N':sn.N,'tick':sn.tick,
            'RAW_sha256':observer.sha(observer.pbytes(raw)),'clocks_sha256':observer.sha(observer.pbytes(clocks)),
            'rows':[[i,str(v),str(clocks[i])]for i,v in enumerate(raw)if v],
            'clock_default':str(default),'clock_exceptions':[[i,str(v)]for i,v in enumerate(clocks)if v!=default],
            'channels':sn.channels,'pending_native':sn.pending,'metadata':sn.metadata,'next_event_id':sn.next_event_id,
            'next_sequence':sn.next_sequence,'paused':sn.paused,'phase':sn.phase,'checksum_valid':sn.checksum_valid,
            'omitted_native_receipt_ledger_count':len(sn.receipts),
            'scope':'Exact complete physical arrays, interfaces, pending native input and saved metadata/progress; NOT a resumable snapshot. Historical native receipt ledger remains in the local complete state.'}
        write(ev/relative,witness);states[digest]=relative
        context['state_witnesses'][relative]={'source_sha256':digest,'witness_sha256':sha(ev/relative),'N':sn.N,'tick':sn.tick}
        context['omitted_full_native'].append({'source':str(source),'sha256':digest,'bytes':source.stat().st_size,'reason':'Complete native bytes retained locally; exported exact causal fields/current protocol, not a resumable life'})
        del sn;return relative
    for number,source in enumerate(windows,1):
        tag='W'+str(number);dest=ev/tag;dest.mkdir();x=read(source/'REGISTROS_VENTANA.json.gz');proto=read(source/'PROTOCOLO.json')
        if x.get('error')or x['owner_final']['running']:raise ValueError('Do not treat a failed/live window as a closed proof')
        for name in('REGISTROS_VENTANA.json.gz','PROTOCOLO.json','ADMISIONES.jsonl','CODIGO_EJECUTADO.py','FUENTES_ANTES_TICKS.json','RESUMEN.json','OWNER_OUT.txt','OWNER_ERR.txt'):copy(source/name,dest/name)
        shutil.copytree(source/'codigo',a.stage/'FUENTES'/tag)
        for item in read(source/'FUENTES_ANTES_TICKS.json'):
            f=a.stage/'FUENTES'/tag/item['file']
            if f.stat().st_size!=item['bytes']or sha(f)!=item['sha256']:raise ValueError('Frozen executed source mismatch')
        export=x['export']['paired_export'];manifest_path=Path(export['directory'])/'EXPORTACION_SERVICIO.json'
        if sha(manifest_path)!=export['manifest_sha256']:raise ValueError('Immutable paired-export manifest changed')
        manifest=read(manifest_path);export_root=manifest_path.parent;members={m['file']:m for m in manifest['members']}
        def member(relative):
            f=export_root/relative;m=members[relative]
            if not f.resolve().is_relative_to(export_root.resolve())or f.stat().st_size!=m['bytes']or sha(f)!=m['sha256']:raise ValueError('Actual paired-export member differs')
            return f
        copy(manifest_path,dest/'EXPORTACION_SERVICIO.json')
        # Only the CLOSED immutable export backup, never S/.../cola.sqlite3.
        dbfile=member('cola.sqlite3');dbsha=sha(dbfile)
        if dbfile.parent.resolve()!=export_root.resolve()or dbfile.name!='cola.sqlite3':raise ValueError('Not an archived export journal')
        conn=sqlite3.connect(dbfile.as_uri()+'?mode=ro&immutable=1',uri=True);conn.row_factory=sqlite3.Row
        selected=set(k for k in x['records']if not k.endswith('_parsed'))|{r['id']for r in x['pending']}|{r['id']for r in proto.get('expected_initial_pending',[])}
        selected_rows=[dict(r)for r in conn.execute('SELECT * FROM requests WHERE id IN('+','.join('?'for _ in selected)+') ORDER BY seq',sorted(selected))]
        unresolved=[dict(r)for r in conn.execute("SELECT * FROM requests WHERE status IN('queued','processing','uncertain') ORDER BY seq")]
        schema=[dict(r)for r in conn.execute("SELECT type,name,sql FROM sqlite_master WHERE name IN('requests','meta') ORDER BY name")]
        counts=[dict(r)for r in conn.execute('SELECT status,count(*) AS count FROM requests GROUP BY status ORDER BY status')]
        conn.close()
        if sha(dbfile)!=dbsha:raise ValueError('Archived DB changed during immutable read')
        write(dest/'COLA_EXPORTADA_OBSERVADA.json',{'source_sha256':dbsha,'bytes':dbfile.stat().st_size,'selected_rows':selected_rows,
            'outstanding':unresolved,'schema':schema,'counts':counts,'source_locator':str(dbfile),'read_mode':'SQLite mode=ro immutable=1 of manifest-validated closed export; live journal was not opened'})
        export_id=x['export']['id'];outbox=member('resultados/'+export_id+'.json');copy(outbox,dest/'OUTBOX_EXPORT_ORIGINAL.json')
        exported_native=member(manifest['native_snapshot'])
        entry={'tag':tag,'folder':tag,'initial_state':native_witness(S/x['initial']['snapshot'],x['initial']['snapshot_sha256']),
            'export_state':native_witness(exported_native,manifest['snapshot_sha256']),
            'final_state':native_witness(S/x['final']['snapshot'],x['final']['snapshot_sha256']),
            'paired_manifest_sha256':sha(manifest_path),'database_sha256':dbsha,'outbox_export_sha256':sha(outbox)}
        context['windows'].append(entry)
        for identifier,transport in x['records'].items():
            if identifier.endswith('_parsed'):continue
            parsed=json.loads(transport['result']);result=parsed.get('result',{});rows=result.get('rows',[])
            if not rows:continue
            payload=json.loads(transport['payload']);situations=payload['situaciones'];last_episode=result['final']['operational']['episodes']
            for slot,(situation,row)in enumerate(zip(situations,rows)):
                episode=last_episode-(len(rows)-slot-1);mode=situation['modo'];operations=[]
                if row.get('kind')=='APD02_native_goal_opportunities':
                    dirname=('apd02_goal_'if mode=='apd02-meta'else'apd02_goal_resume_')+str(episode)+'/world'
                    operations=[(o['opportunity'],o['environment_effect'].get('committed_effect'))for o in row['result']['opportunities']]
                elif row.get('kind')=='APD02_quality_request':dirname='apd02_'+str(episode);operations=[(0,row['committed_effect'])]
                else:continue
                for opportunity,receipt in operations:
                    if not receipt or not receipt.get('artifact'):continue
                    artifact=receipt['artifact'];relative='artefactos_trabajador/'+dirname+'/'+artifact['relative_path'];actual=member(relative)
                    if actual.stat().st_size!=artifact['bytes']or sha(actual)!=artifact['sha256']:raise ValueError('Real actual goal file disagrees with committed effect')
                    target='ARTEFACTOS/'+tag+'/'+identifier+'_'+str(slot)+'_'+str(opportunity)
                    copy(actual,ev/target/artifact['relative_path'])
                    context['artifacts'][tag+':'+identifier+':'+str(slot)+':'+str(opportunity)]={'directory':target,'relative_export_member':relative,
                        'bytes':artifact['bytes'],'sha256':artifact['sha256'],'episode_inferred_from_frozen_session_counter':episode}
    for name in('auditar_evento_objetivo_apd02_r02.py','recalcular_main_objetivo_r01.py',Path(__file__).name):copy(HERE/name,a.stage/'RECALCULO'/name)
    copy(S/'capacidades/observador_causal_retrospectivo_01.py',a.stage/'RECALCULO/observador_causal_retrospectivo_01.py')
    write(ev/'CONTEXTO_ARCHIVADO.json',context)
    print(json.dumps({'stage':str(a.stage),'windows':len(windows),'state_witnesses':len(states),'actual_files':len(context['artifacts']),'native_ticks':0},ensure_ascii=False))
if __name__=='__main__':main()
