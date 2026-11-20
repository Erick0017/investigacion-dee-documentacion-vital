"""Misma física R02; metadatos operativos sin telemetría microscópica anidada.
La revisión R02 quedó detenida por longitud de metadata; no fallo cognitivo.
"""
import hashlib,importlib.util,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('restoration_r02_exact',HERE/'restauracion_r02.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);b=r.b
def save(self,label):
    # Interfaces, física, clocks, agenda y recibos los conserva el snapshot
    # oficial. La traza de auditoría no es estado operativo ni target accesible.
    metadata={'label':self.label,'N':b.N,'I':b.I,'V':b.V,'requests':self.requests,'tick':self.tick,'rows_count':len(self.rows),'recipe':'MA02 restorative excursion R03','source':'NEW T0 no learned fields copied'}
    self.world.runtime.set_snapshot_metadata(b.KEY,b.encode_metadata(metadata))
    path=b.OUT/(self.label+'.'+label+'.deetsnap.gz');proof=b.save_world_snapshot(self.world,path,compress=True)
    return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'proof':str(proof)}
b.Common.save=save
if __name__=='__main__':
    b.put(b.OUT/'PROTOCOLO_RESTAURACION_R03.json',{'frozen_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'physics_unchanged_from':'restauracion_r02.py','difference':'bounded operational metadata, full primary trace separate','previous_run':'MA02_RESTAURACION_R02_MAIN stopped by official metadata length validation before first query of fourth bank; prefix snapshots preserved','reader':'unique pureZ across eight fixed gates atq+4; no token used','all_results_preserved':True})
    r.run('MA02_RESTAURACION_R03_MAIN',[1,-1,1,-1]);r.run('MA02_RESTAURACION_R03_OPPOSITE',[-1,1,-1,1]);r.run('MA02_RESTAURACION_R03_NOGUARD',[1,-1,1,-1],False)
