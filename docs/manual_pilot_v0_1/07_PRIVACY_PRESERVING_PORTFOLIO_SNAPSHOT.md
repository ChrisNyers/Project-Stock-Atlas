# 07 — Privacy-Preserving Portfolio Snapshot

## Purpose

This file defines how the human operator's current portfolio context is
captured for use in `03_CAPITAL_COMPARISON_FRAMEWORK.md` ("Improve what we
own") and `04_HUMAN_OPERATING_LOOP.md`, without any brokerage integration
and with data exposure minimized.

## Core Rule

> **Portfolio inputs are user-controlled and privacy-minimized. No
> brokerage credentials or direct brokerage integration.**

Pilot 1 does not connect to any brokerage API, does not store or request
brokerage login credentials, OAuth tokens, or account numbers, and does not
poll or sync any external account automatically. All portfolio context
enters this pilot exclusively through manual, user-controlled input.

## What Is Captured

A Portfolio Snapshot is a **manually entered, point-in-time** record
containing only what the human operator chooses to disclose, at the
minimum level of detail needed to support the comparison framework:

- Ticker and approximate position size category (e.g. "core holding,"
  "small position," "watch-only, no position") rather than exact share
  counts or dollar values, unless the human operator explicitly chooses to
  record exact figures for their own reference.
- Approximate cost basis or holding period, only if the human judges it
  relevant to a specific comparison (e.g. tax-aware "Improve what we own"
  reasoning).
- Cash position category (e.g. "meaningful dry powder available" vs.
  "fully invested"), not necessarily an exact balance.

## What Is Never Captured

- Brokerage usernames, passwords, API keys, or OAuth tokens of any kind.
- Account numbers, routing numbers, or any other account-identifying
  credential.
- Any automated feed, scrape, or sync from a brokerage or custodian.
- Data from any third party about the operator's holdings — this snapshot
  is self-reported by the human operator only.

## Snapshot Format

A Portfolio Snapshot is a dated, manually written note, not a database
record or a live-synced object:

```
PORTFOLIO SNAPSHOT

Date:               [YYYY-MM-DD]
Recorded by:        [human name / identifier]

Holdings (self-reported, approximate):
  [TICKER] — [position size category] — [notes, optional]
  ...

Cash position (self-reported, approximate):
  [category, e.g. "meaningful dry powder" / "fully invested" / "specific
  amount if operator chooses to disclose it"]

Notes:
  [any context relevant to Improve/Compare/Test/Move reasoning in
  03_CAPITAL_COMPARISON_FRAMEWORK.md]
```

## Storage

Portfolio Snapshots, when created, should be stored as plain-text or
markdown files under the human operator's own control (e.g. a local,
non-committed directory, or a location the operator designates). This
documentation package does not itself create, store, or commit any
snapshot containing real portfolio data — this file defines the format
and rules only.

## Relationship to Decisions

A Portfolio Snapshot informs the "Improve what we own" and "Compare what we
could own" modes of `03_CAPITAL_COMPARISON_FRAMEWORK.md`. It is context, not
authorization. Per that framework, no Portfolio Snapshot, on its own,
authorizes a Portfolio Action.
