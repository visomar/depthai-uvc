import time

import depthai as dai

UVC_RESOLUTION = (1920, 1080)
KEEP_ALIVE_POLL_SECONDS = 0.1


def build_uvc_board_config() -> dai.BoardConfig:
    """The device must know about UVC before boot to set up its USB descriptor."""
    board_config = dai.BoardConfig()
    board_config.uvc = dai.BoardConfig.UVC(*UVC_RESOLUTION)
    board_config.uvc.frameType = dai.ImgFrame.Type.NV12
    return board_config


def main() -> None:
    with dai.Pipeline() as pipeline:
        pipeline.setBoardConfig(build_uvc_board_config())
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
