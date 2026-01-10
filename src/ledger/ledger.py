from typing import List, Dict, Optional, Iterator
from uuid import UUID
import hashlib
import json
from datetime import datetime, timezone

from src.models.cost_event import CostEvent

class CostLedger:
    """
    A tamper-evident, append-only ledger for cost events.
    
    The ledger maintains a deterministic order of events and supports
    replayability through hashing and versioning.
    """
    
    def __init__(self):
        self._events: List[CostEvent] = []
        self._hashes: List[str] = []
        
    def add_event(self, event: CostEvent) -> None:
        """Add a cost event to the ledger."""
        # Ensure events are added in chronological order
        if self._events and event.timestamp < self._events[-1].timestamp:
            raise ValueError("Events must be added in chronological order")
            
        self._events.append(event)
        self._update_hash()
        
    def _update_hash(self) -> None:
        """Update the ledger's hash based on current events."""
        # Create a deterministic representation of all events
        event_data = [self._event_to_dict(e) for e in self._events]
        data_str = json.dumps(event_data, sort_keys=True, default=str)
        
        # Hash the serialized data
        self._hashes.append(hashlib.sha256(data_str.encode()).hexdigest())
        
    def _event_to_dict(self, event: CostEvent) -> Dict:
        """Convert a cost event to a dictionary for hashing."""
        return {
            "event_id": str(event.event_id),
            "timestamp": event.timestamp.isoformat(),
            "execution_id": str(event.execution_id),
            "component": event.component,
            "action": event.action,
            "unit_cost": event.unit_cost,
            "quantity": event.quantity,
            "total_cost": event.total_cost,
            "currency": event.currency,
            "cost_source": event.cost_source,
            "pricing_version": event.pricing_version,
            "base_unit": event.base_unit,
            "metadata": event.metadata
        }
        
    def get_events(self) -> Iterator[CostEvent]:
        """Get all events in chronological order."""
        yield from self._events
        
    def get_events_by_execution(self, execution_id: UUID) -> List[CostEvent]:
        """Filter events by execution ID."""
        return [e for e in self._events if e.execution_id == execution_id]
        
    def get_events_by_component(self, component: str) -> List[CostEvent]:
        """Filter events by component."""
        return [e for e in self._events if e.component == component]
        
    def get_total_cost(self) -> float:
        """Calculate the total cost across all events."""
        return sum(e.total_cost for e in self._events)
        
    def get_ledger_hash(self) -> str:
        """Get the current hash of the ledger."""
        if not self._hashes:
            # Return hash of empty ledger for consistency
            return hashlib.sha256(b"[]").hexdigest()
        return self._hashes[-1]
        
    def verify_integrity(self, expected_hash: str) -> bool:
        """Verify that the ledger matches an expected hash."""
        return self.get_ledger_hash() == expected_hash
        
    def replay_cost(self, execution_id: UUID) -> float:
        """Recompute total cost for a specific execution."""
        events = self.get_events_by_execution(execution_id)
        return sum(e.total_cost for e in events)