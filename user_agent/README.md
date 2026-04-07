# User Agent

An AI-powered User Agent for the [Agentic Credit Broking Protocol](../docs/whitepaper.md). It mediates between a human user and a Credit Broker, translating natural conversation into structured protocol operations using Claude as the AI backbone.

## Quick start

### Prerequisites

- A running Credit Broker server (e.g. the [mock broker](../mock_broker/README.md) on `http://localhost:8000`)
- An Anthropic API key

### Installation

```bash
cd user_agent
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

### Running

```bash
export ANTHROPIC_API_KEY=your-key-here
.venv/bin/user-agent
```

### CLI options

```bash
.venv/bin/user-agent --broker-url http://localhost:8000 --model claude-sonnet-4-20250514 --user-id jane@example.com
```

| Flag | Default | Description |
|------|---------|-------------|
| `--broker-url` | `http://localhost:8000` | Broker API URL |
| `--model` | `claude-sonnet-4-20250514` | Claude model to use |
| `--user-id` | Generated UUID | User identifier for the case |

## How it works

1. On startup, the agent connects to the broker and fetches its vocabulary (fact types, attribute types, goal types)
2. The vocabulary is injected into Claude's system prompt alongside protocol rules
3. The user chats naturally about wanting a loan
4. Claude translates the conversation into protocol operations (Open Case, Provide, Select, etc.) using tool calls
5. Broker responses (events, plans, offers, actions) are interpreted by Claude and presented to the user
6. Regulated content (disclosures, consents, declarations, instructions) is displayed verbatim in visual boxes — Claude does not paraphrase or summarise it
7. The full conversation is recorded as a transcript and submitted to the broker for the evidence model

## Regulated content handling

The agent uses a hybrid approach for regulated broker actions:

- Claude identifies that a regulated action needs to be presented
- It calls a `present_regulated_content` tool, passing the verbatim content
- The CLI intercepts this and displays the content in a distinctive visual box
- The user responds directly (acknowledge, grant/refuse, affirm/deny, authorise)
- The response is passed back to Claude, which then resolves the action with the broker

This guarantees that regulated content is never altered by the AI while keeping Claude in the loop for flow management.

## Architecture

```
user_agent/
├── cli.py          # Conversation loop and entry point
├── client.py       # HTTP client for broker API
├── models.py       # Pydantic models (broker wire format)
├── tools.py        # Claude tool definitions and dispatch
├── prompts.py      # System prompt builder with vocabulary
├── transcript.py   # Conversation transcript accumulator
└── display.py      # Regulated content display
```

## Licence

This code is licensed under the Apache License 2.0. See the mock broker's [LICENSE](../mock_broker/LICENSE) for details.
