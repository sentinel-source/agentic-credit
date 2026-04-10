"""Main conversation loop for the User Agent CLI."""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid

import anthropic

from .client import BrokerClient
from .display import handle_regulated_content
from .prompts import build_system_prompt
from .tools import TOOL_DEFINITIONS, SessionState, execute_tool


def main() -> None:
    parser = argparse.ArgumentParser(description="AI-powered User Agent for credit broking")
    parser.add_argument("--broker-url", default="http://localhost:8000", help="Broker API URL")
    parser.add_argument("--model", default="claude-sonnet-4-20250514", help="Claude model to use")
    parser.add_argument("--user-id", default=None, help="User ID for the case (default: generated)")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is required.", file=sys.stderr)
        sys.exit(1)

    user_id = args.user_id or uuid.uuid4().hex[:12]

    # Connect to broker and load vocabulary
    broker = BrokerClient(base_url=args.broker_url)
    try:
        vocabulary = broker.load_vocabulary()
    except Exception as e:
        print(f"Error: Could not connect to broker at {args.broker_url}: {e}", file=sys.stderr)
        sys.exit(1)

    system_prompt = build_system_prompt(vocabulary)
    claude = anthropic.Anthropic(api_key=api_key)

    session = SessionState(user_id=user_id)
    messages: list[dict] = []

    print("Credit Broking Assistant")
    print("-" * 40)
    print(f"Connected to broker at {args.broker_url}")
    print(f"User ID: {user_id}")
    print("Type 'quit' to exit.\n")

    try:
        _conversation_loop(claude, broker, session, messages, system_prompt, args.model)
    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        if session.case_id and not session.case_complete:
            print("Withdrawing from case...")
            try:
                broker.withdraw(session.case_id)
            except Exception:
                pass
    finally:
        broker.close()


def _conversation_loop(
    claude: anthropic.Anthropic,
    broker: BrokerClient,
    session: SessionState,
    messages: list[dict],
    system_prompt: str,
    model: str,
) -> None:
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except EOFError:
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            if session.case_id and not session.case_complete:
                print("\nWithdrawing from case...")
                try:
                    broker.withdraw(session.case_id)
                except Exception:
                    pass
            print("Goodbye!")
            break

        session.transcript.add_user(user_input)
        messages.append({"role": "user", "content": user_input})

        # Claude turn — may involve multiple rounds of tool calls
        _run_claude_turn(claude, broker, session, messages, system_prompt, model)

        if session.case_complete:
            print("\nThe broking process is complete. Type 'quit' to exit or continue chatting.")


def _run_claude_turn(
    claude: anthropic.Anthropic,
    broker: BrokerClient,
    session: SessionState,
    messages: list[dict],
    system_prompt: str,
    model: str,
) -> None:
    while True:
        response = claude.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        assistant_content = response.content
        messages.append({"role": "assistant", "content": assistant_content})

        if response.stop_reason == "end_turn":
            for block in assistant_content:
                if hasattr(block, "text") and block.text:
                    print(f"\nAssistant: {block.text}")
                    session.transcript.add_assistant(block.text)
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in assistant_content:
                if hasattr(block, "text") and block.text:
                    print(f"\nAssistant: {block.text}")
                    session.transcript.add_assistant(block.text)

                if block.type == "tool_use":
                    if block.name == "present_regulated_content":
                        # Intercept: display verbatim and get user response
                        result_str = handle_regulated_content(block.input)
                        # Record in transcript
                        result_data = json.loads(result_str)
                        session.transcript.add_regulated_display(
                            block.input.get("action_type", ""),
                            block.input.get("content", ""),
                            result_data.get("user_response", ""),
                        )
                    else:
                        result_str = execute_tool(block.name, block.input, broker, session)

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_str,
                    })

            messages.append({"role": "user", "content": tool_results})
            # Loop back to call Claude again with tool results
            continue

        # Unexpected stop reason
        break


if __name__ == "__main__":
    main()
