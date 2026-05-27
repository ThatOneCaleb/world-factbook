#!/usr/bin/env python3
"""
Send a file via iMessage using macOS AppleScript.

Usage: python3 tools/send_imessage.py "6162369210" "/path/to/file.pdf"
"""

import os
import subprocess
import sys


def send_imessage(phone_number, file_path, message=""):
    """Send a file attachment via iMessage."""
    # Normalize phone number
    digits = "".join(c for c in phone_number if c.isdigit())
    if len(digits) == 10:
        digits = "1" + digits
    formatted = f"+{digits}"

    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        print(f"ERROR: File not found: {abs_path}")
        sys.exit(1)

    # Build AppleScript to send file via iMessage
    applescript = f'''
    tell application "Messages"
        set targetService to 1st account whose service type = iMessage
        set targetBuddy to participant "{formatted}" of targetService
        send POSIX file "{abs_path}" to targetBuddy
    end tell
    '''

    if message:
        applescript = f'''
        tell application "Messages"
            set targetService to 1st account whose service type = iMessage
            set targetBuddy to participant "{formatted}" of targetService
            send "{message}" to targetBuddy
            delay 1
            send POSIX file "{abs_path}" to targetBuddy
        end tell
        '''

    print(f"Sending to {formatted}: {abs_path}")
    result = subprocess.run(
        ["osascript", "-e", applescript],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"ERROR: AppleScript failed: {result.stderr}")
        sys.exit(1)

    print(f"SUCCESS: File sent to {formatted} via iMessage")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python3 tools/send_imessage.py "phone_number" "/path/to/file.pdf" ["optional message"]')
        sys.exit(1)

    phone = sys.argv[1]
    fpath = sys.argv[2]
    msg = sys.argv[3] if len(sys.argv) > 3 else ""
    send_imessage(phone, fpath, msg)
