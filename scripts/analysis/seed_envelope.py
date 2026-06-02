"""
scripts/analysis/seed_envelope.py

v0.3.0 Workstream B helper: ingest k-eff from a set of benchmark-msre
CI runs (one per RNG seed) and emit the seed-stability envelope:
mean, sample stdev, pooled within-seed sigma, SEM, and per-seed
deviations vs canonical.

Inputs
------
Either:

  (a) Direct k/sigma pairs on the command line:
        python -m scripts.analysis.seed_envelope \
            --pair 1 1.02397 0.00053 \
            --pair 2 1.02335 0.00049 \
            --pair 5 1.02416 0.00048

  (b) JSON file listing run IDs to fetch via gh CLI (requires gh in PATH
      and api_credentials set up in the running shell):
        python -m scripts.analysis.seed_envelope \
            --runs runs.json --repo KhaiB10/promethea

Output
------
Markdown table + summary line, written to stdout.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import subprocess
import sys
from typing import Iterable


CANONICAL_K = 1.02364  # v0.2.0 VIII.0 canonical (200k * 200)

K_LINE_RE = re.compile(
    r"Combined k-effective\s*=\s*([\d.]+)\s*\+/-\s*([\d.]+)"
)


def fetch_k_from_run(run_id: int, repo: str) -> tuple[float, float]:
    """Fetch combined k-eff from a CI run by grepping its log archive.

    Uses `gh api repos/{repo}/actions/runs/{id}/logs`, which streams a
    zip. We pipe through `unzip -p -` to read entries to stdout, then
    grep for the canonical OpenMC line.
    """
    cmd = ["gh", "api", f"repos/{repo}/actions/runs/{run_id}/logs"]
    proc = subprocess.run(cmd, capture_output=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(
            f"gh api failed for run {run_id}: {proc.stderr.decode()[:200]}"
        )
    # Pipe zip to unzip -p (extract all to stdout)
    unzip = subprocess.run(
        ["unzip", "-p", "-"], input=proc.stdout, capture_output=True, check=False
    )
    for line in unzip.stdout.decode(errors="ignore").splitlines():
        m = K_LINE_RE.search(line)
        if m:
            return float(m.group(1)), float(m.group(2))
    raise RuntimeError(f"no k-eff line found in run {run_id} logs")


def summarize(seeds: dict[int, tuple[float, float]]) -> str:
    ks = [v[0] for v in seeds.values()]
    sigs = [v[1] for v in seeds.values()]
    n = len(ks)
    mean = statistics.mean(ks)
    stdev_sample = statistics.stdev(ks) if n > 1 else 0.0
    pooled = math.sqrt(sum(s * s for s in sigs) / n)
    sem = stdev_sample / math.sqrt(n) if n > 1 else 0.0

    lines = [
        "| Seed | k | sigma (within) | delta vs mean (pcm) |",
        "|------|---|----------------|---------------------|",
    ]
    for s in sorted(seeds):
        k, u = seeds[s]
        lines.append(
            f"| {s} | {k:.5f} | {u:.5f} | {1e5 * (k - mean):+.0f} |"
        )
    lines.extend([
        "",
        f"- N seeds: {n}",
        f"- Mean k: {mean:.5f}",
        f"- Between-seed sample stdev: {stdev_sample:.5f}  ({stdev_sample * 1e5:.0f} pcm)",
        f"- Pooled within-seed sigma: {pooled:.5f}  ({pooled * 1e5:.0f} pcm)",
        f"- SEM (between-seed): {sem:.5f}  ({sem * 1e5:.0f} pcm)",
        f"- vs VIII.0 canonical k = {CANONICAL_K}: "
        f"delta = {1e5 * (mean - CANONICAL_K):+.0f} pcm",
    ])
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument(
        "--pair", nargs=3, action="append", metavar=("SEED", "K", "SIGMA"),
        help="Direct k/sigma triple: seed k sigma. Repeatable.",
    )
    parser.add_argument(
        "--runs", help="Path to JSON file: {seed: run_id, ...}",
    )
    parser.add_argument(
        "--repo", default="KhaiB10/promethea",
        help="GitHub repo for --runs mode",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    seeds: dict[int, tuple[float, float]] = {}
    if args.pair:
        for s, k, u in args.pair:
            seeds[int(s)] = (float(k), float(u))
    if args.runs:
        with open(args.runs, "r", encoding="utf-8") as fh:
            mapping = json.load(fh)
        for seed_str, run_id in mapping.items():
            k, u = fetch_k_from_run(int(run_id), args.repo)
            seeds[int(seed_str)] = (k, u)

    if not seeds:
        print("error: provide --pair or --runs", file=sys.stderr)
        return 2

    print(summarize(seeds))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
