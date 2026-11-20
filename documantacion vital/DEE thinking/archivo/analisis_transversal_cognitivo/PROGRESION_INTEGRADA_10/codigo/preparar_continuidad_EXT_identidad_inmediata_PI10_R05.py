"""Pure prospective EXT identity fix: retain D history, bind actual parent."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;src=H/'continuidad_EXT_post_COMMITTED_PI10_R04.py';out=H/'continuidad_EXT_post_COMMITTED_PI10_R05.py';text=src.read_text('utf8');text=text.replace("ACTOR='pi10_dispositivo_EXT_R01.py'","ACTOR='pi10_dispositivo_EXT_R02.py'")
old="scope['source_main_before_EXT_binding']={k:copy.deepcopy(v)for k,v in scope.items()if k.startswith('source_main_')};scope.update(life_id=EXT,role='reproduction',source_main_life_id=MAIN,source_main_tick=a.tick,source_main_snapshot_sha256=a.snapshot_sha256,source_main_manifest_sha256=a.manifest_sha256,source_immediate_life_id=MAIN,source_immediate_tick=a.tick,source_immediate_snapshot_sha256=a.snapshot_sha256)"
new="need(scope.get('source_main_life_id')==OLD_D and scope.get('source_main_tick')==922371 and scope.get('source_main_snapshot_sha256')=='72743ad2fc708e41c2529af8f7192fe1087184562e4cd094f469384faedcd331','Historical D source fields stay literal; never rename D as Main14');scope['source_immediate_before_EXT_binding']={k:copy.deepcopy(v)for k,v in scope.items()if k.startswith('source_immediate_')};scope.update(life_id=EXT,role='reproduction',source_immediate_life_id=MAIN,source_immediate_tick=a.tick,source_immediate_snapshot_sha256=a.snapshot_sha256,source_immediate_manifest_sha256=a.manifest_sha256)"
assert text.count(old)==1;text=text.replace(old,new);ast.parse(text)
def exact(p,t):
 if p.exists():assert p.read_text('utf8')==t
 else:
  with p.open('x',encoding='utf8')as f:f.write(t)
exact(out,text);plan=H/'preparar_plan_EXT2_PI10_R05.py';pt=(H/'preparar_plan_EXT2_PI10_R04.py').read_text('utf8');assert pt.count('continuidad_EXT_post_COMMITTED_PI10_R04.py')==1;pt=pt.replace('continuidad_EXT_post_COMMITTED_PI10_R04.py','continuidad_EXT_post_COMMITTED_PI10_R05.py');ast.parse(pt);exact(plan,pt);print(json.dumps({'cloner':str(out),'cloner_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'plan_builder':str(plan),'plan_builder_sha256':hashlib.sha256(plan.read_bytes()).hexdigest(),'Native':0}))
