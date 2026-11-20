"""Update only editorial draft from actual RP/panel/future closures. No DOCX."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
P=Path(__file__).resolve().parents[1];file=P/'documentos/HECHOS_FINALES_1_38_PI09_BORRADOR.json';before=file.read_bytes();d=json.loads(before);assert d['closed_for_authoring']is False
def ref(name):
    p=P/name;return {'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
rp=json.loads((P/'control/RP_D6_FAMILIA_REGISTRADA_PI09_R01.json').read_text('utf8'));panel=json.loads((P/'control/PI09_PANEL_POST_D12_R03.json').read_text('utf8'));last=json.loads((P/'control/PI09_D_RETENCION7_R03.json').read_text('utf8'))
assert rp['registered']and rp['actual_prior_native_replay_ticks']==10136 and panel['closed']and panel['error']is None and panel['final_tick']==920520 and last['closed']and last['error']is None and last['final_tick']==922371
M=d['manual_sections'];C=d['compendium_sections']
M[4]['paragraphs'][1]='La receta de familia DRF también se ejecutó por el frente RP: preparación, seis episodios y estado final. Son ocho solicitudes y seis oportunidades, con 10136 ticks y 1139 entradas solicitadas:1137 aplicadas y dos conflictos. Reprodujo cinco usos útiles y el primer fallo, sin ocultarlo. La comparación completa Native y de prefijo fue positiva y el registro posterior añadió cero ticks. No reproduce como ensayo independiente el panel y uso posteriores del estado maduro.'
M[4]['sources']+=['control/COMPARACION_RP_D6_FAMILIA_PI09_R01.json','control/RP_D6_FAMILIA_REGISTRADA_PI09_R01.json']
M[9]['paragraphs'][0]='Este JSON no autoriza aún la autoría: closed_for_authoring es false. El principal real confirmado en el último comprobante de selección sigue siendo Native T903603. Sus estados públicos conservaron ordinal12/18 en consulta,31/32 en C2C y4/8 en FI. Discovery cerró el panel anterior12/12 en T920520 y después un nuevo uso D ordinal6: útil,190/190 entradas admitidas, hasta T922371. D quedó en7/12, con cinco ofertas futuras. Son recursos finitos explícitos.'
M[9]['paragraphs'][1]='El panel de doce funciones se observó antes de ese último uso. No se atribuye un segundo panel completo al corte922371. La primera selección de ese uso fue cero Native válido y NoQuery material; la segunda fue neutral, FI+ y mensaje íntegro. Root debe enlazar la reapertura0 de la fuente y su decisión efectiva antes de fijar la edición final. No se declara ningún uso material posterior a COMMITTED.'
M[9]['paragraphs'].append('Si D se incorpora, el resultado C1 de doce oportunidades seguirá siendo historia heredada y reproducida. Su API material ancestral R02 queda de sólo lectura en el sistema D; no se promete que las doce situaciones antiguas sin la nueva guarda se hayan vuelto a aprobar. La continuación operativa usa el nuevo contrato y contador D. El Manual1.37 y sus capítulos permanecen literales. La publicación1.38 y su revisión visual siguen pendientes en este borrador.')
M[9]['sources']+=['control/PI09_PANEL_POST_D12_R03.json','control/PI09_D_RETENCION7_R03.json']
for i in(4,9):C[i]={'heading':M[i]['heading'],'paragraphs':[' '.join(M[i]['paragraphs'])],'sources':list(M[i]['sources'])}
d['front']['conservation_summary']='Hito1: dos clones12/12 más5/5, con ganancia P0 adicional cero. Después de D se comprobó un panel12/12 en T920520 y un nuevo uso D útil en T922371. No se atribuye un panel completo nuevo a ese corte final. La selección y reapertura finales aún deben cerrarse por Root.'
d['front']['control_table']['Estado de esta edición']='closed_for_authoring:false. RP DRF6, panel12/12 y uso D posterior cerrados. Faltan Source0/decisión/selección final efectivas. No ejecutar autoría o publicación desde este borrador.'
d['pending_finalization']['D_conservation']={'status':'ACTUAL_CLOSED_12OF12','proof':ref('control/PI09_PANEL_POST_D12_R03.json'),'cut':920520}
d['pending_finalization']['D_last_use_after_reopen']={'status':'ACTUAL_CLOSED_USEFUL','proof':ref('control/PI09_D_RETENCION7_R03.json'),'ordinal':6,'final_tick':922371,'D_remaining':5,'first_Native_choice':0,'first_choice_is_NULL':False,'Native_requested_applied':190}
d['pending_finalization']['D_material_replay']={'status':'ACTUAL_NATIVE_REPLAY_REGISTERED','proof':ref('control/RP_D6_FAMILIA_REGISTRADA_PI09_R01.json'),'actual_replay_ticks':10136,'opportunities':6,'material_requests_in_recipe':8,'useful':5,'not_independent_statistical_replication':True}
existing={x['path']for x in d['evidence']}
for name in('control/RP_D6_FAMILIA_REGISTRADA_PI09_R01.json','control/COMPARACION_RP_D6_FAMILIA_PI09_R01.json','control/PI09_PANEL_POST_D12_R03.json','control/PI09_D_RETENCION7_R03.json'):
    r=ref(name)
    if r['path']not in existing:d['evidence'].append(r)
d['cut_utc']=datetime.now(timezone.utc).isoformat();d['last_observed_D_experimental_cut']={'life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01','N':67,'T':922371,'ordinal':7,'total':12,'remaining':5,'not_yet_attributed_as_selected':True}
backup=P/'documentos/revisiones'/('HECHOS_138_ANTES_CIERRES_D_'+hashlib.sha256(before).hexdigest()[:12]+'.json')
with backup.open('xb')as f:f.write(before)
file.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'file':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'closed_for_authoring':False,'DOCX_or_Native_executed':False}))
