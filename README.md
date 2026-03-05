# voiceinput

Voice-to-text input for Claude Code. Hold a push-to-talk key, speak, and the transcribed text is injected into your tmux pane. Fully offline using faster-whisper.

## Installation

```bash
pip install -e .
```

The first run will download the whisper model (~150MB for base.en).

## Input device access

Your user needs read access to `/dev/input/event*` devices. Add yourself to the `input` group:

```bash
sudo usermod -aG input $USER
```

Then log out and back in. Alternatively, create a udev rule:

```
# /etc/udev/rules.d/99-input.rules
KERNEL=="event*", SUBSYSTEM=="input", MODE="0660", GROUP="input"
```

## Usage

Run `voiceinput` in a separate terminal (or tmux pane) while Claude Code runs in another pane:

```bash
voiceinput
```

Hold **F4** (default), speak, release. The transcribed text appears in your active tmux pane.

### Options

| Flag | Env var | Default | Description |
|------|---------|---------|-------------|
| `--hotkey` | `VOICEINPUT_HOTKEY` | `KEY_F4` | evdev key name |
| `--tmux-target` | `VOICEINPUT_TMUX_TARGET` | (current pane) | tmux pane target |
| `--model-size` | `VOICEINPUT_MODEL_SIZE` | `base.en` | whisper model size |
| `--silence-threshold` | `VOICEINPUT_SILENCE_THRESHOLD` | `500` | RMS silence threshold |
| `--sample-rate` | `VOICEINPUT_SAMPLE_RATE` | `16000` | audio sample rate |
| `--device-path` | `VOICEINPUT_DEVICE_PATH` | (auto-detect) | evdev input device path |

## Troubleshooting

**"No keyboard device found"** — Specify `--device-path /dev/input/eventN` manually. List devices with `python -c "import evdev; [print(d) for d in evdev.list_devices()]"`.

**Audio not recording** — Check `pactl list sources short` to verify your mic is available. Use `VOICEINPUT_SAMPLE_RATE` if your mic doesn't support 16kHz.

**Text goes to wrong pane** — Use `--tmux-target` to specify the pane, e.g. `--tmux-target mysession:0.1`.
