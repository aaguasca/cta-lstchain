import pytest
from pathlib import Path


def test_parse_dl1():
    from lstchain.paths import parse_dl1_filename

    run = parse_dl1_filename('dl1_LST-1.1.Run01920.0000.fits.h5')
    assert run.tel_id == 1
    assert run.run == 1920
    assert run.subrun == 0
    assert run.stream == 1

    run = parse_dl1_filename(Path('dl1_LST-1.1.Run01920.0000.fits.h5'))
    assert run.tel_id == 1
    assert run.run == 1920
    assert run.subrun == 0
    assert run.stream == 1

    run = parse_dl1_filename('dl1_LST-1.Run01920.0000.fits.h5')
    assert run.tel_id == 1
    assert run.run == 1920
    assert run.subrun == 0
    assert run.stream is None

    run = parse_dl1_filename('dl1_LST-1.Run01920.0000.h5')
    assert run.tel_id == 1
    assert run.run == 1920
    assert run.subrun == 0
    assert run.stream is None

    run = parse_dl1_filename('dl1_LST-1.Run01920.0000.fits.hdf5')
    assert run.tel_id == 1
    assert run.run == 1920
    assert run.subrun == 0
    assert run.stream is None

    with pytest.raises(ValueError):
        run = parse_dl1_filename('foo.fits.fz')


def test_dl1_to_filename():
    from lstchain.paths import run_to_dl1_filename, Run

    assert run_to_dl1_filename(
        tel_id=1, run=1920, subrun=2
    ) == 'dl1_LST-1.Run01920.0002.h5'
    assert run_to_dl1_filename(
        tel_id=1, run=1920, subrun=3, stream=2
    ) == 'dl1_LST-1.2.Run01920.0003.h5'

    run = Run(tel_id=2, run=5, subrun=1)
    assert run_to_dl1_filename(*run) == 'dl1_LST-2.Run00005.0001.h5'


def test_dl2_to_filename():
    from lstchain.paths import run_to_dl2_filename, Run

    assert run_to_dl2_filename(
        tel_id=1, run=1920, subrun=2
    ) == 'dl2_LST-1.Run01920.0002.h5'
    assert run_to_dl2_filename(
        tel_id=1, run=1920, subrun=3, stream=2
    ) == 'dl2_LST-1.2.Run01920.0003.h5'

    run = Run(tel_id=2, run=5, subrun=1)
    assert run_to_dl2_filename(*run) == 'dl2_LST-2.Run00005.0001.h5'


def test_parse_r0():
    from lstchain.paths import parse_r0_filename

    run = parse_r0_filename('LST-1.1.Run01920.0000.fits.fz')
    assert run.tel_id == 1
    assert run.stream == 1
    assert run.run == 1920
    assert run.subrun == 0

    run = parse_r0_filename(Path('LST-1.1.Run01920.0000.fits.fz'))
    assert run.tel_id == 1
    assert run.stream == 1
    assert run.run == 1920
    assert run.subrun == 0

    with pytest.raises(ValueError):
        run = parse_r0_filename('foo.fits.fz')


def test_r0_to_filename():
    from lstchain.paths import run_to_r0_filename

    assert run_to_r0_filename(
        tel_id=1, run=1920, subrun=3, stream=2
    ) == 'LST-1.2.Run01920.0003.fits.fz'


def test_muon_filename():
    from lstchain.paths import run_to_muon_filename

    assert run_to_muon_filename(
        tel_id=1, run=2, subrun=3
    ) == 'muon_LST-1.Run00002.0003.fits.gz'

    assert run_to_muon_filename(
        tel_id=1, run=2, subrun=3, gzip=False
    ) == 'muon_LST-1.Run00002.0003.fits'

    assert run_to_muon_filename(
        tel_id=1, run=2, subrun=3, stream=4
    ) == 'muon_LST-1.4.Run00002.0003.fits.gz'
