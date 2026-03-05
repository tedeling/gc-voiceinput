import subprocess


def inject_text(text: str, target: str = "", submit: bool = False) -> None:
    cmd = ["tmux", "send-keys"]
    if target:
        cmd.extend(["-t", target])
    cmd.extend(["-l", text])
    subprocess.run(cmd, check=True)

    if submit:
        cmd = ["tmux", "send-keys"]
        if target:
            cmd.extend(["-t", target])
        cmd.append("Enter")
        subprocess.run(cmd, check=True)
