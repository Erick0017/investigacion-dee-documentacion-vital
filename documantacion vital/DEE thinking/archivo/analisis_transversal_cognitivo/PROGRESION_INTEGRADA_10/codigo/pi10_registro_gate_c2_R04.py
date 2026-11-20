"""Exact actual C2 contrast schema, frozen source/primaries, no Native."""
from pathlib import Path
import hashlib,json
CONTRAST='9c03f0386d279cd691e9e9a48456e045b81b7bad88c3c7e509514f733d3637d3'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def need(ok,msg):
 if not ok:raise ValueError(msg)
def check(contrastfile,campaign,recalc):
 contrastfile=Path(contrastfile);campaign=Path(campaign);c=read(contrastfile);need(sha(contrastfile)==CONTRAST and c.get('schema')=='DEE.PI10.real_nonfailure_utility_comparison.R02'and c.get('Native_executed')is False,'Exact closed C2 comparison schema/hash, no generic groups assumption')
 sourcefile=campaign/'fuentes/RECALCULO_REAL_NONE12_PI10_R03.json';need(sha(sourcefile)==c['source_sha256']=='527e015e6f98eb47dfdd54ac4da56838712973a2c37acf8667fb9c9bafc5dcf9','Actual C2 source recalc binding');source=read(sourcefile);index=campaign/'fuentes/REAL_NONE12_CERRADAS_PORTABLE_R01/INDEX.json';need(sha(index)==source['closed_index_sha256'],'Actual closed primary index binding');need(recalc.bundle(index)==source,'Archived RAW/receipt/64B projection differs from actual C2 recalc')
 rr=source['groups']['real'];nn=source['groups']['nonfailure'];need(rr['complete_horizon']and nn['complete_horizon']and rr['observed']==nn['observed']==12 and rr['reserved_opportunities']==nn['reserved_opportunities']==9,'Twelve ordered actual opportunities and nine reserved in each closed arm')
 for name,g in(('real',rr),('nonfailure',nn)):
  v=c['groups'][name];need(v['opportunities']==g['observed']and v['reserved']==g['reserved_opportunities']and v['physical']==g['physical_delivered']and v['attributed']==g['attributed_useful']and v['reserved_attributed']==g['reserved_useful'],'Actual contrast aggregates differ from primaries: '+name)
 need(c['all_paired_STATE_bit_same']and c['all_paired_query_ticks_same']and [v['ordinal']for v in c['paired_samples_and_clocks']]==list(range(12))and all(v['same_STATE_bit']and v['same_query_ticks']for v in c['paired_samples_and_clocks']),'Declared matched STATE/bit and phases required')
 gain=rr['reserved_useful']-nn['reserved_useful'];physicalgain=rr['physical_delivered']-nn['physical_delivered'];need(gain==c['reserved_attributed_gain']and physicalgain==c['whole_physical_gain']and gain>=2 and physicalgain>=1,'Prospective local gain≥2reserved attributed and≥1whole physical required');need(rr['reserved_useful']==9 and rr['physical_delivered']==10 and rr['attributed_useful']==9,'Exact actual real12 scientific cut')
 return rr,nn,gain,physicalgain
