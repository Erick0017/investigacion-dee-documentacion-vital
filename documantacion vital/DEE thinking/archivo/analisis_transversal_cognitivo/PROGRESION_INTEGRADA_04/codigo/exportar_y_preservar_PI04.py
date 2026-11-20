"""Existing paused-owner full export, then verified atomic move to stable RP.

The same process retains the actual owner handle until its clean exit, avoiding
PID-reuse assumptions. No experimental queries, Native steps or promotion.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,sys
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0'
S=P/'estados/candidato_R02/sistema';RP=C/'reproducibilidad'
sys.path.insert(0,str(P/'codigo'))
from servicio_ensayo_R02 import Owner
sys.path.insert(0,str(RP))
from preservar_revision_pi03 import pair_check,valid_name
from observador_pasivo import snapshot_view,compare_native

def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def load(f):return json.loads(f.read_text(encoding='utf-8-sig'))
def write_new(path,data):
    with path.open('x',encoding='utf-8')as f:
        json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--vida',required=True)
    ap.add_argument('--alias',required=True);ap.add_argument('--tick',required=True,type=int)
    a=ap.parse_args();assert a.vida.startswith('ECI02_PI03_REPRO_PI04_')
    alias=valid_name(a.alias);destination=RP/'materiales'/alias
    proof=P/'control'/('EXPORTACION_ESTABLE_'+alias+'.json')
    assert not destination.exists()and not proof.exists()
    cardfile=S/'estado/vidas'/a.vida/'VIDA.json';card=load(cardfile)
    assert card['physical']['tick']==a.tick
    before=snapshot_view(S/card['snapshot'])
    with Owner(a.vida,'PI04_EXPORT_'+alias)as owner:
        assert owner.initial['paused'] and owner.initial['tick']==a.tick
        row=owner.control('exportar')
        value=json.loads(row['result'])if isinstance(row['result'],str)else row['result']
        assert value['before_tick']==value['after_tick']==a.tick
    assert owner.proc.poll()==0 and owner.job is None,'Own exact writer must be cleanly closed, not merely a stale status'
    card_after=load(cardfile);current=snapshot_view(S/card_after['snapshot'])
    comparison=compare_native(before,current,allow_service=True)
    pair=value['paired_export'];source=Path(pair['directory']).resolve(strict=True)
    expected=(S/'estado/servicios_persistentes'/a.vida/'exportaciones').resolve(strict=True)
    assert source.parent==expected and source.is_dir()and not source.is_symlink()
    assert destination.resolve(strict=False).is_relative_to((RP/'materiales').resolve())
    assert source.drive.casefold()==destination.drive.casefold()
    for base,dirs,files in os.walk(source,followlinks=False):
        for n in [*dirs,*files]:
            f=Path(base)/n
            assert not f.is_symlink()and not(getattr(f.lstat(),'st_file_attributes',0)&0x400),'No linked export members'
    entry={'source':str(source),'manifest_sha256':pair['manifest_sha256'],'life_id':a.vida,'N':67,'tick':a.tick}
    _,manifest,checked=pair_check(entry)
    exported=snapshot_view(source/'VIDA.deetsnap.gz')
    exported_comparison=compare_native(exported,current,allow_service=True)
    cfgfile=RP/'RECURSOS.json';cfgbytes=cfgfile.read_bytes();cfg=json.loads(cfgbytes)
    assert alias not in cfg['pairs']
    stage=proof.with_name(proof.stem+'_EN_CURSO.json')
    record={'schema':'DEE.PI04.stable_closed_full_pair.v1','local_cut':datetime.datetime.now().astimezone().isoformat(),'life_id':a.vida,'tick':a.tick,'source':str(source),'destination':str(destination),'alias':alias,'manifest_sha256':pair['manifest_sha256'],'source_physical':card_after['physical'],'zero_tick_export_comparison':comparison,'export_source_comparison':exported_comparison,'actual_owned_process_handle_exit_code':owner.proc.poll(),'actual_owned_job_closed':owner.job is None,'paired_export_transport':row,'new_native_ticks':0,'copied_full_pair':False,'no_principal_selected':True,'historical_paths_rewritten':False,'completed':False}
    write_new(stage,record)
    source.rename(destination)
    _,_,after=pair_check(dict(entry,source=str(destination)))
    assert after==checked and not source.exists()
    assert cfgfile.read_bytes()==cfgbytes,'Concurrent resource edits: preserve stage and destination, never retry'
    backup=P/'control'/('RECURSOS_ANTES_'+alias+'.json');backup.write_bytes(cfgbytes)
    cfg['pairs'][alias]={'product_relative':destination.relative_to(C).as_posix(),'manifest_sha256':pair['manifest_sha256'],'life_id':a.vida,'N':67,'tick':a.tick,'role':'scientific_prefix','source':str(source),'source_relocation':{'proof':str(proof),'origin':str(source),'current':str(destination),'manifest_sha256':pair['manifest_sha256']}}
    tmp=cfgfile.with_name('RECURSOS.'+alias+'.writing');write_new(tmp,cfg);os.replace(tmp,cfgfile)
    record.update(completed=True,members=len(manifest['members']),bytes=sum(x['bytes']for x in manifest['members']),registered_resources_sha256=sha(cfgfile),after_pair_check=after)
    write_new(proof,record)
    print(json.dumps({'proof':str(proof),'pair':str(destination),'tick':a.tick,'members':record['members'],'bytes':record['bytes'],'manifest_sha256':pair['manifest_sha256'],'new_Native_ticks':0},ensure_ascii=False))
if __name__=='__main__':main()
