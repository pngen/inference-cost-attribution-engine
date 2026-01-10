from typing import List, Dict, Optional
from uuid import UUID

from src.models.cost_event import CostEvent
from src.models.pricing import PricingModel
from src.ledger.ledger import CostLedger

class ReplayEngine:
    """
    Engine for replaying cost calculations and verifying ledger integrity.
    
    Supports deterministic cost recomputation and delta analysis.
    """
    
    def __init__(self, pricing_models: Dict[str, PricingModel]):
        self.pricing_models = pricing_models
        
    def replay_execution(self, execution_id: UUID, 
                        ledger: CostLedger) -> float:
        """
        Recompute the total cost for an execution using current pricing.
        
        Args:
            execution_id: The ID of the execution to replay
            ledger: The ledger containing cost events
            
        Returns:
            The recomputed total cost
            
        Raises:
            ValueError if any event references unknown pricing model
        """
        events = ledger.get_events_by_execution(execution_id)
        total_cost = 0.0
        
        for event in events:
            # Validate that we have the correct pricing model
            if event.pricing_version not in self.pricing_models:
                raise ValueError(f"Unknown pricing version: {event.pricing_version}")
                
            pricing_model = self.pricing_models[event.pricing_version]
            
            # Recalculate cost using current pricing
            calculated_cost = pricing_model.calculate_cost(event.quantity)
            
            # Verify that the event's cost matches our calculation
            if abs(calculated_cost - event.total_cost) > 1e-6:
                raise ValueError(
                    f"Cost mismatch for event {event.event_id}: "
                    f"expected {calculated_cost}, got {event.total_cost}"
                )
                
            total_cost += calculated_cost
            
        return total_cost
        
    def compare_replay_with_original(self, execution_id: UUID,
                                   original_ledger: CostLedger,
                                   current_pricing: Dict[str, PricingModel]) -> Dict:
        """
        Compare a replay with the original ledger to identify any differences.
        
        Returns:
            Dictionary containing comparison results and any deltas
        """
        try:
            # Try to replay using current pricing
            replayed_cost = self.replay_execution(execution_id, original_ledger)
            
            # Get original cost from ledger
            original_events = original_ledger.get_events_by_execution(execution_id)
            original_cost = sum(e.total_cost for e in original_events)
            
            return {
                "execution_id": execution_id,
                "original_cost": original_cost,
                "replayed_cost": replayed_cost,
                "delta": replayed_cost - original_cost,
                "status": "match" if abs(replayed_cost - original_cost) < 1e-6 else "mismatch"
            }
        except Exception as e:
            return {
                "execution_id": execution_id,
                "error": str(e),
                "status": "error"
            }