import itertools

import pytest

from oak_hands.gestures import FingerState, Gesture, angle_degrees, finger_state, recognize_gesture, thumb_state

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
        (True, (True, True, True, True), Gesture.FIVE),
        (False, (False, False, False, False), Gesture.FIST),
        (True, (False, False, False, False), Gesture.THUMB),
        (False, (False, False, False, True), Gesture.PINKY),
        (False, (False, True, False, False), Gesture.FU),
        (False, (True, True, True, False), Gesture.BRITISH_THREE),
        (False, (False, True, True, True), Gesture.OK),
        (True, (False, True, True, True), Gesture.OK),
        (True, (True, False, False, True), Gesture.SPIDERMAN),
        (False, (True, False, False, True), Gesture.ROCK_AND_ROLL),
        (False, (True, True, False, False), Gesture.PEACE),
        (False, (True, False, False, False), Gesture.ONE),
        (True, (True, False, False, False), Gesture.TWO),
        (True, (True, True, False, False), Gesture.THREE),
        (False, (True, True, True, True), Gesture.FOUR),
    ],
)
def test_recognizes_gesture(thumb, fingers, gesture):
    assert recognize_gesture(make_hand(thumb, fingers)) == gesture


def test_unknown_finger_combination_is_not_a_gesture():
    assert recognize_gesture(make_hand(False, (True, False, True, False))) is None


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


def test_no_hand_matches_two_gestures():
    for states in itertools.product((FingerState.EXTENDED, FingerState.FOLDED), repeat=5):
        assert sum(gesture.matches(states) for gesture in Gesture) <= 1


def test_gesture_matches_its_finger_pattern():
    assert Gesture.ONE.matches((FingerState.FOLDED, FingerState.EXTENDED, *(FingerState.FOLDED,) * 3))


def test_wildcard_finger_matches_any_state():
    folded_thumb = (FingerState.FOLDED, FingerState.FOLDED, *(FingerState.EXTENDED,) * 3)
    extended_thumb = (FingerState.EXTENDED, *folded_thumb[1:])
    bent_thumb = (FingerState.BENT, *folded_thumb[1:])

    assert all(Gesture.OK.matches(states) for states in (folded_thumb, extended_thumb, bent_thumb))
