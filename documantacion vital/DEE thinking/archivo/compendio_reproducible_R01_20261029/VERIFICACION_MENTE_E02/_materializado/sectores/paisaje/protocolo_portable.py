"""Ejecuta bytes históricos con una única sustitución de ruta de intérprete.

PY era una ruta absoluta del instrumento anfitrión en external_trial.py.
No se modifica ninguna entrada, calendario DEE, lector, actuador ni resultado.
"""
from pathlib import Path
import ast,sys,os
file=Path(sys.argv[1]).resolve();sys.argv=[str(file),*sys.argv[2:]]
sys.path.insert(0,str(file.parent))
tree=ast.parse(file.read_text(encoding='utf8'));removed=0
for node in list(tree.body):
 if isinstance(node,ast.Assign)and any(isinstance(q,ast.Name)and q.id=='PY'for q in node.targets):tree.body.remove(node);removed+=1
if removed:
 if not os.environ.get('DEE_EXTERNAL_PYTHON'):raise RuntimeError('Falta --external-python explícito para el puente')
assert removed<=1
exec(compile(tree,str(file),'exec'),{'__name__':'__main__','__file__':str(file),'PY':os.environ.get('DEE_EXTERNAL_PYTHON')})
