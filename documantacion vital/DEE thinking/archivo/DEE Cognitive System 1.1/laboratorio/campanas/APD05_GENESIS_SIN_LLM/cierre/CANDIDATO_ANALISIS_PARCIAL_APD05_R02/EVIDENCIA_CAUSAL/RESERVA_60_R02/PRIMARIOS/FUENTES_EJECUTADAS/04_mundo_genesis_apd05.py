"""Explicit optional owner domain extension; existing operations remain unchanged."""
from pathlib import Path
import hashlib
from app.servicio_persistente import NativeWorld

class GenesisNativeWorld(NativeWorld):
    def _open_locked(self):
        result=super()._open_locked()
        from capacidades import percepcion_vigencia_apd05 as version_sensor
        self.code_sha256['genesis_owner_extension']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        self.code_sha256['genesis_version_sensor']=hashlib.sha256(Path(version_sensor.__file__).read_bytes()).hexdigest()
        return result

    def validate(self,payload):
        rows=payload.get('situaciones',[])
        extended=[r for r in rows if isinstance(r.get('modo'),str)and r['modo'].startswith('apd05')]
        if payload.get('operacion')=='sesion'and extended:
            if self.backend!='mente_unificada'or len(rows)!=1:raise ValueError('One explicit APD05 operation in the shared-world owner')
            from capacidades import percepcion_vigencia_apd05 as version_sensor
            version_sensor.validate(self.a,rows[0]);return
        return super().validate(payload)

    def execute(self,payload):
        rows=payload.get('situaciones',[])
        if payload.get('operacion')=='sesion'and len(rows)==1 and str(rows[0].get('modo','')).startswith('apd05'):
            self.before_mutation('APD05_version_perception_request')
            from capacidades import percepcion_vigencia_apd05 as version_sensor
            value=version_sensor.dispatch(self.a,rows[0],self.work_directory,feedback=payload.get('retorno','real'),actuator=payload.get('actuador','closed'))
            return {'version':'APD05.explicit_optional_owner_extension.R01','rows':[value],
                'INSTRUMENTO_FENCE':{'denied':self.guard['denied_operations'],'scope':self.guard['scope']}}
        return super().execute(payload)
