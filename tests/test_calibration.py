import pytest

from forestconnectome.validate.calibration import IsotonicConfidenceCalibrator


pytest.importorskip("sklearn")


def test_isotonic_calibration_is_monotonic_and_bounded():
    calibrator = IsotonicConfidenceCalibrator().fit(
        [0.1, 0.2, 0.7, 0.8, 0.9, 1.0],
        [0, 0, 0, 1, 1, 1],
    )
    predicted = calibrator.predict([0.15, 0.75, 0.95])
    assert predicted == sorted(predicted)
    assert all(0.0 <= value <= 1.0 for value in predicted)
