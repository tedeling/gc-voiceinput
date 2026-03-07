#!/bin/bash
# Wrapper that starts Claude Code in tmux + a single shared voiceinput daemon
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
SESSION="claude-voice-$$"

# Start voiceinput daemon if not already running
if ! pgrep -f "voiceinput" > /dev/null 2>&1; then
    tmux new-session -d -s voiceinput-daemon
    tmux send-keys -t voiceinput-daemon "source '$SCRIPT_DIR/.venv/bin/activate' && voiceinput" Enter
fi

# Start Claude Code in a new tmux session
tmux new-session -d -s "$SESSION" -x "$(tput cols)" -y "$(tput lines)"
tmux send-keys -t "$SESSION" "claude $*" Enter
tmux attach -t "$SESSION"
