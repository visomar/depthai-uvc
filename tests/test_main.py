import depthai as dai
import pytest

from oak_uvc.main import supports_native_uvc


@pytest.mark.parametrize("usb_speed", [dai.UsbSpeed.SUPER, dai.UsbSpeed.SUPER_PLUS])
def test_usb3_speeds_support_native_uvc(usb_speed):
    assert supports_native_uvc(usb_speed)


@pytest.mark.parametrize("usb_speed", [dai.UsbSpeed.LOW, dai.UsbSpeed.FULL, dai.UsbSpeed.HIGH])
def test_usb2_and_slower_speeds_use_virtual_webcam(usb_speed):
    assert not supports_native_uvc(usb_speed)
