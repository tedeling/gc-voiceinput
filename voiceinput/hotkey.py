import asyncio
from collections.abc import Callable
from pathlib import Path

import evdev
from evdev import ecodes


def find_keyboard(device_path: str = "") -> evdev.InputDevice:
    if device_path:
        return evdev.InputDevice(device_path)

    candidates = []
    for path in sorted(evdev.list_devices()):
        dev = evdev.InputDevice(path)
        caps = dev.capabilities(verbose=False)
        if ecodes.EV_KEY not in caps:
            dev.close()
            continue
        keys = caps[ecodes.EV_KEY]
        if ecodes.KEY_A not in keys or ecodes.KEY_Z not in keys:
            dev.close()
            continue
        candidates.append(dev)

    if not candidates:
        raise RuntimeError("No keyboard device found. Specify --device-path manually.")

    def score(d: evdev.InputDevice) -> tuple[int, int, int]:
        # Penalize virtual uinput devices (solaar, etc.)
        is_virtual = "uinput" in (d.phys or "") or "solaar" in d.name.lower()
        name_lower = d.name.lower()
        has_kb = "keyboard" in name_lower or "kbd" in name_lower
        key_count = len(d.capabilities(verbose=False).get(ecodes.EV_KEY, []))
        return (0 if is_virtual else 1, 1 if has_kb else 0, key_count)

    best = max(candidates, key=score)
    for d in candidates:
        if d is not best:
            d.close()

    if best is None:
        raise RuntimeError("No keyboard device found. Specify --device-path manually.")
    return best


async def listen(
    device: evdev.InputDevice,
    key_codes: dict[int, bool],
    on_press: Callable[[], None],
    on_release: Callable[[bool], None],
) -> None:
    """Listen for hotkeys. key_codes maps evdev key code -> auto_submit flag."""
    active_key: int | None = None
    async for event in device.async_read_loop():
        if event.type != ecodes.EV_KEY or event.code not in key_codes:
            continue
        if event.value == 1 and active_key is None:  # key down
            active_key = event.code
            on_press()
        elif event.value == 0 and event.code == active_key:  # key up
            active_key = None
            on_release(key_codes[event.code])
