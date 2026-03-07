#!/bin/bash
# Wrapper that starts Claude Code + voiceinput together in tmux
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SESSION="claude-voice-$$"

tmux new-session -d -s "$SESSION" -x "$(tput cols)" -y "$(tput lines)"

# Main pane: Claude Code (takes most of the space)
tmux send-keys -t "$SESSION" "claude $*" Enter

# Small bottom pane for voiceinput
tmux split-window -t "$SESSION" -v -l 5
tmux send-keys -t "$SESSION" "source '$SCRIPT_DIR/.venv/bin/activate' && voiceinput --target '$SESSION:0.0'" Enter

# Focus the Claude pane
tmux select-pane -t "$SESSION:0.0"

tmux attach -t "$SESSION"
