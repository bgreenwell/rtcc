# rtcc

Random triangles on concentric circles: the probability that three points, one
drawn uniformly from each of three concentric circles of radii `r1`, `r2`, and
`r3`, form an obtuse triangle.

- Exact probabilities from a one-dimensional quadrature, not simulation.
- The obtuse probability broken down by which vertex carries the obtuse angle.
- Monte Carlo estimates for cross-checking, with a standard error.
- Equal radii reproduce the classical answer of 3/4.
- Averaging over random radii covers any rotationally symmetric sampling
  scheme, including three independent bivariate normals.

## Installation

```bash
git clone https://github.com/bgreenwell/rtcc
cd rtcc
uv sync
```

## Quick start

```bash
$ uv run rtcc 1 1 1
radii            1, 1, 1
P(obtuse)        0.750000
  at vertex 1    0.250000
  at vertex 2    0.250000
  at vertex 3    0.250000

$ uv run rtcc 1 2 3 --simulate 1000000 --seed 1
radii            1, 2, 3
P(obtuse)        0.757947
  at vertex 1    0.472162
  at vertex 2    0.285784
  at vertex 3    0.000000
simulated        0.758088 (SE 0.000428)
```

From Python:

```python
from rtcc import p_obtuse, p_vertices, simulate

p_obtuse(1, 1, 1)        # 0.7500000000000002
p_vertices(1, 2, 3)      # array([4.72162279e-01, 2.85784243e-01, 1.11022302e-16])
simulate(1, 2, 3, n=10**6, seed=1).sum()
```

Only the ratios of the radii matter, so `rtcc 1 2 3` and `rtcc 2 4 6` agree. A
radius of zero is allowed and pins that vertex to the common center.

A vertex on a circle with `rk**2 >= ri**2 + rj**2` can never carry the obtuse
angle, and its entry comes back as zero to quadrature precision rather than
exactly zero, as above. Compare against a tolerance, not `== 0`.

## Documentation

The derivation, its special cases, and the simulation study are in
`paper/paper.qmd`; render it with `uv run quarto render paper/paper.qmd`.

## Development

```bash
uv run ruff check . && uv run pytest
```

Pull requests welcome. Work on a branch off `main`; see `AGENTS.md` for the
project layout.
