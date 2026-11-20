"""Gramática explícita: interpreta solicitudes, no resuelve sus preguntas."""
from dataclasses import dataclass
import re
import unicodedata


def normalized(text):
    folded=''.join(c for c in unicodedata.normalize('NFKD',text.casefold()) if not unicodedata.combining(c))
    return re.sub(r'\s+',' ',folded.strip(' \t\r\n¿?¡!.,'))


@dataclass(frozen=True)
class Command:
    operation: str
    argument: str | None = None


def parse(text):
    s=normalized(text)
    known={
        'ayuda':'help','que puedo preguntar':'help','salir':'exit',
        'que pasara despues':'predict','predice antes de observar':'predict',
        'ocurrira lo mismo':'predict','predice':'predict',
        'observa otra vez':'sense','observa el entorno':'sense','observa':'observe','muestra el estado':'observe',
        'compara esto con lo anterior':'compare','compara':'compare',
        'que fuente necesitas observar':'source','que distincion importa':'source',
        'avanza el entorno':'advance','continua':'advance',
        'guarda la sesion':'save','continua desde la sesion guardada':'load',
        'carga la sesion':'load','instancia nueva':'new','crear instancia':'new',
    }
    if s in known:return Command(known[s])
    for prefix,op in [('presenta experiencia ','experience'),('experiencia ','experience'),('mira ','experience')]:
        if s.startswith(prefix):return Command(op,s[len(prefix):].strip())
    # Preserve user spelling of opaque aliases and filesystem paths.
    m=re.fullmatch(r'\s*a esto lo llamaremos\s+(.+?)\s*[.!]?\s*',text,re.I)
    if m:return Command('alias',m.group(1).strip())
    m=re.fullmatch(r'\s*(?:guarda|guardar)\s+(?:la sesion\s+)?(?:en\s+)?(.+?)\s*',text,re.I)
    if m:return Command('save',m.group(1).strip())
    m=re.fullmatch(r'\s*(?:carga|cargar|continua desde)\s+(.+?)\s*',text,re.I)
    if m:return Command('load',m.group(1).strip())
    raise ValueError('Entrada no admitida. Escribe «ayuda» para ver la gramática real.')


HELP=(
    'INTERFAZ: órdenes: «Instancia nueva», «Presenta experiencia A/B», '
    '«¿Qué pasará después?», «¿Ocurrirá lo mismo?», «Predice antes de observar», '
    '«Observa otra vez» (acontecimiento del entorno), «Muestra el estado» (lectura pasiva), '
    '«Avanza el entorno», «A esto lo llamaremos X», '
    '«Guarda la sesión [en ruta]», «Continúa desde la sesión guardada» y «Salir». '
    'Compara/fuente sólo se activan si el ente exporta esas emisiones. '
    'A/B son nombres externos de sensores físicos, no significados aprendidos. '
    'Los alias son referencias de interfaz, no nuevas asociaciones adquiridas.'
)
