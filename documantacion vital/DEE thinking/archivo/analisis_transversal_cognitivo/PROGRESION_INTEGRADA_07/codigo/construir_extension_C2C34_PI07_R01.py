"""Prepare NEW external30to34 source around the exact preserved C2C body."""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';S=P/'estados/candidato/sistema';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_CAND_01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=S/'capacidades/pi05_c2c_ofertas_R01.py'
 if sha(source)!='3b7054996f694dd596f551d15612c649741d56df1710af47d651d31b51f98bbe':raise ValueError('Exact historical26to30 module only')
 text=source.read_text('utf8')
 replacements={
 'Explicit PI05 environment26→30':'Explicit PI07 environment30→34',
 'Original26protocol/body preserved':'Original30protocol/body preserved',
 'declared effective30protocol':'declared effective34protocol',
 "VERSION='DEE.PI05.C2C.explicit_environment30.R01'":"VERSION='DEE.PI07.C2C.explicit_environment34.R01'",
 "KEY='DEE.Cognitive.PI05.C2C.explicit_environment30.R01'":"KEY='DEE.Cognitive.PI07.C2C.explicit_environment34.R01'\nPREVIOUS_KEY='DEE.Cognitive.PI05.C2C.explicit_environment30.R01'\nLIFE='"+LIFE+"'",
 "EXTEND='eci01-pi05-c2c-ampliar';STATE='eci01-pi05-c2c-extension-estado'":"EXTEND='eci01-pi07-c2c-ampliar';STATE='eci01-pi07-c2c-extension-estado'",
 "'PROTOCOLO_PI05_C2C_EXTENSION_R01.json'":"'PROTOCOLO_PI07_C2C_EXTENSION_R01.json'",
 "return base\n\ndef code_files":"from capacidades import pi05_c2c_ofertas_R01 as previous\n return previous._effective(base)\n\ndef code_files",
 "p['schema']!='DEE.PI05.C2C.explicit_environment.protocol.v1'":"p['schema']!='DEE.PI07.C2C.explicit_environment34.protocol.v1'",
 "len(old['schedule'])!=26 or len(new['schedule'])!=30 or new['schedule'][:26]!=old['schedule']or new['schedule'][26:]":"len(old['schedule'])!=30 or len(new['schedule'])!=34 or new['schedule'][:30]!=old['schedule']or new['schedule'][30:]",
 'Original26schedule':'Original30schedule',
 "'PI05_C2C30_same_scientific_body'":"'PI07_C2C34_same_scientific_body'",
 "if KEY not in _entries(a):return base":"if KEY not in _entries(a):\n  from capacidades import pi05_c2c_ofertas_R01 as previous\n  return previous.effective_component(a,base,for_dependencies=for_dependencies)",
 "'PI05_C2C_OFERTAS_R01'":"'PI07_C2C_OFERTAS_R01'",
 "if not identity['life_id'].startswith('ECI02_PI03_REPRO_PI04_PI05_')or int(a.world.runtime.dimension)!=67:":"if identity['life_id']!=LIFE or int(a.world.runtime.dimension)!=67 or base._selected_life_id()==LIFE:",
 "m['ordinal']!=22 or len(m['rows'])!=22":"m['ordinal']!=30 or len(m['rows'])!=30",
 'Exact closed real22history':'Exact closed real30history',
 'Original26protocol':'Original30protocol',
 "len(old['resources'])!=26 or old['ordinal']!=22":"len(old['resources'])!=30 or old['ordinal']!=30",
 'Exact26resources/closed22device':'Exact30resources/closed30device',
 'range(26,30)':'range(30,34)',
 "'PI05.C2.additional.resource.'":"'PI07.C2.additional.resource.'",
 "'initial_ordinal':22,'original_resources':26,'effective_resources':30":"'initial_ordinal':30,'original_resources':30,'effective_resources':34",
 "'from':26,'to':30,'ordinal_unchanged':22":"'from':30,'to':34,'ordinal_unchanged':30",
 "'resources_before':26,'resources_after':30,'ordinal_preserved':22":"'resources_before':30,'resources_after':34,'ordinal_preserved':30",
 "'effective_from_ordinal':22":"'effective_from_ordinal':30",
 "'original26schedule_preserved'":"'original30schedule_preserved'",
 "'PI05_EXPLICIT_ENVIRONMENT26_TO30'":"'PI07_EXPLICIT_ENVIRONMENT30_TO34'",
 "'ordinal_preserved':22":"'ordinal_preserved':30",
 "device.m['ordinal']!=22":"device.m['ordinal']!=30",
 "current_ordinal_at_extension=22":"current_ordinal_at_extension=30",
 "'old26resource_references_unchanged'":"'old30resource_references_unchanged'",
 "'resources_before':26,'resources_after':30,'ordinal_before':22,'ordinal_after':22":"'resources_before':30,'resources_after':34,'ordinal_before':30,'ordinal_after':30",
 "'future_role':'26/27lastreopeningtests;28/29remainavailable;hostpreparedopportunitiesnotanswers'":"'future_role':'30/31declared material uses;32/33remainavailable;newexternaloffersnotlearning'",
 }
 for before,after in replacements.items():
  if before not in text:raise ValueError('Expected exact source fragment absent: '+before)
  text=text.replace(before,after)
 first=text.index('def code_files():');last=text.index('\ndef _protocol():',first)
 text=text[:first]+'''def code_files():
 from capacidades import pi05_c2c_ofertas_R01 as previous
 return tuple(dict.fromkeys([Path(__file__),MANIFEST,Path(__file__).with_name('PROTOCOLO_PI07_C2C_34_R01.json'),*previous.code_files()]))
'''+text[last:]
 text=text.replace("before=base._physical(a);root=_home(directory);", "previous_literal=_entries(a)[PREVIOUS_KEY];before=base._physical(a);root=_home(directory);")
 text=text.replace("if m['rows']!=oldm['rows']or device.m['products']", "if _entries(a)[PREVIOUS_KEY]!=previous_literal or m['rows']!=oldm['rows']or device.m['products']")
 text=text.replace("return {'version':VERSION,'ready':True,'new_native_ticks':0,", "return {'version':VERSION,'ready':True,'new_native_ticks':0,'requests':[],'old_environment30_metadata_literal_unchanged':_entries(a)[PREVIOUS_KEY]==previous_literal,")
 # Validate old30 provenance without changing its literal ready/history KEY.
 text=text.replace("if KEY in _entries(a):raise ValueError('Existing extension preserved; never reset/readmit/refill automatically')", "if KEY in _entries(a):raise ValueError('Existing34extension preserved; never reset/readmit/refill automatically')\n  if PREVIOUS_KEY not in _entries(a):raise ValueError('Actual inherited26to30history required')\n  previous=json.loads(_entries(a)[PREVIOUS_KEY])\n  if not previous.get('ready')or previous.get('pending')or previous.get('uncertain'):raise ValueError('Original30environment must remain coherently closed')")
 ast.parse(text);target=H/'pi07_c2c_ofertas_R01.py'
 if target.exists():raise FileExistsError('Preserve new extension source')
 target.write_text(text,encoding='utf8');print(json.dumps({'module':str(target),'sha256':sha(target),'bytes':target.stat().st_size,'Native_executed':False}))
if __name__=='__main__':main()
