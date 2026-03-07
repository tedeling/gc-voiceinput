# voiceinput

Voice-to-text input for Claude Code. Hold a push-to-talk key, speak, and the transcribed text is injected into your Claude Code session. Uses Groq's Whisper API by default for fast, accurate transcription.

## Prerequisites

- Linux with Python 3.10+
- `libportaudio2` for audio capture
- `tmux` for terminal multiplexing
- A [Groq API key](https://console.groq.com/keys) (free)

```bash
sudo apt install libportaudio2 tmux
```

## Installation

```bash
cd voiceinput
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Input device access

Your user needs read access to `/dev/input/event*` devices:

```bash
sudo usermod -aG input $USER
```

Log out and back in for this to take effect. In the meantime, `newgrp input` works in the current shell.

### Groq API key

```bash
export GROQ_API_KEY="your-key-here"
```

Add this to your `~/.bashrc` to persist it.

## Quick start

The easiest way to use voiceinput is the `claude-voice` wrapper:

```bash
# Optional: symlink for convenience
sudo ln -s "$(pwd)/claude-voice.sh" /usr/local/bin/claude-voice

# Start Claude Code with voice input
claude-voice
```

This starts Claude Code in a tmux session with a shared voiceinput daemon running in the background. Just hold the hotkey and speak.

### Hotkeys

| Key | Action |
|-----|--------|
| **F4** | Record and type text into Claude Code |
| **F5** | Record, type text, and auto-submit (sends Enter) |

## Multiple instances

Run `claude-voice` multiple times to open multiple Claude Code sessions. A single voiceinput daemon is shared across all of them. Text is injected into whichever session you most recently interacted with.

```bash
# Terminal 1
claude-voice

# Terminal 2
claude-voice
```

Focus the Claude session you want, hold F5, speak — text goes there.

## Manual setup (without wrapper)

If you prefer to manage tmux yourself:

```bash
# In the Claude Code pane, get the pane target:
tmux display-message -p '#{session_name}:#{window_index}.#{pane_index}'

# In another pane, run voiceinput with that target:
source /path/to/voiceinput/.venv/bin/activate
voiceinput --target 0:0.0
```

## Options

| Flag | Env var | Default | Description |
|------|---------|---------|-------------|
| `--hotkey` | `VOICEINPUT_HOTKEY` | `KEY_F4` | evdev key name for type-only |
| `--submit-hotkey` | `VOICEINPUT_SUBMIT_HOTKEY` | `KEY_F5` | evdev key name for type+submit |
| `--target` | `VOICEINPUT_TARGET` | (auto-detect) | tmux pane target |
| `--backend` | `VOICEINPUT_BACKEND` | `groq` | `groq` or `local` |
| `--groq-api-key` | `GROQ_API_KEY` | | Groq API key |
| `--model-size` | `VOICEINPUT_MODEL_SIZE` | `base.en` | whisper model (local backend) |
| `--silence-threshold` | `VOICEINPUT_SILENCE_THRESHOLD` | `10` | RMS silence threshold |
| `--sample-rate` | `VOICEINPUT_SAMPLE_RATE` | `16000` | audio sample rate |
| `--device-path` | `VOICEINPUT_DEVICE_PATH` | (auto-detect) | evdev input device path |
| `--instance` | | | named routing, e.g. `--instance p210=session:0.0` |

### Local transcription

To use local faster-whisper instead of Groq:

```bash
pip install -e ".[local]"
voiceinput --backend local
```

## Troubleshooting

**"No keyboard device found"** — You're not in the `input` group or the device isn't detected. Specify manually with `--device-path /dev/input/eventN`. List devices:
```bash
python3 -c "import evdev; [print(evdev.InputDevice(d).path, evdev.InputDevice(d).name) for d in evdev.list_devices()]"
```

**"(silence, skipped)" on every recording** — Your mic may have very low levels. Lower the threshold with `--silence-threshold 2` or check your audio device with `pactl list sources short`.

**Wrong language detected** — The Groq backend is set to English by default. For other languages, edit the `language` parameter in `voiceinput/transcribe.py`.

**"No active tmux session found"** — voiceinput can't find a tmux client to send text to. Make sure Claude Code is running inside tmux.
