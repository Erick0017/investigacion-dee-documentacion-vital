"""Prepare additional original short recoveries without modifying sealed Core1."""
from pathlib import Path
import base64,gzip,hashlib,json
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE';OUT=RUN/'notes/core_extension_v2';OUT.mkdir(parents=True,exist_ok=True)
index=json.loads((CORE/'documentacion/INDICE_MIEMBROS.json').read_text(encoding='utf8'))['paths'];c5='historico/CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/'
selected={
 'ordered':{n:c5+'resultados/'+g+'/'+n+'/MEASUREMENTS.json'for n,g in(('ORDERED_D01_AB','ordered_discovery'),('ORDERED_D02_BA','ordered_discovery'),('ORDERED_C05_AB_REMOVE_PRODUCT','ordered_confirmation'),('ORDERED_C06_AB_SHAM_PRODUCT','ordered_confirmation'),('ORDERED_R01_AB_NEW_LOADS_TRANSLATED','ordered_confirmation'),('ORDERED_R02_BA_NEW_LOADS_TRANSLATED','ordered_confirmation'))},
 'stream':{n:c5+'resultados/order_stream_confirmation/'+n+'/MEASUREMENTS.json'for n in('STREAM_AB_CONTEXT_PLUS','STREAM_BA_CONTEXT_MINUS','STREAM_NO_HISTORY','STREAM_AB_READER_OMITTED','STREAM_RESERVED_GAP2','STREAM_RESERVED_GAP4')},
 'network':{n:c5+'resultados/'+g+'/'+n+'/MEASUREMENTS.json'for n,g in(('RING_A1_SELF','network_dialogue_screen'),('RING_A2_DUPLEX','network_dialogue_screen'),('RING_A4','network_dialogue_screen'),('RING_A2_SOURCE_U2_OMITTED','network_dialogue_confirmation'),('RING_A2_SENT_MESSAGE_CUT','network_dialogue_confirmation'),('RING_A2_SENT_MESSAGE_SHAM','network_dialogue_confirmation'),('RING_A2_RESERVED_ROLE_EXCHANGE','network_dialogue_confirmation'))},
 'architectures':{n:'historico/CPC6/resultados/ARCHITECTURE_SCREEN_01/'+n+'/MEASUREMENTS.json'for n in('AS01_ONE_COMPOUND','AS02_TWO_COMPOUNDS','AS03_FOUR_COMPOUNDS','AS04_FOUR_NO_ACTUAL','AS05_FOUR_NO_SOURCE_LEARNING','AS06_RESERVED_FOUR_OTHER_HISTORY_CONTENT')},
 'bridge':{n:'historico/CPC6/resultados/'+g+'/'+n+'/MEASUREMENTS.json'for n,g in(('BD31_TWO_COMPOUNDS_LATE_SUPPORT','ARCHITECTURE_BRIDGE_DELAYED_04'),('BD32_RELAY_OMITTED_LATE_SUPPORT','ARCHITECTURE_BRIDGE_DELAYED_04'),('BD33_U1_SOURCE_UNPAIRED_LATE_SUPPORT','ARCHITECTURE_BRIDGE_DELAYED_04'),('BC04_RESERVED_RECEIVER_LOAD_QUERY','ARCHITECTURE_BRIDGE_CONFIRM_05'))}
}
needed={index[p]['sha256']:p for d in selected.values()for p in d.values()};values={}
with gzip.open(CORE/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz','rt',encoding='ascii')as f:
 for line in f:
  item=json.loads(line);h=item['sha256']
  if h not in needed:continue
  b=base64.b64decode(item['base64']);assert hashlib.sha256(b).hexdigest()==h;values[needed[h]]=json.loads(b)
result={'schema':'DEE_CORE.extension_inputs.v1','parent_candidate_sha256':'79c74f48386790b589a2c07c669439b44b1a98501de9e924f72d82740fe72354','design_precedes_new_recovery':True,'note':'Onlycurrentexperience/environmentconfigurationentersrecoveredparticipant. OriginalexpectedprimariesareopenedAFTEReachtrajectory. Historicalreservesremaintechnicalreproductions,notnewscientificheld-outs.','groups':{}}
for group,items in selected.items():
 result['groups'][group]=[]
 for name,p in items.items():
  value=values[p];result['groups'][group].append({'id':name,'input_configuration':value['case'],'primary':p,'primary_sha256':index[p]['sha256'],'primary_top_keys':list(value)})
(OUT/'RECUPERACION_EXTENSION_CONGELADA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({g:len(v)for g,v in result['groups'].items()}))
