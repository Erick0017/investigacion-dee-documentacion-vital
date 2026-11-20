from __future__ import annotations

import sys

import dee_thinking as dt


def run(mode: str, path: str) -> None:
    lazy = dt.TickOptions()
    lazy.backend = dt.Backend.LAZY
    lazy.threads = 2
    if mode == "save-h1":
        config = dt.DelayPositionConfig()
        config.input_delay = 3
        dt.save_delay_position_checkpoint(config, 5, path, lazy)
        print("python_save_h1 tick=5 input_delay=3")
    elif mode == "resume-h1":
        config = dt.DelayPositionConfig()
        config.input_delay = 3
        result = dt.resume_delay_position_checkpoint(path, lazy)
        uninterrupted = dt.run_delay_position(config, lazy)
        assert result.measurement == 3
        assert result.final_raw == uninterrupted.final_raw
        assert result.final_clock == uninterrupted.final_clock
        print("python_resume_h1 raw_clock_exact=true measurement=3")
    elif mode == "save-h2-separated":
        dt.save_separated_repertoire_checkpoint(
            dt.SeparatedRepertoireConfig(), 10, path, lazy
        )
        print("python_save_h2_separated tick=10 channels=3")
    elif mode == "resume-h2-separated":
        config = dt.SeparatedRepertoireConfig()
        result = dt.resume_separated_repertoire_checkpoint(path, lazy)
        uninterrupted = dt.run_separated_repertoire(config, lazy)
        assert result.all_exact
        assert result.final_raw == uninterrupted.final_raw
        assert result.final_clock == uninterrupted.final_clock
        print("python_resume_h2_separated raw_clock_exact=true channels=3")
    elif mode == "save-h2-overlap":
        dt.save_overlap_repertoire_checkpoint(
            dt.OverlapRepertoireConfig(), 15, path, lazy
        )
        print("python_save_h2_overlap tick=15 on_fiber=true")
    elif mode == "resume-h2-overlap":
        config = dt.OverlapRepertoireConfig()
        result = dt.resume_overlap_repertoire_checkpoint(path, lazy)
        uninterrupted = dt.run_overlap_repertoire(config, lazy)
        assert result.merge_exact
        assert result.final_raw == uninterrupted.final_raw
        assert result.final_clock == uninterrupted.final_clock
        print("python_resume_h2_overlap raw_clock_exact=true merge_exact=true")
    elif mode == "save-f1":
        dt.save_reusable_revision_checkpoint(dt.ReusableRevisionConfig(), 40, path, lazy)
        print("python_save_f1 tick=40")
    elif mode == "resume-f1":
        config = dt.ReusableRevisionConfig()
        result = dt.resume_reusable_revision_checkpoint(path, lazy)
        uninterrupted = dt.run_reusable_revision(config, lazy)
        assert list(result.response_loads) == [4149, 4165, 4181]
        assert result.final_raw == uninterrupted.final_raw
        assert result.final_clock == uninterrupted.final_clock
        print("python_resume_f1 raw_clock_exact=true responses=4149,4165,4181")
    elif mode == "save-f2":
        dt.save_environmental_return_checkpoint(dt.EnvironmentalReturnConfig(), 40, path, lazy)
        print("python_save_f2 tick=40")
    elif mode == "resume-f2":
        config = dt.EnvironmentalReturnConfig()
        result = dt.resume_environmental_return_checkpoint(path, lazy)
        uninterrupted = dt.run_environmental_return(config, lazy)
        assert list(result.downstream_loads) == [24, 55, 62, 62, 67]
        assert result.overflow_total > 0
        assert result.final_raw == uninterrupted.final_raw
        assert result.final_clock == uninterrupted.final_clock
        print("python_resume_f2 raw_clock_exact=true downstream=24,55,62,62,67")
    elif mode == "save-h3":
        config = dt.RepairConfig()
        config.authorize_diagnostic_damage = True
        dt.save_trained_redundancy_repair_checkpoint(config, 12, path, lazy)
        print("python_save_h3 tick=12 diagnostic_damage_authorized=true")
    elif mode == "resume-h3":
        config = dt.RepairConfig()
        config.authorize_diagnostic_damage = True
        result = dt.resume_trained_redundancy_repair_checkpoint(path, lazy)
        uninterrupted = dt.run_trained_redundancy_repair(config, lazy)
        assert result.reconstructed_at_arrival
        assert result.fresh_function
        assert result.final_raw == uninterrupted.final_raw
        assert result.final_clock == uninterrupted.final_clock
        print("python_resume_h3 raw_clock_exact=true reconstructed=true")
    else:
        raise SystemExit(f"unknown protocol bridge mode: {mode}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: protocol_checkpoint_bridge.py "
            "save-h1|resume-h1|save-h2-separated|resume-h2-separated|"
            "save-h2-overlap|resume-h2-overlap|save-h3|resume-h3|"
            "save-f1|resume-f1|save-f2|resume-f2 PATH"
        )
    run(sys.argv[1], sys.argv[2])
