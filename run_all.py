"""Run the entire pipeline end-to-end (from repo root)."""
import subprocess, sys

STEPS = [
    ("Build per-stadium demand",      "src.part1_lrp.build_demand"),
    ("Part I: solve LRP + compare",   "src.part1_lrp.run"),
    ("Part I: sensitivity",           "src.part1_lrp.sensitivity"),
    ("Part II: generate scenarios",   "src.part2_stochastic.scenarios"),
    ("Part II: stochastic model",     "src.part2_stochastic.model"),
    ("Part II: sensitivity",          "src.part2_stochastic.sensitivity"),
    ("Figures",                       "src.common.visualize"),
]

for title, mod in STEPS:
    print("\n" + "=" * 70 + f"\n>>> {title}  (python -m {mod})\n" + "=" * 70)
    r = subprocess.run([sys.executable, "-m", mod])
    if r.returncode != 0:
        print(f"!! step failed: {mod}")
        sys.exit(1)
print("\nAll steps completed. See outputs/results and outputs/figures.")
