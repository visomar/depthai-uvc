# DepthAI - OAK test

Base project for building on top of a Luxonis OAK-D camera using [DepthAI](https://docs.luxonis.com/software-v3/) v3. It currently includes a device info program and a UVC webcam program.

## Requirements

| Tool | Version |
| --- | --- |
| Python | 3.14 (3.15 is not supported yet because DepthAI has no 3.15 wheels) |
| pip | recent (comes with Python; `pip install --upgrade pip` if in doubt) |
| DepthAI | `>=3.11,<4` (installed automatically by pip) |
| Git | any recent version |
| Hardware | Luxonis OAK-D connected over USB (USB 3 cable recommended) |

Platform notes:
- **macOS / Windows:** no extra setup is needed for the camera itself. The USB 2.0 webcam mode (see below) also needs [OBS Studio](https://obsproject.com/) installed, because it provides the virtual camera.
- **Linux:** install the Luxonis udev rules so the camera is accessible without root:
  ```sh
  echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/80-movidius.rules
  sudo udevadm control --reload-rules && sudo udevadm trigger
  ```
- **Linux, USB 2.0 webcam mode:** install and load [v4l2loopback](https://github.com/umlaeute/v4l2loopback) to get a virtual camera device, e.g. `sudo modprobe v4l2loopback exclusive_caps=1`.

## Setup (on a new machine)

```sh
git clone <repository-url> depthai
cd depthai
python3.14 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Check that the install worked:

```sh
python -c "import depthai; print(depthai.__version__)"
```

## Run

Plug in the OAK-D, then:

### Device info (`oak-info`)

```sh
oak-info
# or
python -m oak_info.main
```

It prints the DepthAI version, the device name and ID, the USB speed, and the connected cameras.

### UVC webcam (`oak-uvc`)

```sh
oak-uvc
# or
python -m oak_uvc.main
```

It makes the camera show up as a webcam that any app can use. Keep the program running while you use the webcam; press Ctrl+C to stop. Startup takes a few seconds because the camera is booted twice: once to detect the USB speed, and once to start streaming.

Depending on the USB connection it works in one of two ways:

| USB speed | Mode | Details |
| --- | --- | --- |
| USB 3 | Native UVC | The camera itself acts as a webcam using the DepthAI UVC node (1920x1080, 30 fps). |
| USB 2.0 or lower | Virtual webcam (experimental) | Only runs with `--experimental`. The UVC node does not work over USB 2.0. Instead the camera compresses video to MJPEG (1920x1080, 30 fps) and the computer republishes it as a virtual webcam with [pyvirtualcam](https://github.com/letmaik/pyvirtualcam). Needs OBS (macOS/Windows) or v4l2loopback (Linux), see Requirements. In your apps, pick the virtual camera (named "OBS Virtual Camera" on macOS/Windows). |

On USB 2.0 or lower, `oak-uvc` exits with the error `USB 2.0 or lower is not supported` unless you pass the flag. The virtual webcam mode is untested, so it is opt-in:

```sh
oak-uvc --experimental
```

**Virtual camera requirements for USB 2.0 mode (pyvirtualcam):**
- **macOS:** install [OBS Studio](https://obsproject.com/). pyvirtualcam uses its virtual camera, so OBS must be installed (you may need to start its virtual camera once so macOS registers it).
- **Windows:** install [OBS Studio](https://obsproject.com/) for the same reason.
- **Linux:** install and load [v4l2loopback](https://github.com/umlaeute/v4l2loopback), e.g. `sudo modprobe v4l2loopback exclusive_caps=1`.

## Test

```sh
pytest
```

## Project layout

```
pyproject.toml     # package metadata and dependencies
src/oak_info/      # prints device info (oak-info)
src/oak_uvc/       # exposes the camera as a USB webcam (oak-uvc)
  main.py            #   detects USB speed and picks the mode
  native_uvc.py      #   USB 3: the camera acts as a UVC webcam
  virtual_webcam.py  #   USB 2.0: MJPEG stream republished as a virtual webcam
tests/             # pytest tests
AGENTS.md          # guidelines for AI agents and contributors
```

## Contributing

See [AGENTS.md](AGENTS.md): add tests, keep code simple and well named, follow Python best practices.
