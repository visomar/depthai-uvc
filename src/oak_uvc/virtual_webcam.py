import cv2
import depthai as dai
import numpy as np
import pyvirtualcam

RESOLUTION = (1920, 1080)
FPS = 30
MJPEG_QUALITY = 90
OUTPUT_QUEUE_SIZE = 4


def decode_mjpeg_frame(encoded_frame_data: np.ndarray) -> np.ndarray:
    """Decode one MJPEG frame into a BGR image."""
    image = cv2.imdecode(encoded_frame_data, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode MJPEG frame")
    return image


def create_mjpeg_queue(pipeline: dai.Pipeline) -> dai.MessageQueue:
    """Compress frames on the camera so they fit through a USB 2.0 connection."""
    camera = pipeline.create(dai.node.Camera).build()
    camera_output = camera.requestOutput(RESOLUTION, dai.ImgFrame.Type.NV12, fps=FPS)
    encoder = pipeline.create(dai.node.VideoEncoder).build(
        camera_output,
        frameRate=FPS,
        profile=dai.VideoEncoderProperties.Profile.MJPEG,
    )
    encoder.setQuality(MJPEG_QUALITY)
    return encoder.out.createOutputQueue(maxSize=OUTPUT_QUEUE_SIZE, blocking=False)


def run_virtual_webcam() -> None:
    """Stream the camera to the host and republish it there as a virtual webcam."""
    width, height = RESOLUTION
    with dai.Pipeline() as pipeline:
        mjpeg_queue = create_mjpeg_queue(pipeline)
        with pyvirtualcam.Camera(width, height, FPS, fmt=pyvirtualcam.PixelFormat.BGR) as virtual_camera:
            pipeline.start()
            print(f"Virtual webcam '{virtual_camera.device}' is running. Press Ctrl+C to stop.")
            try:
                while pipeline.isRunning():
                    encoded_frame = mjpeg_queue.get()
                    virtual_camera.send(decode_mjpeg_frame(encoded_frame.getData()))
            except KeyboardInterrupt:
                print("Stopping virtual webcam.")
