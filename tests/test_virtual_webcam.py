import cv2
import numpy as np
import pytest

from oak_uvc.virtual_webcam import decode_mjpeg_frame


def test_decode_mjpeg_frame_returns_bgr_image_of_original_size():
    original = np.full((48, 64, 3), 128, dtype=np.uint8)
    _, encoded = cv2.imencode(".jpg", original)

    decoded = decode_mjpeg_frame(encoded)

    assert decoded.shape == (48, 64, 3)


def test_decode_mjpeg_frame_rejects_invalid_data():
    with pytest.raises(ValueError):
        decode_mjpeg_frame(np.frombuffer(b"not a jpeg", dtype=np.uint8))
