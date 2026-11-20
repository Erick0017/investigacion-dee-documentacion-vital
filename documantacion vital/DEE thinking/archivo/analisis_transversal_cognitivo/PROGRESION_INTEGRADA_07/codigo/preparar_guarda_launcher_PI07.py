"""Prepare one technical launcher guard for an existing moved continuation."""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';H=P/'codigo';source=C/'sistema/app/usar_dee.py';target=H/'PI07_LAUNCHER_EXISTENTE_PREPARADO/app/usar_dee.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if target.exists():raise FileExistsError('Preserve prior technical guard')
 old=source.read_text('utf8');needle='    def import_new(self, life):\n        paired = (self.root / self.config["source_paired_export_manifest"]).resolve(strict=True)'
 if old.count(needle)!=1:raise ValueError('Exact OriginalBackend import point required')
 new=old.replace(needle,'    def import_new(self, life):\n        if self.config.get("existing_continuation_only"):\n            raise ValueError("Esta selección abre una continuación completa existente; no ofrece un par nuevo para --nueva. Use la vida seleccionada o una receta diagnóstica explícita conservada.")\n        paired = (self.root / self.config["source_paired_export_manifest"]).resolve(strict=True)')
 ast.parse(new);target.parent.mkdir(parents=True);target.write_text(new,encoding='utf8')
 proof={'schema':'DEE.PI07.existing_launcher.no_false_seed.guard.v1','status':'PREPARADO_NO_APLICADO','file':'app/usar_dee.py','source':str(target),'before_sha256':sha(source),'sha256':sha(target),'scope':'One early external transport refusal only when config.existing_continuation_only is true. Existing reopen uses its registered Supervisor protocol; no Native/actor/old default change.','Native_executed':False,'product_modified':False}
 out=P/'control/PI07_GUARDA_LAUNCHER_PREPARADA_R01.json'
 with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(out),'sha256':sha(out),'Native_executed':False}))
if __name__=='__main__':main()
