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
- **macOS / Windows:** no extra setup is usually needed.
- **Linux:** install the Luxonis udev rules so the camera is accessible without root:
  ```sh
  echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/80-movidius.rules
  sudo udevadm control --reload-rules && sudo udevadm trigger
  ```

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

It uses the DepthAI UVC node so the camera is detected as a USB webcam (1920x1080) that any app can use. Keep the program running while you use the webcam; press Ctrl+C to stop. The camera may re-enumerate as a UVC device once the stream starts.

## Test

```sh
pytest
```

## Project layout

```
pyproject.toml     # package metadata and dependencies
src/oak_info/      # prints device info (oak-info)
src/oak_uvc/       # exposes the camera as a USB webcam (oak-uvc)
AGENTS.md          # guidelines for AI agents and contributors
```

## Contributing

See [AGENTS.md](AGENTS.md): add tests, keep code simple and well named, follow Python best practices.
