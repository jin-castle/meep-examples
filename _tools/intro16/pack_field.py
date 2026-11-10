"""Pack an existing cylindrical Meep Er DFT field; never run a simulation."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

p = argparse.ArgumentParser()
p.add_argument('source', type=Path)
args = p.parse_args()
folder = Path(__file__).resolve().parent
source = args.source.resolve()
d = np.load(source, allow_pickle=False)
# The cylindrical get_dft_array output is (z,r), independently checked against eps.
er = d['er']
lim = float(np.abs(er).max())
rgba = np.zeros((*er.shape, 4), np.uint8)
rgba[:, :, 0] = np.rint(np.clip(er.real / lim, -1, 1) * 127.5 + 127.5)
rgba[:, :, 1] = np.rint(np.clip(er.imag / lim, -1, 1) * 127.5 + 127.5)
rgba[:, :, 3] = 255
packed = rgba.tobytes()
(folder / 'field.bin').write_bytes(packed)
runfile = source.with_name(source.name.replace('_fields.npz', '.json'))
run = json.loads(runfile.read_text())
radii = [float(np.sqrt(n * .5 * (200 + n * .5 / 4))) for n in range(1, 26)]
info = {
    'source': str(source), 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'run_metadata_sha256': hashlib.sha256(runfile.read_bytes()).hexdigest(),
    'field_sha256': hashlib.sha256(packed).hexdigest(),
    'source_axes': ['z', 'r'], 'source_shape': list(d['er'].shape),
    'radial_stride': 1, 'nx': int(er.shape[1]), 'ny': int(er.shape[0]),
    'extent': d['extent'].tolist(), 'lim': lim,
    'encoding': 'RGBA8, rows z ascending, columns r ascending; R=Re(Er)/lim and G=Im(Er)/lim mapped [-1,1] to [0,255]; B=0,A=255',
    'max_component_quantization_error_normalized': 1 / 255,
    'component': 'Er (cylindrical radial electric component)', 'm': -1,
    'fcen': 2, 'wavelength_um': .5, 'glass_index': 1.5, 'resolution': run['resolution'],
    'zone_radii_um': radii, 'num_zones': 25,
    'substrate_z_um': [-2.25, -.25], 'raised_glass_z_um': [-.25, .25],
    'source_z_um': -2.25, 'n2f_top_z_um': 2.25,
    'formula': 'Re[Er(r,z) exp(i*m*phi-i*phase)], m=-1; world=(r*cos(phi),8*z,r*sin(phi))',
    'interpretation': 'Saved cylindrical near-field complex Er DFT coefficient revolved with its actual m=-1 angular factor. This is a steady-state phase cycle, not a transient. Axial display scale is 8x for all apparatus/field/source coordinates. No field is fabricated between the computational cell and the distant focus.',
    'farfield': {'complex_field_available': False, 'saved_arrays': ['rr','Ir','zz','Iz'], 'focus_design_distance_um': 200,
                 'computed_peak_distance_um': run['z_peak'], 'not_shown': 'Only real intensity profiles were saved for the distant focus; the animation contains no far-field phase reconstruction.'},
    'display': {'axial_magnification': 8, 'loop_seconds': 8, 'phase_cycles': 2, 'fps': 30, 'size': [1280,720],
                'colormap': 'signed linear RdBu, negative red, positive blue; clamp(3*Re(Er)/lim,-1,1)',
                'fixed_color_gain': 3, 'opacity': '1-exp(-.35*abs(Re(Er)/lim)^1.3*world_ray_step); zero transparent; complex magnitude below .012 omitted'},
}
(folder / 'field.json').write_text(json.dumps(info, indent=2) + '\n', encoding='utf-8')
print('packed', er.shape, len(packed), 'bytes; R25', radii[-1], 'um; lim', lim)
