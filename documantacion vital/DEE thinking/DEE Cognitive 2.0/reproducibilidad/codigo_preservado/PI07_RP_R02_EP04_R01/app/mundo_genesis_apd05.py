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
        from capacidades import progresion_integrada_01 as pi
        for name in ('progresion_integrada_01.py','pi01_traza_legal_base.py'):
            path=Path(__file__).resolve().parents[1]/'capacidades'/name
            self.code_sha256[name]=hashlib.sha256(path.read_bytes()).hexdigest()
        pi.resources_valid(self.a,self.work_directory)
        from capacidades import pi02_habitat_R04 as habitat
        from capacidades.adapter_habitat_R04 import wrap
        # Validate the paired external workbench before publishing a ready owner.
        # This is an instrument/continuity check, not an actor memory query.
        habitat.operational_dependencies(self.a,self.work_directory)
        self.a=wrap(self.a,self.work_directory)
        for name in ('progresion_integrada_02.py','pi02_habitat_R04.py','adapter_habitat_R04.py','fi_async_R04.py','pi02_advertencia_R03.py'):
            path=Path(__file__).resolve().parents[1]/'capacidades'/name
            self.code_sha256[name]=hashlib.sha256(path.read_bytes()).hexdigest()
        from capacidades import progresion_integrada_03_R01 as pi03
        from capacidades import pi03_tarea_diferida_R02 as task
        if task.KEY in dict(self.a.world.runtime.snapshot_metadata_entries):
            task.operational_dependencies(self.a,self.work_directory)
        else:
            pi03.operational_dependencies(self.a,self.work_directory)
        for name in ('progresion_integrada_03_R01.py','pi03_credito_generico_R01_BORRADOR.py','PROTOCOLO_PI03_R01.json','pi03_tarea_diferida_R02.py','pi03_dispositivo_diferido_R02_PROPUESTA.py','PROTOCOLO_PI03_TAREA_R02.json','pi03_suministro_explicito_R03.py','pi03_cadena_variable_R04.py','pi03_diagnostico_cola_R05.py','pi03_diagnostico_cola_R05b.py','pi03_proteccion_cola_OP3.py','pi03_diagnostico_cola_R05c.py'):
            self.code_sha256[name]=hashlib.sha256((Path(__file__).resolve().parents[1]/'capacidades'/name).read_bytes()).hexdigest()
        from capacidades import pi04_dispatcher as pi04
        pi04.operational_dependencies(self.a,self.work_directory)
        for path in pi04.code_files():
            self.code_sha256['PI04/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
        from capacidades import pi05_transito_causal_R01 as pi05
        for path in pi05.code_files():
            self.code_sha256['PI05/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
        from capacidades import pi05_guardia_transito_R01 as support
        for path in support.code_files():
            self.code_sha256['PI05/support/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
        from capacidades import pi07_observar_ep04_R01 as pi07
        pi07.operational_dependencies(self.a,self.work_directory)
        for path in pi07.code_files():
            self.code_sha256['PI07/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
        return result

    def validate(self,payload):
        row=self._eci01_row(payload)
        if row is not None and str(row.get('modo','')).startswith('eci01-pi07-'):
            from capacidades import pi07_observar_ep04_R01 as pi07
            pi07.validate(self.a,row)
            return
        if row is not None and row.get('modo')in('eci01-pi05-c2c-ampliar','eci01-pi05-c2c-extension-estado'):
            from capacidades import pi05_c2c_ofertas_R01 as extension
            extension.validate(self.a,row)
            return
        if row is not None and row.get('modo')in('eci01-pi05-fiplus-guardia','eci01-pi05-fiplus-sham','eci01-pi05-guardia-preparar','eci01-pi05-sham-preparar'):
            from capacidades import pi05_guardia_transito_R01 as support
            support.validate(self.a,row)
            return
        if row is not None and str(row.get('modo','')).startswith('eci01-pi05-'):
            from capacidades import pi05_transito_causal_R01 as pi05
            pi05.validate(self.a,row)
            return
        if row is not None and str(row.get('modo','')).startswith('eci01-pi04-'):
            from capacidades import pi04_dispatcher as pi04
            pi04.validate(self.a,row)
            return
        if row is not None and row.get('modo') == 'eci01-pi03-cola-proteger':
            from capacidades import pi03_proteccion_cola_OP3 as support
            support.validate(self.a,row,directory=self.work_directory)
            return
        if row is not None and row.get('modo') == 'eci01-pi03-diagnostico-cola':
            from capacidades import pi03_diagnostico_cola_R05c as tail
            tail.validate(self.a,row,directory=self.work_directory)
            return
        if row is not None and row.get('modo') == 'eci01-pi03-tarea-suministrar':
            from capacidades import pi03_suministro_explicito_R03 as supply
            supply.validate(self.a,row,directory=self.work_directory)
            return
        if row is not None and row.get('modo') in ('eci01-pi03-tarea-suministrar-cadena','eci01-pi03-tarea-cadena-corte','eci01-pi03-tarea-cadena-estado'):
            from capacidades import pi03_cadena_variable_R04 as chain
            chain.validate(self.a,row,directory=self.work_directory)
            return
        if row is not None and str(row.get('modo','')).startswith('eci01-pi03-tarea-'):
            from capacidades import pi03_tarea_diferida_R02 as task
            task.validate(self.a,row)
            return
        if row is not None and str(row.get('modo','')).startswith('eci01-pi03-'):
            from capacidades import progresion_integrada_03_R01 as pi03
            pi03.validate(self.a,row)
            return
        if row is not None and str(row.get('modo','')).startswith('eci01-pi02-'):
            from capacidades import progresion_integrada_02 as pi02
            pi02.validate(self.a,row)
            return
        if row is not None and str(row.get('modo','')).startswith('eci01-pi01-'):
            from capacidades import progresion_integrada_01 as pi
            pi.validate(self.a,row)
            return
        if row is not None and row.get('modo')=='eci01-aritmetica-directa':
            if self.backend!='mente_unificada':raise ValueError('Explicit inherited unified backend required')
            from capacidades import aritmetica_directa_eci02 as direct
            direct.validate(self.a,row)
            return
        if row is not None:
            if self.backend!='mente_unificada':raise ValueError('Explicit inherited unified backend required')
            from capacidades import acceso_integrado_eci01 as acceso_eci01
            acceso_eci01.validate(self.a,row)
            return
        rows=payload.get('situaciones',[])
        extended=[r for r in rows if isinstance(r.get('modo'),str)and r['modo'].startswith('apd05')]
        if payload.get('operacion')=='sesion'and extended:
            if self.backend!='mente_unificada'or len(rows)!=1:raise ValueError('One explicit APD05 operation in the shared-world owner')
            from capacidades import percepcion_vigencia_apd05 as version_sensor
            version_sensor.validate(self.a,rows[0]);return
        return super().validate(payload)

    def execute(self,payload):
        row=self._eci01_row(payload)
        if row is not None and str(row.get('modo','')).startswith('eci01-pi07-'):
            from capacidades import pi07_observar_ep04_R01 as pi07
            pi07.validate(self.a,row)
            self.before_mutation('PI07_EXPLICIT_NEW_TC_SENSOR_FIXED_ACTUATOR_PROTOCOL')
            value=pi07.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)
            return {'version':pi07.VERSION,'rows':[value]}
        if row is not None and row.get('modo')in('eci01-pi05-c2c-ampliar','eci01-pi05-c2c-extension-estado'):
            from capacidades import pi05_c2c_ofertas_R01 as extension
            extension.validate(self.a,row)
            self.before_mutation('PI05_EXPLICIT_ENVIRONMENT26_TO30_NO_NATIVE_EDIT')
            value=extension.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)
            return {'version':extension.VERSION,'rows':[value]}
        if row is not None and row.get('modo')in('eci01-pi05-fiplus-guardia','eci01-pi05-fiplus-sham','eci01-pi05-guardia-preparar','eci01-pi05-sham-preparar'):
            from capacidades import pi05_guardia_transito_R01 as support
            support.validate(self.a,row)
            self.before_mutation('PI05_ONE_TIME_LEGAL_RAW_EMPTY_GUARD_OR_SHAM')
            value=support.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)
            return {'version':support.VERSION,'rows':[value]}
        if row is not None and str(row.get('modo','')).startswith('eci01-pi05-'):
            from capacidades import pi05_transito_causal_R01 as pi05
            pi05.validate(self.a,row)
            self.before_mutation('PI05_EXPLICIT_TRANSIT_INSTRUMENT_OR_EXTERNAL_CONTROL')
            value=pi05.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)
            return {'version':pi05.VERSION,'rows':[value]}
        if row is not None and str(row.get('modo','')).startswith('eci01-pi04-'):
            from capacidades import pi04_dispatcher as pi04
            pi04.validate(self.a,row)
            self.before_mutation('PI04_EXPLICIT_DIAGNOSTIC_PROTOCOL')
            value=pi04.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)
            return {'version':pi04.VERSION,'rows':[value]}
        if row is not None and row.get('modo') == 'eci01-pi03-cola-proteger':
            from capacidades import pi03_proteccion_cola_OP3 as support
            support.validate(self.a,row,directory=self.work_directory)
            self.before_mutation('PI03_QUALIFIED_ONE_TIME_P0_POSTREAD_SUPPORT')
            value=support.dispatch(self.a,row,directory=self.work_directory,actuator=payload.get('actuador','closed'))
            return {'version':support.VERSION,'rows':[value]}
        if row is not None and row.get('modo') == 'eci01-pi03-diagnostico-cola':
            from capacidades import pi03_diagnostico_cola_R05c as tail
            tail.validate(self.a,row,directory=self.work_directory)
            self.before_mutation('PI03_FROZEN_ZERO_TAIL_GUARD_DIAGNOSTIC')
            value=tail.dispatch(self.a,row,directory=self.work_directory,actuator=payload.get('actuador','closed'))
            return {'version':tail.VERSION,'rows':[value]}
        if row is not None and row.get('modo') == 'eci01-pi03-tarea-suministrar':
            from capacidades import pi03_suministro_explicito_R03 as supply
            supply.validate(self.a,row,directory=self.work_directory)
            self.before_mutation('PI03_EXPLICIT_ENVIRONMENTAL_SUPPLY')
            value=supply.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)
            return {'version':supply.VERSION,'rows':[value]}
        if row is not None and row.get('modo') in ('eci01-pi03-tarea-suministrar-cadena','eci01-pi03-tarea-cadena-corte','eci01-pi03-tarea-cadena-estado'):
            from capacidades import pi03_cadena_variable_R04 as chain
            chain.validate(self.a,row,directory=self.work_directory)
            self.before_mutation('PI03_VARIABLE_ACTUAL_NATIVE_DATA_CHAIN')
            value=chain.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)
            return {'version':chain.VERSION,'rows':[value]}
        if row is not None and str(row.get('modo','')).startswith('eci01-pi03-tarea-'):
            from capacidades import pi03_tarea_diferida_R02 as task
            task.validate(self.a,row)
            self.before_mutation('PI03_USEFUL_DELAYED_NATIVE_TASK')
            value=task.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)
            return {'version':task.VERSION,'rows':[value]}
        if row is not None and str(row.get('modo','')).startswith('eci01-pi03-'):
            from capacidades import progresion_integrada_03_R01 as pi03
            pi03.validate(self.a,row)
            self.before_mutation('PI03_CONTROLLED_NATIVE_PROTOCOL')
            value=pi03.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)
            return {'version':pi03.VERSION,'rows':[value]}
        if row is not None and str(row.get('modo','')).startswith('eci01-pi02-'):
            from capacidades import progresion_integrada_02 as pi02
            pi02.validate(self.a,row)
            self.before_mutation('PI02_DECLARED_CONTROLLED_PROTOCOL')
            value=pi02.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)
            return {'version':pi02.VERSION,'rows':[value],'INSTRUMENTO_FENCE':{'denied':self.guard['denied_operations'],'scope':self.guard['scope']}}
        if row is not None and str(row.get('modo','')).startswith('eci01-pi01-'):
            from capacidades import progresion_integrada_01 as pi
            pi.validate(self.a,row)
            self.before_mutation('PI01_DECLARED_EXPERIMENTAL_PROTOCOL')
            value=pi.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)
            return {'version':pi.VERSION,'rows':[value],'INSTRUMENTO_FENCE':{'denied':self.guard['denied_operations'],'scope':self.guard['scope']}}
        if row is not None and row.get('modo')=='eci01-aritmetica-directa':
            from capacidades import aritmetica_directa_eci02 as direct
            direct.validate(self.a,row)
            self.before_mutation('ECI02_OPERATOR_SELECTED_NATIVE_ARITHMETIC_P0')
            value=direct.execute(self.a,row,actuator=payload.get('actuador','closed'))
            return {'version':direct.VERSION,'rows':[value],
                'INSTRUMENTO_FENCE':{'denied':self.guard['denied_operations'],'scope':self.guard['scope']}}
        if row is not None:
            from capacidades import acceso_integrado_eci01 as acceso_eci01
            acceso_eci01.validate(self.a,row)
            if row['modo']!='eci01-entorno-estado':self.before_mutation('ECI01_FIXED_EARLY_ACCESS')
            value=acceso_eci01.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)
            return {'version':acceso_eci01.VERSION,'rows':[value],
                'INSTRUMENTO_FENCE':{'denied':self.guard['denied_operations'],'scope':self.guard['scope']}}
        rows=payload.get('situaciones',[])
        if payload.get('operacion')=='sesion'and len(rows)==1 and str(rows[0].get('modo','')).startswith('apd05'):
            self.before_mutation('APD05_version_perception_request')
            from capacidades import percepcion_vigencia_apd05 as version_sensor
            value=version_sensor.dispatch(self.a,rows[0],self.work_directory,feedback=payload.get('retorno','real'),actuator=payload.get('actuador','closed'))
            return {'version':'APD05.explicit_optional_owner_extension.R01','rows':[value],
                'INSTRUMENTO_FENCE':{'denied':self.guard['denied_operations'],'scope':self.guard['scope']}}
        return super().execute(payload)

    def _eci01_row(self,payload):
        rows=payload.get('situaciones',[])
        selected=[r for r in rows if isinstance(r.get('modo'),str)and r['modo'].startswith('eci01-')]
        if not selected:return None
        if payload.get('operacion')!='sesion'or len(rows)!=1:raise ValueError('One explicit ECI01 request only; no mixing with another protocol')
        return selected[0]

    def operational_dependencies(self):
        from capacidades import acceso_eci01
        result=acceso_eci01.extend_operational_dependencies(self.a,super().operational_dependencies())
        from capacidades import progresion_integrada_01 as pi
        result['PI01']=pi.resources_valid(self.a,self.work_directory)
        from capacidades import progresion_integrada_02 as pi02
        result['PI02']=pi02.operational_dependencies(self.a,self.work_directory)
        from capacidades import pi03_diagnostico_cola_R05c as tail
        result['PI03_tail_diagnostic']=tail.operational_dependencies(self.a,self.work_directory)
        from capacidades import pi03_diagnostico_cola_R05b as previous_tail_B
        result['PI03_tail_diagnostic_B_preserved']=previous_tail_B.operational_dependencies(self.a,self.work_directory)
        from capacidades import pi03_proteccion_cola_OP3 as support
        result['PI03_prepared_postread_support']=support.operational_dependencies(self.a,self.work_directory)
        from capacidades import pi04_dispatcher as pi04
        result['PI04']=pi04.operational_dependencies(self.a,self.work_directory)
        from capacidades import pi07_observar_ep04_R01 as pi07
        result['PI07']=pi07.operational_dependencies(self.a,self.work_directory)
        return result

    def external_uncertainty(self):
        from capacidades import pi07_observar_ep04_R01 as pi07
        if pi07.uncertain(self.a):return True
        from capacidades import pi04_dispatcher as pi04
        if pi04.uncertain(self.a):return True
        from capacidades import pi03_diagnostico_cola_R05b as previous_tail_B
        if previous_tail_B.uncertain(self.a):return True
        from capacidades import pi03_proteccion_cola_OP3 as support
        if support.uncertain(self.a):return True
        from capacidades import pi03_diagnostico_cola_R05 as previous_tail
        if previous_tail.uncertain(self.a):return True
        from capacidades import pi03_diagnostico_cola_R05c as tail
        if tail.uncertain(self.a):return True
        from capacidades import acceso_eci01
        from capacidades import progresion_integrada_01 as pi
        from capacidades import progresion_integrada_02 as pi02
        return super().external_uncertainty()or acceso_eci01.external_uncertainty(self.a)or pi.uncertain(self.a)or pi02.uncertain(self.a)
