# oak-app

Base project for building on top of a Luxonis OAK-D camera using [DepthAI](https://docs.luxonis.com/software-v3/) v3. For now it only imports the library, connects to the camera, and prints the device info.

## Requirements

| Tool | Version |
| --- | --- |
| Python | 3.10 or newer (developed on 3.14.7) |
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
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Check that the install worked:

```sh
python -c "import depthai; print(depthai.__version__)"
```

## Run

Plug in the OAK-D, then:

```sh
oak-app
# or
python -m oak_app.main
```

It prints the DepthAI version, the device name and ID, the USB speed, and the connected cameras.

## Test

```sh
pytest
```

## Project layout

```
pyproject.toml     # package metadata and dependencies
src/oak_app/       # application code
AGENTS.md          # guidelines for AI agents and contributors
```

## Contributing

See [AGENTS.md](AGENTS.md): add tests, keep code simple and well named, follow Python best practices.
