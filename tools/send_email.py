#!/usr/bin/env python3
"""
Send an email with a file attachment using macOS Mail.app via AppleScript.

Usage: python3 tools/send_email.py "recipient@email.com" "/path/to/file.pdf" "Subject" "Body message"
"""

import os
import subprocess
import sys


def send_email(to_address, file_path, subject, body=""):
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        print(f"ERROR: File not found: {abs_path}")
        sys.exit(1)

    # Escape quotes for AppleScript
    subject_safe = subject.replace('"', '\\"')
    body_safe = body.replace('"', '\\"')

    applescript = f'''
    tell application "Mail"
        set newMessage to make new outgoing message with properties {{subject:"{subject_safe}", content:"{body_safe}", visible:false}}
        tell newMessage
            make new to recipient at end of to recipients with properties {{address:"{to_address}"}}
            make new attachment with properties {{file name:(POSIX file "{abs_path}" as alias)}} at after the last paragraph
        end tell
        send newMessage
    end tell
    '''

    print(f"Sending email to {to_address} with attachment: {abs_path}")
    result = subprocess.run(
        ["osascript", "-e", applescript],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"ERROR: AppleScript failed: {result.stderr}")
        sys.exit(1)

    print(f"SUCCESS: Email sent to {to_address}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print('Usage: python3 tools/send_email.py "email" "/path/to/file.pdf" "Subject" ["Body"]')
        sys.exit(1)

    email = sys.argv[1]
    fpath = sys.argv[2]
    subj = sys.argv[3]
    body_text = sys.argv[4] if len(sys.argv) > 4 else ""
    send_email(email, fpath, subj, body_text)
