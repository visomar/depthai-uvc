import time

import depthai as dai

RESOLUTION = (1920, 1080)
FPS = 30
KEEP_ALIVE_POLL_SECONDS = 0.1


def build_uvc_device_config(resolution: tuple[int, int]) -> dai.Device.Config:
    """The device must know about UVC at boot to set up its USB descriptor."""
    device_config = dai.Device.Config()
    device_config.board.uvc = dai.BoardConfig.UVC(*resolution)
    device_config.board.uvc.frameType = dai.ImgFrame.Type.NV12
    return device_config


def run_native_uvc() -> None:
    """Expose the camera as a USB webcam from the camera itself (needs USB 3 bandwidth)."""
    # The device is created before the pipeline because a default device would
    # already be booted without UVC by the time a board config could be set.
    with dai.Device(build_uvc_device_config(RESOLUTION)) as device, dai.Pipeline(device) as pipeline:
        camera = pipeline.create(dai.node.Camera).build()
        uvc = pipeline.create(dai.node.UVC)
        camera.requestOutput(RESOLUTION, dai.ImgFrame.Type.NV12, fps=FPS).link(uvc.input)

        pipeline.start()
        print("Camera is now exposed as a USB webcam. Press Ctrl+C to stop.")
        try:
            while pipeline.isRunning():
                time.sleep(KEEP_ALIVE_POLL_SECONDS)
        except KeyboardInterrupt:
            print("Stopping UVC stream.")
