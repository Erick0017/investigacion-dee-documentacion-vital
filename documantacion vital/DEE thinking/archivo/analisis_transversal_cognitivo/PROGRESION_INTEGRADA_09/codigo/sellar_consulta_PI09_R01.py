"""Prospective once-only PI09 scientific seal; no DEE import or world."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
P=Path(__file__).resolve().parents[1];H=P/'codigo';P8=P.with_name('PROGRESION_INTEGRADA_08')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=H/'SELLO_PI09_CONSULTA_R01.json'
 if out.exists():raise FileExistsError('Frozen scientific seal already exists')
 proto=H/'PROTOCOLO_PI09_CONSULTA_R01.json';wrapper=H/'pi09_consulta_selectiva_R01.py';criteria=H/'CRITERIOS_PI09_R01.json'
 if sha(wrapper)!='59d7cc5740ae5d9ca99ad30a86fc793a08f9fc89b23e03cb62377e2c844b2ecd' or sha(proto)!='cb6973e6f1bd747de8da73ecda37497579370330f828ea43d559a61c86e45ad5':raise ValueError('Final pure-tested sources changed')
 source=P8/'codigo/pi08_consulta_condicional_C_R03.py';dest=H/source.name
 if sha(source)!='07072d230c33f75eccd3cd46751e404bfb24745756e1575e50705c0c76f8870f':raise ValueError('Literal inherited C source changed')
 if dest.exists():
  if sha(dest)!=sha(source):raise ValueError('Existing source differs')
 else:shutil.copyfile(source,dest)
 mf=P/'pares/C_HEREDADA_T884835/EXPORTACION_SERVICIO.json';m=json.loads(mf.read_text('utf-8-sig'))
 if sha(mf)!='08a8e65deb2071b7653bc0ab95f3d55b8038191a4f585c6803f6d81c16e8182f':raise ValueError('Actual coherent C pair changed')
 base='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_';arms={'native_real':base+'NATIVE_01','always_real':base+'ALWAYS_01','never':base+'NEVER_01','always_desacoplado':base+'YOKE_01'}
 v={'schema':'DEE.PI09.selective_consultation.source_seal.R01','sealed_utc':datetime.now(timezone.utc).isoformat(),'protocol_sha256':sha(proto),'criteria_sha256':sha(criteria),'source_prefix':{'life_id':m['life_id'],'tick':884835,'N':67,'physical':m['physical'],'snapshot_sha256':m['snapshot_sha256'],'manifest_sha256':sha(mf),'manifest':str(mf)},'arms':arms,'operational_native_id':arms['native_real'],'native_reproduction_ids':[base+'REPRO_01'],'diagnostic_readonly_ids':[base+'PANEL_01',base+'AR0_01',base+'AR36_01',base+'AR64_01',base+'AR0NOD_01'],'files_sha256':{p.name:sha(p)for p in(wrapper,proto,dest)},'no_Native_before_this_seal':True,'new_scientific_question':'Value of actual gated information and bounded Native conditional use across a continuous B/C descendant; own credit for asking remains unproven until separately isolated.','frozen_decode':'Inherited C preview RAW direction ->bit, query1 physical signature, query2 TC/q4, FI0/NULL and actual message predicate; no target in actor.'}
 out.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'seal':str(out),'sha256':sha(out),'arms':arms,'Native_ticks':0},ensure_ascii=False))
if __name__=='__main__':main()
