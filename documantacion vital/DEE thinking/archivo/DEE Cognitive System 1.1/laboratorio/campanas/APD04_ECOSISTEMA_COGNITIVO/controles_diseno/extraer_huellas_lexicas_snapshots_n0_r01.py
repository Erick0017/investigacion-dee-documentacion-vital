"""Read existing complete lexical checkpoints. No engine/tick import or call.

Selected sparse observations and complete-field comparison can delimit hidden
context, not assign a unique carrier ancestry across unobserved intervals.
"""
from pathlib import Path
import hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[4]
CTRL=Path(__file__).resolve().parent
EV=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
OUT=CTRL/'HUELLAS_LEXICAS_SNAPSHOTS_N0_R01.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def body(p):return json.loads(read(p)['request']['result'])
def main():
    if OUT.exists():raise FileExistsError('Do not replace a completed N0 extraction')
    p=CTRL/'FUENTES_CONTROLES_EJECUTADO_R01/sistema/capacidades/observador_causal_retrospectivo_01.py'
    spec=importlib.util.spec_from_file_location('apd04_frozen_read_only_snapshot_parser',p);obs=importlib.util.module_from_spec(spec);spec.loader.exec_module(obs)
    groups={'LEX_PLUS':'CONTROLES_LEXICO_REFERENCIA_AUX_R01','LEX_MINUS':'CONTROLES_LEXICO_REFERENCIA_AUX_R01',
        'LEX_OMIT':'CONTROLES_LEXICO_REFERENCIA_AUX_R01','LEX_B_OMIT':'CONTROLES_DOCENTE_B_AUX_R01','LEX_B_PLUS':'CONTROLES_DOCENTE_B_AUX_R01'}
    # K, A hub, B hub, and both teacher sources. Include a bounded3D ROI so
    # equal nominal-hub contents cannot conceal a neighboring discrepancy.
    nominal=[[47,7,47],[50,7,47],[50,10,47],[53,13,50],[53,13,44]]
    frames=[];comparisons=[]
    for serial in(7,8):
        loaded={}
        for label,group in groups.items():
            files=list((EV/group/label).glob(str(serial).zfill(2)+'_*.json'))
            if len(files)!=1:raise ValueError('Selected existing event is missing or duplicated: '+label)
            primary=files[0];event=body(primary);c=event['committed_snapshot'];path=ROOT/'sistema'/c['snapshot'];s=obs.Snapshot(path)
            if s.encoded_sha256!=c['snapshot_sha256']or s.tick!=c['physical']['tick']:raise ValueError('Snapshot identity differs from primary')
            roi=[]
            for x in range(44,56):
                for y in range(4,17):
                    for z in range(42,53):
                        o=s.observation([x,y,z])
                        if int(o['raw'])or int(o['clock'])!=s.tick:roi.append(o)
            frames.append({'branch':label,'serial':serial,'primary':str(primary.relative_to(ROOT)),'primary_sha256':sha(primary),
                'snapshot':str(path.relative_to(ROOT)),'snapshot_sha256':sha(path),'summary':s.summary(),
                'nominal_sites':[s.observation(q)for q in nominal],'ROI':{'box_inclusive':[[44,55],[4,16],[42,52]],'rows_raw_nonzero_or_clock_exception':roi},
                'operational_pending':s.pending,'coverage':'Snapshot instant only. No observed collision lineage between saved instants.'})
            loaded[label]=s
        base=loaded['LEX_PLUS']
        for label,s in loaded.items():
            if label=='LEX_PLUS':continue
            diff=[i for i,(a,b)in enumerate(zip(base.raw,s.raw))if a!=b]
            clocks=[i for i,(a,b)in enumerate(zip(base.clocks,s.clocks))if a!=b]
            comparisons.append({'serial':serial,'a':'LEX_PLUS','b':label,'ticks':[base.tick,s.tick],
                'RAW_different_sites':len(diff),'clock_different_sites':len(clocks),
                'RAW_differences':[{'site':obs.coord(i,s.N),'a':obs.fields(base.raw[i]),'b':obs.fields(s.raw[i]),'clock_a':str(base.clocks[i]),'clock_b':str(s.clocks[i])}for i in diff],
                'pending_equal':base.pending==s.pending,'channels_equal':base.channels==s.channels,
                'scope':'Complete RAW/clocks comparison only. Event IDs/receipts and acquired operational metadata are not erased or treated as identical causal state.'})
        del loaded
    result={'schema':'APD04.lexical.snapshot_context.N0.R01','new_native_ticks':0,'parser_sha256':sha(p),
        'frames':frames,'comparisons':comparisons,'limits':['A first B query is material and can alter later acquisition/access.',
        'These endpoints do not prove unique carrier lineage or the exact collision sequence. Teacher and omission controls constrain interpretation.',
        'A detectable RAW difference is not automatically information usable by the organization. Native output evidence is separate.']}
    with OUT.open('x',encoding='utf8',newline='\n')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'output':str(OUT),'frames':len(frames),'comparisons':len(comparisons),'bytes':OUT.stat().st_size,'sha256':sha(OUT),'new_native_ticks':0}))
if __name__=='__main__':main()
