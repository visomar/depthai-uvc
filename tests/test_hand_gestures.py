import pytest

from oak_hands.gestures import FingerState, angle_degrees, finger_state, recognize_gesture, thumb_state

LANDMARK_COUNT = 21
FINGER_JOINTS_BY_FINGER = ((6, 7, 8), (10, 11, 12), (14, 15, 16), (18, 19, 20))
EXTENDED_THUMB = {1: (0.45, 0.8), 2: (0.4, 0.7), 3: (0.35, 0.6), 4: (0.3, 0.5)}
FOLDED_THUMB = {1: (0.45, 0.8), 2: (0.4, 0.7), 3: (0.45, 0.6), 4: (0.5, 0.65)}


def make_hand(thumb_extended: bool, fingers_extended: tuple[bool, bool, bool, bool]) -> list[tuple[float, float]]:
    """An upright hand; y grows downwards, so an extended fingertip is above its joints."""
    landmarks = [(0.5, 0.9)] * LANDMARK_COUNT
    landmarks[5] = (0.5, 0.5)
    for index, point in (EXTENDED_THUMB if thumb_extended else FOLDED_THUMB).items():
        landmarks[index] = point
    for extended, (pip, dip, tip) in zip(fingers_extended, FINGER_JOINTS_BY_FINGER):
        x = 0.5 + 0.02 * pip
        landmarks[pip] = (x, 0.4)
        landmarks[dip] = (x, 0.3 if extended else 0.45)
        landmarks[tip] = (x, 0.2 if extended else 0.5)
    return landmarks


@pytest.mark.parametrize(
    "thumb, fingers, gesture",
    [
        (True, (True, True, True, True), "FIVE"),
        (False, (False, False, False, False), "FIST"),
        (True, (False, False, False, False), "OK"),
        (False, (True, True, False, False), "PEACE"),
        (False, (True, False, False, False), "ONE"),
        (True, (True, False, False, False), "TWO"),
        (True, (True, True, False, False), "THREE"),
        (False, (True, True, True, True), "FOUR"),
    ],
)
def test_recognizes_gesture(thumb, fingers, gesture):
    assert recognize_gesture(make_hand(thumb, fingers)) == gesture


def test_unknown_finger_combination_is_not_a_gesture():
    assert recognize_gesture(make_hand(False, (False, True, False, False))) is None


def test_bent_finger_prevents_recognition():
    landmarks = make_hand(True, (True, True, True, True))
    landmarks[7] = (0.5 + 0.02 * 6, 0.1)  # index dip above its tip: neither extended nor folded

    assert finger_state(landmarks, (6, 7, 8)) == FingerState.BENT
    assert recognize_gesture(landmarks) is None


def test_thumb_states():
    assert thumb_state(make_hand(True, (False,) * 4)) == FingerState.EXTENDED
    assert thumb_state(make_hand(False, (False,) * 4)) == FingerState.FOLDED


def test_degenerate_landmarks_do_not_raise():
    assert recognize_gesture([(0.5, 0.5)] * LANDMARK_COUNT) is None


def test_angle_between_perpendicular_rays_is_90_degrees():
    assert angle_degrees((1.0, 0.0), (0.0, 0.0), (0.0, 1.0)) == pytest.approx(90.0)


def test_angle_with_a_zero_length_ray_is_zero():
    assert angle_degrees((0.0, 0.0), (0.0, 0.0), (1.0, 1.0)) == 0.0
