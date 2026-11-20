"""Late explicitly timestamped read-only hardware detail; not a budget reset."""
import json,os,platform,sys,winreg
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'HARDWARE\DESCRIPTION\System\CentralProcessor\0')as key:cpu=winreg.QueryValueEx(key,'ProcessorNameString')[0].strip()
data={'schema':'CPC8R.hardware.supplement.v1','observed_utc':datetime.now(timezone.utc).isoformat(),'machine':platform.node(),'cpu_registry_name':cpu,'logical_CPU_count':os.cpu_count(),'OS':platform.platform(),'architecture':platform.machine(),'Python':sys.version,'initial_RAM_and_disk_record':'revision/RECURSOS_INICIALES.json','budget':'BUDGET.json','scope':'This CPU/machine detail was collected at the stated later time; original start/QPC/deadline unchanged. No CPU competitive benchmark, power or energy measurement.'}
path=ROOT/'revision/RECURSOS_COMPLEMENTARIOS.json'
with path.open('x',encoding='utf8')as stream:json.dump(data,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps(data,ensure_ascii=False))
