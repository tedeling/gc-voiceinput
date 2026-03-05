import asyncio
import signal
import sys
import termios
import tty

from evdev import ecodes

from voiceinput.audio import AudioRecorder
from voiceinput.config import Config
from voiceinput.hotkey import find_keyboard, listen
from voiceinput.inject import inject_text
from voiceinput.router import Router
from voiceinput.transcribe import create_transcriber


def main() -> None:
    cfg = Config.load()

    print(f"Loading transcriber (backend={cfg.backend})...", flush=True)
    transcriber = create_transcriber(cfg.backend, cfg.model_size, cfg.groq_api_key)
    print("Ready.", flush=True)

    recorder = AudioRecorder(
        sample_rate=cfg.sample_rate,
        silence_threshold=cfg.silence_threshold,
    )

    key_codes = {}
    for name in (cfg.hotkey, cfg.submit_hotkey):
        code = getattr(ecodes, name, None)
        if code is None:
            print(f"Unknown key: {name}", file=sys.stderr)
            sys.exit(1)
        key_codes[code] = (name == cfg.submit_hotkey)

    device = find_keyboard(cfg.device_path)
    print(f"Using input device: {device.name} ({device.path})", flush=True)
    print(f"Type-only: {cfg.hotkey} | Type+Submit: {cfg.submit_hotkey}", flush=True)
    router = Router(cfg.instances)
    if cfg.target:
        print(f"Target: {cfg.target}", flush=True)
    if cfg.instances:
        print(f"Instances: {', '.join(cfg.instances.keys())}", flush=True)
    print("Ready. Hold the hotkey and speak.", flush=True)

    def on_press() -> None:
        print("Recording...", flush=True)
        recorder.start()

    def on_release(submit: bool) -> None:
        audio = recorder.stop()
        if audio is None:
            print("(silence, skipped)", flush=True)
            return

        print("Transcribing...", flush=True)
        text = transcriber.transcribe(audio)
        if text is None:
            print("(no speech detected)", flush=True)
            return

        target, routed_text = router.route(text)
        target = target or cfg.target
        if target != cfg.target and target:
            print(f"> [{target}] {routed_text}", flush=True)
        else:
            routed_text = text
            print(f"> {text}", flush=True)
        inject_text(routed_text, target, submit=submit)

    # Suppress terminal escape codes from F-keys by disabling input echo
    old_tty = None
    if sys.stdin.isatty():
        fd = sys.stdin.fileno()
        old_tty = termios.tcgetattr(fd)
        tty.setcbreak(fd)

    loop = asyncio.new_event_loop()

    def shutdown() -> None:
        for task in asyncio.all_tasks(loop):
            task.cancel()

    loop.add_signal_handler(signal.SIGINT, shutdown)
    loop.add_signal_handler(signal.SIGTERM, shutdown)

    try:
        loop.run_until_complete(listen(device, key_codes, on_press, on_release))
    except asyncio.CancelledError:
        pass
    finally:
        device.close()
        if old_tty is not None:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_tty)
        print("\nStopped.", flush=True)


if __name__ == "__main__":
    main()
