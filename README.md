# Inference Cost Attribution Engine (ICAE)

## One-sentence value proposition

ICAE provides audit-grade cost attribution for AI intelligence execution, making every unit of cost economically legible and traceable.

## Overview

The Inference Cost Attribution Engine (ICAE) is a deterministic, auditable system that attributes costs to individual actions in AI inference workflows. It serves as the ground-truth ledger for intelligence execution costs, answering precisely "how much did this intelligence cost, and why?"

ICAE operates on the principle that if a cost cannot be attributed, it is treated as a system failure. The system produces explicit, itemized cost events that are versioned, replayable, and aggregatable without loss of provenance.

## Architecture diagram

<pre>
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────────┐
│   External      │    │  Cost Adapters   │    │   Pricing Models     │
│   Systems       │───▶│                  │───▶│                      │
│ (DIO, ZT-AAS)   │    │  - Execution     │    │  - Versioned         │
│                 │    │    Transcript    │    │    Pricing Data      │
└─────────────────┘    │  - Tool Logs     │    │  - Tiered Pricing    │
                       │  - API Metadata  │    │  - Fixed Fees        │
                       └──────────────────┘    └──────────────────────┘
                                 │                        │ 
                                 ▼                        ▼ 
                       ┌──────────────────┐    ┌──────────────────────┐
                       │   Cost Events    │    │   Cost Ledger        │
                       │                  │    │                      │
                       │  - Event ID      │    │  - Append-only       │
                       │  - Timestamp     │    │  - Tamper-evident    │
                       │  - Execution ID  │    │  - Deterministic     │
                       │  - Component     │    │  - Hashable          │
                       │  - Action        │    │  - Replayable        │
                       │  - Unit Cost     │    │                      │
                       │  - Quantity      │    └──────────────────────┘
                       │  - Total Cost    │              │ 
                       │  - Currency      │              ▼ 
                       │  - Cost Source   │    ┌──────────────────────┐
                       │  - Pricing Ver.  │    │  Replay Engine       │
                       │  - Base Unit     │    │                      │
                       │  - Metadata      │    │  - Cost Reproduction │
                       └──────────────────┘    │  - Integrity Check   │
                                               │  - Delta Analysis    │
                                               └──────────────────────┘
</pre>

## Core Components

### 1. Cost Event Model
- Immutable data structure representing a single cost attribution
- Enforces deterministic, explicit cost recording
- Includes full provenance metadata for auditability

### 2. Pricing Models
- Versioned, immutable pricing definitions
- Supports token-based, request-based, and time-based pricing
- Handles tiered pricing structures with fixed fees

### 3. Cost Ledger
- Append-only, tamper-evident storage of cost events
- Deterministic ordering and hashing for verification
- Supports per-run, per-component, and aggregate views

### 4. Replay Engine
- Recomputes costs using current pricing models
- Verifies ledger integrity through deterministic replay
- Identifies discrepancies between original and replayed costs

### 5. Adapters
- Convert external data formats into cost events
- Explicit, non-invasive integration points
- Supports execution transcripts, tool logs, and API metadata

## Usage

ICAE is designed for integration into AI systems that require precise cost attribution. The system consumes:

1. **Execution Transcripts** - From orchestration systems like DIO
2. **Agent Action Logs** - From systems like ZT-AAS  
3. **Tool Invocation Metadata** - For tracking tool call costs
4. **Pricing Tables** - Versioned pricing data for cost calculation

The system produces:
- Deterministic cost ledgers with full attribution
- Replayable cost computations
- Audit-ready cost events with provenance

## Design Principles

### Economic Legibility
Every cost must be traceable to its source. No aggregation is allowed at the event level.

### Determinism and Replayability  
All cost calculations are deterministic and can be reproduced exactly given:
- Execution transcript
- Pricing version snapshot
- System state

### Auditability Over Convenience
The system prioritizes transparency and verifiability over convenience features.

### Explicit Failure Semantics
All failure modes are explicitly modeled and recorded as first-class events.

## Requirements

### Must Have
- Cost event model with full provenance
- Versioned pricing models
- Append-only cost ledger
- Replay and verification capabilities
- Adapter-based integration system

### Non-Goals
ICAE is **not**:
- A billing platform
- A cost estimator
- A forecasting engine  
- A vendor dashboard replacement
- An optimization engine

It exists to produce economic truth, not recommendations.

## Demonstration Scenarios

1. **Full Cost Attribution**: Single inference with model invocation and tool calls
2. **Retry Impact**: Cost analysis of failed requests and retries
3. **Cache Economics**: Comparison of cache hits vs misses
4. **Multi-Component Costs**: Breakdown of costs across models, tools, and APIs
5. **Cost Replay**: Verification that original costs can be reproduced exactly
6. **Pricing Version Changes**: Impact analysis when pricing changes

These examples demonstrate that ICAE produces numbers that are real, verifiable, and economically meaningful - suitable for CFO or CTO review.