"""Phase 0 inventory: compute SHA-256 for raw + final artifacts and emit manifests.

Large binary artifacts (4000 trajectory .npz, 40 checkpoint .zip) are already recorded in
per-unit SHA256SUMS files under results/rigorous/artifacts/<run_id>/SHA256SUMS. We hash those
authority files and the per-run JSON provenance, plus source code, configs, canonical outputs,
the derived ledger, manuscript source and PDF. This keeps the inventory complete and traceable
without duplicating multi-GB hashing that the run pipeline already committed.

Outputs:
    manifests/raw_artifacts.sha256
    manifests/raw_artifacts.csv
    manifests/source_commit.txt
"""
from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPRO = REPO / "reproducibility"
MAN = REPRO / "manifests"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rows_for(patterns):
    for rel, atype, immutable, required_for, note in patterns:
        p = REPO / rel
        if p.exists():
            yield rel, atype, p.stat().st_size, sha256(p), immutable, required_for, note


def main() -> int:
    MAN.mkdir(parents=True, exist_ok=True)
    inventory = []

    # source code
    for rel in [
        "scripts/a2c_new.py", "scripts/vnict_hybrid_experiments.py",
        "scripts/run_rigorous_manifest.py", "scripts/rigorous_orchestrator.py",
        "scripts/experiment_manifest.py", "scripts/aggregate_experiments.py",
    ]:
        inventory.append((rel, "source_code", "yes", "implementation", "physics/runner/orchestration"))
    # configuration / manifest / environment
    inventory += [
        ("experiments/rigorous_manifest.json", "config", "yes", "protocol", "run matrix + constants"),
        ("experiments/rigorous_manifest.schema.json", "config", "yes", "protocol", "manifest schema"),
        ("environment-lock.txt", "environment", "yes", "reproduction", "pinned package versions"),
    ]
    # canonical raw outputs
    inventory += [
        ("results/rigorous/canonical/episode_audit.csv", "raw_ledger_source", "yes", "all_results", "per-rollout audit (4001 rows incl. 1 smoke)"),
        ("results/rigorous/canonical/aggregate.json", "raw_aggregate", "yes", "all_results", "aggregate provenance"),
        ("results/rigorous/canonical/final_statistics.json", "derived_stats", "yes", "tables_figures", "manuscript source-of-truth stats"),
        ("results/rigorous/canonical/SHA256SUMS", "checksums", "yes", "integrity", "canonical checksum authority"),
        ("results/rigorous/canonical/qa_status.json", "metadata", "yes", "provenance", "qa status"),
    ]
    # derived ledger (this audit)
    inventory += [
        ("reproducibility/data/raw/rollout_ledger.csv", "canonical_ledger", "yes", "all_results", "regenerated append-only ledger (3000 controller rollouts)"),
        ("reproducibility/data/raw/rollout_ledger.schema.json", "schema", "yes", "all_results", "ledger schema"),
        ("reproducibility/data/raw/manuscript_claims.csv", "claims", "yes", "reconciliation", "claims to verify"),
    ]
    # manuscript
    inventory += [
        ("FAIR2026/ReviewPackage/Paper_Final/latex/vnict_hybrid_main.tex", "manuscript_source", "yes", "manuscript", "LaTeX source"),
        ("FAIR2026/ReviewPackage/Paper_Final/latex/references.bib", "manuscript_source", "yes", "manuscript", "bibliography"),
        ("FAIR2026/ReviewPackage/Paper_Final/latex/vnict_hybrid_main.pdf", "manuscript_pdf", "yes", "manuscript", "final PDF"),
    ]

    resolved = list(rows_for(inventory))

    # per-unit authority files (run JSON provenance + SHA256SUMS) for all 80 canonical units + smoke
    runs_dir = REPO / "results" / "rigorous" / "runs"
    if runs_dir.exists():
        for p in sorted(runs_dir.glob("*.json")):
            rel = p.relative_to(REPO).as_posix()
            resolved.append((rel, "run_provenance", p.stat().st_size, sha256(p), "yes", "unit_integrity", "per-run provenance incl. checkpoint/map hashes"))
    art_dir = REPO / "results" / "rigorous" / "artifacts"
    if art_dir.exists():
        for p in sorted(art_dir.glob("*/SHA256SUMS")):
            rel = p.relative_to(REPO).as_posix()
            resolved.append((rel, "unit_checksums", p.stat().st_size, sha256(p), "yes", "unit_integrity", "authority for that unit's npz+checkpoint checksums"))

    with open(MAN / "raw_artifacts.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["relative_path", "artifact_type", "bytes", "sha256", "immutable", "required_for", "notes"])
        for rel, atype, size, digest, immutable, req, note in resolved:
            w.writerow([rel, atype, size, digest, immutable, req, note])

    with open(MAN / "raw_artifacts.sha256", "w", encoding="utf-8") as f:
        for rel, atype, size, digest, immutable, req, note in resolved:
            f.write(f"{digest}  {rel}\n")

    commit = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    (MAN / "source_commit.txt").write_text(commit + "\n", encoding="utf-8")

    print(f"[manifests] inventoried {len(resolved)} artifacts; commit={commit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
