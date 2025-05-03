#!/usr/bin/env python3
import subprocess
import shlex

# Path to your shell script
CLAUDE_SCRIPT = "./send_to_claude.sh"

def send_to_claude(message: str) -> None:
    """
    Sends `message` to Claude by invoking the shell script.
    Does nothing if `message` is empty.
    """
    if not message:
        return

    try:
        # You can switch to run() if you want to wait for completion
        subprocess.Popen([CLAUDE_SCRIPT, message])
    except FileNotFoundError:
        print(f"Error: script not found at {CLAUDE_SCRIPT}")
    except Exception as e:
        print(f"Error sending to Claude: {e}")

if __name__ == "__main__":
    # Example: send "hello" when run directly
    send_to_claude("hello")
