import subprocess


def inject_text(text: str, target: str = "") -> None:
    cmd = ["tmux", "send-keys"]
    if target:
        cmd.extend(["-t", target])
    cmd.extend(["-l", text])
    subprocess.run(cmd, check=True)
