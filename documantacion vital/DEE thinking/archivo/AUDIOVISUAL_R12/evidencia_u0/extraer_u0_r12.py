"""Directed R12 extraction of CLOSED thinking4.5 measurements; stdlib only.

No engine imports, worlds, ticks, teaching or saved-life mutations. Read sources
as data. Existing gzip uint64 buffers are preserved exactly in base64. Sparse
points are decoded views, independently checked against recorded field reads.
"""
from pathlib import Path
from array import array
import argparse
import base64
import collections
import gzip
import hashlib
import json
import sys
import zipfile
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
THINK = OUT.parents[2]
DEFAULT = THINK / '4.5/DEE_thinking_4_5_0/validation'
INTEGRATED = ['IR_P01_GUARDED_M1', 'IR_C02_AUX_OFFPATH',
              'IR_C01_OFFPATH_GUARDS', 'IR_R607_GUARDED_M1', 'IR_MATCH_CURRENT']
REPERTOIRE = ['UP_M1_P11', 'UP_M1_R101', 'UP_M1_S11',
              'UP_M2_P11', 'UP_M2_R101', 'UP_M2_S11']
FULL_TICKS = {'IR_P01_GUARDED_M1': {0,19,70,75,142,338,405,472},
              'IR_C02_AUX_OFFPATH': {0,338,472},
              'IR_C01_OFFPATH_GUARDS': {338},
              'IR_R607_GUARDED_M1': {338,472},
              'IR_MATCH_CURRENT': {0,19,70}}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def meta(p):
    b=p.read_bytes()
    return {'path':str(p),'bytes':len(b),'sha256':sha(b)}

def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def fields(raw):
    def signed(k):
        a=(raw>>k)&15
        return a-16 if a&8 else a
    return {'raw':str(raw),'state':raw&0xffffffff,
            's_reg':(raw>>32)&65535,
            'direction':[signed(k)for k in (48,52,56)],'semantic':(raw>>60)&15}

def observed(obj,pointer=''):
    if isinstance(obj,dict):
        if all(k in obj for k in ('site','raw','clock')):
            p=dict(obj);p['raw']=str(p['raw']);p['clock']=str(p['clock'])
            p['source_pointer']=pointer
            for k,v in fields(int(p['raw'])).items():
                if k in p and p[k]!=v:
                    raise ValueError('Recorded RAW/field disagreement: '+pointer+'/'+k)
            return [p]
        return [p for k,v in obj.items() for p in observed(v,pointer+'/'+str(k))]
    if isinstance(obj,list):
        return [p for i,v in enumerate(obj)for p in observed(v,pointer+'/'+str(i))]
    return []

def unique(points):
    d={}
    for p in points:
        k=tuple(p['site'])
        if k in d and (d[k]['raw'],d[k]['clock'])!=(p['raw'],p['clock']):
            raise ValueError('Conflicting same-stage point '+str(k))
        if k not in d:d[k]=p
    return list(d.values())

def buffer(root,descriptor,n):
    p=root/descriptor['path'];encoded=p.read_bytes();decoded=gzip.decompress(encoded)
    assert sha(encoded)==descriptor['sha256_compressed'],p
    assert sha(decoded)==descriptor['sha256_uncompressed'],p
    assert len(decoded)==n**3*8==descriptor['bytes'],p
    a=array('Q');a.frombytes(decoded)
    if sys.byteorder!='little':a.byteswap()
    return a,{'source':meta(p),'recorded_descriptor':descriptor,
              'complete_compressed_bytes_base64':base64.b64encode(encoded).decode('ascii')}

def case_extract(root,name,all_buffers=False):
    p=root/'RESULT.json';cpath=root/'CONFIG.json';r=load(p);cfg=load(cpath)
    n=cfg['geometry']['N'];assert r['library']=='4.5.0'
    frames=[];checked=0
    for i,f in enumerate(r['frames']):
        tick=int(f['tick']);pts=unique(observed(f,'/frames/'+str(i)))
        frame={'tick':tick,'N':n,'points':pts,'source_pointer':'/frames/'+str(i),
               'scope':'Recorded field sites only; no absence is inferred outside these sites.',
               'complete_RAW_clock_buffers':False}
        chosen=tick in FULL_TICKS.get(name,{70,338}) or all_buffers
        if chosen and 'raw'in f and 'clock'in f:
            a,ra=buffer(root,f['raw'],n);b,cl=buffer(root,f['clock'],n)
            for point in pts:
                x,y,z=point['site'];idx=(x*n+y)*n+z
                assert (str(a[idx]),str(b[idx]))==(point['raw'],point['clock']), (name,tick,point)
                checked+=1
            full=[]
            for idx,raw in enumerate(a):
                if raw:
                    x,rem=divmod(idx,n*n);y,z=divmod(rem,n)
                    full.append({'site':[x,y,z],'clock':str(b[idx]),**fields(raw),
                                 'source_pointer':'/frames/'+str(i)+'/raw'})
            # Explicit RAW0 field reads are kept too; other RAW0 cells remain
            # exactly recoverable from the complete buffers, not inferred.
            kept={tuple(p['site'])for p in full}
            full.extend(p for p in pts if tuple(p['site'])not in kept)
            frame.update(points=full,complete_RAW_clock_buffers=True,
                scope='All nonzero RAW, including state0, plus explicit RAW0 reader sites. Complete buffers preserve every RAW and clock.',
                raw_buffer=ra,clock_buffer=cl,
                nonzero_RAW_count=sum(bool(v)for v in a),
                nonzero_RAW_with_state0=sum(bool(v)and(v&0xffffffff)==0 for v in a))
        frames.append(frame)
    calls=r['calls'];status=collections.Counter(q.get('final_receipt',{}).get('status','unrecorded')for q in calls)
    out={'source':meta(p),'configuration_source':meta(cpath),'case':cfg['case'],
         'engine_record':r['engine'],'geometry':cfg['geometry'],
         'original_preparations':r['preparations'],'original_technical':r['technical'],
         'scope':r['scope'],'frames':frames,'recorded_frames_exact':r['frames'],
         'calls_exact':calls,'receipt_status_counts':dict(status),
         'readouts_exact':r['readouts'],'checkpoints_exact':r['checkpoints'],
         'source_final_operative':r.get('final_operative'),
         'recorded_field_points_checked_against_complete_buffers':checked,
         'evidence_type':'A for retained local records; B for a sequence of separated stages.',
         'animation_limit':'Hold or cut between retained ticks. No interpolation of matter, continuous lineage, or unobserved microtrajectory is accredited.'}
    return out

def panel(c,label):
    return [q for q in c['readouts_exact']if q.get('panel')==label]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--primary-root',type=Path,default=DEFAULT)
    ap.add_argument('--output',type=Path,default=OUT/'U0_DATOS_R12.json.gz')
    ap.add_argument('--with-all-buffers',action='store_true')
    args=ap.parse_args()
    cases={}
    for family,names in [('cpc_ports_4_5_final6',INTEGRATED),('finite_revision_4_5_final6',REPERTOIRE)]:
        for name in names:
            cases[name]=case_extract(args.primary_root/family/name,name,args.with_all_buffers)
    maincase=cases['IR_P01_GUARDED_M1'];off=cases['IR_C02_AUX_OFFPATH']
    post=panel(maincase,'POST_REVISION_472');prior=panel(maincase,'LOWER_338')
    assert len(post)==len(prior)==14
    prior_by={q['form']:q for q in prior}
    others=[q for q in post if q['form']!='L03']
    assert all(q['covered']and q['value']==prior_by[q['form']]['value']for q in others)
    assert len(others)==13 and next(q for q in post if q['form']=='L03')['value']==1
    def frame(c,t):return next(f for f in c['frames']if f['tick']==t)
    equal338={}
    for name in ['IR_C02_AUX_OFFPATH','IR_R607_GUARDED_M1']:
        f=frame(cases[name],338);m=frame(maincase,338)
        equal338[name]={k:f[k]['recorded_descriptor']['sha256_uncompressed']==m[k]['recorded_descriptor']['sha256_uncompressed']for k in ['raw_buffer','clock_buffer']}
    manual=THINK/'4.5/DEE_thinking_4_5_0_Libro_Blanco_y_Manual_Tecnico.docx'
    w='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    with zipfile.ZipFile(manual)as z:tree=ET.fromstring(z.read('word/document.xml'))
    paragraphs=tree.findall('.//'+w+'p')
    manual_excerpt=[{'paragraph_index_0based':i,'text':''.join(t.text or ''for t in paragraphs[i].iter(w+'t'))}for i in range(1311,1420)]
    sources=[args.primary_root/'tools/cpc_port.py',args.primary_root/'tools/revision_port.py']
    original=THINK/'casos practicos/trabajo_codex/CPC7/resultados/integrated_revision/IR_P01_GUARDED_M1'
    original_meta=[meta(original/name)for name in ['MEASUREMENTS.json','BASE338_MEASUREMENTS.json']]
    doc={'schema':'DEE.R12.U0.directed_primary_extraction.R01','no_new_DEE_ticks':True,
      'extractor':meta(Path(__file__)),'source_root':str(args.primary_root),
      'source_code_read_as_text_only':[meta(p)for p in sources],
      'manual':{'source':meta(manual),'requested_pages':[64,66,67,68,69],
        'read_sections':'57revision M1/M2;58U0;59continuous use;60prediction/comparison/question;61association after use.',
        'page_mapping':'OOXML contains no lastRenderedPageBreak. Exact paragraph indices are recorded; no page-image inspection is claimed.',
        'paragraphs_read':manual_excerpt},
      'identity':{'primary':'IR_P01_GUARDED_M1 from the closed thinking4.5.0 native port. One preparation in its archived record; not a new run.',
        'antecedent_primary_metadata':original_meta,
        'separation':'IR_R607,IR_MATCH_CURRENT,other controls and K2M1/M2 are distinct archived preparations; none is merged into the primary life or with R08lumaMINUS.'},
      'buffer_layout':{'dtype':'little-endian uint64','linear_index':'(x*N+y)*N+z',
        'RAW_fields':'state=bits0..31;s_reg=32..47;direction=signed4 at48,52,56;semantic=60..63',
        'validation':'Every recorded point in each exported complete buffer is independently checked against both buffer values; decoded field reads are also checked against source records.'},
      'cases':cases,
      'scenes':{
        'S04':{'case':'IR_P01_GUARDED_M1','retention_panels':['LOWER_204','LOWER_338'],'source_key':'readouts_exact',
            'limit':'Fourteen lower banks, not16 repeatedly available memories. The two high banks have another access contract.'},
        'S05':{'case':'IR_P01_GUARDED_M1','lesson_tick':402,'contact_tick':405,'query_tick':469,'read_tick':472,
            'revised_form':'L03','other_witness_forms':[q['form']for q in others],
            'other_witnesses_retained':13,'offpath_control':'IR_C02_AUX_OFFPATH',
            'M1_M2_separate_cases':REPERTOIRE,
            'limit':'M1integrated inU0;M2belongs toseparateK2repertoire, with its own offpath control.'},
        'S08':{'case':'IR_P01_GUARDED_M1','observed_ticks':[5,11,15,19,70,72],
            'matching_control':'IR_MATCH_CURRENT',
            'limit':'Matchingcurrent is the preserved finite technical variant, not a newly discovered scientific reserve. Comparator, paths, current-report timing and action opportunities are prepared. No general uncertainty/absence policy.'},
        'S11':{'case':'IR_P01_GUARDED_M1','teaching_input_tick':72,'association_tick':75,'query_tick':139,'read_tick':142,
            'limit':'Externally taught opaque form following physical use, not spontaneous naming or language. No unobserved causal trajectory between retained stages.'}},
      'checks':{'14_panel_before':len(prior),'14_panel_after':len(post),'13_unretrained_witnesses':len(others),
         'L03_before':prior_by['L03']['value'],'L03_after':next(q['value']for q in post if q['form']=='L03'),
         'T338_complete_buffer_equalities':equal338},
      'global_scope':'Archival read-only extraction. Counts are contracts of separate finite prepared lives. No new simulation, Native import, tick, acquisition, preservation claim outside a measured window, or visual QA.'}
    encoded=gzip.compress((json.dumps(doc,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf8'),mtime=0)
    with args.output.open('xb')as f:f.write(encoded)
    print(json.dumps({'output':meta(args.output),'cases':len(cases),'primary_frames':len(maincase['frames']),
          'primary_ticks':[f['tick']for f in maincase['frames']],
          'full_buffers_primary':[f['tick']for f in maincase['frames']if f['complete_RAW_clock_buffers']],
          'checks':doc['checks'],'Native_imported':False},ensure_ascii=False))

if __name__=='__main__':main()
