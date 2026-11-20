"""Reuse the exact synthetic sealer fixture with only the R03 wrapper changed."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'pruebas/probar_sellar_vincular_C02.py';text=source.read_text('utf8')
text=text.replace("m.ROOT=work\n", "m.ROOT=work\nr03=load(ROOT/'control/sellar_vincular_C02_R03.py','_seal_R03_fixture');r03.base.ROOT=work\n")
text=text.replace('result=m.seal(args,persistence=p,bridge=types.SimpleNamespace(bind_checkpoint=bind))',
                  'result=r03.seal(args,persistence=p,bridge=types.SimpleNamespace(bind_checkpoint=bind))')
text=text.replace("'SELLADO_VINCULO_SINTETICO_'", "'SELLADO_VINCULO_R03_SINTETICO_'")
text=text.replace("'SYNTHETIC_OPAQUE_NATIVE_ROOT_AND_BINDER_DOUBLE_ONLY'", "'R03_WRAPPER_SYNTHETIC_OPAQUE_NATIVE_ROOT_AND_BINDER_DOUBLE_ONLY'")
text=text.replace("'source_sha256':m.sha(ROOT/'control/sellar_vincular_C02.py')", "'source_sha256':m.sha(ROOT/'control/sellar_vincular_C02_R03.py')")
exec(compile(text,str(source)+':R03_fixture_reuse','exec'),{'__file__':str(source),'__name__':'__main__'})
