"""Validate existing failed technical MP4 bytes, without creating ZIP or captures."""
from pathlib import Path
import importlib.util,json,hashlib,ast
ROOT=Path(__file__).resolve().parents[1]
def main():
    path=ROOT/'control/expediente_compacto_v3_R02.py';ast.parse(path.read_text('utf8'))
    spec=importlib.util.spec_from_file_location('_mp4_pack_R02',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    clip=ROOT/'video/capturas/PRUEBA_GDI_REAL_ROOT_R02_ESCRITORIO.mp4'
    raw=clip.read_bytes();before=hashlib.sha256(raw).hexdigest()
    assert before=='8ad892a5ada95ce4170e6e723cc88511190d46a72ebaba35defb0a18e436c220'
    valid=m.validate_short_technical_mp4(raw)
    assert valid['width']==1280 and valid['height']==650 and valid['frames']==14 and valid['audio_tracks']==0
    m.validate_content('EVIDENCIA/P01/PRUEBA_FALLIDA.mp4',raw)
    passed=['actual_original_container_structure']
    bad=[('truncated',raw[:-8]),('not_mp4',b'notMP4')]
    index=raw.rfind(b'avc1');assert index>=0
    bad.append(('protected_or_other_codec',raw[:index]+b'encv'+raw[index+4:]))
    index=raw.rfind(b'vide');assert index>=0
    bad.append(('audio_or_nonvideo_track',raw[:index]+b'soun'+raw[index+4:]))
    for name,value in bad:
        try:m.validate_short_technical_mp4(value)
        except (ValueError,StopIteration,struct_error()):
            passed.append(name);continue
        raise AssertionError('Expected rejection:'+name)
    directory=ROOT/'control/FIXTURES_MP4_VALIDATOR_R02'
    if directory.exists():raise ValueError('Preserve earlier validator fixtures')
    directory.mkdir()
    plan={'schema':'DEE.INTEGRAL.V3.explicit_export_plan.R01','finalized':False,
        'files':[{'source':str(clip),'archive':'EVIDENCIA/P01/PRUEBA_FALLIDA.mp4','role':'technical_capture_primary'}]}
    good=directory/'PLAN_TECNICO_NO_ZIP.json';good.write_text(json.dumps(plan),encoding='utf8')
    m.read_plan(good);passed.append('explicit_technical_role_plan')
    plan['files'][0]['role']='comparison_primary'
    wrong=directory/'PLAN_ROL_INVALIDO_NO_ZIP.json';wrong.write_text(json.dumps(plan),encoding='utf8')
    try:m.read_plan(wrong)
    except ValueError:passed.append('wrong_role_rejected')
    else:raise AssertionError('Wrong role accepted')
    assert hashlib.sha256(clip.read_bytes()).hexdigest()==before
    report={'schema':'DEE.R07.MP4.packager.validation.R02','tests':len(passed),'passed':len(passed),'checks':passed,
        'source_clip_sha256':before,'source_clip_bytes':len(raw),'source_metadata':valid,
        'full_pixel_decode_reused_from':'video/QA_GDI_REAL_ROOT_R02_ESCRITORIO/VERIFICACION.json',
        'container_validator_does_not_decode_pixels':True,'ZIPs_created':0,'captures':0,'Native_DB_MCP_calls':0,
        'original_clip_changed':False,'R01_packager_untouched_by_adaptation':True}
    (directory/'RESULTADO_FIXTURES.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report))
def struct_error():
    import struct
    return struct.error
if __name__=='__main__':main()
