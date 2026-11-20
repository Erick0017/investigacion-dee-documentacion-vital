"""Create a portable three-snapshot index and exact pack-selection snippet.

Only reads explicitly named closed snapshot bytes with the standalone
passive parser. Does not load DEE, restore a life or copy an operational tree.
"""
from pathlib import Path,PurePosixPath
import argparse,hashlib,importlib.util,json
H=Path(__file__).resolve().parent
def need(ok,why):
    if not ok:raise ValueError(why)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fuentes',type=Path,required=True);p.add_argument('--salida-indice',type=Path,required=True);p.add_argument('--salida-seleccion',type=Path,required=True);args=p.parse_args()
    cfg=json.loads(args.fuentes.read_text('utf-8-sig'));need(cfg['schema']=='DEE.PI10.snapshot_export_sources.R01','Explicit actual closed snapshot sources')
    need(not args.salida_indice.exists()and not args.salida_seleccion.exists(),'No overwrite of existing snapshot indices')
    sp=importlib.util.spec_from_file_location('passive',H/'recalcular_snapshots_incluidos_PI10_R01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
    entries=[];files=[];roles=set()
    for source in cfg['snapshots']:
        role=source['role'];need(role in('neutral','learned','replay','principal_final')and role not in roles,'Unique snapshot role');roles.add(role)
        path=Path(source['source']).resolve(strict=True);need(path.name.endswith('.deetsnap.gz'),'Whole original compressed snapshot only')
        b=path.read_bytes();view,_=m.parse(b,source['life_id']);name=source['filename'];need(PurePosixPath(name).name==name and ':'not in name and '\\'not in name,'Simple internal filename')
        entries.append({'role':role,'file':name,'sha256':hashlib.sha256(b).hexdigest(),'life_id':source['life_id'],'expected_physical':view['physical'],'optional_analysis_role':role=='principal_final'})
        files.append({'source':str(path),'member':cfg['zip_snapshot_directory'].rstrip('/')+'/'+name,'role':'optional_snapshot','required':True,'optional':True,
          'priority':0 if role=='principal_final'else 10 if role=='replay'else 20 if role=='learned'else 30})
        need(path.read_bytes()==b,'Snapshot changed concurrently; no index')
    need({'neutral','learned','replay'}<=roles,'Three required analytical roles must be present')
    index={'schema':'DEE.PI10.three_snapshot_analysis.R01','snapshots':entries,
      'scope':'Whole Native snapshots only. SQLite, environment artifacts and complete operational stores stay local. No Native execution or restoration in this preparation.'}
    args.salida_indice.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n','utf8')
    indexmember=cfg['zip_snapshot_directory'].rstrip('/')+'/INDICE_SNAPSHOTS.json'
    snippet={'schema':'DEE.PI10.snapshot_pack_selection_snippet.R01','files':[{'source':str(args.salida_indice.absolute()),'member':indexmember,'role':'snapshot_index'},*files],
      'pure_recalculation':{'script':cfg.get('zip_recalc_directory','CODIGO_Y_RECALCULO').rstrip('/')+'/recalcular_snapshots_incluidos_PI10_R01.py',
        'args':['--indice',indexmember,'--salida','05_CONTROL/RECALCULO_SNAPSHOTS_EXTRAIDO.json'],'output':'05_CONTROL/RECALCULO_SNAPSHOTS_EXTRAIDO.json',
        'schema':'DEE.PI10.portable_snapshot_prefix_analysis.R01','requires_optional_members':[f['member']for f in files if f['priority']>0],
        'skip_if_optional_evidence_omitted':True},'Native_executed':False}
    args.salida_seleccion.write_text(json.dumps(snippet,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps({'index':str(args.salida_indice),'index_sha256':hashlib.sha256(args.salida_indice.read_bytes()).hexdigest(),'selection':str(args.salida_seleccion),'Native_executed':False}))
if __name__=='__main__':main()
