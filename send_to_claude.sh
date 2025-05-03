#!/usr/bin/env bash
INPUT="$1"
# only run if INPUT is not empty
if [[ -n "$INPUT" ]]; then
  osascript <<EOF
tell application "Claude" to activate
delay 0.1
tell application "System Events"
  keystroke "$INPUT"
  keystroke return
end tell
# tell application "iTerm" to activate

EOF
fi