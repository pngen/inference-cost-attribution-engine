from dataclasses import dataclass
from typing import Dict, List, Optional
from uuid import UUID

@dataclass(frozen=True)
class PricingTier:
    """Represents a pricing tier for a model or service."""
    min_quantity: float
    max_quantity: Optional[float]  # None means no upper bound
    unit_cost: float

@dataclass(frozen=True)
class PricingModel:
    """
    A versioned pricing model that defines how costs are calculated.
    
    This is the source of truth for all cost calculations in ICAE.
    """
    # Unique identifier for this pricing model
    id: UUID
    
    # Version string (e.g., "v1.2.3")
    version: str
    
    # Name of the component being priced
    component: str
    
    # Type of pricing (token, request, compute, etc.)
    pricing_type: str
    
    # Base unit for this pricing model
    base_unit: str
    
    # Pricing tiers - if empty, flat rate applies
    tiers: List[PricingTier]
    
    # Optional fixed fee per invocation
    fixed_fee: Optional[float] = None
    
    # Optional metadata about the pricing model
    metadata: Optional[Dict[str, str]] = None

    def calculate_cost(self, quantity: float) -> float:
        """
        Calculate cost for a given quantity based on the pricing tiers.
        
        For tiered pricing, calculates cumulative cost across all applicable tiers.
        Example: If tiers are [0-100 @ $1, 100+ @ $0.5] and quantity is 150:
            - First 100 units: 100 * $1 = $100
            - Next 50 units: 50 * $0.5 = $25
            - Total: $125
        
        Returns:
            Total cost for the specified quantity
            
        Raises:
            ValueError if quantity is negative or no applicable tier exists
        """
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
            
        total_cost = self.fixed_fee or 0.0
        
        # If there are no tiers, this shouldn't happen in production
        # but handle it gracefully
        if not self.tiers:
            raise ValueError("No pricing tiers defined")
        
        # Sort tiers by min_quantity to ensure correct processing
        sorted_tiers = sorted(self.tiers, key=lambda t: t.min_quantity)
        
        # Validate that tiers cover the quantity
        if quantity < sorted_tiers[0].min_quantity:
            raise ValueError(
                f"No applicable pricing tier for quantity {quantity}. "
                f"Minimum tier starts at {sorted_tiers[0].min_quantity}"
            )
        
        remaining_quantity = quantity
        processed_up_to = 0.0
        
        for tier in sorted_tiers:
            # If we've processed all quantity, we're done
            if remaining_quantity <= 0:
                break
                
            # Skip tiers that start after our quantity
            if tier.min_quantity > quantity:
                break
                
            # Calculate how much quantity falls into this tier
            tier_start = max(tier.min_quantity, processed_up_to)
            tier_end = tier.max_quantity if tier.max_quantity is not None else float('inf')
            
            # How much of our quantity falls into this tier?
            quantity_in_tier = min(quantity, tier_end) - tier_start
            
            if quantity_in_tier > 0:
                total_cost += quantity_in_tier * tier.unit_cost
                processed_up_to = min(quantity, tier_end)
                remaining_quantity -= quantity_in_tier
        
        # If we still have remaining quantity, no tier covered it
        if remaining_quantity > 1e-9:  # Use small epsilon for floating point comparison
            raise ValueError(
                f"No applicable pricing tier for quantity {quantity}. "
                f"Only {processed_up_to} units were covered by tiers."
            )
        
        return total_cost