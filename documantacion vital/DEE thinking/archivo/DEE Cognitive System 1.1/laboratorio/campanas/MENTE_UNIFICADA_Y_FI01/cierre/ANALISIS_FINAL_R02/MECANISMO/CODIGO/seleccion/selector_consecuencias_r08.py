"""Actual local work -> generic failure0 -> scalar inhibition -> later choice.

Frozen asymmetric physical outcome codec: failure supplies zero material at A-Z
at the next predeclared odd391 opportunity. Neither correct worker nor observed
sign chooses the return port. It can fail under an inverted environment law.
"""
import base64,gzip,hashlib,importlib.util,json,time
from pathlib import Path
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation
from dee_thinking.persistence import load_world_snapshot,save_world_snapshot,encode_metadata
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/seleccion'
def module(name,file):
    s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
a=module('accretion','selector_acrecion_base.py');worker=module('worker','worker_fuente_utilizada.py')
E=(33,33,33);A=(32,32,33);B=(34,32,33)
QS=(1100,1800,2000,2100,2200,2300,2400,2500,2600)
FEEDBACK=(1173,1955);KEY='MUFI01.selector.consequence.r08'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):
    if p.exists():raise FileExistsError(p)
    b=json.dumps(x,ensure_ascii=False,sort_keys=True).encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def run(label,initial='B',mode='real',law='minus'):
    parent=OUT/('MUFI_S06_TOUCH_'+initial+'.T910.deetsnap.gz');w,_=load_world_snapshot(parent);obs=lambda p:exact_observation(w.runtime.observe(d.Coordinate(*p)))
    a.declare(w,prefix='consequence');requests=[];rows=[];operations=[];shots=[];folder=OUT/(label+'.worker');folder.mkdir(exist_ok=False)
    # Apparatus extension on this exact evaluation fork, identical in all arms.
    # A legal state0SEM4 boundary outside references and selector avoids a central
    # neutral-output recurrence; no interior content is erased or overwritten.
    stop=(33,36,33);prestop=obs(stop)
    if int(prestop['raw'])!=0:raise ValueError('Do not overwrite a nonempty causal site')
    c=d.ChannelSpec();c.name='consequence.neutral.stop';c.injection_site=d.Coordinate(*stop);c.direction=d.Direction(0,0,0);c.state=0;c.semantic=4;c.allow_experience=True;c.allow_probe=True
    i=d.InterfaceSpec();i.name=c.name;i.channel=c;w.declare_interface(i);requests.append(a.submit(w,c.name,0,920))
    for q in QS:requests+=a.query(w,q,5,prefix='consequence')
    def snap():
        meta={'identity':label,'parent_sha256':sha(parent),'parent_tick':910,'architecture_extension':'single legalstate0SEM4 neutraloutputboundaryat920','mode':mode,'N':67,'tick':int(w.runtime.current_tick),'requests':requests,'external_environment':{'law':law,'late_law_inversion_at_query':2500,'future_opportunities':list(QS),'failure_sensor_open_first_opportunities':2,'generic_failure_return_port':'fixedA-Z, zero payload, odd391slots1173/1955','operations':operations},'scope':'Return encodes actualfailure/neutraldeadline, nevercorrectaction or historicaltarget; noDEEmetadatadecision.'}
        w.runtime.set_snapshot_metadata(KEY,encode_metadata(meta));p=OUT/(label+'.T'+str(w.runtime.current_tick)+'.deetsnap.gz');save_world_snapshot(w,p,compress=True);shots.append({'path':str(p),'sha256':sha(p),'tick':int(w.runtime.current_tick)})
    events=sorted({910,921,1000,1172,1173,1174,1954,1955,1956,2660,*[q+k for q in QS for k in range(10)]})
    for t in events:
        w.run_until(t)
        row={'tick':t,'A':obs(A),'B':obs(B),'E':obs(E),'contactA':obs((32,32,32)),'contactB':obs((34,32,32)),'reader':a.read(w),'local':[obs(a.at(E,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]};rows.append(row)
        if t in(1000,1172,1174,1954,1956,2660):snap()
        if t not in[q+6 for q in QS]:continue
        j=[q+6 for q in QS].index(t);decision=row['reader']['choice'];actuator=decision if decision in(-1,1)else None
        current_law='plus'if j>=7 else law
        observations=[13+(j%3),7]if current_law=='plus'else[7,13+(j%3)]
        receipt=None;output=None;executed=actuator is not None and mode!='nulled'
        if executed:
            request={'executed_worker':actuator,'raw_observations':observations,'capacity_credit':0,'domain':'trabajadores','pending_transaction':None,'attempt':j+1,'native_tick':t,'output_directory':str(folder)}
            receipt=worker.process(request);output=folder/receipt['output_name']
        # A physical neutral Y result / absence executes no convenient fallback.
        # The environmental opportunity expires, and this is an actual failure
        # of use. An annulled actuator similarly produces no useful consequence.
        success=bool(receipt and receipt['accepted']);failure=not success
        returned=None
        if j<2 and failure and mode!='omitted':
            arrival=FEEDBACK[j]+(1 if mode=='phase_shift'else 0)
            returned=a.experience(w,'A',arrival,prefix='consequence');requests.append(returned)
        op={'query_tick':QS[j],'native_tick':t,'physical_decision':decision,'native_read':row['reader'],'actuator_mapping':'-1/1 unchanged; Y0/none no command, no smart fallback','executed':executed,'annulled':mode=='nulled','worker_request':request if executed else None,'worker_receipt':receipt,'actual_output':{'name':output.name,'sha256':sha(output),'bytes':output.stat().st_size,'base64':base64.b64encode(output.read_bytes()).decode()}if output else None,'opportunity_success':success,'deadline_or_worker_failure':failure,'generic_failure_return':returned,'environment_law_for_auditor_only':current_law,'sensor_window':j<2,'participant_observation':'samegenericquery5; serviceeligibilityobservations andlaw nevertransduced'}
        operations.append(op)
    r={'schema':KEY,'identifier':label,'initial_history_for_evaluator_only':initial,'mode':mode,'law':law,'parent':{'path':str(parent),'sha256':sha(parent),'tick':910},'apparatus_extension':{'site':stop,'pre':prestop,'scheduled_tick':920,'state':0,'semantic':4,'load':0},'rows':rows,'operations':operations,'requests':[a.receipt(w,x)for x in requests],'snapshots':shots,'sources':{p.name:sha(p)for p in(Path(__file__),HERE/'selector_acrecion_base.py',HERE/'worker_fuente_utilizada.py')},'scope':'Local asymmetric consequence-conditioned access/action experiment; not ageneralpolicy. Teaching0changesoneaccretionclockopportunity, not directmemorywrite. Neutral/noactioncountsasfailure, nointelligentfallback.'}
    put(OUT/(label+'.json.gz'),r);print(json.dumps({'label':label,'decisions':[o['physical_decision']for o in operations],'executed':[o['executed']for o in operations],'success':[o['opportunity_success']for o in operations],'returns':[o['generic_failure_return']is not None for o in operations],'final_refs':{'A':obs(A),'B':obs(B)}}),flush=True)
if __name__=='__main__':
    put(OUT/'PROTOCOLO_CONSECUENCIAS_R08.json',{'before_first_tick_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'parent':'R06 completeT910oppositelearnedhistories, no re-teaching','queries':list(QS),'payload':5,'fixed_actuator':'nativeXsign±1 unchanged; centralY0 orabsence is noaction; opportunitydeadlinefailure, notfallback','actual_environment':'existing isolated fileworker, rawobservations[7,13..15] requireminus or[13..15,7] requireplus; law checkedAFTERnativeemission; bytescompress/hashandreadback','generic_sensor':'failure ONLY atfirsttwoopportunities -> zero contactatfixedA-Z arriving1173/1955; noaction/correctbank/history argument','arms':['REALminus','OMITTEDminus','PHASE_PLUS1minus','REALplus','ACTUATOR_NULLEDplus','OPPOSITEinitialAminus'],'prediction':'REALminus positivefailure thencentralYdeadlinefailure thennegativeuseful5reserves; omit/phase1staypositive; realplusstaypositiveuseful; nulledplusacquiressamebiasbutnoexternalwork. Invertlawtoplusat2500/2600: learnedminusbecomesunhelpful, localbiasnotgeneralstrategy.','extension':'samelegalstate0SEM4stopatE+3Yin920 allarms, RAW0precheck; architecturedeclaredbeforeevaluation','observer':'sameall3physicalactuatorsatq+6; nohistoryorcorrectlawinput','horizon':2660,'classification':'P0asymmetricoutcomecodec andopportunityclock; acquiredscalar/decisionP1; P2localinterpretationrequirespairedcausalityanddoesnotimplycreditassignment/generalregulation.'})
    run('MUFI_S08_REAL_MINUS');run('MUFI_S08_OMITTED_MINUS',mode='omitted');run('MUFI_S08_PHASE1_MINUS',mode='phase_shift');run('MUFI_S08_REAL_PLUS',law='plus');run('MUFI_S08_NULLED_PLUS',mode='nulled',law='plus');run('MUFI_S08_OPPOSITE_MINUS',initial='A')
