from pathlib import Path
import json,sys
Path(sys.argv[1]).write_text(json.dumps({'schema':'DEE.PI08.fence_continuation_probe.v1','ran_after_successful_SystemExit0':True,'new_Native_ticks':0}),encoding='utf-8')
raise SystemExit(0)
