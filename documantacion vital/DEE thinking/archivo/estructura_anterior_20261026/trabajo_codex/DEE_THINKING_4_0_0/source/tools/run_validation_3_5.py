"""3.5 command entry point, reusing the proven non-physical command harness."""
from pathlib import Path
import importlib.util
import sys

def main():
    path=Path(__file__).with_name("run_validation_3_0.py")
    spec=importlib.util.spec_from_file_location("command_harness_retained",path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module.main()

if __name__=="__main__":raise SystemExit(main())
