import depthai as dai


def main() -> None:
    print(f"DepthAI version: {dai.__version__}")

    with dai.Pipeline() as pipeline:
        device = pipeline.getDefaultDevice()
        print(f"Connected to: {device.getDeviceName()} ({device.getDeviceId()})")
        print(f"USB speed: {device.getUsbSpeed().name}")
        print(f"Cameras: {[s.name for s in device.getConnectedCameras()]}")


if __name__ == "__main__":
    main()
