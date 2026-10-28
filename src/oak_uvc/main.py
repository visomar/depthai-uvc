import depthai as dai

from oak_uvc.native_uvc import run_native_uvc
from oak_uvc.virtual_webcam import run_virtual_webcam

USB3_SPEEDS = (dai.UsbSpeed.SUPER, dai.UsbSpeed.SUPER_PLUS)


def detect_usb_speed() -> dai.UsbSpeed:
    with dai.Device() as device:
        return device.getUsbSpeed()


def supports_native_uvc(usb_speed: dai.UsbSpeed) -> bool:
    """Native UVC streams uncompressed 1080p, which only fits in USB 3 bandwidth."""
    return usb_speed in USB3_SPEEDS


def main() -> None:
    usb_speed = detect_usb_speed()
    if supports_native_uvc(usb_speed):
        print(f"USB speed: {usb_speed.name}, using native UVC")
        run_native_uvc()
    else:
        print(f"USB speed: {usb_speed.name}, using virtual webcam (MJPEG over USB 2.0)")
        run_virtual_webcam()


if __name__ == "__main__":
    main()
