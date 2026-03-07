import subprocess


def _get_active_pane() -> str:
    """Get the active pane of the most recently used non-daemon tmux client."""
    result = subprocess.run(
        ["tmux", "list-clients", "-F", "#{client_activity} #{session_name}"],
        capture_output=True, text=True, check=True,
    )
    best_session = None
    best_time = -1
    for line in result.stdout.strip().splitlines():
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        activity, session = parts
        if "voiceinput" in session:
            continue
        t = int(activity)
        if t > best_time:
            best_time = t
            best_session = session

    if not best_session:
        raise RuntimeError("No active tmux session found.")

    result = subprocess.run(
        ["tmux", "display-message", "-t", best_session, "-p",
         "#{session_name}:#{window_index}.#{pane_index}"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def inject_text(text: str, target: str = "", submit: bool = False) -> None:
    target = target or _get_active_pane()

    cmd = ["tmux", "send-keys", "-t", target, "-l", text]
    subprocess.run(cmd, check=True)

    if submit:
        subprocess.run(["tmux", "send-keys", "-t", target, "Enter"], check=True)
