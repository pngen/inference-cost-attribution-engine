from abc import ABC, abstractmethod
from typing import List, Dict, Any
from uuid import UUID

from src.models.cost_event import CostEvent

class CostAdapter(ABC):
    """
    Abstract base class for adapters that convert external data into cost events.
    
    Adapters must be explicit about their inputs and outputs.
    """
    
    @abstractmethod
    def to_cost_events(self, data: Any) -> List[CostEvent]:
        """
        Convert external data into a list of cost events.
        
        Args:
            data: External data structure (e.g., execution transcript)
            
        Returns:
            List of CostEvents representing the costs in the input data
            
        Raises:
            ValueError if data cannot be processed
        """
        pass

class ExecutionTranscriptAdapter(CostAdapter):
    """
    Adapter for converting execution transcripts into cost events.
    
    This is a minimal example - real implementations would handle
    more complex scenarios like retries, tool calls, etc.
    """
    
    def to_cost_events(self, data: Dict[str, Any]) -> List[CostEvent]:
        # Example implementation - in practice this would be much more detailed
        events = []
        
        # Process model invocations
        for invocation in data.get("model_invocations", []):
            event = CostEvent(
                event_id=UUID(invocation["event_id"]),
                timestamp=invocation["timestamp"],
                execution_id=UUID(data["execution_id"]),
                component="model",
                action="invoke",
                unit_cost=invocation["unit_cost"],
                quantity=invocation["quantity"],
                total_cost=invocation["total_cost"],
                currency=invocation["currency"],
                cost_source=invocation["cost_source"],
                pricing_version=invocation["pricing_version"],
                base_unit=invocation.get("base_unit", "token")
            )
            events.append(event)
            
        return events