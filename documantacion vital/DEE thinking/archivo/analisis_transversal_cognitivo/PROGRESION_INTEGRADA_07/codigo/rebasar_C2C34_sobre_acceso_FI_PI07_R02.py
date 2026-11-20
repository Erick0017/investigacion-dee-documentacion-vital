"""Prepare a NEW C2C34 installer based on the frozen future FI facade.

Do not execute Source installation or Native. R01 installer/stage preserved.
R02 application CAS requires the FI facade to have been really applied first.
"""
from pathlib import Path
import ast,hashlib
H=Path(__file__).resolve().parent
def main():
 source=H/'preparar_C2C34_PI07_R01.py';text=source.read_text('utf8')
 replacements={"D=H/'FUENTES_C2C34_PI07_R01'":"D=H/'FUENTES_C2C34_PI07_R02'\nFI=H/'FUENTES_ACCESO_FI_PI07_R01'",
 "C2C34_PI07_DELTA_CONDICIONAL_R01.json":"C2C34_PI07_DELTA_CONDICIONAL_R02.json",
 "C2C34_PI07_DELTA_APLICADO_R01.json":"C2C34_PI07_DELTA_APLICADO_R02.json",
 "ORIGINALES_C2C34_PI07_R01":"ORIGINALES_C2C34_PI07_R02",
 "old=(S/'app'/n).read_text('utf8');new=old":"old=(FI/'app'/n).read_text('utf8');new=old",
 "'before_sha256':None if name in newnames else sha(S/name)":"'before_sha256':None if name in newnames else sha((FI if name.startswith('app/')else S)/name)"}
 for before,after in replacements.items():
  if before not in text:raise ValueError('Expected exact source fragment absent: '+before)
  text=text.replace(before,after)
 needle="  oldp=S/'capacidades/PROTOCOLO_PI05_C2C_30_R01.json';newp=H/'PROTOCOLO_PI07_C2C_34_R01.json'"
 extra="  fi_plan=read(P/'control/ACCESO_FI_PI07_PREPARADO_R01.json')\n  for row in fi_plan['files']:\n   if sha(FI/row['file'])!=row['sha256']:raise ValueError('Prepared FI source differs; do not rebase blindly')\n"
 if text.count(needle)!=1:raise ValueError('Exact plan point required')
 text=text.replace(needle,extra+needle)
 needle=";save(planfile,plan)"
 extra="\n  plan['prepared_FI_basis']={'proof':str(P/'control/ACCESO_FI_PI07_PREPARADO_R01.json'),'sha256':sha(P/'control/ACCESO_FI_PI07_PREPARADO_R01.json'),'scope':'Only three C2C34P0insertions ahead of the future FI facade; all new FI facade imports retained.'}\n  plan['preserved'].update({name:sha(FI/'capacidades'/name)for name in('pi07_acceso_FI_regulado_R01.py','PROTOCOLO_PI07_ACCESO_FI_R01.json','acceso_integrado_eci01.py')})\n  save(planfile,plan)"
 if text.count(needle)!=1:raise ValueError('Exact serialization point required')
 text=text.replace(needle,extra)
 ast.parse(text);out=H/'preparar_C2C34_PI07_R02.py'
 if out.exists():raise FileExistsError('Preserve prior R02')
 out.write_text(text,encoding='utf8');print(out,hashlib.sha256(out.read_bytes()).hexdigest())
if __name__=='__main__':main()
