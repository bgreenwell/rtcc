import numpy as np
import pytest
from scipy.integrate import quad

from rtcc import p_obtuse, p_vertex, p_vertices, simulate
from rtcc.cli import main


def legendre_chi2(s, terms=2000):
    k = np.arange(terms)
    return np.sum(s ** (2 * k + 1) / (2 * k + 1.0) ** 2)


def test_equal_radii_give_three_quarters():
    assert p_obtuse(1, 1, 1) == pytest.approx(0.75, abs=1e-10)
    assert p_vertices(2.5, 2.5, 2.5) == pytest.approx([0.25] * 3, abs=1e-10)


def test_only_ratios_matter():
    assert p_obtuse(3, 6, 9) == pytest.approx(p_obtuse(1, 2, 3), abs=1e-10)


def test_symmetric_in_the_other_two_radii():
    assert p_vertex(1.3, 0.7, 2.0) == pytest.approx(p_vertex(1.3, 2.0, 0.7), abs=1e-10)


def test_vertex_on_a_dominant_circle_is_never_obtuse():
    assert p_vertex(np.hypot(1, 2), 1, 2) == pytest.approx(0.0, abs=1e-10)
    assert p_vertex(5.0, 1, 2) == pytest.approx(0.0, abs=1e-10)
    assert p_vertex(1.4, 1, 1) > 0.0  # 1.4 < sqrt(2)


def test_vertex_at_the_center():
    # A vertex at the origin sees two independent uniform directions.
    assert p_vertex(0.0, 1.0, 3.0) == 0.5
    # With r3 = 0 and r1 <= r2, P(obtuse) = 1 - arcsin(r1 / r2) / pi.
    for r1, r2 in [(1.0, 1.0), (1.0, 2.0), (0.4, 3.0)]:
        expected = 1.0 - np.arcsin(r1 / r2) / np.pi
        assert p_obtuse(r1, r2, 0.0) == pytest.approx(expected, abs=1e-10)


def test_two_equal_radii_closed_form():
    # r1 = r2 = 1, r3 = rho >= sqrt(2): P = 1 - (4 / pi^2) * chi_2(1 / rho).
    for rho in [np.sqrt(2), 2.0, 3.0, 10.0]:
        expected = 1.0 - 4.0 * legendre_chi2(1.0 / rho) / np.pi**2
        assert p_obtuse(1.0, 1.0, rho) == pytest.approx(expected, abs=1e-9)


def test_bounds():
    radii = [(1, 1, 1), (1, 1, 0.2), (0.3, 1, 1.05), (1, 5, 25), (1, 2, 3)]
    for r in radii:
        assert 0.5 <= p_obtuse(*r) < 1.0


@pytest.mark.parametrize("radii", [(1, 0, 0), (0, 0, 0), (0, 1, 0)])
def test_two_zero_radii_are_rejected(radii):
    # Two vertices at the center leave no triangle. Without this guard the
    # exact route summed past 1 while the simulator reported nothing obtuse.
    for fn in (p_vertices, p_obtuse):
        with pytest.raises(ValueError, match="at most one radius"):
            fn(*radii)
    with pytest.raises(ValueError, match="at most one radius"):
        simulate(*radii, n=10)
    with pytest.raises(SystemExit):
        main([str(r) for r in radii])


def test_negative_radii_are_rejected():
    with pytest.raises(ValueError, match="nonnegative"):
        p_obtuse(1, 2, -1)
    with pytest.raises(SystemExit):
        main(["1", "2", "-1"])


def test_one_zero_radius_still_supported():
    assert p_obtuse(1, 1, 0) == pytest.approx(0.5, abs=1e-10)
    assert main(["1", "2", "0"]) == 0


def test_gaussian_mixture_kernel():
    # Rayleigh radii give the Gaussian convention, whose obtuse probability is
    # 3/4. The proof reduces to E[1/(1+U)] = 1/sqrt(2) for arcsine U, checked
    # here by quadrature rather than by sampling.
    integrand = lambda u: 1 / (np.pi * np.sqrt(u * (1 - u)) * (1 + u))  # noqa: E731
    assert quad(integrand, 0, 1)[0] == pytest.approx(1 / np.sqrt(2), abs=1e-10)
    # P = (3/2) * (1 - E[1/(1+U)]^2) = (3/2)(1 - 1/2) = 3/4.
    assert 1.5 * (1 - quad(integrand, 0, 1)[0] ** 2) == pytest.approx(0.75, abs=1e-10)


@pytest.mark.parametrize(
    "radii", [(1, 1, 1), (1, 1, 2), (1, 2, 3), (1, 1, 0.5), (0.5, 0.8, 1.0)]
)
def test_quadrature_matches_simulation(radii):
    n = 400_000
    mc = simulate(*radii, n=n, seed=42)
    exact = p_vertices(*radii)
    se = np.sqrt(np.clip(exact * (1 - exact), 1e-12, None) / n)
    assert np.all(np.abs(mc - exact) < 4 * se)
