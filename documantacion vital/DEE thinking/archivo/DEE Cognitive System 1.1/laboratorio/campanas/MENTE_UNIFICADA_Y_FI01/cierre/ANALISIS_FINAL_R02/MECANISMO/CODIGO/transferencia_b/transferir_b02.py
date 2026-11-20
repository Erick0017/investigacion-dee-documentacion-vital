"""Two bounded, explicit transfer families from one immutable A-cut.

Actor input is raw scalar or public context. Environmental acceptance laws and
expected headers never become native inputs. P0 shared representation is NOT
evidence of acquired abstraction or autonomous context selection.
"""
from __future__ import annotations
import gc,gzip,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import frontend_b01_r2 as f
OUT=f.OUT.parent/'B02'
ARMS=['T','U','H'];ARRIVALS=[16813+782*j for j in range(19)]

def ref(a,ni):return [ni[7].obs(a,p)for p in[(14,14,15),(16,14,15)]]
def teach_block(a,arm,indices,ni):
    from capacidades import selector_acrecion_nativo as sel
    rows=[]
    for j in indices:
        f.memory_guard();t=ARRIVALS[j];r0=ref(a,ni)
        if arm=='U':r=ni[7].send(a,'FI01.BT.sham.lesson',(15,15,23),(0,0,0),t,0)
        else:r=sel.experience(a.world,'A'if arm=='T'else'B',t,'MU.selector')
        frames=[]
        for tt in(t-1,t,t+1,t+2):
            a.run_until(tt);frames.append({'tick':a.tick,'refs':ref(a,ni),'contact':[ni[7].obs(a,p)for p in[(14,14,14),(16,14,14),(15,15,23)]]})
        rows.append({'lesson':j+1,'scheduled_arrival':t,'pre':r0,'frames':frames,'request':sel.receipt(a.world,r)})
    return {'arm':arm,'lessons':rows,'final_references':ref(a,ni),'scope':'Explicit native inhibitory accretion curriculum. Not environmental reward or learned action selection.'}

def worker_fixture(arm,index,worker,values,ni):
    folder=OUT/'archivos_reales'/arm/('fixture'+str(index));folder.mkdir(parents=True,exist_ok=True)
    q={'domain':'trabajadores','executed_worker':worker,'raw_observations':values,'capacity_credit':0,'pending_transaction':None,'attempt':1,'native_tick':0,'output_directory':str(folder.resolve())}
    cmd=[sys.executable,'-I','-B','-X','utf8',str(f.SYSTEM/'capacidades/eo02_trabajador_local.py')]
    p=subprocess.run(cmd,input=json.dumps(q),encoding='utf-8',text=True,capture_output=True,timeout=15)
    if p.returncode:raise RuntimeError(p.stderr)
    receipt=json.loads(p.stdout);path=folder/receipt['output_name'];b=path.read_bytes()
    return {'worker_request':q,'worker_receipt':receipt,'path':str(path),'sha256':f.digest(path),'actual_readback_bytes':len(b),'payload_base64':__import__('base64').b64encode(b).decode('ascii')}

def magnitude(a,ni,fixtures):
    source=[f.trial(a,'source_scalar_'+str(x),x,ni)for x in(13,32)]
    destination=[]
    for j,fix in enumerate(fixtures):
        # Identity transduction of an actual file measurement. The actor does
        # not receive fixture worker, accepted flag, labels, threshold or law.
        actual=Path(fix['path']).read_bytes();row=f.trial(a,'destination_first_use_'+str(j),len(actual),ni)
        choice=row['reader']['choice'];normal=(-1 if len(actual)<20 else 1)
        row['environment_after_action']={'actual_bytes':len(actual),'file_sha256':f.digest(fix['path']),'normal_gate_command':normal,
          'useful_aligned':choice==normal,'useful_counterlaw':choice==-normal,'feedback_sent':False,'law_not_native_input':True}
        destination.append(row)
    return {'source_scalar_trials':source,'destination_trials':destination,'references_end':ref(a,ni),
      'scope':'Reuse of explicitly acquired quantitative comparison via a prepared identity scalar codec. Not abstract concept transfer; no feedback before any destination action.'}

def association_teach(a,arm,ni,end):
    from capacidades import mente_acumulativa_r02 as ma
    if arm=='U':
        a.run_until(end);return {'arm':arm,'omitted_new_teaching':True,'end_tick':a.tick,'scope':'Omission control: fewer physical teaching carriers, not a dose-matched sham.'}
    result=ma.teach(a,'gamma',-1 if arm=='T'else 1,revision=True)
    a.run_until(end);return {'arm':arm,'teaching':result,'end_tick':a.tick}

def association_use(a,ni):
    from capacidades import mente_acumulativa_r02 as ma
    rows=[]
    for stage in('source_arbitrary_signal','destination_header_first','destination_header_reserved'):
        r=ma.query(a,'gamma',detail=True);choice=r['reader']['formed_native_command']
        header=b'DEE-CONTEXT-RIGHT\n'if choice==-1 else b'DEE-CONTEXT-LEFT\n'if choice==1 else None
        file=None
        if header is not None:
            folder=OUT/'headers'/str(a.world.runtime.current_tick);folder.mkdir(parents=True,exist_ok=True)
            file=folder/(stage+'.header');file.write_bytes(header)
        rows.append({'stage':stage,'native':r,'external_emission':{'file':str(file)if file else None,'bytes_hex':header.hex()if header else None,
          'sha256':f.digest(file)if file else None,'aligned_target_hex':b'DEE-CONTEXT-RIGHT\n'.hex(),'useful_aligned':choice==-1,'useful_counterlaw':choice==1,'feedback_sent':False},
          'scope':'Fixed arbitrary sign-to-header transduction. Public gamma selects a prepared route; learnt content supplies sign. No learnt semantic header routing asserted.'})
    return {'rows':rows,'scope':'Distinct circulating signed-association family, not a second sign of the scalar comparator.'}

def retention(a,ni):
    from capacidades import mente_acumulativa_r02 as ma
    tokens=['alfa','zeta','epsilon','gamma','beta','delta']
    return {'rows':[ma.query(a,t,detail=False)for t in tokens],'scope':'Consecutive actual queries in this own life, denominators include missing/ambiguous outputs; gamma intentionally revised.'}

def main():
    authorization,ni=f.bootstrap();Store=ni[3];store=Store();now=ni[5];code=f.digest(__file__)
    f.dump(OUT/'PROTOCOLO.json',{'revision':'BT.two_families.R1','frozen_before_first_tick':now(),'authorization':authorization,'code_sha256':code,
      'frontend_code_sha256':f.digest(f.__file__),'source':f.CUT,'source_sha256':f.EXPECTED,'parent':'MU_MAIN','arms':ARMS,'fixed_arrivals':ARRIVALS,
      'scalar_curriculum':{'T':'19zeroAcontacts','U':'19zero far-peripheral dir0 shams; count/dose but NOT same route/dwell','H':'19zeroBcontacts'},
      'scalar_predicted_reference_difference_not_actor_input':{'T':-20,'U':-1,'H':18},'source_scalar_values':[13,32],
      'destination_fixtures':[[1,[7,7]],[-1,[7,7]],[1,[12,13]],[-1,[12,13]]],
      'destination_scalar_codec':'Actual readback byte count inserted unchanged atS q+3; same6site decoder; generic query identical. No law, correct gate, checksum or fixtureID enters native world.',
      'environment_law_after_action':'Normal gate accepts native− ifactualbytes<20 else+; fixed counterlaw inverted. Both are external task scoring, never actor input. No destination feedback.',
      'association_curriculum':{'T':'explicit gamma revision−','U':'new teaching omitted, equalage','H':'explicit gamma revision+'},
      'association_destination':'Fixed sign-to-ASCIIheader only; target evaluated after emission. P0sharedrepresentation, no abstraction or learned bank-selection assertion.',
      'protection':'Exact closedAcompleteforks only; no parent advance, no learned region copies, no RAW or clocks edits.'})
    summaries=[]
    for arm in ARMS:
        life='FI01_BT_TWO_'+arm
        if store.life_dir(life).exists():raise FileExistsError(life)
        store.fork('MU_MAIN',life,kind='B_TWO_RELATION_TRANSFER',checkpoint=f.CUT);gc.collect();f.memory_guard()
        fixtures=[worker_fixture(arm,j,w,v,ni)for j,(w,v)in enumerate([(1,[7,7]),(-1,[7,7]),(1,[12,13]),(-1,[12,13])])]
        f.dump(OUT/(arm+'_FIXTURES.json'),fixtures)
        prep=store.mutate(life,'BT_TWO_P0_FRONTEND',lambda a:f.prepare(a,ni),{'code_sha256':code});f.dump(OUT/(arm+'_PREP.json.gz'),prep);del prep
        for k,inds in enumerate([range(0,1),range(1,10),range(10,19)]):
            result=store.mutate(life,'BT_TWO_SCALAR_EXPERIENCE_'+str(k),lambda a:teach_block(a,arm,inds,ni),{'code_sha256':code,'arm':arm});f.dump(OUT/(arm+'_LESSONS_'+str(k)+'.json.gz'),result);del result
        result=store.mutate(life,'BT_TWO_MAGNITUDE_FIRST_TRANSFER',lambda a:magnitude(a,ni,fixtures),{'code_sha256':code,'law_never_actor_input':True});f.dump(OUT/(arm+'_MAGNITUDE.json.gz'),result)
        magnitude_choices=[x['reader']['choice']for x in result['result']['destination_trials']]
        tick=result['physical']['tick'];del result
        from capacidades import mente_acumulativa_r02 as ma
        lesson_end=ma.phase(tick)+3
        result=store.mutate(life,'BT_TWO_ASSOCIATION_EXPERIENCE',lambda a:association_teach(a,arm,ni,lesson_end),{'code_sha256':code});f.dump(OUT/(arm+'_ASSOCIATION_TEACH.json.gz'),result);del result
        result=store.mutate(life,'BT_TWO_ASSOCIATION_FIRST_TRANSFER',lambda a:association_use(a,ni),{'code_sha256':code});f.dump(OUT/(arm+'_ASSOCIATION_USE.json.gz'),result)
        association_choices=[x['native']['reader']['formed_native_command']for x in result['result']['rows']];del result
        result=store.mutate(life,'BT_TWO_OLD_MEMORY_PANEL',lambda a:retention(a,ni),{'code_sha256':code});f.dump(OUT/(arm+'_RETENTION.json.gz'),result)
        row={'arm':arm,'life':life,'magnitude_choices':magnitude_choices,'association_choices':association_choices,
          'old_memory_choices':[[x['context_signal'],x['reader']['formed_native_command']]for x in result['result']['rows']],
          'end_tick':result['physical']['tick'],'snapshot_sha256':result['INSTRUMENTO']['snapshot_sha256']};summaries.append(row);print(json.dumps(row),flush=True)
        del result;gc.collect();f.memory_guard()
    f.dump(OUT/'RESUMEN.json',{'arms':summaries,'source_unchanged':f.digest(f.SYSTEM/f.CUT)==f.EXPECTED,'peak_RSS_bytes':f.memory_guard()})
if __name__=='__main__':main()
