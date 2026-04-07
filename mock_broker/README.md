# Mock Credit Broker

A mock Credit Broker server implementing the [Agentic Credit Broking Protocol](../docs/whitepaper.md). It simulates a consumer credit (personal loan) broking journey, providing a working API for User Agent development and testing.

## Quick start

```bash
cd mock_broker
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/mock-broker
```

The server starts on `http://localhost:8000`. Interactive API documentation is available at `/docs`.

### Running tests

```bash
.venv/bin/pytest tests/ -v
```

### CLI options

```bash
.venv/bin/mock-broker --host 127.0.0.1 --port 9000 --reload
```

## API endpoints

### Protocol operations

| Method | Path | Operation | Description |
|--------|------|-----------|-------------|
| POST | `/cases` | Open Case | Initiate a new broking engagement |
| POST | `/cases/{id}/provide` | Provide | Submit financial facts, attributes, or goals |
| GET | `/cases/{id}/state` | Get State | Query current case state (no side effects) |
| POST | `/cases/{id}/select` | Select | Commit to a plan or offer |
| POST | `/cases/{id}/resolve` | Resolve Action | Respond to a pending broker action |
| POST | `/cases/{id}/withdraw` | Withdraw | End the engagement |

All mutating operations return `{ "events": [...], "pending_action": ... }`.

### Vocabulary resources

| Method | Path | Description |
|--------|------|-------------|
| GET | `/vocabulary/fact-types` | Financial fact types the broker recognises |
| GET | `/vocabulary/attribute-types` | Party attribute types the broker accepts |
| GET | `/vocabulary/goal-types` | Financial goal types the broker supports |

## Scripted journey

The mock follows a predetermined personal loan broking scenario. Each case progresses through the same stages:

1. **Open Case** — broker requests income, employment, and debt information
2. **Provide** data — broker discloses its FCA-regulated identity and service basis
3. **Acknowledge** disclosure — broker requests consent for a soft credit search
4. **Grant** consent — broker generates loan plans with suitability assessments
5. **Select** a plan — broker sources lender offers and discloses regulated product information (APR, total repayable, fees)
6. **Acknowledge** offer disclosure — user may now select an offer
7. **Select** an offer — broker requests a declaration that information is true and complete
8. **Affirm** declaration — broker issues an instruction to proceed to the lender
9. **Authorise** instruction — case is transferred; broker issues a Case Outcome

### Blocking rules

When a broker action is pending, only `Resolve Action` is permitted (plus `Provide` when the pending action is an Information Request). `Get State` is always available. Blocked operations return HTTP 409.

## Evidence model

Every operation is recorded in a structured evidence log attached to the case. Each entry captures the operation type, a timestamp, the structured data involved, and any transcript provided by the User Agent. The evidence log is returned as part of the `Get State` response.

Transcripts are optional and can be submitted alongside `Provide` and `Resolve Action` requests via the `transcript` field. They are stored opaquely for audit purposes, as described in the protocol specification.

## Scope and limitations

This is a mock implementation intended for development and testing. The following protocol features are **not implemented**:

- **Trust model** — no User Agent authentication, progressive trust calibration, or broker-controlled surface fallback. All operations are accepted regardless of the calling agent's identity.
- **Benchmarking** — no compliance evaluation or certification registry.
- **Replay** — no complaint investigation replay capability.
- **Revised events** — the `PlansRevised` and `OffersRevised` event types are defined but not emitted, as the scripted journey does not include plan or offer revision scenarios.
- **Multiple journeys** — only the consumer credit (personal loan) scenario is supported. The engine is stage-based; extending it with additional scenarios (e.g. mortgage, credit card) would require additional step definitions.

These features are described in the [protocol whitepaper](../docs/whitepaper.md) and are candidates for future development.

## Licence

This code is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

The protocol specification in the parent repository is licensed under CC BY-SA 4.0 by Clear Score Technology Limited.
