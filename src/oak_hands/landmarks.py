def padded_size(size: tuple[float, float], padding: float) -> tuple[float, float]:
    """Size of a box after adding `padding` on each of its four sides (all normalized)."""
    width, height = size
    return width + 2 * padding, height + 2 * padding


def clamp_to_unit(value: float) -> float:
    return min(max(value, 0.0), 1.0)


def crop_to_image_coordinates(
    crop_points: list[tuple[float, float]],
    crop_center: tuple[float, float],
    crop_size: tuple[float, float],
) -> list[tuple[float, float]]:
    """Map points normalized to a crop onto the image the crop was taken from."""
    x_min = crop_center[0] - crop_size[0] / 2
    y_min = crop_center[1] - crop_size[1] / 2
    return [
        (clamp_to_unit(x_min + crop_size[0] * x), clamp_to_unit(y_min + crop_size[1] * y))
        for x, y in crop_points
    ]


def handedness_label(right_hand_probability: float) -> str:
    return "Right" if right_hand_probability >= 0.5 else "Left"


def hand_label(handedness: str, gesture: str | None) -> str:
    return f"{handedness} {gesture}" if gesture else handedness
