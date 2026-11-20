"""Small Spanish command interface for the consolidated native sessions.

This parser selects an explicitly requested operation. It neither chooses an
answer nor extends a measured opaque association into unrestricted language.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shlex
from .consolidated import (RepertoireSession, IntegratedSession,
                           load_consolidated_session)

HELP = ["nuevo repertorio [1..65]", "nuevo integrado", "nuevo remoto (experimental)", "historia AB|BA",
        "experiencia L01 -1 0 [paired|unpaired|no_event|no_symbol]",
        "bloque L01:+1,L02:-1 0", "consecuencia -1", "accion",
        "ensenar-forma [paired|unpaired|omitted]", "preguntar-forma [139]",
        "consulta L01,L02 67 [5]", "actualizar L01 +1 268 [M1|M2]",
        "fuentes +1 -1 [paired|unpaired|omitted] (remoto)", "uso-remoto", "ensenar-primera [modo]",
        "programar-primera 50", "segunda-forma [modo]", "lecturas",
        "hasta 70", "observar [L01]", "recibos", "guardar archivo.deetsnap.gz",
        "cargar [remoto] archivo.deetsnap.gz", "reiniciar confirmar", "salir"]


class ConsolidatedConversation:
    def __init__(self):
        self.session = None

    def _require(self):
        if self.session is None:raise ValueError("Primero nuevo o cargar")
        return self.session

    def _integrated(self):
        s=self._require()
        if not isinstance(s,IntegratedSession):raise ValueError("La operación requiere el perfil integrado")
        return s

    def execute(self,line):
        if not isinstance(line,str):raise TypeError("La orden debe ser texto")
        a=shlex.split(line,posix=True)
        if not a or a[0].startswith('#'):return None
        op=a.pop(0).lower()
        if op=="ayuda":return {"procedencia":"INTERFAZ","gramatica":HELP,
            "alcance":"Órdenes estructuradas, no conversación libre. La clase±1 es una lectura física dentro del decoder publicado, no65significadosNSM."}
        if op=="nuevo":
            if self.session is not None:raise ValueError("Ya existe una continuidad; use reiniciar confirmar")
            if a==["integrado"]:self.session=IntegratedSession.create()
            elif a==["remoto"]:
                from .remote_reader import RemoteReaderSession
                self.session=RemoteReaderSession.create()
            elif 1<=len(a)<=2 and a[0]=="repertorio":self.session=RepertoireSession.create(count=int(a[1]) if len(a)==2 else 16)
            else:raise ValueError("nuevo repertorio [cantidad] | nuevo integrado | nuevo remoto")
            return {"procedencia":"INSTRUMENTO","operacion":"PREPARACION_NUEVA_T0",
                    "perfil":self.session.session_kind,"tick":self.session.tick,"formas":getattr(self.session,'forms',()),
                    "dominio":self.session.preparation.domain if hasattr(self.session,'preparation') else 'EXPERIMENTAL_CPC6_N67_READER_WINDOW162'}
        if op=="reiniciar":
            if a!=["confirmar"]:raise ValueError("reiniciar confirmar: no borra archivos")
            self.session=None;return {"procedencia":"INTERFAZ","operacion":"REINICIO_VISIBLE"}
        if op=="cargar":
            if self.session is not None or len(a) not in(1,2):raise ValueError("cargar [remoto] archivo requiere ausencia de instancia activa")
            if len(a)==2:
                if a[0]!='remoto':raise ValueError('El único selector adicional es remoto')
                from .remote_reader import RemoteReaderSession
                self.session=RemoteReaderSession.load_snapshot(a[1])
            else:self.session=load_consolidated_session(a[0])
            return {"procedencia":"INSTRUMENTO","operacion":"RESTAURACION_NO_PREPARACION",
                    "tick":self.session.tick,"almacenamiento":self.session.storage_proof}
        s=self._require()
        if s.session_kind=='remote_reader_experimental' and op in('historia','fuentes','consecuencia','uso-remoto','ensenar-primera','programar-primera','segunda-forma','lecturas'):
            if op=='historia' and len(a)==1:value=s.experience_order(a[0])
            elif op=='fuentes' and len(a) in(2,3):value=s.acquire_sources(int(a[0]),int(a[1]),mode=a[2] if len(a)==3 else'paired')
            elif op=='consecuencia' and len(a)==1:value=s.consequence(int(a[0]))
            elif op=='uso-remoto' and not a:value=s.late_use()
            elif op=='ensenar-primera' and len(a)<=1:value=s.teach_first_form(mode=a[0] if a else'paired')
            elif op=='programar-primera' and len(a)==1:value=s.query_first_form(tick=int(a[0]))
            elif op=='segunda-forma' and len(a)<=1:value=s.learn_second_form(mode=a[0] if a else'paired')
            elif op=='lecturas' and not a:return {'procedencia':'INSTRUMENTO','capturas_de_consultas_fisicas':s.readings,'alcance':'Lecturas capturadas identificadas por tick; no se usan para responder una nueva consulta.'}
            else:raise ValueError('Argumentos fuera de la gramática remota; consulte ayuda')
            return {'procedencia':'INSTRUMENTO','operacion':'PROTOCOLO_REMOTO_EXPERIMENTAL_PROGRAMADO','tick_actual':s.tick,'resultado':value}
        if s.session_kind=='remote_reader_experimental' and op not in('hasta','observar','recibos','guardar'):
            raise ValueError('Operación no publicada por el perfil remoto experimental; consulte ayuda')
        if op=="historia":
            if len(a)!=1:raise ValueError("historia AB|BA")
            value=self._integrated().experience_order(a[0]);kind="ACONTECIMIENTOS_PROGRAMADOS"
        elif op=="experiencia":
            if len(a) not in(3,4):raise ValueError("experiencia L01 ±1 tick [modo]")
            value=s.acquire(a[0],int(a[1]),int(a[2]),mode=a[3] if len(a)==4 else"paired");kind="EXPERIENCIA_PROGRAMADA"
        elif op=="bloque":
            if len(a)!=2:raise ValueError("bloque L01:+1,L02:-1 tick")
            pairs=[item.split(':') for item in a[0].split(',')]
            if any(len(item)!=2 for item in pairs) or len({item[0] for item in pairs})!=len(pairs):
                raise ValueError("Cada forma aparece una vez con su consecuencia actual")
            value=s.acquire_block({name:int(sign) for name,sign in pairs},int(a[1]));kind="BLOQUE_EXPERIENCIAS_PROGRAMADO"
        elif op=="consecuencia":
            if len(a)!=1:raise ValueError("consecuencia ±1")
            value=self._integrated().consequence(int(a[0]));kind="SENSOR_ACTUAL_PROGRAMADO"
        elif op=="accion":
            if a:raise ValueError("accion no recibe una acción correcta: aporta el recurso comúnT69")
            value=self._integrated().action();kind="OPORTUNIDAD_FISICA_COMUN"
        elif op=="ensenar-forma":
            if len(a)>1:raise ValueError("ensenar-forma [paired|unpaired|omitted]")
            value=self._integrated().teach_form(mode=a[0] if a else"paired");kind="ENSENANZA_POSTERIOR_DE_CUE_OPACO"
        elif op=="preguntar-forma":
            if len(a)>1:raise ValueError("preguntar-forma [tick]")
            return {"procedencia":"ENTE","operacion":"SONDA_FISICA_POR_FORMA_OPACA",
                    "lectura":self._integrated().query_form(int(a[0]) if a else 139)}
        elif op=="consulta":
            if len(a) not in(2,3):raise ValueError("consulta L01,L02 tick [payload]")
            return {"procedencia":"ENTE","operacion":"CONSULTA_FISICA_CONSUMIBLE",
                    "lectura":s.query(a[0].split(','),int(a[1]),payload=int(a[2]) if len(a)==3 else 5)}
        elif op=="actualizar":
            if len(a) not in(3,4):raise ValueError("actualizar L01 ±1 tick [M1|M2]")
            method={"M1":"double_teacher","M2":"symmetric_counterflow"}.get(a[3] if len(a)==4 else"M1")
            if method is None:raise ValueError("Método M1 o M2")
            value=s.revise(a[0],int(a[1]),int(a[2]),method=method);kind="REVISION_PREPARADA_PROGRAMADA"
        elif op=="hasta":
            if len(a)!=1:raise ValueError("hasta tick_absoluto")
            value=s.run_until(int(a[0]));kind="EVOLUCION_NATIVA"
        elif op=="observar":
            if len(a)>1:raise ValueError("observar [L01]")
            if s.session_kind=='remote_reader_experimental':
                if a:raise ValueError('observar remoto no toma una forma de repertorio')
                return {'procedencia':'INSTRUMENTO','lectura':s.observe()}
            return {"procedencia":"INSTRUMENTO","lectura":s.observe(a[0] if a else None)}
        elif op=="recibos":
            if a:raise ValueError("recibos no recibe argumentos")
            return {"procedencia":"INSTRUMENTO","recibos":s.receipts()}
        elif op=="guardar":
            if len(a)!=1:raise ValueError("guardar archivo.deetsnap[.gz]")
            return {"procedencia":"INSTRUMENTO","operacion":"GUARDADO_INTEGRAL","archivo":s.save_snapshot(a[0])}
        else:raise ValueError("Orden fuera de gramática; escriba ayuda")
        return {"procedencia":"INSTRUMENTO","operacion":kind,"tick_actual":s.tick,"resultado":value,
                "nota":"Programado no significa aplicado. Consulte los recibos después de evolucionar; ausencia, rechazo y cero son datos distintos."}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--events',type=Path);p.add_argument('--transcript',type=Path);p.add_argument('--strict',action='store_true')
    a=p.parse_args(argv);c=ConsolidatedConversation();events=[];failed=False
    source=a.events.read_text(encoding='utf-8-sig').splitlines() if a.events else None
    while True:
        if source is not None:
            if not source:break
            line=source.pop(0)
        else:
            try:line=input('DEE4.5> ')
            except EOFError:break
        if line.strip().lower()=='salir':break
        try:row={"orden":line,"resultado":c.execute(line)}
        except (ValueError,TypeError,RuntimeError,OSError) as error:
            failed=True;row={"orden":line,"error":type(error).__name__,"mensaje":str(error)}
        events.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
        if a.transcript:
            a.transcript.parent.mkdir(parents=True,exist_ok=True)
            a.transcript.write_text(json.dumps({"schema":"dee_thinking.consolidated.es.v1","eventos":events},ensure_ascii=False,indent=2),encoding='utf-8')
    return 1 if a.strict and failed else 0


if __name__=='__main__':raise SystemExit(main())
