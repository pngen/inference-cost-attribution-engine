#!/usr/bin/env python3
"""
Inference Cost Attribution Engine (ICAE) - Main Entry Point

This module demonstrates the core functionality of ICAE by showing:
1. Creating cost events
2. Building a ledger
3. Replaying costs
4. Verifying integrity

Usage:
    python src/main.py
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from src.models.cost_event import CostEvent
from src.models.pricing import PricingModel, PricingTier
from src.ledger.ledger import CostLedger
from src.replay.replay_engine import ReplayEngine
from src.adapters.adapter import ExecutionTranscriptAdapter

def create_sample_pricing_models() -> Dict[str, PricingModel]:
    """Create sample pricing models for demonstration."""
    
    # Sample token-based pricing model with tiers
    token_pricing = PricingModel(
        id=uuid.uuid4(),
        version="v1.0.0",
        component="gpt-4",
        pricing_type="token",
        base_unit="token",
        tiers=[
            PricingTier(min_quantity=0, max_quantity=10000, unit_cost=0.03),
            PricingTier(min_quantity=10000, max_quantity=None, unit_cost=0.02)
        ]
    )
    
    # Sample fixed fee model
    request_pricing = PricingModel(
        id=uuid.uuid4(),
        version="v1.0.0",
        component="external_api",
        pricing_type="request",
        base_unit="request",
        tiers=[],
        fixed_fee=0.50
    )
    
    return {
        "gpt-4:v1.0.0": token_pricing,
        "external_api:v1.0.0": request_pricing
    }

def create_sample_cost_events() -> List[CostEvent]:
    """Create sample cost events for demonstration."""
    
    # Create a sample execution ID
    execution_id = uuid.uuid4()
    
    # Sample model invocation event with tiered pricing
    model_event = CostEvent(
        event_id=uuid.uuid4(),
        timestamp=datetime.now(timezone.utc),
        execution_id=execution_id,
        component="model",
        action="invoke",
        unit_cost=0.03,  # $0.03 per token
        quantity=1500,   # 1500 tokens
        total_cost=45.0, # $45.00 (correct calculation)
        currency="USD",
        cost_source="openai",
        pricing_version="gpt-4:v1.0.0",
        base_unit="token"
    )
    
    # Sample external API call event
    api_event = CostEvent(
        event_id=uuid.uuid4(),
        timestamp=datetime.now(timezone.utc),
        execution_id=execution_id,
        component="external_api",
        action="call",
        unit_cost=0.50,  # $0.50 per request
        quantity=1,      # 1 request
        total_cost=0.50, # $0.50
        currency="USD",
        cost_source="third_party_service",
        pricing_version="external_api:v1.0.0",
        base_unit="request"
    )
    
    return [model_event, api_event]

def main():
    """Demonstrate core ICAE functionality."""
    
    print("=== Inference Cost Attribution Engine (ICAE) Demo ===\n")
    
    # 1. Create sample pricing models
    print("1. Creating pricing models...")
    pricing_models = create_sample_pricing_models()
    print(f"   Created {len(pricing_models)} pricing models\n")
    
    # 2. Create cost events
    print("2. Creating cost events...")
    events = create_sample_cost_events()
    print(f"   Created {len(events)} cost events\n")
    
    # 3. Build ledger
    print("3. Building cost ledger...")
    ledger = CostLedger()
    for event in events:
        ledger.add_event(event)
    print(f"   Ledger built with hash: {ledger.get_ledger_hash()}\n")
    
    # 4. Show total cost
    print("4. Total cost calculation:")
    total_cost = ledger.get_total_cost()
    print(f"   Total cost: ${total_cost:.2f}\n")
    
    # 5. Replay cost using current pricing
    print("5. Replaying costs with current pricing...")
    replay_engine = ReplayEngine(pricing_models)
    execution_id = events[0].execution_id
    try:
        replayed_cost = replay_engine.replay_execution(execution_id, ledger)
        print(f"   Reproduced cost: ${replayed_cost:.2f}")
        print("   ✓ Replay successful - costs match\n")
    except Exception as e:
        print(f"   ✗ Replay failed: {e}\n")
    
    # 6. Verify integrity
    print("6. Verifying ledger integrity...")
    original_hash = ledger.get_ledger_hash()
    is_valid = ledger.verify_integrity(original_hash)
    print(f"   Ledger integrity: {'✓ Valid' if is_valid else '✗ Invalid'}\n")
    
    # 7. Show event details
    print("7. Cost events in ledger:")
    for i, event in enumerate(ledger.get_events(), 1):
        print(f"   {i}. {event.component} ({event.action}): "
              f"${event.total_cost:.2f} ({event.quantity} {event.base_unit})")
    
    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    main()