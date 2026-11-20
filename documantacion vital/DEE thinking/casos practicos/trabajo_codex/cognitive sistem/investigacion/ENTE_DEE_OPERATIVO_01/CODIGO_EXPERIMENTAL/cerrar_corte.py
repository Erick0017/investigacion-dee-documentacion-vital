"""Cierra el corte alcanzado desde archivos existentes. No importa el motor."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,gzip,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];SYSTEM=ROOT/'sistema';E=ROOT/'evidencia/campanas/ENTE_DEE_OPERATIVO_01';C=HERE/'cierre'
sys.path.insert(0,str(SYSTEM))
from capacidades.observador_causal_retrospectivo_01 import Snapshot
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,r):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():raise FileExistsError('Closed result protected: '+str(p))
    p.write_text(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def main():
    final=json.load(gzip.open(E/'54_CONTINUACION_NUEVO_PROCESO.json.gz','rt',encoding='utf8'))['result'];s=final['result']['final']
    rec=read(SYSTEM/'estado/vidas/EO01_MAIN/VIDA.json')
    assert rec['physical']['tick']==121681
    snap=Snapshot(SYSTEM/rec['snapshot']);assert snap.encoded_sha256==rec['snapshot_sha256']
    protected=[]
    for life,expected in [('CF01_MAIN','205a34e3b0925fe6d9631d4934aaf29c427171f123d4176adf68bf44d76e07bb'),('E1_SOCIAL_11','51e2ec6a41f906607848c003c6a22e3e33690f57d20dcae90c8dbbc7ab9ad396')]:
        r=read(SYSTEM/'estado/vidas'/life/'VIDA.json');actual=sha(SYSTEM/r['snapshot'])
        assert actual==r['snapshot_sha256']==expected
        protected.append({'life':life,'tick':r['physical']['tick'],'snapshot':r['snapshot'],'sha256':actual,'original_protected_state_unchanged':True})
    active=read(SYSTEM/'estado/ACTIVO.json');assert active['life_id']=='E1_SOCIAL_11'and active['tick']==3154
    life_index=[]
    for p in sorted((SYSTEM/'estado/vidas').glob('EO01*/VIDA.json')):
        r=read(p);f=SYSTEM/r['snapshot']
        life_index.append({'life':r['life_id'],'parent':r.get('parent'),'branch':r['branch'],'profile':r['profile'],'tick':r['physical']['tick'],'snapshot':r['snapshot'],'sha256':r['snapshot_sha256'],'bytes':f.stat().st_size,'record':p.relative_to(ROOT).as_posix(),'not_a_merge_of_other_branches':True})
    summary=snap.summary();write(E/'SNAPSHOT_FINAL_COMPLETO_VERIFICADO.json',{'summary':summary,'channels':snap.channels,'pending':snap.pending,'no_ticks':True,'decoded_checksum_valid':snap.checksum_valid,'scope':'Complete saved bytes parsed; no restoration or native functional test. Native restoration/use occurred in manager operation54.'})
    continuity={'schema':'EO01.continuity.closed.v1','closed_scientific_utc':datetime.now(timezone.utc).isoformat(),'software':'Cognitive1.1.0 / EO01protocol3','life':'EO01_MAIN','profile':rec['profile'],'architecture':'Lived MI02.unified.r9 N26 with A/B and explicit external fixtures','parent':rec['parent'],'tick':rec['physical']['tick'],'snapshot':rec['snapshot'],'snapshot_sha256':rec['snapshot_sha256'],'physical':rec['physical'],'own_reference':[q['s_reg']for q in s['witness']['own']],'context':[q['s_reg']for q in s['witness']['context_A']],'B_private_reference':[q['s_reg']for q in s['witness']['private_B']],'external_environment':s['service']['environment'],'FIFO':s['service']['queue'],'bookkeeping_note':'calibrated backlog lists failed attempts, not open FIFO jobs. service.revision1 is historical metadata; actual code revision3 and per-episode source hashes identify the running protocol.','pending_inputs':len(snap.pending),'last_operation':'54: complete saved life loaded in a new process, new raw jobs23:35 and11:24,2/2 useful,+/-; no reset or field repair.','current_capacity':'Relative native comparison/use with effective local calibration12; mutable by later actual consequences; privateB61/19 and context7/5 retained. Optional external B-valve instrument available, disabled in current explicitly reset FIFO fixture. Not65semantics or general control.','negative_limits':['Direct new B messages do not persistently overwrite occupied context7/5 or alter A actions in the examined native path.','Old calibrated relations9/6/10 are historical states, not three simultaneously retained context-sensitive concepts.','Motor sample/hold1, opportunity calendars and generic supplies remain prepared assistance.','Queue retry initiation belongs to environment. B valve/resource transduction is external P0.'], 'continuation_commands':['bifurcar EO01_MAIN MI_ENTE','ente-servicio --vida MI_ENTE --mediciones=23:35,11:24','guardar --vida MI_ENTE','ente-servicio --vida MI_ENTE --mediciones=6:18,10:23'],'same_world_not_T0_reconstruction':True,'protected_originals':protected,'active_unchanged':active,'all_new_lives_index':'evidencia/campanas/ENTE_DEE_OPERATIVO_01/INDICE_ESTADOS_COMPLETOS.json','full_snapshots_local_and_selected_in_collaboration_zip':True,'analysis_zip_is_not_an_operational_backup':True}
    write(ROOT/'CONTINUIDAD_ENTE_DEE_OPERATIVO_01.json',continuity)
    write(E/'INDICE_ESTADOS_COMPLETOS.json',{'schema':'EO01.local_complete_states.v1','system_root_at_execution':str(SYSTEM),'entries':life_index,'protected_originals':protected,'no_ticks':True,'all_diagnostic_lives_remain_separate':True})
    write(HERE/'REANUDACION.json',{'status':'SCIENTIFIC_CUT_CLOSED_NO_AUTOMATIC_NEW_CAMPAIGN','life':'EO01_MAIN','tick':121681,'snapshot':rec['snapshot'],'sha256':rec['snapshot_sha256'],'main_writer_stopped':True,'remaining_work':'Integration documents, clean exact-ZIP distribution test and final analysis export; do not advance original MAIN for these checks.','budget':'PRESUPUESTO.json remains the original8hour limit; never restart.'})
    print(json.dumps({'life':'EO01_MAIN','tick':121681,'snapshot':rec['snapshot'],'checksum':snap.checksum_valid,'channels':len(snap.channels),'pending':len(snap.pending),'receipts':len(snap.receipts),'new_lives':len(life_index),'protected_originals':protected},ensure_ascii=False))
if __name__=='__main__':main()
