"""R12 S04/S05/S08/S11: views of CLOSED U0 observations, no DEE imports.

Progress selects editorial holds/cuts. It never moves physical coordinates,
interpolates RAW/clocks or supplies an unobserved tick. Source and control lives
remain separate. The CPC7 comparator observation is explicitly attributed.
"""
from pathlib import Path
from functools import lru_cache
from copy import deepcopy
import gzip,hashlib,json,struct

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'evidencia_u0/U0_DATOS_R12.json.gz'
COTEJO=ROOT/'evidencia_u0/COTEJO_ORIGEN_U0_R12.json'
PRIMARY='IR_P01_GUARDED_M1'
RESERVE='IR_R607_GUARDED_M1'
MATCH='IR_MATCH_CURRENT'

def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
@lru_cache(maxsize=8)
def file_source(path):
    return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
@lru_cache(maxsize=1)
def data():return json.loads(gzip.decompress(DATA.read_bytes()))
@lru_cache(maxsize=1)
def cotejo():return json.loads(COTEJO.read_text(encoding='utf8'))
def case(name=PRIMARY):return data()['cases'][name]
def frame(name,tick):return next(f for f in case(name)['frames']if f['tick']==tick)
def recorded(name,tick):return next(f for f in case(name)['recorded_frames_exact']if int(f['tick'])==tick)
def hub(name,form):return next(f['hub']for f in case(name)['geometry']['forms']if f['name']==form)
def sign(v):return '+'if v>0 else'-'if v<0 else'0'

@lru_cache(maxsize=16)
def channels(name):
    """Only read the archived v2 checkpoint's fixed interface descriptors.

    Their exact coordinates were not repeated in the JSON geometry. Checkpoint
    SHA is bound to the primary RESULT record before parsing. No native loader.
    """
    c=case(name);checkpoint=c['checkpoints_exact'][0]
    path=Path(c['source']['path']).parent/checkpoint['path'];encoded=path.read_bytes()
    h=hashlib.sha256(encoded).hexdigest();assert h==checkpoint['sha256']
    b=gzip.decompress(encoded)if encoded[:2]==b'\x1f\x8b'else encoded;i=0
    def take(n):
        nonlocal i
        v=b[i:i+n];assert len(v)==n;i+=n;return v
    def u(fmt):return struct.unpack(fmt,take(struct.calcsize(fmt)))[0]
    def text():return take(u('<I')).decode('utf8')
    assert take(8)==b'DEETSNP1'and u('<I')==2
    n=u('<I');tick=u('<Q');take(1+8+8);text();total=u('<Q');assert total==n**3
    take(16*total);count=u('<I');assert count<65536
    result={}
    for _ in range(count):
        key=text();site=[u('<I')for _ in range(3)];state=u('<I')
        direction=[u('<i')for _ in range(3)];semantic=u('<B');exp=u('<B');probe=u('<B')
        result[key]={'site':site,'state':state,'direction':direction,'semantic':semantic,
                     'allow_experience':exp,'allow_probe':probe}
    return result,{'path':str(path),'sha256':h,'pointer':'/snapshot-v2/channels',
                   'tick':tick,'N':n,'life':name,'scope':'Prepared interface coordinates; not an observed moving carrier.'}

def calls(name,ports,tick):
    return [q for q in case(name)['calls_exact']if q['port']in ports and int(q['at'])==tick]
def roi(sites,pad=1.2):
    return [[min(s[i]for s in sites)-pad for i in range(3)],
            [max(s[i]for s in sites)+pad for i in range(3)]]
def inside(p,b):return all(a<=x<=z for x,a,z in zip(p,b[0],b[1]))
def source_binding(name,tick,reader=None,control=None,pointer=None):
    c=case(name);f=frame(name,tick)
    return {**c['source'],'pointer':pointer or f['source_pointer'],'tick':tick,
            'life':name,'N':f['N'],'reader':reader,'control':control,
            'scope':f['scope'],'complete_RAW_clock_buffers':f['complete_RAW_clock_buffers']}

def make_panel(name,tick,label,bounds,reader_sites=(),input_ports=(),teaching_ports=(),
               directions=(),difference=(),control=None):
    f=frame(name,tick);pts=deepcopy([p for p in f['points']if inside(p['site'],bounds)])
    ins=[];teachers=[];extra=[]
    if input_ports or teaching_ports:
        ch,origin=channels(name);extra.append(origin)
        ins=[ch[k]['site']for k in input_ports];teachers=[ch[k]['site']for k in teaching_ports]
    roles={tuple(s):'input'for s in ins};roles.update({tuple(s):'teaching'for s in teachers})
    roles.update({tuple(s):'difference'for s in difference})
    for p in pts:p['role']=roles.get(tuple(p['site']),'control'if control else'site')
    binding=source_binding(name,tick,list(reader_sites),control)
    p={'N':f['N'],'tick':tick,'points':pts,'label':label,'bounds':bounds,
       'reader_sites':list(reader_sites),'input_sites':ins,'teaching_sites':teachers,
       'direction_sites':list(directions),'difference_sites':list(difference),
       'source':binding,'evidence_bindings':[binding,*extra]}
    return p

def form_bounds(name,form,revision=False):
    ch,_=channels(name);sites=[hub(name,form)]
    sites.extend(ch[k]['site']for k in [form+'.signal',form+'.event.minus',form+'.event.plus'])
    if revision and name==PRIMARY:
        sites.extend(ch[k]['site']for k in ch if k.startswith('revision.second.treatment.'))
    return roi(sites,1.2)

def readout(name,form,panel):
    return next(q for q in case(name)['readouts_exact']if q['form']==form and q['panel']==panel)
def attach_readout(p,name,q):
    p['reader_sites']=[q['physical']['site']]
    index=case(name)['readouts_exact'].index(q)
    p['reader_evidence']={**case(name)['source'],'pointer':'/readouts/'+str(index),
                          'record':deepcopy(q),'qualified':bool(q['covered']),
                          'life':name,'N':p['N'],'tick':int(q['tick'])}
    if q['covered']:
        assert q['receipt']['status']=='applied'and q['value']is not None
        p['output_text']=sign(q['value'])
    else:p['bottom']='Sin resultado'
    return p

@lru_cache(maxsize=1)
def functional_predicate_source():
    """Bind the archived post-trajectory classifier, reading it only as text."""
    origin=Path(data()['identity']['antecedent_primary_metadata'][1]['path'])
    old=json.loads(origin.read_text(encoding='utf8'))
    path=origin.parent/'executed_source/selective_native.py'
    src=file_source(path)
    assert src['sha256']==old['executed_source']['selective_native.py']
    return {**src,'symbol':'execute: post-trajectory questions/information/actions classifications'}

def functional_bottom(panel,name,kind):
    """Qualify every configured local reader, never infer function from silence.

    These are the frozen archival classifiers applied offline to observed
    fields. Other nonzero RAW/control carriers are retained and drawn unchanged.
    """
    tick,group={'question':(19,'questions'),'information':(70,'own_banks'),
                'use':(72,'actions')}[kind]
    f=recorded(name,tick);observations=f[group];readers=[]
    for label,p in observations.items():
        direction=p['direction'];active=p['state']>0 and p['semantic']!=5
        if kind=='question':valid=active and direction in ([-1,0,0],[1,0,0])
        else:
            valid=active and direction[0]in(-1,1)and direction[1]in(-1,1)and direction[2]==(0 if kind=='information'else 1)
        readers.append({'reader':label,'physical':deepcopy(p),'qualified':bool(valid)})
    assert len(readers)==len(case(name)['geometry'][{'question':'need','information':'banks','use':'actions'}[kind]].get('branches',{})) if kind=='question'else len(readers)==2
    valid=any(q['qualified']for q in readers)
    yes,no={'question':('Pregunta emitida','No emitida'),
            'information':('Acceso observado','Sin acceso'),
            'use':('Uso posterior','Sin uso')}[kind]
    panel['bottom']=yes if valid else no
    pointer=frame(name,tick)['source_pointer']+'/'+group
    panel['bottom_evidence']={**case(name)['source'],'pointer':pointer,
        'life':name,'N':panel['N'],'tick':tick,'readers':readers,
        'qualified':valid,'predicate_source':functional_predicate_source(),
        'predicate':('active AND direction[±1,0,0]'if kind=='question'else
                     'active AND directionX/Y in±1 AND directionZ='+str(0 if kind=='information'else 1)),
        'scope':'Only the complete configured local reader set at this retained tick. No assertion of global silence, memory absence or unobserved motion.',
        'reading_method':'Offline classification of existing observations; no new native query or read event.'}
    return panel

def base(title,panels,notice='',footer='',evidence='Etapas',**extra):
    bindings=[b for p in panels for b in p.get('evidence_bindings',[])]
    physical=[{'N':p['N'],'tick':p['tick'],'points':[
        {k:v for k,v in q.items()if k in ['site','raw','clock','state','s_reg','direction','semantic']}for q in p['points']]}for p in panels]
    return {'title':title,'evidence_type':evidence,'notice':notice,'footer':footer,
            'panels':panels,'source':file_source(DATA),
            'evidence_bindings':bindings,'source_data_hash':digest(physical),
            'no_new_DEE_ticks':True,'phase_is_editorial_not_physical':True,
            'trajectory_limit':'Recorded stages only; no unobserved material motion or continuous lineage.',**extra}

def s04(shot,p):
    if shot==1:
        ticks=[0,3,335,338];tick=ticks[min(3,int(p*4))];b=form_bounds(PRIMARY,'L03')
        port='L03.signal';teach=['L03.event.minus']if tick in [0,3]else[]
        pp=make_panel(PRIMARY,tick,'Experiencia'if tick<335 else'Uso posterior',b,
                      [hub(PRIMARY,'L03')],[port],teach,directions=[hub(PRIMARY,'L03')])
        if tick==338:attach_readout(pp,PRIMARY,readout(PRIMARY,'L03','LOWER_338'))
        return base('Experiencia'if tick<335 else'Uso posterior',[pp],
                    'Saltos temporales','U0 · asociación y lector delimitados')
    if shot==2:
        b=form_bounds(PRIMARY,'L03');tick=335 if p<.3 else 338;ps=[]
        for name,label in [(PRIMARY,'Historia A'),(RESERVE,'Historia B')]:
            q=make_panel(name,tick,label,b,[hub(name,'L03')],['L03.signal'],
                         directions=[hub(name,'L03')],control='Distinct archived training histories; common query335/payload5. Not identical full physical state338.')
            if tick==338:attach_readout(q,name,readout(name,'L03','LOWER_338'))
            ps.append(q)
        return base('Misma consulta',ps,'Historias distintas','Misma geometría, sonda y lector')
    if shot==3:
        form=['L04','L05','L06'][min(2,int(p*3))];q=readout(PRIMARY,form,'LOWER_338')
        pp=make_panel(PRIMARY,338,form,form_bounds(PRIMARY,form),[q['physical']['site']],
                      directions=[q['physical']['site']])
        attach_readout(pp,PRIMARY,q)
        return base('Repertorio comprobado',[pp],footer='Un acceso por vez · panel finito',evidence='Registro')
    raise KeyError(shot)

def s05(shot,p):
    if shot==1:
        tick=[338,402,405,472][min(3,int(p*4))];b=form_bounds(PRIMARY,'L03',True)
        teach=['L03.event.plus','revision.second.treatment.plus']if tick in [402,405]else[]
        pp=make_panel(PRIMARY,tick,'L03',b,[hub(PRIMARY,'L03')],
                      ['L03.signal'],teach,directions=[hub(PRIMARY,'L03')],difference=[hub(PRIMARY,'L03')])
        if tick in [338,472]:attach_readout(pp,PRIMARY,readout(PRIMARY,'L03','LOWER_338'if tick==338 else'POST_REVISION_472'))
        return base('Nueva experiencia'if tick in [338,402,405]else'Respuesta revisada',[pp],
                    'Misma U0 · etapas','Revisión M1 · lector posterior')
    if shot==2:
        witness='L04'if p<.5 else'L05';ps=[]
        for form,label in [('L03','Revisada'),(witness,'Testigo '+witness)]:
            q=readout(PRIMARY,form,'POST_REVISION_472')
            pp=make_panel(PRIMARY,472,label,form_bounds(PRIMARY,form),[q['physical']['site']],directions=[q['physical']['site']])
            ps.append(attach_readout(pp,PRIMARY,q))
        number=data()['checks']['13_unretrained_witnesses']
        return base('Otras asociaciones comprobadas',ps,footer=str(number)+'/'+str(number)+' testigos consultados',evidence='Registro')
    if shot==3:
        method='M1'if p<.5 else'M2';local=p*2 if p<.5 else(p-.5)*2
        tick=70 if local<.35 else 338;group='BEFORE_REVISION'if tick==70 else'AFTER_REVISION'
        treatment='UP_'+method+'_P11';sham='UP_'+method+'_S11';b=form_bounds(treatment,'L01');ps=[]
        for name,label in [(treatment,'En ruta'),(sham,'Fuera de ruta')]:
            q=readout(name,'L01',group);pp=make_panel(name,tick,label,b,[q['physical']['site']],
                directions=[q['physical']['site']],control='Separate K2repertoire '+method+' treatment/offpath_sham; do not attribute to integratedU0.')
            attach_readout(pp,name,q)
            if q['receipt']['status']=='rejected_occupied':
                assert not q['covered']and q['value']is None
                pp['bottom']='Puerto ocupado'
                pp['bottom_evidence']={**deepcopy(pp['reader_evidence']),
                    'interpretation':'The recorded query was rejected_occupied; this is not an admitted answer of opposite content or numeric zero.'}
            ps.append(pp)
        return base('Experiencia'if tick==70 else'Cambio reutilizable',ps,'Otro ensayo · '+method,
                    'NULL no es cero ni signo contrario',
                    protocol_requests={name:[q for q in case(name)['calls_exact']if 264<=int(q['at'])<=268]for name in [treatment,sham]})
    raise KeyError(shot)

def s08(shot,p):
    g=case()['geometry']
    if shot==1:
        stage=min(3,int(p*4))
        if stage in [0,1]:
            tick=5 if stage==0 else 11;body=g['body'];sites=[body[k]for k in ['A','B','center','emission_site']]
            b=roi(sites,1.5);ports=[]if stage==0 else['need.actual.left.-1','need.actual.right.-1']
            pp=make_panel(PRIMARY,tick,'Señal previa'if stage==0 else'Dato actual',b,
                          [body['emission_site']],ports,directions=[body['emission_site']])
            if stage==1:
                # The port frame does not retain an input-carrier field at11.
                # Show its real interface annotation + original admitted receipt,
                # never manufacture a RAW carrier from payload17.
                ch,_=channels(PRIMARY);port=ports[1];site=ch[port]['site']
                pp['label']='Señal previa';pp['input_sites']=[]
                entry=make_panel(PRIMARY,11,'Dato actual',roi([site],2.2),input_ports=[port])
                admitted=calls(PRIMARY,ports,11)
                assert all(q['final_receipt']['status']=='applied'for q in admitted)
                entry['bottom']='Entrada admitida';entry['request_evidence']=deepcopy(admitted)
                return base('Dato actual',[pp,entry],'Entrada registrada',
                    'Portador de entrada no muestreado',admitted_report_calls=admitted)
            return base('Señal previa'if stage==0 else'Dato actual',[pp],'Etapas observadas',
                        'Informe externo por entradas preparadas',admitted_report_calls=calls(PRIMARY,ports,11))
        if stage==2:
            c=cotejo();src=c['source_comparison_hubs_T15'];obs=src['observations']['right'];b=roi([obs['site']],2.2)
            origin={**src['source'],'pointer':src['pointer']+'/right','tick':15,'life':c['source_life'],'N':67,
                    'reader':obs['site'],'control':'Original execution; boundaries0/70/75/142/338byte-equal to the port. Complete original19not retained.'}
            pp={'N':67,'tick':15,'points':[{**deepcopy(obs),'raw':str(obs['raw']),'clock':str(obs['clock']),'role':'difference'}],
                'label':'Comparación','bounds':b,'reader_sites':[obs['site']],
                'direction_sites':[obs['site']],'source':origin,'evidence_bindings':[origin]}
            return base('Dato actual',[pp],'CPC7 · origen cotejado','T15 del origen · etapas separadas',
                        cotejo_source=file_source(COTEJO))
        site=g['need']['branches']['right.different']['request_site'];b=roi([site],2.2)
        pp=make_panel(PRIMARY,19,'Pregunta',b,[site],directions=[site],difference=[site])
        functional_bottom(pp,PRIMARY,'question')
        return base('Pregunta',[pp],'U0 · pregunta observada','La ruta comparadora está preparada')
    if shot==2:
        tick=70 if p<.5 else 72;bank=g['banks']['right']['hub'];action=g['actions']['own.use.minus']['site']
        b=roi([bank,action],2);ps=[]
        for name,label in [(PRIMARY,'Discrepancia'),(MATCH,'Coincidencia')]:
            target=bank if tick==70 else action
            pp=make_panel(name,tick,label,b,[target],directions=[target],difference=[target],
                          control='IR_MATCH_CURRENT changes current report−1to+1; an archived finite technical matching variant, not a fresh scientific reserve.')
            functional_bottom(pp,name,'information'if tick==70 else'use')
            ps.append(pp)
        return base('Pregunta'if tick==70 else'Uso de información',ps,'Oportunidad común',
                    'Contenido adquirido; uso en etapa posterior')
    if shot==3:
        if p<.4:
            return base('Oportunidad preparada',[],evidence='Esquema',footer='Agenda y recursos del investigador',scheme={'kind':'agenda'},phase=1)
        site=g['need']['branches']['right.different']['request_site'];b=roi([site],2.2);ps=[]
        for name,label in [(PRIMARY,'Discrepancia'),(MATCH,'Coincidencia')]:
            pp=make_panel(name,19,label,b,[site],directions=[site],difference=[site],
                        control='Fixed comparator and opportunities; different actual report.')
            ps.append(functional_bottom(pp,name,'question'))
        return base('Selección nativa',ps,'Registros locales','Oportunidades y tiempos preparados',evidence='Registro')
    raise KeyError(shot)

def name_read(name,key):
    c=case(name);g=c['geometry']['names'][key];f=recorded(name,142);p=deepcopy(f['names'][key])
    request=calls(name,[g['query_port']],139)[0];rr=request['final_receipt']
    valid=rr['status']=='applied'and p['state']>0 and p['semantic']==1 and p['s_reg']>request['payload']and p['direction']in([-1,-1,0],[-1,1,0])
    return {'physical':p,'receipt':rr,'payload':request['payload'],'coverage':valid,
            'value':p['direction'][1]if valid else None,'source_pointer':frame(name,142)['source_pointer']+'/names/'+key,
            'predicate':'Frozen CPC7selective_native.decoded_name: applied AND active AND semantic1 AND load>query AND direction[-1,±1,0].',
            'reading_method':'Offline evaluation of retained fields and original receipt, not a new probe or native read event.',
            'equivalent_predicate_source':data()['source_code_read_as_text_only'][0],
            'equivalent_predicate_symbol':'directional'}
def name_panel(key,tick,label,bounds):
    g=case()['geometry']['names'][key];port=g['teach_port']if tick in [72,75]else g['query_port']
    pp=make_panel(PRIMARY,tick,label,bounds,[g['site']],
                  []if tick in [72,75]else[port],[port]if tick in [72,75]else[],directions=[g['site']])
    if tick==142:
        q=name_read(PRIMARY,key);pp['reader_evidence']={**case()['source'],'pointer':q['source_pointer'],'record':q,'qualified':q['coverage']}
        if q['coverage']:pp['output_text']=sign(q['value'])
        else:pp['bottom']='Sin resultado'
    return pp

def s11(shot,p):
    key='right.minus';g=case()['geometry']['names'][key];ch,_=channels(PRIMARY)
    b=roi([g['site'],ch[g['teach_port']]['site'],ch[g['query_port']]['site']],1.4)
    if shot==1:
        tick=[72,75,139,142][min(3,int(p*4))];pp=name_panel(key,tick,'Señal'if tick<139 else'Uso adquirido',b)
        return base('Señal'if tick<139 else'Uso adquirido',[pp],'Misma U0 · etapas',
                    'Señal externa, asociación interna')
    if shot==2:
        if p<.4:return base('Codificación',[],evidence='Esquema',footer='Interfaz preparada, sin diccionario interno',scheme={'kind':'codec'},phase=1)
        pp=name_panel(key,142,'Relación adquirida',b)
        return base('Relación adquirida',[pp],footer='La salida procede del lector',evidence='Registro')
    if shot==3:
        other='left.minus';ps=[name_panel(key,142,'Ruta utilizada',b)]
        go=case()['geometry']['names'][other];bo=roi([go['site'],ch[go['teach_port']]['site'],ch[go['query_port']]['site']],1.4)
        ps.append(name_panel(other,142,'Otra candidata',bo))
        for pp in ps:
            pp['evidence_bindings'][0]['control']='SameU0,all4candidate teaching/query pulses. Unselected candidate is a local negative control; not an unpaired/omitted preparation.'
        return base('Lenguaje funcional',ps,'Accesos delimitados',
                    'Una asociación; no conceptos universales',evidence='Registro')
    raise KeyError(shot)

def model(shot_id,progress):
    """Accept original S04.1 or derived S04_P01; returns a fresh model dict."""
    shot_id=shot_id.replace('_P0','.').replace('_P','.')
    scene,shot=shot_id.split('.');p=max(0.,min(1.,float(progress)))
    result={'S04':s04,'S05':s05,'S08':s08,'S11':s11}[scene](int(shot),p)
    if result['evidence_type']=='Esquema':
        result['evidence_bindings']=[{**case()['configuration_source'],
            'pointer':'/geometry','life':PRIMARY,'N':case()['geometry']['N'],
            'tick':None,'reader':None,'control':None,
            'scope':'Prepared interface/opportunity diagram; not an observation of native matter.'}]
    result['shot_id']=shot_id;return result
