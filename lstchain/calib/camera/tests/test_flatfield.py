import numpy as np
import astropy.units as u
from lstchain.calib.camera.flatfield import FlasherFlatFieldCalculator
from ctapipe.containers import ArrayEventContainer
from traitlets.config.loader import Config
from ctapipe.instrument import SubarrayDescription, TelescopeDescription
from astropy.time import Time

def test_flasherflatfieldcalculator():
    """test of flasherFlatFieldCalculator"""
    tel_id = 0
    n_gain = 2
    n_events = 1000
    n_pixels = 1855
    ff_level = 10000
    ff_std = 10

    subarray = SubarrayDescription(
        "test array",
        tel_positions={0: np.zeros(3) * u.m},
        tel_descriptions={
            0: TelescopeDescription.from_name(
                optics_name="SST-ASTRI", camera_name="CHEC"
            ),
        },
    )
    subarray.tel[0].camera.readout.reference_pulse_shape = np.ones((1, 2))
    subarray.tel[0].camera.readout.reference_pulse_sample_width = u.Quantity(1, u.ns)

    config = Config({
        "FixedWindowSum": {
            "window_shift": 5,
            "window_width": 10,
            "peak_index": 20,
            "apply_integration_correction": False,
        }
    })
    ff_calculator = FlasherFlatFieldCalculator(subarray=subarray, charge_product="FixedWindowSum",
                                               sample_size=n_events,
                                               tel_id=tel_id, config=config)
    # create one event
    data = ArrayEventContainer()
    data.meta['origin'] = 'test'
    data.trigger.time = Time(0, format='mjd', scale='tai')
    # initialize mon and r1 data
    data.mon.tel[tel_id].pixel_status.hardware_failing_pixels = np.zeros((n_gain, n_pixels), dtype=bool)
    data.mon.tel[tel_id].pixel_status.pedestal_failing_pixels = np.zeros((n_gain, n_pixels), dtype=bool)
    data.mon.tel[tel_id].pixel_status.flatfield_failing_pixels = np.zeros((n_gain, n_pixels), dtype=bool)
    data.r1.tel[tel_id].waveform = np.zeros((n_gain, n_pixels, 40), dtype=np.float32)
    # data.r1.tel[tel_id].trigger_time = 1000

    rng = np.random.default_rng(0)

    # First test: good event
    while ff_calculator.num_events_seen < n_events:
        # flat-field signal put == delta function of height ff_level at sample 20
        data.r1.tel[tel_id].waveform[:, :, 20] = rng.normal(ff_level, ff_std)

        if ff_calculator.calculate_relative_gain(data):
            assert data.mon.tel[tel_id].flatfield

            print(data.mon.tel[tel_id].flatfield)
            assert np.isclose(np.mean(data.mon.tel[tel_id].flatfield.charge_median), ff_level, rtol=0.01)
            assert np.isclose(np.mean(data.mon.tel[tel_id].flatfield.charge_std), ff_std, rtol=0.05)
            assert np.isclose(np.mean(data.mon.tel[tel_id].flatfield.relative_gain_median), 1, rtol=0.01)
            assert np.isclose(np.mean(data.mon.tel[tel_id].flatfield.relative_gain_std), 0, rtol=0.01)

    # Second test: introduce some failing pixels
    failing_pixels_id = np.array([10, 20, 30, 40])
    data.r1.tel[tel_id].waveform[:, failing_pixels_id, :] = 0
    data.mon.tel[tel_id].pixel_status.pedestal_failing_pixels[:,failing_pixels_id] = True

    while ff_calculator.num_events_seen < n_events:
        if ff_calculator.calculate_relative_gain(data):

            # working pixel have good gain
            assert (data.mon.tel[tel_id].flatfield.relative_gain_median[0, 0] == 1)

            # bad pixels do non influence the gain
            assert np.mean(data.mon.tel[tel_id].flatfield.relative_gain_std) == 0

