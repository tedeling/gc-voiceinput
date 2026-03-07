#!/bin/bash
tmux display-message -p '#{session_name}:#{window_index}.#{pane_index}'
