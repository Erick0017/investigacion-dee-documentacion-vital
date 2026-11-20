"""Read-only structural comparison of frozen OrganizationalWorld hex chunks.

Grammar: official4.5 source/src/organizational.cpp52-125,232-238. No Native.
Section hashes and exact preserved prefixes distinguish lawful added interface
and operation records from silent changes to old descriptors or histories.
"""
from pathlib import Path
import hashlib,importlib.util,json,struct
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0'
OUT=P/'control/COMPARACION_ORGANIZATIONAL_D_A_P0_PI10_R01.json'
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
class Reader:
    def __init__(self,b):self.b=b;self.i=0
    def take(self,n):
        need(0<=n<=len(self.b)-self.i,'Organizational data truncated');b=self.b[self.i:self.i+n];self.i+=n;return b
    def u8(self):return self.take(1)[0]
    def u64(self):return struct.unpack('<Q',self.take(8))[0]
    def count(self):
        v=self.u64();need(v<=1048576,'Finite organizational collection');return v
    def text(self):
        n=self.u64();need(n<=1048576,'Bounded official text');return self.take(n).decode('utf8')
    def coord(self):return list(struct.unpack('<qqq',self.take(24)))
    def optional(self):
        b=self.u8();need(b in(0,1),'Boolean');return self.coord()if b else None
    def symbols(self):
        for _ in range(self.count()):self.text();self.u64()
def parse(chunks):
    n=int(chunks['dee_thinking.organizational.v1.chunks']);text=''.join(chunks['dee_thinking.organizational.v1.'+str(k)]for k in range(n));b=bytes.fromhex(text);r=Reader(b);need(r.u64()==1,'Organizational schema1')
    descriptor={'id':r.text(),'version':r.text(),'N':r.u64(),'origin':r.coord(),'t0':r.u64(),'domain':r.text(),'backend':r.u8(),'threads':r.u64()}
    for _ in range(r.count()):r.text();r.u64()
    for _ in range(r.count()):r.text();r.text()
    for _ in range(r.count()):r.coord();r.u64();r.u64();r.text()
    for _ in range(r.count()):
        r.text();r.text();r.u64();r.optional();r.optional();r.optional()
        for _ in range(r.count()):r.text();r.coord()
        r.take(24*r.count())
    sections={'recipe_before_interfaces':b[:r.i]};interfaces=[]
    for _ in range(r.count()):
        start=r.i;name=r.text();channel=r.text();site=r.coord();state=r.u64();direction=r.coord();semantic=r.u8();experience=r.u8();probe=r.u8()
        r.text();r.u8();r.u64();r.u64();r.symbols();r.text();r.text()
        interfaces.append({'name':name,'channel':channel,'site':site,'state':state,'direction':direction,'semantic':semantic,'experience':experience,'probe':probe,'record_sha256':sha(b[start:r.i])})
    start=r.i
    for _ in range(r.count()):
        r.text();r.text();r.take(24*r.count())
        for _ in range(r.count()):r.text()
        r.take(8*r.count())
    sections['recipe_actions']=b[start:r.i];start=r.i
    for _ in range(r.count()):
        r.text();r.text();r.u8();r.u64()
        for _ in range(r.count()):
            r.take(24);r.take(8*r.count());r.take(24*r.count());r.take(48*r.count())
    sections['protocols']=b[start:r.i];start=r.i
    for _ in range(r.count()):r.coord();r.text();r.take(41)
    sections['diagnostic_edits']=b[start:r.i]
    count=r.count();ops_start=r.i;operations=[];op_offsets=[ops_start]
    for _ in range(count):operations.append(r.text());op_offsets.append(r.i)
    operations_bytes=b[ops_start:r.i];start=r.i
    for _ in range(r.count()):r.text();r.text();r.u8();r.symbols()
    sections['decoders']=b[start:r.i];start=r.i;trace=r.u8();need(trace in(0,1),'Trace flag')
    if trace:
        r.u64();r.u8()
        for _ in range(r.count()):r.text();r.coord()
        for _ in range(r.count()):
            r.text();r.coord();r.coord();r.u64();r.u64()
            if r.u8():r.u64()
            if r.u8():r.u8()
            r.u8()
        for _ in range(r.count()):r.text();r.take(104);r.text()
    sections['trace']=b[start:r.i];need(r.i==len(b),'No trailing unparsed organizational bytes')
    return {'chunks':n,'bytes':len(b),'encoded_sha256':sha(b),'descriptor':descriptor,'sections':{k:{'bytes':len(v),'sha256':sha(v)}for k,v in sections.items()},'interfaces':interfaces,'operations':operations,'operations_bytes':operations_bytes}
def main():
    need(not OUT.exists(),'Previous comparison preserved')
    path=C/'reproducibilidad/observador_pasivo.py';sp=importlib.util.spec_from_file_location('PI10_frozen_snapshot_reader_for_org',path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);views=[];sources=[]
    for name in('PRINCIPAL_D_T922371','P0_COMUN_T922374'):
        pair=P/'pares'/name;mf=json.loads((pair/'EXPORTACION_SERVICIO.json').read_text('utf8'));snap=pair/mf['native_snapshot'];need(sha(snap.read_bytes())==mf['snapshot_sha256'],'Exact closed snapshot identity')
        v=m.snapshot_view(snap);views.append(parse(v['metadata']));sources.append({'pair':str(pair),'manifest_sha256':sha((pair/'EXPORTACION_SERVICIO.json').read_bytes()),'snapshot_sha256':sha(snap.read_bytes()),'tick':v['physical']['tick']})
    a,b=views;equal_sections={k:a['sections'][k]==b['sections'][k]for k in a['sections']}
    old_interfaces_prefix=b['interfaces'][:len(a['interfaces'])]==a['interfaces'];extra_interfaces=b['interfaces'][len(a['interfaces']):]
    old_operations_prefix=b['operations'][:len(a['operations'])]==a['operations'];extra_operations=b['operations'][len(a['operations']):]
    only_additions=all(equal_sections.values())and old_interfaces_prefix and old_operations_prefix and all(r['name'].startswith('PI10.')for r in extra_interfaces)and all(v.startswith('DECLARE_INTERFACE ')or v.startswith('EXPERIENCE_PROTOCOL interface=PI10.')for v in extra_operations)
    out={'schema':'DEE.PI10.frozen_organizational_structural_diff.R01','Native_imported':False,'new_ticks_in_this_recalculation':0,'sources':sources,
      'source_grammar':'Official4.5 archive DEE_thinking_4_5_0/source/src/organizational.cpp52-125 and232-238',
      'before':{k:a[k]for k in('chunks','bytes','encoded_sha256','descriptor','sections')},'after':{k:b[k]for k in('chunks','bytes','encoded_sha256','descriptor','sections')},
      'sections_literal_equal':equal_sections,'old_interfaces_exact_prefix_preserved':old_interfaces_prefix,'added_interfaces':extra_interfaces,
      'old_operations_exact_prefix_preserved':old_operations_prefix,'old_operation_count':len(a['operations']),'new_operation_count':len(b['operations']),'appended_operations':extra_operations,
      'all_organizational_changes_explained_by_added_PI10_interfaces_and_operations':only_additions,
      'scope':'Complete organizational serialization parsed without Native. Byte chunk differences alone do not indicate memory loss. This comparison does not replace physical/causal equality checks at adoption0.'}
    with OUT.open('x',encoding='utf8')as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(OUT),'sha256':sha(OUT.read_bytes()),'sections_literal_equal':equal_sections,'old_interfaces_prefix':old_interfaces_prefix,'new_interfaces':len(extra_interfaces),'old_operations_prefix':old_operations_prefix,'new_operations':len(extra_operations),'only_PI10_additions':only_additions}))
if __name__=='__main__':main()
