"""Extract actual archived observations for R05. Read-only; no DEE imports."""
from pathlib import Path
from array import array
import base64,gzip,hashlib,json,sys

W=Path(__file__).resolve().parent
ROOT=W.parents[3]
ECI=ROOT/'analisis_transversal_cognitivo'
if not ECI.exists():
    ECI=W.parents[2]/'analisis_transversal_cognitivo'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    b=Path(p).read_bytes();return json.loads(gzip.decompress(b) if b[:2]==b'\x1f\x8b' else b)
SKIP={'final','INSTRUMENTO_FENCE','executed_sources','final_service_status','committed_snapshot','buffers','runtime_status','metadata'}
def compact(o):
    if isinstance(o,dict):return {k:compact(v) for k,v in o.items() if k not in SKIP}
    if isinstance(o,list):return [compact(x) for x in o]
    return o
def unpack(p):
    b=gzip.decompress(base64.b64decode(p['data']));assert hashlib.sha256(b).hexdigest()==p['sha256'];a=array('Q');a.frombytes(b)
    if sys.byteorder!='little':a.byteswap()
    return a
def field(v):
    def signed(s):
        a=(v>>s)&15;return a-16 if a&8 else a
    return {'raw':str(v),'state':v&0xffffffff,'semantic':(v>>60)&15,'s_reg':(v>>32)&65535,'direction':[signed(s)for s in(48,52,56)]}
def captures(o,source,trail=''):
    out=[]
    if isinstance(o,dict):
        if 'buffers' in o and isinstance(o['buffers'],dict) and 'raw' in o['buffers'] and 'clock' in o['buffers']:
            a=unpack(o['buffers']['raw']);b=unpack(o['buffers']['clock']);n=o['N']
            assert len(a)==len(b)==n**3
            points=[{'site':[i//(n*n),(i//n)%n,i%n],'clock':str(b[i]),**field(int(v))} for i,v in enumerate(a) if v]
            out.append({'N':n,'tick':o['tick'],'points':points,'RAW_sha256':o['buffers']['raw']['sha256'],'clocks_sha256':o['buffers']['clock']['sha256'],'source':source,'json_pointer':trail,'coverage':'All nonzeroRAW sites, including state0. Clocks retained at those sites; full buffer digests preserved.'})
        for k,v in o.items():
            if k not in ('buffers','final','metadata','committed_snapshot','final_service_status'):
                out+=captures(v,source,trail+'/'+k)
    elif isinstance(o,list):
        for i,v in enumerate(o):out+=captures(v,source,trail+'/'+str(i))
    return out
def primary(p):
    a=read(p);r=a.get('request',{}).get('result',{}).get('result',{})
    return {'source':str(p),'sha256':sha(p),'life':a.get('life'),'label':a.get('label'),'before':a.get('before'),'after':a.get('after'),
            'recorded_result':compact(r),'captures':captures(r,str(p)),
            'operator_payload':a.get('request',{}).get('payload')}
def main():
    B=ECI/'ECI02/estados/LAB_P0/sistema/estado/eci02_resultados'
    picks={
      'S04_before':('ECI02_ALT_CONSOLIDADA','E02_P01_literal_luma'),
      'S04_teacher':('ECI02_L_MINUS','L_MINUS_HISTORIA'),
      'S04_after':('ECI02_L_MINUS','L_MINUS_USO_COMUN'),
      'S04_ret_nara':('ECI02_L_MINUS','L_MINUS_RET_NARA'),
      'S04_ret_MA':('ECI02_L_MINUS','L_MINUS_RET_MA'),
      'S13_plus':('ECI02_L_PLUS','L_PLUS_USO_COMUN'),
      'S13_minus_reserved':('ECI02_L_MINUS','L_MINUS_RESERVA'),
      'S09_neutral':('ECI02_ALT_CONSOLIDADA','E02_P08_P0_neutral'),
      'S09_probe_on':('ECI02_D_R04_ON','RD_ON_TRAZA'),
      'S09_probe_off':('ECI02_D_R04_OFF','RD_OFF_TRAZA'),
      'S12_W11':('ECI02_J_11','J_11_FACTORIAL'),
      'S12_W11_afterMA':('ECI02_J_11','J_11_POST_MA'),
      'S12_W11_afterFI':('ECI02_J_11','J_11_POST_FI')}
    result={k:primary(B/life/(label+'.json.gz'))for k,(life,label)in picks.items()}
    A=ECI/'ECI01/estados/P_COPIA_CERRADA/sistema/estado/eci01_resultados/ECI01_ACCESO_P0'
    result['S05_ALT']={k:primary(A/(k+'.json.gz'))for k in ('R07_ALT_integrated','R07_ALT_idle2680','R07_ALT_idle8040_1','R07_ALT_idle8040_2','R07_ALT_idle8040_3','R07_ALT_nara','R07_ALT_alfa','R07_ALT_balance')}
    p=ECI/'ECI02/datos/PRUEBA_ARITMETICA_DIRECTA_ECI02_R01.json';a=read(p)
    result['S14_direct']={'source':str(p),'sha256':sha(p),'life':a['life'],'requests':compact(a['requests']),
                        'initial_record':compact(a['initial_record']),'final_record':compact(a['final_record']),
                        'reopened_exact_last_checkpoint':a['reopened_exact_last_checkpoint'],'reopen_zero_ticks':a['reopen_zero_ticks'],
                        'reopen_native_protocol_equal':a['reopen_native_protocol_equal'],'first_result_for_literal_transport':a['first_result_for_literal_transport']}
    p=ECI/'ECI01/datos/PROTOCOLO_ECI01_R01.json';a=read(p)
    result['S11_ALT_protocol']={'source':str(p),'sha256':sha(p),'protocol':a}
    out=W/'datos/evidencia_actual_R05.json';out.parent.mkdir(exist_ok=True)
    assert not out.exists(),'Preserve existing extraction'
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'output':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'sections':{k:len(v.get('captures',[]))if isinstance(v,dict)else None for k,v in result.items()},'new_ticks':0},ensure_ascii=True))
if __name__=='__main__':main()
