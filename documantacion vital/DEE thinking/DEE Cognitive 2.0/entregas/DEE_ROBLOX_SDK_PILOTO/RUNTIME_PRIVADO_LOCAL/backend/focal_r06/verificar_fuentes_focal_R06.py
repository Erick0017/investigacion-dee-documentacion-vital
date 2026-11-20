"""Read only the explicit focal source manifest. No state/Native/HTTP."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from sdk_common import RUNTIME,canonical,sha,verify_focal_sources
if __name__=='__main__':
    print(canonical({'schema':'DEE.SDK.FocalSourceVerification.R06',
        'focalSourcesSha256':verify_focal_sources(),
        'core26ManifestSha256':sha(RUNTIME/'configuracion/FUENTES_CORE_RUNTIME_R06_0_1_1.json'),
        'NativeImported':False,'identityCreated':False,'ledgerOpened':False,'materialReady':False}))
