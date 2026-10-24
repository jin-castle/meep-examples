"""Analytic aperture profiles for the Beam Lab experiments.

These functions describe electric-current sheet amplitudes, not exact vector
Maxwell eigenmodes. Lengths use the same arbitrary unit as the Meep cell.
"""

import numpy as np
from scipy.special import airy


def positive(value, name):
    value = float(value)
    if not np.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def gaussian(y, waist, frequency=1.0, angle_deg=0.0, index=1.0):
    waist = positive(waist, "waist")
    frequency = positive(frequency, "frequency")
    index = positive(index, "index")
    if not np.isfinite(angle_deg) or abs(angle_deg) >= 90:
        raise ValueError("angle_deg must lie strictly between -90 and 90")
    y = np.asarray(y)
    return np.exp(-(y / waist) ** 2 + 2j * np.pi * frequency * index
                  * np.sin(np.deg2rad(angle_deg)) * y)


def laguerre_p0(y, z, waist, charge):
    waist = positive(waist, "waist")
    if isinstance(charge, bool) or not isinstance(charge, (int, np.integer)):
        raise ValueError("charge must be an integer")
    if abs(charge) > 20:
        raise ValueError("this educational aperture supports |charge| <= 20")
    r = np.hypot(y, z)
    order = abs(charge)
    # The analytic radial maximum occurs at r = waist*sqrt(order/2).
    maximum = (order / np.e) ** (order / 2) if order else 1.0
    return ((np.sqrt(2) * r / waist) ** order * np.exp(-(r / waist) ** 2)
            * np.exp(1j * charge * np.arctan2(z, y)) / maximum)


def airy_aperture(y, scale, alpha, half_width):
    scale = positive(scale, "scale")
    alpha = positive(alpha, "alpha")
    half_width = positive(half_width, "half_width")
    if alpha > 1:
        raise ValueError("alpha must be <= 1 for this finite aperture")
    y = np.asarray(y)
    u = np.clip(y, -half_width, half_width) / scale
    # Fixed numerical normalization of the continuous, finite aperture.
    sample = np.linspace(-half_width / scale, half_width / scale, 8193)
    maximum = np.max(np.abs(airy(sample)[0] * np.exp(alpha * sample)))
    values = airy(u)[0] * np.exp(alpha * u) / maximum
    return np.where(np.abs(y) <= half_width, values, 0.0)


def boundary_x(y, curvature):
    if not np.isfinite(curvature):
        raise ValueError("curvature must be finite")
    return curvature * np.asarray(y) ** 2


def phase_winding(values):
    """Closed polygon winding, with low-amplitude/singular loops rejected."""
    values = np.asarray(values, dtype=complex)
    if values.ndim != 1 or len(values) < 16 or not np.all(np.isfinite(values)):
        raise ValueError("winding needs at least 16 finite complex samples")
    peak = np.max(np.abs(values))
    if peak == 0 or np.min(np.abs(values)) < 1e-5 * peak:
        raise ValueError("phase winding is undefined near a zero on the loop")
    return float(np.sum(np.angle(np.roll(values, -1) * values.conj())) / (2 * np.pi))
