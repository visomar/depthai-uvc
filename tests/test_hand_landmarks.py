import pytest

from oak_hands.landmarks import clamp_to_unit, crop_to_image_coordinates, handedness_label, padded_size


def test_padding_is_added_on_every_side():
    assert padded_size((0.2, 0.4), 0.1) == pytest.approx((0.4, 0.6))


@pytest.mark.parametrize("value, expected", [(-0.5, 0.0), (0.3, 0.3), (1.7, 1.0)])
def test_clamp_to_unit(value, expected):
    assert clamp_to_unit(value) == expected


def test_crop_corners_map_to_the_crop_box_in_the_image():
    points = crop_to_image_coordinates([(0.0, 0.0), (1.0, 1.0)], crop_center=(0.5, 0.5), crop_size=(0.4, 0.2))

    assert points == pytest.approx([(0.3, 0.4), (0.7, 0.6)])


def test_crop_center_maps_to_the_crop_center():
    points = crop_to_image_coordinates([(0.5, 0.5)], crop_center=(0.25, 0.75), crop_size=(0.3, 0.3))

    assert points == pytest.approx([(0.25, 0.75)])


def test_points_outside_the_image_are_clamped():
    points = crop_to_image_coordinates([(0.0, 1.0)], crop_center=(0.05, 0.95), crop_size=(0.4, 0.4))

    assert points == [(0.0, 1.0)]


@pytest.mark.parametrize("probability, label", [(0.1, "Left"), (0.49, "Left"), (0.5, "Right"), (0.9, "Right")])
def test_handedness_label(probability, label):
    assert handedness_label(probability) == label
