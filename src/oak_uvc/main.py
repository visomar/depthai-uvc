import time

import depthai as dai

UVC_RESOLUTION = (1920, 1080)
KEEP_ALIVE_POLL_SECONDS = 0.1


def build_uvc_device_config() -> dai.Device.Config:
    """The device must know about UVC at boot to set up its USB descriptor."""
    device_config = dai.Device.Config()
    device_config.board.uvc = dai.BoardConfig.UVC(*UVC_RESOLUTION)
    device_config.board.uvc.frameType = dai.ImgFrame.Type.NV12
    return device_config


def main() -> None:
    # The device is created before the pipeline because a default device would
    # already be booted without UVC by the time a board config could be set.
    with dai.Device(build_uvc_device_config()) as device, dai.Pipeline(device) as pipeline:
        camera = pipeline.create(dai.node.Camera).build()
        uvc = pipeline.create(dai.node.UVC)
        camera.requestOutput(UVC_RESOLUTION, dai.ImgFrame.Type.NV12).link(uvc.input)

        pipeline.start()
        print("Camera is now exposed as a USB webcam. Press Ctrl+C to stop.")
        try:
            while pipeline.isRunning():
                time.sleep(KEEP_ALIVE_POLL_SECONDS)
        except KeyboardInterrupt:
            print("Stopping UVC stream.")


if __name__ == "__main__":
    main()
