"""Probability that a random triangle on three concentric circles is obtuse.

Vertex ``k`` is drawn uniformly from the circle of radius ``r_k``, all three
circles centered at the origin, and the three vertices are independent.
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import quad

__all__ = ["p_vertex", "p_vertices", "p_obtuse", "simulate"]


def _check(r1: float, r2: float, r3: float) -> None:
    """Reject radii outside the domain the formula is derived for.

    Two zero radii put two vertices at the center, so there is no triangle and
    no angle to be obtuse. Without this the exact and simulated routes disagree:
    the quadrature applies its ``rk == 0`` shortcut to each coincident vertex in
    turn and sums past 1, while the simulator's strict inequality finds no
    obtuse angle at all.
    """
    if min(r1, r2, r3) < 0:
        raise ValueError("radii must be nonnegative")
    if sum(r == 0 for r in (r1, r2, r3)) > 1:
        raise ValueError("at most one radius may be zero")


def p_vertex(rk: float, ri: float, rj: float) -> float:
    """Probability that the angle at the vertex on the circle of radius ``rk``
    is obtuse, where ``ri`` and ``rj`` are the other two radii.

    Evaluates

    .. math::
        p_k = \\tfrac12 - \\frac{2}{\\pi^2}\\int_0^{t_{\\max}}
              \\arcsin\\!\\left[\\min\\left(1,
              \\frac{\\sqrt{r_k^2 - r_i^2\\sin^2 t}}{r_j}\\right)\\right] dt ,

    with :math:`t_{\\max} = \\arcsin\\min(1, r_k/r_i)`. The result is symmetric
    in ``ri`` and ``rj``, and is zero whenever ``rk**2 >= ri**2 + rj**2``.
    """
    _check(rk, ri, rj)
    if rk == 0:
        return 0.5
    t_max = np.arcsin(min(1.0, rk / ri)) if ri > 0 else np.pi / 2

    def integrand(t):
        d = np.sqrt(max(rk**2 - (ri * np.sin(t)) ** 2, 0.0))
        return np.pi / 2 if d >= rj else np.arcsin(d / rj)

    # Adaptive quadrature needs the point where the arcsine saturates, since the
    # integrand is only piecewise smooth there. The guard is exactly the
    # condition for that point to fall inside (0, t_max): the saturation radius
    # sqrt(rk**2 - rj**2) must be below min(ri, rk).
    kink = []
    if 0 < rj < rk <= np.hypot(ri, rj):
        kink.append(np.arcsin(min(1.0, np.sqrt(rk**2 - rj**2) / ri)))
    area = quad(integrand, 0.0, t_max, points=kink or None)[0]
    return 0.5 - 2.0 * area / np.pi**2


def p_vertices(r1: float, r2: float, r3: float) -> np.ndarray:
    """Probabilities that the obtuse angle sits at vertex 1, 2, or 3."""
    _check(r1, r2, r3)
    return np.array(
        [
            p_vertex(r1, r2, r3),
            p_vertex(r2, r3, r1),
            p_vertex(r3, r1, r2),
        ]
    )


def p_obtuse(r1: float, r2: float, r3: float) -> float:
    """Probability that the triangle is obtuse.

    A triangle has at most one obtuse angle, so this is the sum of the three
    per-vertex probabilities. Equal radii give 3/4.
    """
    return float(p_vertices(r1, r2, r3).sum())


def simulate(
    r1: float, r2: float, r3: float, n: int = 1_000_000, seed: int | None = None
) -> np.ndarray:
    """Monte Carlo estimates of the three per-vertex probabilities."""
    _check(r1, r2, r3)
    rng = np.random.default_rng(seed)
    radii = np.array([r1, r2, r3])
    theta = rng.uniform(0.0, 2.0 * np.pi, size=(n, 3))
    pts = np.stack([radii * np.cos(theta), radii * np.sin(theta)], axis=-1)
    return np.array(
        [
            np.mean(((pts[:, i] - pts[:, k]) * (pts[:, j] - pts[:, k])).sum(1) < 0)
            for k, i, j in [(0, 1, 2), (1, 2, 0), (2, 0, 1)]
        ]
    )
