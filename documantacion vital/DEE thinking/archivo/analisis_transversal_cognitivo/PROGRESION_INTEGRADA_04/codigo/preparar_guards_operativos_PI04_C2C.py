"""Stage candidate permissions only. Never edits S2/product or executes DEE."""
from pathlib import Path
import ast,hashlib,json
P4=Path(__file__).resolve().parents[1];SRC=P4/'estados/candidato_R02/sistema/capacidades';OUT=P4/'codigo/PI04_GUARDS_OPERATIVOS_CANDIDATOS/C2C_OP1'
def sha(b):return hashlib.sha256(b).hexdigest()
def replace_function(text,name,replacement):
 tree=ast.parse(text);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name);lines=text.splitlines(keepends=True)
 return ''.join(lines[:node.lineno-1])+replacement.rstrip()+'\n'+''.join(lines[node.end_lineno:])
def change_call_in_function(text,name,old,new):
 tree=ast.parse(text);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name);lines=text.splitlines(keepends=True);fragment=''.join(lines[node.lineno-1:node.end_lineno])
 if fragment.count(old)!=1:raise ValueError(name+' call anchor')
 fragment=fragment.replace(old,new)
 return ''.join(lines[:node.lineno-1])+fragment+''.join(lines[node.end_lineno:])
def main():
 if OUT.exists():raise FileExistsError('Candidate revision already exists; preserve')
 (OUT/'ANTES').mkdir(parents=True)
 names=('pi04_coordinacion_central_C2C.py','pi04_e3_contingencia.py')
 original={name:(SRC/name).read_bytes()for name in names}
 for name,data in original.items():(OUT/'ANTES'/name).write_bytes(data)
 b=original[names[0]].decode('utf-8-sig').replace('\r\n','\n')
 guard='''
OPERATIONAL_GUARD_REVISION = "PI04.C2C.permission.OP1_CANDIDATE"
OPERATIONAL_LIFE_ID = "ECI02_PI03_REPRO_PI04_MAIN_02"

def _system_root():
    return Path(__file__).resolve().parents[1]

def _selected_life_id():
    active = _system_root() / "estado" / "ACTIVO.json"
    if not active.is_file():
        return None
    selected = json.loads(active.read_text(encoding="utf-8-sig"))
    return selected.get("life_id", selected.get("preferred_life"))

def _require_adopted_C2C_use(a, identity, p, ph, operation, directory):
    # Permission only: no RAW/clock, response, reference or protocol edit.
    if identity["life_id"] != OPERATIONAL_LIFE_ID or operation not in (OPPORTUNITY, STATE):
        raise ValueError("ACTIVO permits only exact adopted C2C opportunity/state; preparation/admission/cuts/calibration remain forbidden")
    m = _get(a)
    if (not m.get("ready") or not m.get("admitted") or m.get("arm") != "real"
            or m.get("life_id") != OPERATIONAL_LIFE_ID
            or any(m.get(k) for k in ("pending", "uncertain", "halted_reason"))
            or m.get("calibrations") or m.get("protocol_sha256") != ph
            or p.get("status") != "SEALED_FOR_EVALUATION"):
        raise ValueError("Exact adopted C2C must be admitted real, ready, closed and protocol-consistent")
    if directory is not None:
        raw = Path(directory).absolute()
        expected = _system_root() / "estado" / "servicios_locales" / OPERATIONAL_LIFE_ID
        if not raw.is_dir() or raw.resolve() != expected.resolve():
            raise ValueError("Exact existing owned local-service home required for adopted C2C")
        for part in (raw, *raw.parents):
            if part.exists() and (part.is_symlink() or getattr(part.lstat(), "st_file_attributes", 0) & 1024):
                raise ValueError("No symlink/junction home for adopted C2C")
            if part == _system_root():
                break
    return m
'''
 new_identity='''def _identity(a, directory=None, *, operation=None):
    p, ph = protocol(material=True)
    r01, _ = _hardware().protocol()
    # Keep the frozen hardware source unchanged. Its directory=None path
    # validates physical identity without its blanket no-ACTIVO home check.
    identity = _hardware()._identity(a, r01)
    if not identity["life_id"].startswith(PREFIX) or int(a.world.runtime.dimension) != 67:
        raise ValueError("Only an explicit inherited PI04 N67 life")
    selected = _selected_life_id()
    if selected == identity["life_id"]:
        _require_adopted_C2C_use(a, identity, p, ph, operation, directory)
    elif directory is not None:
        # Diagnostic controls preserve their original directory/main refusal.
        identity = _hardware()._identity(a, r01, directory)
    if directory is not None and Path(directory).resolve().name != identity["life_id"]:
        raise ValueError("Exact existing owned-life directory required")
    hardware = _hardware()._get(a)
    if not hardware.get("ready") or hardware.get("pending") or hardware.get("uncertain"):
        raise ValueError("Inherited eligibility apparatus is not complete and closed")
    old = _entries(a).get("DEE.Cognitive.PI02.continuous_workbench.R04")
    if old is not None:
        old = _decode(old)
        if old.get("enabled") or old.get("active") is not None:
            raise ValueError("Explicitly pause inherited O/H bridge and close its job first")
    for key in ("DEE.Cognitive.PI03.useful_delayed_task.R02", "DEE.Cognitive.PI04.E3.contingency.R01"):
        if key in _entries(a):
            state = _decode(_entries(a)[key])
            if state.get("pending") or state.get("uncertain") or state.get("supply_pending") or state.get("halted_reason"):
                raise ValueError("An inherited task/E3 operation is not closed: " + key)
    return p, ph, identity
'''
 b=replace_function(b,'_identity',new_identity)
 b=b.replace('def _identity(a, directory=None, *, operation=None):',guard+'\ndef _identity(a, directory=None, *, operation=None):',1)
 b=change_call_in_function(b,'validate','    if row["modo"] == STATE:\n        return','    if row["modo"] == STATE:\n        _identity(a, operation=STATE)\n        return')
 b=change_call_in_function(b,'validate','_identity(a)','_identity(a, operation=row["modo"])')
 b=change_call_in_function(b,'dispatch','_identity(a,directory)','_identity(a,directory,operation=row["modo"])')
 b=change_call_in_function(b,'_opportunity_body','_identity(a,directory)','_identity(a,directory,operation=OPPORTUNITY)')
 b=change_call_in_function(b,'state','    result={','    _identity(a,directory,operation=STATE)\n    result={')
 e=original[names[1]].decode('utf-8-sig').replace('\r\n','\n')
 e=e.replace('def _identity(a,directory=None):','def _identity(a,directory=None,*,material=True):',1)
 e=change_call_in_function(e,'_identity','_guard(a,directory,material=True)','_guard(a,directory,material=material)')
 e=change_call_in_function(e,'operational_dependencies','_identity(a,directory)','_identity(a,directory,material=False)')
 candidates={names[0]:b,names[1]:e};changed={}
 for name,text in candidates.items():
  ast.parse(text);(OUT/name).write_text(text,encoding='utf-8')
  before={x.name:ast.dump(x)for x in ast.parse(original[name].decode('utf-8-sig')).body if isinstance(x,ast.FunctionDef)}
  after={x.name:ast.dump(x)for x in ast.parse(text).body if isinstance(x,ast.FunctionDef)}
  changed[name]={'changed_existing_functions':[k for k,v in before.items()if after.get(k)!=v],'new_functions':[k for k in after if k not in before]}
 fixed=('pi04_selector_contextual_C2_R01.py','pi04_sensor_central_C2C_R01.py','pi04_coordinacion_simetrica_C2B.py','progresion_integrada_03_R01.py','pi03_tarea_diferida_R02.py','pi04_coordinacion_adquirida.py','PROTOCOLO_PI04_C2C_R01.json','PROTOCOLO_PI04_C2_R01.json','PROTOCOLO_PI04_C2B_R01.json')
 protocol=json.loads((SRC/'PROTOCOLO_PI04_C2C_R01.json').read_text(encoding='utf-8'))
 for name in candidates:
  if name in protocol['dependencies_sha256']:raise ValueError('Candidate would change a frozen protocol dependency; requires separate recorded migration')
 proof={'schema':'PI04.C2C.operational_guards.CANDIDATE_ONLY.v1','source_system':str(SRC.parent),'candidate_folder':str(OUT),'changes':changed,
  'before':{n:{'bytes':len(v),'sha256':sha(v)}for n,v in original.items()},'candidate':{n:{'bytes':len(v.encode('utf-8')),'sha256':sha(v.encode('utf-8'))}for n,v in candidates.items()},
  'fixed_dependencies_NOT_modified':{n:{'bytes':(SRC/n).stat().st_size,'sha256':sha((SRC/n).read_bytes())}for n in fixed},
  'C2C_and_E3_self_not_in_C2C_protocol_dependencies':True,'C2C_protocol_bytes_unchanged':True,
  'material_whitelist':'Exact ACTIVO ECI02_PI03_REPRO_PI04_MAIN_02 only C2C OPPORTUNITY/STATE, admitted real ready/no pending/uncertain/halt and matching sealed protocol; other material modes fail',
  'E3_change':'Only readonly operational_dependencies passes material=False to existing task guard. E3 material/admission/ordinal18 exhaustion unchanged.',
  'old_sensor_finding':'Original _guard checks complete identity N67 and PI04 life prefix, not ACTIVO. Exact proposed ID already matches; no sensor change required.',
  'old_C2_finding':'Its operational_dependencies reads journal/device directly without _identity, so it remains usable as halted historical evidence; no old-C2 change required.',
  'deployment_performed':False,'Native_verification':'NOT_EXECUTED; ROOT must test on an adopted-like isolated complete copy after states qualify','Native_ticks':0,'DEE_imports':0}
 (OUT/'PREPARACION_CANDIDATA.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'candidate':str(OUT),'changes':changed,'Native_ticks':0,'deployed':False},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
