"""Pure R03->R04 ledger-only adaptation, diagnostic scope/protections retained."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;src=H/'ejecutar_plan_PI10_R03.py';out=H/'ejecutar_plan_PI10_R04.py';ledger=H/'ledger_PI10_traslado_integral_R02.py';text=src.read_text('utf8');needles={"file=H/'ledger_PI10_R01.py'":"file=H/'ledger_PI10_traslado_integral_R02.py'","'55ec5b9b131f251a7b452b19adc2df38a07eaf54ab049804f2205359631a3ff3'":repr(hashlib.sha256(ledger.read_bytes()).hexdigest())}
for old,new in needles.items():assert text.count(old)==1;text=text.replace(old,new)
text=text.replace("'technical_supervisor_revision':'R03 R02 guard/Job/ledger unchanged; fixed actual integer transport, noninteger dependent abstention zero Native'","'technical_supervisor_revision':'R04 only adds exact same-ID product movement to R03 ledger; no duplicate/refunded world, all diagnostic/Job/guard/transport protections retained'");ast.parse(text)
if out.exists():assert out.read_text('utf8')==text
else:
 with out.open('x',encoding='utf8')as f:f.write(text)
print(json.dumps({'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'ledger_sha256':hashlib.sha256(ledger.read_bytes()).hexdigest(),'Native':0}))
