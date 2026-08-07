"""Command line interface: ``rtcc R1 R2 R3``."""

from __future__ import annotations

import argparse
import json

import numpy as np

from rtcc.obtuse import p_vertices, simulate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="rtcc",
        description=(
            "Probability that a triangle with one vertex uniform on each of "
            "three concentric circles is obtuse. Only the ratios of the radii "
            "matter."
        ),
    )
    parser.add_argument("radii", type=float, nargs=3, metavar=("R1", "R2", "R3"))
    parser.add_argument(
        "--simulate",
        type=int,
        default=0,
        metavar="N",
        help="also estimate the probability from N simulated triangles",
    )
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args(argv)

    if min(args.radii) < 0:
        parser.error("radii must be nonnegative")
    if sum(r == 0 for r in args.radii) > 1:
        parser.error("at most one radius may be zero: two would coincide at the center")

    exact = p_vertices(*args.radii)
    result = {
        "radii": args.radii,
        "p_obtuse": float(exact.sum()),
        "p_vertex": exact.tolist(),
    }
    if args.simulate > 0:
        mc = simulate(*args.radii, n=args.simulate, seed=args.seed)
        p = mc.sum()
        result["simulated"] = {
            "n": args.simulate,
            "p_obtuse": float(p),
            "p_vertex": mc.tolist(),
            "std_error": float(np.sqrt(p * (1.0 - p) / args.simulate)),
        }

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    r1, r2, r3 = args.radii
    print(f"radii            {r1:g}, {r2:g}, {r3:g}")
    print(f"P(obtuse)        {exact.sum():.6f}")
    for k, p in enumerate(exact, start=1):
        print(f"  at vertex {k}    {p:.6f}")
    if args.simulate > 0:
        sim = result["simulated"]
        print(f"simulated        {sim['p_obtuse']:.6f} (SE {sim['std_error']:.6f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
