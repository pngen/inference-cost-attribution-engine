import pytest
from datetime import datetime, timezone
from uuid import uuid4

from src.models.cost_event import CostEvent
from src.ledger.ledger import CostLedger

def test_add_event():
    """Test adding events to the ledger."""
    ledger = CostLedger()
    
    event1 = CostEvent(
        event_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        execution_id=uuid4(),
        component="model",
        action="invoke",
        unit_cost=0.03,
        quantity=1000,
        total_cost=30.0,
        currency="USD",
        cost_source="openai",
        pricing_version="gpt-4:v1.0.0",
        base_unit="token"
    )
    
    ledger.add_event(event1)
    assert len(list(ledger.get_events())) == 1

def test_chronological_ordering():
    """Test that events are added in chronological order."""
    ledger = CostLedger()
    
    event1 = CostEvent(
        event_id=uuid4(),
        timestamp=datetime(2023, 1, 1),
        execution_id=uuid4(),
        component="model",
        action="invoke",
        unit_cost=0.03,
        quantity=1000,
        total_cost=30.0,
        currency="USD",
        cost_source="openai",
        pricing_version="gpt-4:v1.0.0",
        base_unit="token"
    )
    
    event2 = CostEvent(
        event_id=uuid4(),
        timestamp=datetime(2023, 1, 2),
        execution_id=uuid4(),
        component="model",
        action="invoke",
        unit_cost=0.03,
        quantity=1000,
        total_cost=30.0,
        currency="USD",
        cost_source="openai",
        pricing_version="gpt-4:v1.0.0",
        base_unit="token"
    )
    
    ledger.add_event(event1)
    ledger.add_event(event2)
    
    events = list(ledger.get_events())
    assert len(events) == 2
    assert events[0].timestamp < events[1].timestamp

def test_invalid_ordering():
    """Test that adding events out of order raises an error."""
    ledger = CostLedger()
    
    event1 = CostEvent(
        event_id=uuid4(),
        timestamp=datetime(2023, 1, 2),  # Later timestamp
        execution_id=uuid4(),
        component="model",
        action="invoke",
        unit_cost=0.03,
        quantity=1000,
        total_cost=30.0,
        currency="USD",
        cost_source="openai",
        pricing_version="gpt-4:v1.0.0",
        base_unit="token"
    )
    
    event2 = CostEvent(
        event_id=uuid4(),
        timestamp=datetime(2023, 1, 1),  # Earlier timestamp
        execution_id=uuid4(),
        component="model",
        action="invoke",
        unit_cost=0.03,
        quantity=1000,
        total_cost=30.0,
        currency="USD",
        cost_source="openai",
        pricing_version="gpt-4:v1.0.0",
        base_unit="token"
    )
    
    ledger.add_event(event1)
    
    # NOW this should correctly fail
    with pytest.raises(ValueError, match="Events must be added in chronological order"):
        ledger.add_event(event2)

def test_get_events_by_execution():
    """Test filtering events by execution ID."""
    ledger = CostLedger()
    
    exec_id1 = uuid4()
    exec_id2 = uuid4()
    
    event1 = CostEvent(
        event_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        execution_id=exec_id1,
        component="model",
        action="invoke",
        unit_cost=0.03,
        quantity=1000,
        total_cost=30.0,
        currency="USD",
        cost_source="openai",
        pricing_version="gpt-4:v1.0.0",
        base_unit="token"
    )
    
    event2 = CostEvent(
        event_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        execution_id=exec_id2,
        component="model",
        action="invoke",
        unit_cost=0.03,
        quantity=1000,
        total_cost=30.0,
        currency="USD",
        cost_source="openai",
        pricing_version="gpt-4:v1.0.0",
        base_unit="token"
    )
    
    ledger.add_event(event1)
    ledger.add_event(event2)
    
    events1 = ledger.get_events_by_execution(exec_id1)
    assert len(events1) == 1
    assert events1[0].execution_id == exec_id1
    
    events2 = ledger.get_events_by_execution(exec_id2)
    assert len(events2) == 1
    assert events2[0].execution_id == exec_id2

def test_total_cost_calculation():
    """Test total cost calculation."""
    ledger = CostLedger()
    
    event1 = CostEvent(
        event_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        execution_id=uuid4(),
        component="model",
        action="invoke",
        unit_cost=0.03,
        quantity=1000,
        total_cost=30.0,
        currency="USD",
        cost_source="openai",
        pricing_version="gpt-4:v1.0.0",
        base_unit="token"
    )
    
    event2 = CostEvent(
        event_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        execution_id=uuid4(),
        component="model",
        action="invoke",
        unit_cost=0.03,
        quantity=500,
        total_cost=15.0,
        currency="USD",
        cost_source="openai",
        pricing_version="gpt-4:v1.0.0",
        base_unit="token"
    )
    
    ledger.add_event(event1)
    ledger.add_event(event2)
    
    assert ledger.get_total_cost() == 45.0

def test_ledger_hashing():
    """Test ledger hashing functionality."""
    ledger = CostLedger()
    
    # Empty ledger
    hash1 = ledger.get_ledger_hash()
    assert hash1 != ""
    
    # Add event
    event = CostEvent(
        event_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        execution_id=uuid4(),
        component="model",
        action="invoke",
        unit_cost=0.03,
        quantity=1000,
        total_cost=30.0,
        currency="USD",
        cost_source="openai",
        pricing_version="gpt-4:v1.0.0",
        base_unit="token"
    )
    
    ledger.add_event(event)
    hash2 = ledger.get_ledger_hash()
    assert hash2 != hash1
    
    # Verify integrity
    assert ledger.verify_integrity(hash2) == True
    assert ledger.verify_integrity(hash1) == False

def test_replay_cost():
    """Test replaying cost for an execution."""
    ledger = CostLedger()
    
    exec_id = uuid4()
    
    event1 = CostEvent(
        event_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        execution_id=exec_id,
        component="model",
        action="invoke",
        unit_cost=0.03,
        quantity=1000,
        total_cost=30.0,
        currency="USD",
        cost_source="openai",
        pricing_version="gpt-4:v1.0.0",
        base_unit="token"
    )
    
    event2 = CostEvent(
        event_id=uuid4(),
        timestamp=datetime.now(timezone.utc),
        execution_id=exec_id,
        component="model",
        action="invoke",
        unit_cost=0.03,
        quantity=500,
        total_cost=15.0,
        currency="USD",
        cost_source="openai",
        pricing_version="gpt-4:v1.0.0",
        base_unit="token"
    )
    
    ledger.add_event(event1)
    ledger.add_event(event2)
    
    replayed_cost = ledger.replay_cost(exec_id)
    assert replayed_cost == 45.0