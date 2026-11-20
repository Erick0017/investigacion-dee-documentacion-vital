"""Single resumable CORE15 entrypoint."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];HERE=Path(__file__).resolve().parent
STEPS=[
 ("initialize_core15.py",ROOT/"RESULTS"/"C15A01_TRANSVERSAL_AUDIT.json"),
 ("run_core15_shadow_discovery.py",ROOT/"RESULTS"/"C15D00_SHADOW_DISCOVERY_SUMMARY.json"),
 ("freeze_core15_shadow_claims.py",ROOT/"SOURCE_FREEZE.json"),
 ("generate_core15_fresh_challenges.py",ROOT/"FRESH_CHALLENGES"/"CHALLENGE_WAVE_A.json"),
 ("run_core15_shadow_holdouts.py",ROOT/"RESULTS"/"C15H00_FRESH_HOLDOUT_SUMMARY.json"),
 ("analyze_core15.py",ROOT/"RESULTS"/"C15A99_FINAL_SYNTHESIS.json"),
 ("package_core15.py",ROOT/"CORE15_SEAL.json"),
]
def main():
 for script,marker in STEPS:
  if marker.exists():print(f"SKIP COMPLETE {script}");continue
  subprocess.run([sys.executable,"-I","-B",str(HERE/script)],cwd=ROOT,check=True)
 print((ROOT/"CORE15_SEAL.json").read_text(encoding="utf-8"))
if __name__=="__main__":main()
