"""Default read-only. Root --aplicar syncs only current metadata and closes facts.
Never edits ACTIVO, promotion receipts, snapshots, queues, engine or history.
"""
from pathlib import Path
import argparse,copy,datetime,hashlib,json,os,shutil,sqlite3
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';LIFE='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
CURRENT='af74c8f47e43ed3b2395a338a23a6cbd42f105ec2cff4daac15b7a4d45e90832'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return{'path':str(Path(p).resolve()),'sha256':sha(p)}
def need(x,s):
 if not x:raise ValueError(s)
def atomic(path,value):
 tmp=path.with_name(path.name+'.pi05_post0.tmp');need(not tmp.exists(),'Existing interrupted metadatawrite preserved')
 with tmp.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,path)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');a=ap.parse_args()
 out=P/'control/SINCRONIZACION_POST_REAPERTURA_PI05.json';need(not out.exists(),'Existing synchronization preserved, never repeatblindly')
 reopening=P/'control/REAPERTURA_SELECCIONADA_PRODUCTO_PI05.json';adoption=P/'control/ADOPCION_PRODUCTO_PI05.json';facts=P/'control/CIERRE_CIENTIFICO_PI05.json'
 proof=read(reopening);adopt=read(adoption);active_file=S/'estado/ACTIVO.json';active=read(active_file);card_file=S/'estado/vidas'/LIFE/'VIDA.json';card=read(card_file)
 need(adopt['phase']=='COMMITTED'and adopt['life_id']==LIFE and active['life_id']==LIFE and active['world_id']==card['world_id']and active['tick']==824911 and active['snapshot_sha256']==CURRENT and active['snapshot']==card['snapshot'],'Actual active pointer must match current selected0cut; historical COMMITTED receipt remains separate')
 need(sha(active_file)==proof['global_active_after_sha256'],'Current active file changed after selected0proof')
 need(proof['life_id']==LIFE and proof['new_ticks']==0 and all(proof[k]is True for k in('physical_unchanged','pending_reconciled','operational_state_valid','owner_closed'))and proof.get('error')is None,'Actual selected0reopening mustbe closed/valid')
 need(card['physical']==adopt['record']['physical']and card['physical']['N']==67 and card['physical']['tick']==824911 and card['snapshot_sha256']==proof['snapshot_sha256']==CURRENT and sha(S/card['snapshot'])==CURRENT,'Current exact saved selected0cut required')
 need(not(S/'estado/locks'/(card['world_id']+'.lock')).exists()and not(card_file.parent/'FUTURO_INTERRUMPIDO.json').exists(),'Preserve live/interruptedworld')
 db=S/'estado/servicios_persistentes'/LIFE/'cola.sqlite3';need(not any(Path(str(db)+suffix).exists()for suffix in('-wal','-shm','-journal')),'SQLiteauxpresent; no writingagainstuncertainowner')
 con=sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  owner=json.loads(con.execute("select value from meta where key='owner'").fetchone()[0]);need(not owner.get('running'),'Target ownerstillrunning')
  need(not con.execute("select id from requests where status in('queued','processing','uncertain')").fetchall(),'Unconciliated transport')
 finally:con.close()
 project_path=C/'PROYECTO.json';continuity_path=C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json';seed_path=C/'aplicacion/GENESIS/SELECCION_CANDIDATA.json'
 paths=[project_path,continuity_path,seed_path,facts];before={str(x):sha(x)for x in paths};protected={str(x):sha(x)for x in(active_file,adoption,reopening,card_file,S/card['snapshot'])}
 project=read(project_path);continuity=read(continuity_path);seed=read(seed_path);m=read(facts);need(project['selected_life']==continuity['life_id']==LIFE and seed['source_alias']==LIFE,'Currentselectorsmustagree')
 need(seed['source_snapshot_sha256']=='a63805765aaff9a1de938fd70181771f6f7b784bd19784472b895ab341ec1c31','Preserve exact historical science seed')
 old_pointer=copy.deepcopy(continuity['latest_snapshot']);old_id=copy.deepcopy(continuity['identity_card']);stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();current={'path_relative_to_product':'sistema/'+card['snapshot'],'sha256':CURRENT}
 project['current_operational_snapshot']=current;project['current_operational_identity_card_sha256']=sha(card_file);project['latest_saved_tick']=824911
 continuity['latest_snapshot']=current;continuity['identity_card']={'path_relative_to_product':'sistema/estado/vidas/'+LIFE+'/VIDA.json','sha256':sha(card_file)};continuity['updated_utc']=stamp
 seed['current_operational_snapshot_sha256']=CURRENT;continuity['selected_seed']=seed
 continuity['PI05_post_selected_reopening']={'proof':info(reopening),'previous_pointer_historical':old_pointer,'previous_identity_card_historical':old_id,'new_ticks':0,'actual_current_snapshot':current,'current_active_pointer_is_distinct_from_historical_commit':True,'historical_committed_reference':adopt['active']}
 principal_text='El único principal es '+LIFE+', perfil fisica_directa, N67, T824911, adoptado COMMITTED. Su padre físico es ECI02_PI03_MAIN, T775355, preservado literalmente. La reapertura seleccionada cerró con cero ticks; el snapshot corriente es af74c8f47e43ed3b2395a338a23a6cbd42f105ec2cff4daac15b7a4d45e90832. La referencia histórica de promoción bb67e5f9b5589f7374b8f446a66ea4544ab453352c862bdd58cd224a7a1c32c2 permanece sin reescritura.'
 summary='PI05 localizó una interferencia y añadió protección física preparada P0. La misma continuación conserva 12 usos históricos, tres comparaciones nuevas y seis productos C2C, con reaperturas. Se adoptó '+LIFE+', N67, T824911; padre físico PI03 T775355. La secuencia sigue asistida y no se demuestra elección aprendida de la guardia ni agencia general.'
 m['principal']={'life_id':LIFE,'N':67,'tick':824911,'profile':'fisica_directa','physical_parent':'ECI02_PI03_MAIN T775355','status':'COMMITTED','current_snapshot_sha256':CURRENT,'historical_committed_snapshot_sha256':adopt['active']['snapshot_sha256']}
 m['cover_summary']=summary;m['resume4']=principal_text;m['release_cut']='Corte científico PI05 del '+m['cut_date_local']+'. '+principal_text;m['state_of_edition']='Edición documental 1.32; base 1.31 preservada literalmente. '+principal_text;m['core_description']='PI05 tránsito causal, protección física preparada P0, conservación conjunta y adopción real del único principal N67 T824911. No agencia general ni guardia aprendida.';m['compendium_current_summary']=summary
 section=next(x for x in m['sections']if x['title'].startswith('48.9'));section['paragraphs'][0]=principal_text+' El conjunto completo se transfirió sin fusionar recuerdos. Se cambió sólo la hoja administrativa corriente C2C.life_id que exige el nuevo contenedor; la comparación de RAW, clocks, interfaces, agenda, recibos y contenidos restantes pasó.'
 section['paragraphs'][-1]='Desde la raíz de Cognitive, motor/python313/python.exe -I -B sistema/gestionar.py reproducibilidad listar muestra las recetas. El mismo comando seguido de verificar pi05_guardia_y_sham_transito_R01 comprueba requisitos sin Native. Reproducir exige esa receta, --variante guardia, una --vida diagnóstica nueva, --destino nuevo y --material. El replay real verificado se conserva en el registro; no se debe ejecutarlo sobre el principal. El uso operativo de C2C conserva el modo existente eci01-pi04-c2c-oportunidad; eci01-pi04-c2c-estado no avanza ticks. Quedan dos ofertas ambientales disponibles.'
 m['compendium_paragraphs'][-1]=m['compendium_paragraphs'][-1].replace('[[CIERRE_REAL_PENDIENTE_SELECCION]]',principal_text)
 m['sources']+=['control/ADOPCION_PRODUCTO_PI05.json','control/REAPERTURA_PRODUCTO_PI05.json y REAPERTURA_SELECCIONADA_PRODUCTO_PI05.json','control/SINCRONIZACION_POST_REAPERTURA_PI05.json','control/COMANDOS_RP_PI05_LECTURA_VERIFICADOS_R02/COMPROBACION.json']
 m['authoring_limits']='Scientific facts closed after actual COMMITTED and both0tickproduct reopenings. Current snapshot and historical adoption reference remain distinct. Word still requires staging/render/publication.'
 m['closed_for_authoring']=True;m['closed_after_actual_adoption_and_selected_reopening']=True
 need('[[CIERRE'not in json.dumps(m,ensure_ascii=False)and'[[PENDIENTE'not in json.dumps(m,ensure_ascii=False),'Unresolved editorialmarker')
 plan={'antecedent_R01':{'file':'codigo/sincronizar_cierre_documental_PI05.py','sha256':'efee261fd199b591fefcac873936fb9f02d1042dbe1149d9e4c8e47339fc8b37','status':'Preserved failed prewrite assumption ACTIVO==historicadoption; no Native/Cwrites'},'schema':'DEE.PI05.post_selected_reopening.current_metadata_sync.v1','at':stamp,'life_id':LIFE,'N':67,'tick':824911,'current_snapshot':current,'historical_adoption_reference':adopt['active'],'current_active_pointer':active,'reopening':info(reopening),'adoption':info(adoption),'before_sha256':before,'new_Native_ticks':0,'Native_experiences_added':0,'current_active_and_promotion_receipts_not_rewritten_by_sync':True,'science_seed_snapshot_preserved':seed['source_snapshot_sha256'],'facts_closed_for_authoring':True,'product_world_state_not_modified':True}
 print(json.dumps({'mode':'APPLY_REQUESTED'if a.aplicar else'READ_ONLY_NO_WRITES','current_snapshot':CURRENT,'historical_adoption_snapshot':adopt['active']['snapshot_sha256'],'facts_can_close':True,'Native_ticks':0},ensure_ascii=False),flush=True)
 if not a.aplicar:return
 backup=P/'control/POST_REAPERTURA_PI05_RESPALDO';need(not backup.exists(),'Preserve prior sync backup');backup.mkdir()
 for path in paths:
  need(sha(path)==before[str(path)],'Concurrent metadata changed beforewrite');shutil.copyfile(path,backup/(path.name));need(sha(backup/path.name)==before[str(path)],'Literal backup differs')
 for path,value in((project_path,project),(continuity_path,continuity),(seed_path,seed),(facts,m)):atomic(path,value)
 need(all(sha(Path(x))==h for x,h in protected.items()),'Protected ACTIVO/promotion/world changed during metadata sync')
 plan['after_sha256']={str(x):sha(x)for x in paths};plan['applied']=True
 with out.open('x',encoding='utf8')as f:json.dump(plan,f,ensure_ascii=False,indent=2)
 print(json.dumps({'proof':info(out),'facts':info(facts),'Native_ticks':0,'current_snapshot':CURRENT},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
