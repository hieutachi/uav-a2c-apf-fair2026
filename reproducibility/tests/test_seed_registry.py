from pathlib import Path

REPRO = Path(__file__).resolve().parents[1]
BASE_SEEDS = [1009, 1013, 1019, 1021, 1031]


def test_seed_windows_collapse_to_32_unique():
    numeric = [b + e for b in BASE_SEEDS for e in range(10)]
    assert len(numeric) == 50
    assert len(set(numeric)) == 32
    assert min(numeric) == 1009 and max(numeric) == 1040


def test_seed_registry_file_matches():
    import yaml  # PyYAML
    reg = yaml.safe_load((REPRO / "configs" / "seed_registry.yaml").read_text(encoding="utf-8"))
    assert reg["training"]["seed_labels"] == [101, 211, 307, 401, 503]
    assert reg["evaluation"]["base_seeds"] == BASE_SEEDS
    assert reg["seed_windows"]["unique_effective_seeds"] == 32
    assert reg["evaluation"]["reset_seed_equals_wind_seed"] is True


def test_evaluation_seed_slots_csv_consistent():
    import csv
    p = REPRO / "data" / "derived" / "evaluation_seed_slots.csv"
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    assert len(rows) == 50
    for r in rows:
        assert int(r["numerical_episode_seed"]) == int(r["evaluation_base_seed"]) + int(r["episode_index"])
    assert len({int(r["numerical_episode_seed"]) for r in rows}) == 32
