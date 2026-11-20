"""Editorial spacing in NEW PI11 prose only; never touches scientific source data."""
from pathlib import Path
import re,json
P=Path(__file__).resolve().parents[1]
src=P/'fuentes/HECHOS_INFORME_PI11_Root_R01.json'
out=P/'fuentes/HECHOS_INFORME_PI11_Root_R02.json'
f=json.loads(src.read_text('utf8'))
def prose(s):
    s=s.replace('C2C','ZZZCTWOCTOKENZZZ')
    s=re.sub(r'(?<=[0-9])(?=[A-Za-zÁÉÍÓÚáéíóúñ])',' ',s)
    s=re.sub(r'\b(con|de|los|las|en|hasta|desde|y|al|por|son|tiene|contiene|produjo|quedan|queda|registró|fueron|tras)(?=[0-9])',r'\1 ',s)
    for a,b in {
      'RAWno':'RAW no','sinentrega':'sin entrega','Nativecompletas':'Native completas',
      'Nativeincompleta':'Native incompleta','PI11adquirido':'PI11 adquirido',
      'enlos':'en los','porlos':'por los','sin ejecutar':'sin ejecutar',
      'Nodecision':'No decisión','noadoptado':'no adoptado','noadoptó':'no adoptó',
      'laparada':'la parada','almismo':'al mismo','delpanel':'del panel',
      'deambosretornos':'de ambos retornos','capacidadPI11':'capacidad PI11',
      'Operandoreal':'Operando real','comparación18':'comparación 18',
      'sinrechazo':'sin rechazo','NativeClock':'Native Clock','losmismos':'los mismos',
      'dela':'de la','delprincipal':'del principal','públicooperativo':'público operativo',
      'bank':'bank','SourceNative':'Source Native','frozen':'frozen',
      'hastaT':'hasta T','deldato':'del dato','delheredado':'del heredado',
      'uncertaintrue':'uncertain=true','nodefine':'no define','encaso':'en caso',
      'Noestá':'No está','Nativeprefix':'Native prefix','entornoPI11':'entorno PI11',
      'nuncael':'nunca el','identidadNative':'identidad Native','QP':'QP',
      'rutasNative':'rutas Native','controlNative':'control Native',
      'iniciativaNative':'iniciativa Native','propietarioNative':'propietario Native',
      'niNative':'ni Native','yNative':'y Native','cada784':'cada 784',
      'shamlocal':'sham local','deJob':'de Job','porNative':'por Native',
      'Sourcecell':'Source cell','delreto':'del reto','fijoantes':'fijo antes',
      'Kernel':'Kernel',
    }.items(): s=s.replace(a,b)
    return s.replace('ZZZCTWOCTOKENZZZ','C2C')
f['opening_paragraphs']=[prose(x) for x in f['opening_paragraphs']]
for sec in f['sections']:
    sec['heading']=prose(sec['heading']); sec['paragraphs']=[prose(x) for x in sec['paragraphs']]
for a in f['arms']: a['label']=prose(a['label']);a['explanation']=prose(a['explanation'])
for a in f['attribution_rows']:
    for k in a: a[k]=prose(a[k])
for k in f['front']:
    if k=='control_table':
        f['front'][k]={a:prose(b) for a,b in f['front'][k].items()}
    else: f['front'][k]=prose(f['front'][k])
with out.open('x',encoding='utf8') as h: json.dump(f,h,ensure_ascii=False,indent=2);h.write('\n')
print(json.dumps({'facts':str(out),'opening_words':len(' '.join(f['opening_paragraphs']).split()),'scope':'New editorial prose only; sources/metrics/IDs untouched'}))

