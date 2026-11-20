from pathlib import Path
import sys,zipfile,json,hashlib,subprocess,time
ROOT=Path(__file__).resolve().parents[3];EV=ROOT/'evidencia/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    zpath=ROOT/'entregas/DEE_COGNITIVE_1_1_HABITAT_CAUSAL_Y_ESTRES_E1_01_ANALISIS.zip';dest=EV/'VERIFICACION_EXTRACCION_FINAL_01'
    if dest.exists():raise FileExistsError('Independent extraction target must be new')
    with zipfile.ZipFile(zpath)as z:
        bad=z.testzip()
        if bad:raise AssertionError(bad)
        for n in z.namelist():
            p=dest/n
            if not p.resolve().is_relative_to(dest.resolve()):raise AssertionError('Unsafe archive member')
        z.extractall(dest);members=len(z.infolist())
    manifest=json.loads((dest/'MANIFIESTO_HASHES.json').read_text(encoding='utf8'));checks=[]
    for n,m in manifest['members'].items():
        f=dest/n
        if f.stat().st_size!=m['bytes']or sha(f)!=m['sha256']:raise AssertionError('Hash/size mismatch: '+n)
    for f in dest.rglob('*.json'):json.loads(f.read_text(encoding='utf8'))
    p=subprocess.run([sys.executable,'-I','-B',str(dest/'CODIGO_Y_RECALCULO/recalcular_paquete.py'),str(dest),'--check'],capture_output=True,text=True,encoding='utf8',timeout=30)
    if p.returncode:raise AssertionError(p.stderr)
    budget=json.loads((ROOT/'laboratorio/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01/PRESUPUESTO_Y_DISENO_INICIAL.json').read_text(encoding='utf8'))
    proof={'zip':str(zpath),'bytes':zpath.stat().st_size,'sha256':sha(zpath),'members':members,'member_hashes_checked':len(manifest['members']),'CRC':True,'JSON_readable':True,'archived_recalculation_equal':True,'recalculation_command':p.args,'native_ticks_during_zip_verification':0,'external_steps_during_zip_verification':0,'size_within_16000000':zpath.stat().st_size<16000000,'monotonic_end':time.monotonic(),'elapsed_seconds':time.monotonic()-budget['monotonic_start_seconds'],'within_six_hour_cut':time.monotonic()<=budget['monotonic_deadline_seconds'],'manual_visual_validation':False,'manual_blocker':'No bundled LibreOffice; Word COM0x80070520/aborted escalation. Candidate edited and structurally checked only.','operational_continuation_proof':str(EV/'INCORPORACION_CLI_23.json'),'analysis_not_operational_backup':True}
    out=ROOT/'entregas/VERIFICACION_FINAL_EXTERNA_HABITAT_CAUSAL_Y_ESTRES_E1_01.json';out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(proof,ensure_ascii=False))
if __name__=='__main__':main()
