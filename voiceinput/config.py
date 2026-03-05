import argparse
import os
from dataclasses import dataclass, field


@dataclass
class Config:
    hotkey: str = "KEY_F4"
    submit_hotkey: str = "KEY_F5"
    target: str = ""
    model_size: str = "base.en"
    silence_threshold: float = 10.0
    sample_rate: int = 16000
    device_path: str = ""
    backend: str = "groq"  # "groq" or "local"
    groq_api_key: str = ""
    instances: dict[str, str] = None  # name -> tmux target

    def __post_init__(self):
        if self.instances is None:
            self.instances = {}

    @classmethod
    def load(cls, argv: list[str] | None = None) -> "Config":
        parser = argparse.ArgumentParser(description="Voice input for Claude Code")
        parser.add_argument("--hotkey", default=None, help="evdev key name for type-only (default: KEY_F4)")
        parser.add_argument("--submit-hotkey", default=None, help="evdev key name for type+submit (default: KEY_F5)")
        parser.add_argument("--target", default=None, help="target identifier (default: focused window)")
        parser.add_argument("--model-size", default=None, help="whisper model size (default: base.en)")
        parser.add_argument("--silence-threshold", type=float, default=None, help="RMS silence threshold (default: 10)")
        parser.add_argument("--sample-rate", type=int, default=None, help="audio sample rate (default: 16000)")
        parser.add_argument("--device-path", default=None, help="evdev input device path (default: auto-detect)")
        parser.add_argument("--backend", default=None, choices=["groq", "local"], help="transcription backend (default: groq)")
        parser.add_argument("--groq-api-key", default=None, help="Groq API key (default: $GROQ_API_KEY)")
        parser.add_argument("--instance", action="append", metavar="NAME=TARGET",
                            help="named instance, e.g. --instance p210=mysession:0.1 (repeatable)")
        args = parser.parse_args(argv)

        cfg = cls()
        for fname in ("hotkey", "submit_hotkey", "target", "model_size", "silence_threshold", "sample_rate", "device_path", "backend", "groq_api_key"):
            cli_val = getattr(args, fname.replace("-", "_"), None)
            if cli_val is not None:
                setattr(cfg, fname, cli_val)
            else:
                env_key = f"VOICEINPUT_{fname.upper()}"
                if fname == "groq_api_key":
                    env_key = os.environ.get("VOICEINPUT_GROQ_API_KEY") or os.environ.get("GROQ_API_KEY", "")
                    if env_key:
                        cfg.groq_api_key = env_key
                    continue
                env_val = os.environ.get(env_key)
                if env_val is not None:
                    ftype = type(getattr(cfg, fname))
                    setattr(cfg, fname, ftype(env_val))
        if args.instance:
            for item in args.instance:
                name, _, target = item.partition("=")
                if name and target:
                    cfg.instances[name.lower()] = target
        return cfg
