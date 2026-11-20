"""Same bounded review for the additive editorial package; preserves R01."""
from pathlib import Path
p=Path(__file__).with_name('revisar_y_sellar_plan_PI09_R01.py')
s=p.read_text('utf-8-sig')
assert s.count('PLAN_ENTREGA_PI09_FINAL.json')==1
assert s.count('PLAN_ANTES_SELLO_ROOT_PI09_R01.json')==1
s=s.replace('PLAN_ENTREGA_PI09_FINAL.json','PLAN_ENTREGA_PI09_FINAL_R02.json').replace('PLAN_ANTES_SELLO_ROOT_PI09_R01.json','PLAN_ANTES_SELLO_ROOT_PI09_R02.json')
exec(compile(s,str(Path(__file__).resolve()),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
