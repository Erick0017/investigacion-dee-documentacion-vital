"""Same present actual input and same acquired high contents, opposite order."""
import importlib.util,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('selector_u0_exact',HERE/'selector_u0_prospectivo.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
if __name__=='__main__':
    b.put(b.OUT/'PROTOCOLO_HISTORIA_COMUN_U0.json',{'before_run_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'new_arm':'MA_U0_SEL_AB_PLUS, AB order, actual+1, own L01+ L02-, same lower curriculum/supplies as MA_U0_SEL_BA_PLUS','criterion':'Common actual+ does not entail same native query: history AB should not generate horizontal different-request at19 or content-transformed action72, unlike BA+. Native bank contents unchanged. Compare all four question sites and both action sites, not host-selected lane.', 'scope':'Finite order-conditioned access, preparation policy fixed, contents acquired. No generalized temporal language, learned query policy or repeated post472 chain.'})
    b.run('MA_U0_SEL_AB_PLUS','AB',1,[1,-1])
