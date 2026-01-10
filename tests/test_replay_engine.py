import pytest
from datetime import datetime, timezone
from uuid import uuid4

from src.models.cost_event import CostEvent
from src.models.pricing import PricingModel, PricingTier
from src.ledger.ledger import CostLedger
from src.replay.replay_engine import ReplayEngine

def test_replay_execution():
    """Test replaying an execution with current pricing."""
    
    # Create sample pricing model
    pricing = PricingModel(
        id=uuid4(),
        version="v1.0.0",
        component="gpt-4",
        pricing_type="token",
        base_unit="token",
        tiers=[
            PricingTier(min_quantity=0, max_quantity=10000, unit_cost=0.03),
            PricingTier(min_quantity=10000, max_quantity=None, unit_cost=0.02)
        ]
    )
    
    pricing_models = {"gpt-4:v1.0.0": pricing}
    replay_engine = ReplayEngine(pricing_models)
    
    # Create ledger with events
    ledger = CostLedger()
    
    exec_id = uuid4()
    
    event1 = CostEvent(
        event_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        execution_id=exec_id,
        component="model",
        action="invoke",
        unit_cost=0.03,
        quantity=1500,
        total_cost=45.0,
        currency="USD",
        cost_source="openai",
        pricing_version="gpt-4:v1.0.0",
        base_unit="token"
    )
    
    ledger.add_event(event1)
    
    # Replay should succeed
    replayed_cost = replay_engine.replay_execution(exec_id, ledger)
    assert replayed_cost == 45.0

def test_replay_with_mismatched_cost():
    """Test that replay fails when event cost doesn't match calculated cost."""
    
    # Create sample pricing model
    pricing = PricingModel(
        id=uuid4(),
        version="v1.0.0",
        component="gpt-4",
        pricing_type="token",
        base_unit="token",
        tiers=[
            PricingTier(min_quantity=0, max_quantity=10000, unit_cost=0.03),
            PricingTier(min_quantity=10000, max_quantity=None, unit_cost=0.02)
        ]
    )
    
    pricing_models = {"gpt-4:v1.0.0": pricing}
    replay_engine = ReplayEngine(pricing_models)
    
    # Create ledger with event that has wrong cost
    ledger = CostLedger()
    
    exec_id = uuid4()
    
    event1 = CostEvent(
        event_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        execution_id=exec_id,
        component="model",
        action="invoke",
        unit_cost=0.03,
        quantity=1500,
        total_cost=44.0,  # Wrong - should be 45.0
        currency="USD",
        cost_source="openai",
        pricing_version="gpt-4:v1.0.0",
        base_unit="token"
    )
    
    ledger.add_event(event1)
    
    # Replay should fail due to mismatched cost
    with pytest.raises(ValueError, match="Cost mismatch"):
        replay_engine.replay_execution(exec_id, ledger)

def test_replay_with_unknown_pricing():
    """Test that replay fails when pricing version is unknown."""
    
    # Create sample pricing model
    pricing = PricingModel(
        id=uuid4(),
        version="v1.0.0",
        component="gpt-4",
        pricing_type="token",
        base_unit="token",
        tiers=[
            PricingTier(min_quantity=0, max_quantity=10000, unit_cost=0.03),
            PricingTier(min_quantity=10000, max_quantity=None, unit_cost=0.02)
        ]
    )
    
    pricing_models = {"gpt-4:v1.0.0": pricing}
    replay_engine = ReplayEngine(pricing_models)
    
    # Create ledger with event using unknown pricing version
    ledger = CostLedger()
    
    exec_id = uuid4()
    
    event1 = CostEvent(
        event_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        execution_id=exec_id,
        component="model",
        action="invoke",
        unit_cost=0.03,
        quantity=1500,
        total_cost=45.0,
        currency="USD",
        cost_source="openai",
        pricing_version="unknown:v1.0.0"  # Unknown version
    )
    
    ledger.add_event(event1)
    
    # Replay should fail due to unknown pricing
    with pytest.raises(ValueError, match="Unknown pricing version"):
        replay_engine.replay_execution(exec_id, ledger)

def test_compare_replay_with_original():
    """Test comparing replay results with original."""
    
    # Create sample pricing model
    pricing = PricingModel(
        id=uuid4(),
        version="v1.0.0",
        component="gpt-4",
        pricing_type="token",
        base_unit="token",
        tiers=[
            PricingTier(min_quantity=0, max_quantity=10000, unit_cost=0.03),
            PricingTier(min_quantity=10000, max_quantity=None, unit_cost=0.02)
        ]
    )
    
    pricing_models = {"gpt-4:v1.0.0": pricing}
    replay_engine = ReplayEngine(pricing_models)
    
    # Create ledger with events
    ledger = CostLedger()
    
    exec_id = uuid4()
    
    event1 = CostEvent(
        event_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        execution_id=exec_id,
        component="model",
        action="invoke",
        unit_cost=0.03,
        quantity=1500,
        total_cost=45.0,
        currency="USD",
        cost_source="openai",
        pricing_version="gpt-4:v1.0.0",
        base_unit="token"
    )
    
    ledger.add_event(event1)
    
    # Compare should show match
    result = replay_engine.compare_replay_with_original(exec_id, ledger, pricing_models)
    assert result["status"] == "match"
    assert result["original_cost"] == 45.0
    assert result["replayed_cost"] == 45.0