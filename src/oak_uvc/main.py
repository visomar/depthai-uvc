import time

import depthai as dai

DEFAULT_RESOLUTION = (1920, 1080)
DEFAULT_FPS = 30
# Uncompressed NV12 at 1080p30 (~93 MB/s) does not fit in USB 2.0 (~25 MB/s usable).
USB2_RESOLUTION = (960, 540)
USB2_FPS = 25
USB3_SPEEDS = (dai.UsbSpeed.SUPER, dai.UsbSpeed.SUPER_PLUS)
KEEP_ALIVE_POLL_SECONDS = 0.1


def detect_usb_speed() -> dai.UsbSpeed:
    with dai.Device() as device:
        return device.getUsbSpeed()


def choose_stream_mode(usb_speed: dai.UsbSpeed) -> tuple[tuple[int, int], int]:
    """Return the (resolution, fps) that fits the bandwidth of the USB connection."""
    if usb_speed in USB3_SPEEDS:
        return DEFAULT_RESOLUTION, DEFAULT_FPS
    return USB2_RESOLUTION, USB2_FPS


def build_uvc_device_config(resolution: tuple[int, int]) -> dai.Device.Config:
    """The device must know about UVC at boot to set up its USB descriptor."""
    device_config = dai.Device.Config()
    device_config.board.uvc = dai.BoardConfig.UVC(*resolution)
    device_config.board.uvc.frameType = dai.ImgFrame.Type.NV12
    return device_config


def main() -> None:
    # The UVC config is fixed at boot, so the USB speed is probed with a plain
    # device first and the camera is then booted again with the right mode.
    usb_speed = detect_usb_speed()
    resolution, fps = choose_stream_mode(usb_speed)
    print(f"USB speed: {usb_speed.name}, using {resolution[0]}x{resolution[1]} at {fps} fps")

    # The device is created before the pipeline because a default device would
    # already be booted without UVC by the time a board config could be set.
    with dai.Device(build_uvc_device_config(resolution)) as device, dai.Pipeline(device) as pipeline:
        camera = pipeline.create(dai.node.Camera).build()
        uvc = pipeline.create(dai.node.UVC)
        camera.requestOutput(resolution, dai.ImgFrame.Type.NV12, fps=fps).link(uvc.input)

        pipeline.start()
        print("Camera is now exposed as a USB webcam. Press Ctrl+C to stop.")
        try:
            while pipeline.isRunning():
                time.sleep(KEEP_ALIVE_POLL_SECONDS)
        except KeyboardInterrupt:
            print("Stopping UVC stream.")


if __name__ == "__main__":
    main()
