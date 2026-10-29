import depthai as dai
import pytest

from oak_uvc.main import UnsupportedUsbSpeedError, select_runner, supports_native_uvc
from oak_uvc.native_uvc import run_native_uvc
from oak_uvc.virtual_webcam import run_virtual_webcam

USB3_SPEEDS = [dai.UsbSpeed.SUPER, dai.UsbSpeed.SUPER_PLUS]
USB2_OR_LOWER_SPEEDS = [dai.UsbSpeed.LOW, dai.UsbSpeed.FULL, dai.UsbSpeed.HIGH]


@pytest.mark.parametrize("usb_speed", USB3_SPEEDS)
def test_usb3_speeds_support_native_uvc(usb_speed):
    assert supports_native_uvc(usb_speed)


@pytest.mark.parametrize("usb_speed", USB2_OR_LOWER_SPEEDS)
def test_usb2_and_slower_speeds_do_not_support_native_uvc(usb_speed):
    assert not supports_native_uvc(usb_speed)


@pytest.mark.parametrize("experimental", [False, True])
@pytest.mark.parametrize("usb_speed", USB3_SPEEDS)
def test_usb3_always_uses_native_uvc(usb_speed, experimental):
    assert select_runner(usb_speed, experimental) is run_native_uvc


@pytest.mark.parametrize("usb_speed", USB2_OR_LOWER_SPEEDS)
def test_usb2_without_experimental_flag_is_rejected(usb_speed):
    with pytest.raises(UnsupportedUsbSpeedError, match="USB 2.0 or lower is not supported"):
        select_runner(usb_speed, experimental=False)


@pytest.mark.parametrize("usb_speed", USB2_OR_LOWER_SPEEDS)
def test_usb2_with_experimental_flag_uses_virtual_webcam(usb_speed):
    assert select_runner(usb_speed, experimental=True) is run_virtual_webcam
