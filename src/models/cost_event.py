from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

@dataclass(frozen=True)
class CostEvent:
    """
    A cost event represents a single unit of cost attribution in the system.
    
    Each cost event must be deterministic and fully attributable to a specific action,
    component, and pricing source. No aggregation is allowed at this level.
    """
    # Unique identifier for this cost event
    event_id: UUID
    
    # Timestamp when the cost was incurred
    timestamp: datetime
    
    # Execution context - ties this event to a specific run or session
    execution_id: UUID
    
    # Component that incurred the cost (model, tool, cache, network, compute)
    component: str
    
    # Action taken that triggered the cost
    action: str
    
    # Unit cost in the specified currency
    unit_cost: float
    
    # Quantity of units consumed
    quantity: float
    
    # Total cost for this event
    total_cost: float
    
    # Currency used for pricing
    currency: str
    
    # Source of the pricing (vendor, internal rate card, etc.)
    cost_source: str
    
    # Versioned reference to the pricing used
    pricing_version: str
    
    # Base unit for this pricing model
    base_unit: str
    
    # Optional metadata for additional context
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.total_cost != self.unit_cost * self.quantity:
            raise ValueError("Total cost must equal unit cost multiplied by quantity")