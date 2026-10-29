"""Rule-based hand gesture recognition from the 21 MediaPipe hand landmarks.

Ported from the hand-pose example in luxonis/oak-examples. Landmarks are (x, y)
image coordinates, so y grows downwards. The hand is expected to be upright.
"""

import math
from enum import Enum, IntEnum

Point = tuple[float, float]

THUMB_BASE, THUMB_KNUCKLE, THUMB_JOINT, THUMB_MIDDLE, THUMB_TIP = 0, 1, 2, 3, 4
INDEX_BASE = 5
THUMB_STRAIGHT_ANGLE_SUM_MIN = 460.0
THUMB_REACH_RATIO_MIN = 1.2
# (pip, dip, tip) landmark indices of the index, middle, ring and little fingers.
FINGER_JOINTS = ((6, 7, 8), (10, 11, 12), (14, 15, 16), (18, 19, 20))


class FingerState(IntEnum):
    BENT = -1
    FOLDED = 0
    EXTENDED = 1


E, F = FingerState.EXTENDED, FingerState.FOLDED


class Gesture(Enum):
    """Each value is the (thumb, index, middle, ring, little) pattern that makes the gesture."""

    FIVE = (E, E, E, E, E)
    FIST = (F, F, F, F, F)
    THUMB = (E, F, F, F, F)
    PEACE = (F, E, E, F, F)
    ONE = (F, E, F, F, F)
    TWO = (E, E, F, F, F)
    THREE = (E, E, E, F, F)
    FOUR = (F, E, E, E, E)
    PINKY = (F, F, F, F, E)
    FU = (F, F, E, F, F)
    BRITISH_THREE = (F, E, E, E, F)
    OK = (F, F, E, E, E)
    SPIDERMAN = (E, E, F, F, E)
    ROCK_AND_ROLL = (F, E, F, F, E)


def angle_degrees(a: Point, vertex: Point, c: Point) -> float:
    """Angle at `vertex` between the rays towards `a` and `c`."""
    ax, ay = a[0] - vertex[0], a[1] - vertex[1]
    cx, cy = c[0] - vertex[0], c[1] - vertex[1]
    lengths = math.hypot(ax, ay) * math.hypot(cx, cy)
    if lengths == 0:
        return 0.0
    cosine = (ax * cx + ay * cy) / lengths
    return math.degrees(math.acos(max(-1.0, min(1.0, cosine))))


def thumb_state(landmarks: list[Point]) -> FingerState:
    """The thumb is extended when it is nearly straight and reaches away from the palm."""
    total_angle = (
        angle_degrees(landmarks[THUMB_BASE], landmarks[THUMB_KNUCKLE], landmarks[THUMB_JOINT])
        + angle_degrees(landmarks[THUMB_KNUCKLE], landmarks[THUMB_JOINT], landmarks[THUMB_MIDDLE])
        + angle_degrees(landmarks[THUMB_JOINT], landmarks[THUMB_MIDDLE], landmarks[THUMB_TIP])
    )
    joint_to_middle = math.dist(landmarks[THUMB_JOINT], landmarks[THUMB_MIDDLE])
    middle_to_index_base = math.dist(landmarks[THUMB_MIDDLE], landmarks[INDEX_BASE])
    is_straight = total_angle > THUMB_STRAIGHT_ANGLE_SUM_MIN
    reaches_away = joint_to_middle > 0 and middle_to_index_base / joint_to_middle > THUMB_REACH_RATIO_MIN
    return FingerState.EXTENDED if is_straight and reaches_away else FingerState.FOLDED


def finger_state(landmarks: list[Point], joints: tuple[int, int, int]) -> FingerState:
    pip, dip, tip = joints
    pip_y, dip_y, tip_y = landmarks[pip][1], landmarks[dip][1], landmarks[tip][1]
    if tip_y < dip_y < pip_y:
        return FingerState.EXTENDED
    if pip_y < tip_y:
        return FingerState.FOLDED
    return FingerState.BENT


def recognize_gesture(landmarks: list[Point]) -> Gesture | None:
    """The gesture the hand is making, or None if it matches none."""
    states = (thumb_state(landmarks), *(finger_state(landmarks, joints) for joints in FINGER_JOINTS))
    try:
        return Gesture(states)
    except ValueError:
        return None
