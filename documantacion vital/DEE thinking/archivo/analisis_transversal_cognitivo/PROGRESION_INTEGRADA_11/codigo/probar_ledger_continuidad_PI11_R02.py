"""Pure temporary-file witnesses for budget continuity; never DEE/Native."""
from pathlib import Path
import hashlib,importlib.util,json,os,shutil,tempfile
H=Path(__file__).resolve().parent; P=H.parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(v,indent=2)+'\n','utf8')
def main():
    folder=Path(tempfile.mkdtemp(prefix='PI11_pure_ledger_R02_')); root=folder/'ROOT'; campaign=root/'archivo/analisis_transversal_cognitivo/PROGRESION_INTEGRADA_11'; product=root/'DEE Cognitive 2.0'; source=campaign/'codigo/ledger_PI11_R01.py'; source.parent.mkdir(parents=True); shutil.copyfile(H/'ledger_PI11_R01.py',source)
    sp=importlib.util.spec_from_file_location('PI11_pure_ledger_under_test',H/'ledger_continuidad_PI11_R02.py'); m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); m.P=campaign; m.C=product; m.SOURCE=source
    main=m.MAIN; none=main.replace('_MAIN01','_NONE01'); initial=947395; tick=975259
    for slug,life,current in (('MAIN01',main,tick),('NONE01',none,initial)):
        write(campaign/'estados'/slug/'sistema/estado/vidas'/life/'VIDA.json',{'life_id':life,'physical':{'tick':current}})
        write(campaign/'estados'/slug/'IMPORTACION_DIAGNOSTICA.json',{'life':life,'result':{'physical':{'tick':initial}}})
    write(campaign/'control/PI11_MAIN01_16_OWNER_R01.json',{'schema':'DEE.PI11.actual.finite_owner_plan.R01','life_id':main,'closed':True,'error':None})
    write(campaign/'control/PI11_NONE01_16_OWNER_R01.json',{'schema':'DEE.PI11.actual.finite_owner_plan.R01','life_id':none,'closed':False,'error':{'type':'instrumental0t'},'initial_tick':initial,'finite_bound':32256})
    before=m.ledger(); old=campaign/'estados/MAIN01/sistema/estado/vidas'/main; target=product/'sistema/estado/vidas'/main; target.parent.mkdir(parents=True); os.rename(old,target)
    mapping=campaign/'control/MAPA_TRASLADO_PRODUCTO_PI11_R01.json'; write(mapping,{'same_life_id':main,'same_world_id':main,'source_system':str(campaign/'estados/MAIN01/sistema'),'target_system':str(product/'sistema')})
    write(campaign/'control/PREPARACION_TRASLADO_PRODUCTO_PI11_R01.json',{'phase':'PREPARED_MOVED_NOT_PROMOTED','life_id':main,'map':{'path':str(mapping),'sha256':sha(mapping)}})
    after=m.ledger(); keys=('observed_saved_ticks','charged_ticks','world_count')
    assert all(before[k]==after[k] for k in keys) and after['world_count']==2 and after['charged_ticks']==tick-initial+32256
    card=target/'VIDA.json'; v=json.loads(card.read_text('utf8')); v['physical']['tick']+=1564; write(card,v); public=m.ledger(); assert public['charged_ticks']==after['charged_ticks']+1564 and public['world_count']==2
    old.mkdir(parents=True); shutil.copyfile(card,old/'VIDA.json')
    duplicate=False
    try: m.ledger()
    except ValueError: duplicate=True
    assert duplicate
    (old/'VIDA.json').unlink(); old.rmdir()
    write(campaign/'control/PI11_PRODUCTO_PUBLICO_OWNER_R01.json',{'schema':'DEE.PI11.actual_public_interface_owner.R01','life_id':main,'closed':False,'error':{'type':'uncertain_fixture'},'initial_tick':tick+1564,'finite_bound':2016})
    uncertain=m.ledger(); assert uncertain['charged_ticks']==public['charged_ticks']+2016 and uncertain['world_count']==2
    # Preserve the pure fixture outside every real state tree for inspection.
    result={'schema':'DEE.PI11.pure_same_ID_budget_continuity_tests.R02','Native_executed':False,'new_Native_ticks':0,'DEE_imported':False,'fixture':str(folder),'passed':5,'checks':{'same_totals_before_after_whole_move':True,'NONE_32256_bound_not_refunded':True,'public_continuation_charged_same_world':True,'duplicate_same_ID_rejected':True,'uncertain_public_phase_bound_retained':True},'before':{k:before[k]for k in keys},'after':{k:after[k]for k in keys},'after_public':{k:public[k]for k in keys},'ledger_R02_sha256':sha(H/'ledger_continuidad_PI11_R02.py')}
    out=P/'control/PRUEBAS_PURAS_LEDGER_CONTINUIDAD_PI11_R02_B.json'
    if out.exists(): raise FileExistsError('Preserve prior pure proof')
    write(out,result); print(json.dumps({'proof':str(out),'passed':5,'Native':0}))
if __name__=='__main__':main()
