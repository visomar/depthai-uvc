import argparse
import sys
from collections.abc import Callable

import depthai as dai

from oak_uvc.native_uvc import run_native_uvc
from oak_uvc.virtual_webcam import run_virtual_webcam

USB3_SPEEDS = (dai.UsbSpeed.SUPER, dai.UsbSpeed.SUPER_PLUS)


class UnsupportedUsbSpeedError(Exception):
    pass


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enable experimental features")
    parser.add_argument(
        "--experimental",
        action="store_true",
        help="Enable experimental features",
    )
    return parser.parse_args()


def detect_usb_speed() -> dai.UsbSpeed:
    with dai.Device() as device:
        return device.getUsbSpeed()


def supports_native_uvc(usb_speed: dai.UsbSpeed) -> bool:
    """Native UVC streams uncompressed 1080p, which only fits in USB 3 bandwidth."""
    return usb_speed in USB3_SPEEDS


def select_runner(usb_speed: dai.UsbSpeed, experimental: bool) -> Callable[[], None]:
    if supports_native_uvc(usb_speed):
        return run_native_uvc
    if experimental:
        return run_virtual_webcam
    raise UnsupportedUsbSpeedError("USB 2.0 or lower is not supported (use --experimental to try the virtual webcam mode)")


def main() -> None:
    experimental = parse_arguments().experimental
    usb_speed = detect_usb_speed()
    print(f"USB speed: {usb_speed.name}")
    try:
        runner = select_runner(usb_speed, experimental)
    except UnsupportedUsbSpeedError as error:
        sys.exit(f"Error: {error}")
    runner()


if __name__ == "__main__":
    main()
