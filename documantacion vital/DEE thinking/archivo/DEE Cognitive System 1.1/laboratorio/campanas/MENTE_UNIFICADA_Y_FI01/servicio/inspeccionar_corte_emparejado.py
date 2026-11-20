"""Read-only prospective distribution cut, not a new service export or tick."""
import argparse,gzip,hashlib,importlib.util,json,sqlite3
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--sistema',type=Path,required=True);a.add_argument('--evidencia',type=Path,required=True);a.add_argument('--salida',type=Path,required=True);p=a.parse_args();s=p.sistema
    card=s/'estado/vidas/MU_MAIN/VIDA.json';v=json.loads(card.read_bytes());sup=json.loads(gzip.decompress((p.evidencia/'SUPLEMENTO_60S_R12/SUPLEMENTO.json.gz').read_bytes()));db=s/'estado/servicios_persistentes/MU_MAIN/cola.sqlite3'
    spec=importlib.util.spec_from_file_location('_read_only_cut_observer',s/'capacidades/observador_causal_retrospectivo_01.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    snapshot=mod.Snapshot(s/v['snapshot']);old=sup['export']['result']['paired_export']if'result'in sup['export']else sup['export']['paired_export']
    # Actual control wrapper is preserved; find, never infer, its export object.
    def walk(x):
        if isinstance(x,dict):
            if x.get('schema')=='DEE.persistent_service.paired_export.v1':yield x
            for y in x.values():yield from walk(y)
        elif isinstance(x,list):
            for y in x:yield from walk(y)
    export_dir=Path(old['directory']);manifest=export_dir/'EXPORTACION_SERVICIO.json';em=json.loads(manifest.read_bytes());old_snapshot=export_dir/em['native_snapshot'];historical=mod.Snapshot(old_snapshot)
    with sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)as con:
        integrity=con.execute('PRAGMA integrity_check').fetchone()[0];owner=json.loads(con.execute('SELECT value FROM meta WHERE key=?',('owner',)).fetchone()[0]);pending=[list(r)for r in con.execute('SELECT id,status FROM requests WHERE status IN (?,?,?)',('queued','processing','uncertain'))]
    protocol=json.loads(snapshot.metadata['DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'])
    r={'schema':'DEE.unified.prospective_paired_distribution_cut.v1','native_ticks':0,'no_Runtime_restored':True,'local_record':{'file':str(card),'sha256':sha(card),'snapshot':v['snapshot'],'snapshot_sha256':v['snapshot_sha256'],'physical':v['physical'],'descriptor':v.get('persistent_service')},'earlier_explicit_export':{'directory':str(export_dir),'manifest_sha256':sha(manifest),'snapshot':str(old_snapshot),'snapshot_sha256':sha(old_snapshot),'physical':em['physical']},'RAW_clocks_same_between_export_and_after_STOP':snapshot.raw==historical.raw and snapshot.clocks==historical.clocks,'complete_snapshots_are_not_claimed_byte_identical':sha(s/v['snapshot'])!=sha(old_snapshot),'current_transport':{'file':str(db),'sha256':sha(db),'integrity_check':integrity,'owner':owner,'pending':pending},'current_snapshot_protocol':protocol,'scope':'Updater must create a new logical paired-package manifest using the CURRENT stopped-world snapshot named by VIDA plus current durable SQLite, exact results and worker artifacts. It must not claim that the earlier fi60s_export is the same byte snapshot. This is a zero-tick read-only selection record, not another runtime or a replacement for the current physical state.'}
    r['issues']=[]
    if sha(s/v['snapshot'])!=v['snapshot_sha256']or integrity!='ok'or owner.get('running')or pending:r['issues'].append('Selected current cut is not ready for stopped paired packaging')
    if snapshot.tick!=protocol['native_tick_at_checkpoint']:r['issues'].append('Protocol physical binding differs')
    p.salida.parent.mkdir(parents=True,exist_ok=True);p.salida.write_text(json.dumps(r,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(r,ensure_ascii=False));return bool(r['issues'])
if __name__=='__main__':raise SystemExit(main())
