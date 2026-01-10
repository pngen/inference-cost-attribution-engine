import pytest
from datetime import datetime, timezone
from uuid import uuid4

from src.models.cost_event import CostEvent

def test_cost_event_creation():
    """Test that cost events are created correctly."""
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
    
    assert event.event_id is not None
    assert event.component == "model"
    assert event.action == "invoke"
    assert event.unit_cost == 0.03
    assert event.quantity == 1000
    assert event.total_cost == 30.0
    assert event.base_unit == "token"

def test_cost_event_validation():
    """Test that cost events validate their total cost."""
    # Valid case
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
    
    # Should not raise exception
    assert event.total_cost == 0.03 * 1000
    
    # Invalid case - mismatched total cost
    with pytest.raises(ValueError, match="Total cost must equal unit cost multiplied by quantity"):
        CostEvent(
            event_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            execution_id=uuid4(),
            component="model",
            action="invoke",
            unit_cost=0.03,
            quantity=1000,
            total_cost=29.0,  # Wrong!
            currency="USD",
            cost_source="openai",
            pricing_version="gpt-4:v1.0.0",
            base_unit="token"
        )