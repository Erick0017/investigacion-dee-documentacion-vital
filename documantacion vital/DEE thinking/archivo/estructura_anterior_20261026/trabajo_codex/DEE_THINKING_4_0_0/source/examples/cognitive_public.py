"""Installed native4 public API. No CPC3 laboratory import or response fixture."""
import json
from pathlib import Path
import tempfile
import dee_thinking as d

def main():
    parameters=d.CognitiveParameters()
    parameters.seed_path=d.reference_seed_path()
    parameters.profile='comparison'
    session=d.CognitiveSession.create(parameters)
    acquired=session.sense()       # Actual current external classes -> native events.
    emitted=session.predict()      # Live MAIN direction, recorded before target83.
    with tempfile.TemporaryDirectory(prefix='dee40-example-') as folder:
        path=str(Path(folder)/'pending.deetsnap')
        session.set_interface_metadata('label','barrera externa declarada')
        session.save_snapshot(path)
        restored=d.CognitiveSession.load_snapshot(path)
        compared=restored.compare() # Actual class only; v27 creates gradient marker.
        unavailable=restored.predict()
    association=d.NativeAssociationSession.create()
    association.train([7,11],5)
    response=association.query_panel(13)
    cascade=d.create_learnable_cascade(2)
    d.experience_composition(cascade,[(3,9),(3,11)])
    composed=d.query_composition(cascade,13)
    print(json.dumps({'version':d.__version__,'acquisition':acquired,'emission':emitted,
                      'comparison':compared,'no_false_marker_reuse':unavailable,
                      'association':response,'composition':composed},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
