"""Display utilities for regulated content and broker responses."""

from __future__ import annotations

import json
import sys


def handle_regulated_content(params: dict) -> str:
    """Display regulated content verbatim and collect user response.

    Returns a JSON string for the tool result sent back to Claude.
    """
    action_type = params.get("action_type", "notice")
    content = params.get("content", "")
    response_options = params.get("response_options", "acknowledge")

    # Display in a distinctive box
    width = 60
    print(f"\n{'=' * width}", file=sys.stderr)
    print(f"  IMPORTANT — {action_type.upper()}", file=sys.stderr)
    print(f"{'=' * width}", file=sys.stderr)
    print(content, file=sys.stderr)
    print(f"{'=' * width}", file=sys.stderr)

    if response_options == "acknowledge":
        input("\nPress Enter to acknowledge: ")
        return json.dumps({"user_response": "acknowledged", "displayed_verbatim": True})

    elif response_options == "grant or refuse":
        while True:
            choice = input("\nDo you consent? (yes/no): ").strip().lower()
            if choice in ("yes", "y"):
                return json.dumps({"user_response": "granted", "displayed_verbatim": True})
            if choice in ("no", "n"):
                return json.dumps({"user_response": "refused", "displayed_verbatim": True})
            print("Please answer yes or no.", file=sys.stderr)

    elif response_options == "affirm or deny":
        while True:
            choice = input("\nDo you confirm this declaration? (yes/no): ").strip().lower()
            if choice in ("yes", "y"):
                return json.dumps({"user_response": "affirmed", "displayed_verbatim": True})
            if choice in ("no", "n"):
                return json.dumps({"user_response": "denied", "displayed_verbatim": True})
            print("Please answer yes or no.", file=sys.stderr)

    elif response_options == "authorise":
        while True:
            choice = input("\nDo you authorise this? (yes/no): ").strip().lower()
            if choice in ("yes", "y"):
                return json.dumps({"user_response": "authorised", "displayed_verbatim": True})
            if choice in ("no", "n"):
                return json.dumps({"user_response": "declined", "displayed_verbatim": True})
            print("Please answer yes or no.", file=sys.stderr)

    # CaseOutcome or unknown — no user response needed
    return json.dumps({"user_response": "none", "displayed_verbatim": True})
