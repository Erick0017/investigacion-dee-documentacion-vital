"""Prepare one exact closed DISC export directly to stable RP, source only."""
from pathlib import Path
import ast,hashlib
H=Path(__file__).resolve().parent;source=H/'exportar_corte_aislado_PI06_R02.py';target=H/'exportar_interferencia_directo_RP_PI06_R03.py'
text=source.read_text('utf-8-sig')
def replace(old,new):
 global text
 if text.count(old)!=1:raise ValueError('Exact edit is not unique: '+old)
 text=text.replace(old,new)
replace("SOURCE_LIFE='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'","SOURCE_LIFE='ECI02_PI03_REPRO_PI04_PI05_PI06_DISC_01'")
replace("parent=(CAMPAIGN/'pares').resolve(strict=True)\n    if ar.destino is None:raise ValueError('Explicit new bounded PI06/pares destination required')\n    dest=ar.destino.resolve(strict=False);expected=parent/dest.name;regular(s);regular(dest)\n    if not re.fullmatch(r'[A-Za-z0-9_]{1,48}_T'+str(ar.tick),dest.name):raise ValueError('Short exact new export name must end in its declared Native tick')",
 "parent=(RP/'materiales').resolve(strict=True);expected=parent/'PI06_POST_INTERFERENCIA_T826449'\n    dest=(expected if ar.destino is None else ar.destino).resolve(strict=False);regular(s);regular(dest)")
replace("if s!=s5 or not re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI06_[A-Za-z0-9_]{1,24}',ar.vida):raise ValueError('Only exact isolated S6 PI06 diagnostic source; never current product Main')",
 "if s!=s5 or ar.vida!=SOURCE_LIFE or ar.tick!=826449:raise ValueError('Only exact closed S6 DISC_01 T826449; never the current product Main')")
replace("if critical[str(snap)]!=card['snapshot_sha256']:raise ValueError('Snapshot encoded identity differs')",
 "if critical[str(snap)]!=card['snapshot_sha256']or card['snapshot_sha256']!='b6256f5da505e2673e2c4e26e6f0b856c7989ccffc8a731fc222d60b82ae9c95':raise ValueError('Exact frozen post-interference snapshot identity differs')")
text=text.replace('Only one new exact PI06 baseline export from the actual closed product Main','Only one new direct RP post-interference alias, never overwrite')
text=text.replace('DEE.PI06.isolated_closed_paired_preservation.R02','DEE.PI06.direct_RP_postinterference_preservation.R03')
text=text.replace('PI06_R02_exact_S6_diagnostic_only','PI06_R03_exact_S6_DISC_T826449_direct_RP')
text=text.replace('Closed declared isolated S6 cut to one new bounded PI06 pair','Closed frozen S6 DISC T826449 directly to one stable RP alias')
ast.parse(text)
with target.open('x',encoding='utf8')as f:f.write(text)
print(target.name,len(target.read_bytes()),hashlib.sha256(target.read_bytes()).hexdigest())
