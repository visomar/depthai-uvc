import time

import depthai as dai

UVC_RESOLUTION = (1920, 1080)
KEEP_ALIVE_POLL_SECONDS = 0.1


def main() -> None:
    with dai.Pipeline() as pipeline:
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
