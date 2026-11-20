"""External life-card provenance after the actual closed adverse panel. No Native state is edited."""
from pathlib import Path
import datetime,hashlib,json,os
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/candidato_R02/sistema';LIFE='ECI02_PI03_REPRO_PI04_MAIN_02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 card=S/'estado/vidas'/LIFE/'VIDA.json';before=card.read_bytes();d=json.loads(before)
 assert d['physical']['N']==67 and d['physical']['tick']==818074 and not d.get('PI04_provenance')
 assert sha(S/d['snapshot'])==d['snapshot_sha256']
 parent=json.loads((C/'sistema/estado/vidas/ECI02_PI03_MAIN/VIDA.json').read_text(encoding='utf8'))
 assert parent['physical']['tick']==775355 and parent['snapshot_sha256']=='5581d3785bf7d7194b5bdb545827aab55f0659d8b3f2c00301425d89616cf07b'
 imp=P/'control/IMPORTACION_ECI02_PI03_REPRO_PI04_MAIN_02.json';assert imp.is_file()
 backup=P/'control/VIDA_FUENTE_ANTES_PROCEDENCIA_PI04.json'
 with backup.open('xb')as f:f.write(before)
 d['PI04_provenance']={'physical_parent_life':'ECI02_PI03_MAIN','physical_parent_tick':775355,'physical_parent_snapshot_sha256':parent['snapshot_sha256'],'initial_complete_prefix':'reproducibilidad/materiales/PI03_FINAL_T775355','actual_import_proof':{'path':str(imp),'sha256':sha(imp)},'source_complete_trajectory':'E3 real, C2 failed11, C2B stopped3, C2C real12+reserve8+retention2, then partial conservation panel stopped at first material regression. No reset, memory merge or control promotion.','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'External administrative provenance only. No RAW, clocks, Native metadata, learned content, queue or actual parent import-container history was rewritten.'}
 tmp=card.with_name('VIDA.PI04_provenance.tmp')
 with tmp.open('x',encoding='utf8')as f:json.dump(d,f,ensure_ascii=False,indent=2)
 os.replace(tmp,card)
 proof={'life':LIFE,'tick':818074,'card_before_sha256':hashlib.sha256(before).hexdigest(),'card_after_sha256':sha(card),'literal_before':str(backup),'snapshot_sha256_unchanged':sha(S/d['snapshot']),'new_Native_ticks':0,'provenance':d['PI04_provenance']}
 out=P/'control/PROCEDENCIA_FISICA_REAL_PI04.json'
 with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
 print(json.dumps({'proof':str(out),'card_after_sha256':sha(card),'Native_ticks':0}))
if __name__=='__main__':main()
