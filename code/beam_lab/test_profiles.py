import unittest
import numpy as np
from profiles import airy_aperture, boundary_x, gaussian, laguerre_p0, phase_winding


class ProfilesTest(unittest.TestCase):
    def test_signed_vortex_winding_and_radial_maximum(self):
        theta = np.linspace(0, 2 * np.pi, 512, endpoint=False)
        for charge in (-3, -2, 0, 2, 3):
            radius = np.sqrt(abs(charge) / 2) if charge else 0.5
            values = laguerre_p0(radius * np.cos(theta), radius * np.sin(theta), 1, charge)
            self.assertAlmostEqual(phase_winding(values), charge, places=12)
            if charge:
                np.testing.assert_allclose(abs(values), 1, atol=1e-14)
                self.assertEqual(laguerre_p0(0, 0, 1, charge), 0)

    def test_gaussian_tilt_and_envelope(self):
        y = np.linspace(-1, 1, 401)
        values = gaussian(y, 0.9, 1, 20)
        np.testing.assert_allclose(abs(values), np.exp(-(y / 0.9) ** 2), atol=1e-15)
        slope = np.polyfit(y, np.unwrap(np.angle(values)), 1)[0]
        self.assertAlmostEqual(slope, 2 * np.pi * np.sin(np.deg2rad(20)), places=12)

    def test_boundary_orientation(self):
        np.testing.assert_allclose(boundary_x(np.array([-2, 0, 2]), 0.1), [0.4, 0, 0.4])
        np.testing.assert_allclose(boundary_x(np.array([-2, 0, 2]), -0.1), [-0.4, 0, -0.4])

    def test_finite_airy_aperture_and_apodization(self):
        y = np.linspace(-5, 5, 1001)
        low = airy_aperture(y, 0.6, 0.08, 4.1)
        high = airy_aperture(y, 0.6, 0.2, 4.1)
        self.assertTrue(np.isfinite(low).all())
        self.assertTrue(np.all(low[abs(y) > 4.1] == 0))
        self.assertLessEqual(np.max(abs(low)), 1.001)
        self.assertLess(np.linalg.norm(high[y < -2]), np.linalg.norm(low[y < -2]))

    def test_invalid_inputs(self):
        for width in (0, -1, np.nan, np.inf):
            with self.assertRaises(ValueError):
                gaussian(0, width)
        with self.assertRaises(ValueError):
            gaussian(0, 1, angle_deg=90)
        with self.assertRaises(ValueError):
            laguerre_p0(0, 0, 1, 1.5)
        with self.assertRaises(ValueError):
            airy_aperture(0, 1, 0, 3)
        with self.assertRaises(ValueError):
            boundary_x(0, np.nan)
        with self.assertRaises(ValueError):
            phase_winding(np.zeros(32))


if __name__ == "__main__":
    unittest.main()
