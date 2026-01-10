import pytest
from uuid import uuid4

from src.models.pricing import PricingModel, PricingTier

def test_flat_rate_pricing():
    """Test flat rate pricing calculation."""
    pricing = PricingModel(
        id=uuid4(),
        version="v1.0.0",
        component="simple_model",
        pricing_type="request",
        base_unit="request",
        tiers=[],
        fixed_fee=5.0
    )
    
    # Test with quantity 0
    assert pricing.calculate_cost(0) == 5.0
    
    # Test with quantity 10
    assert pricing.calculate_cost(10) == 5.0

def test_tiered_pricing():
    """Test tiered pricing calculation."""
    pricing = PricingModel(
        id=uuid4(),
        version="v1.0.0",
        component="tiered_model",
        pricing_type="token",
        base_unit="token",
        tiers=[
            PricingTier(min_quantity=0, max_quantity=1000, unit_cost=0.01),
            PricingTier(min_quantity=1000, max_quantity=None, unit_cost=0.005)
        ]
    )
    
    # Test within first tier
    assert pricing.calculate_cost(500) == 5.0  # 500 * 0.01
    
    # Test at boundary of first tier
    assert pricing.calculate_cost(1000) == 10.0  # 1000 * 0.01
    
    # Test in second tier
    assert pricing.calculate_cost(1500) == 12.5  # 1000 * 0.01 + 500 * 0.005

def test_negative_quantity():
    """Test that negative quantities raise an error."""
    pricing = PricingModel(
        id=uuid4(),
        version="v1.0.0",
        component="test_model",
        pricing_type="token",
        base_unit="token",
        tiers=[PricingTier(min_quantity=0, max_quantity=None, unit_cost=0.01)]
    )
    
    with pytest.raises(ValueError, match="Quantity cannot be negative"):
        pricing.calculate_cost(-1)

def test_tiered_pricing_comprehensive():
    """Test tiered pricing with multiple scenarios."""
    pricing = PricingModel(
        id=uuid4(),
        version="v1.0.0",
        component="tiered_model",
        pricing_type="token",
        base_unit="token",
        tiers=[
            PricingTier(min_quantity=0, max_quantity=1000, unit_cost=0.01),
            PricingTier(min_quantity=1000, max_quantity=5000, unit_cost=0.005),
            PricingTier(min_quantity=5000, max_quantity=None, unit_cost=0.002)
        ]
    )
    
    # Test within first tier
    assert abs(pricing.calculate_cost(500) - 5.0) < 1e-9  # 500 * 0.01
    
    # Test at first tier boundary
    assert abs(pricing.calculate_cost(1000) - 10.0) < 1e-9  # 1000 * 0.01
    
    # Test spanning first two tiers
    # 1000 @ 0.01 + 500 @ 0.005 = 10 + 2.5 = 12.5
    assert abs(pricing.calculate_cost(1500) - 12.5) < 1e-9
    
    # Test at second tier boundary
    # 1000 @ 0.01 + 4000 @ 0.005 = 10 + 20 = 30
    assert abs(pricing.calculate_cost(5000) - 30.0) < 1e-9
    
    # Test into third tier
    # 1000 @ 0.01 + 4000 @ 0.005 + 1000 @ 0.002 = 10 + 20 + 2 = 32
    assert abs(pricing.calculate_cost(6000) - 32.0) < 1e-9

def test_single_unbounded_tier():
    """Test pricing with a single unbounded tier."""
    pricing = PricingModel(
        id=uuid4(),
        version="v1.0.0",
        component="simple_model",
        pricing_type="token",
        base_unit="token",
        tiers=[
            PricingTier(min_quantity=0, max_quantity=None, unit_cost=0.01)
        ]
    )
    
    assert abs(pricing.calculate_cost(100) - 1.0) < 1e-9
    assert abs(pricing.calculate_cost(1000) - 10.0) < 1e-9
    assert abs(pricing.calculate_cost(10000) - 100.0) < 1e-9

def test_no_pricing_tiers():
    """Test that pricing with no tiers raises an error."""
    pricing = PricingModel(
        id=uuid4(),
        version="v1.0.0",
        component="test_model",
        pricing_type="token",
        base_unit="token",
        tiers=[]
    )
    
    with pytest.raises(ValueError, match="No pricing tiers defined"):
        pricing.calculate_cost(100)