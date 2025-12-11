"""
AI Pricing Engine
Dynamic pricing calculation based on problem complexity, materials, and market rates
"""

from typing import Dict, Any, List
from decimal import Decimal
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class PricingEngine:
    """Service for calculating job costs using AI and market data"""
    
    # Base rates for electrical work (RUB per hour)
    BASE_RATES = {
        "electrical": {
            "simple": 800,      # Simple outlet/switch replacement
            "medium": 1500,     # Circuit breaker, wiring repair
            "complex": 3000     # Full rewiring, panel upgrade
        },
        "plumbing": {
            "simple": 900,
            "medium": 1800,
            "complex": 3500
        },
        "renovation": {
            "simple": 700,
            "medium": 1400,
            "complex": 2800
        },
        "appliances": {
            "simple": 1000,
            "medium": 2000,
            "complex": 4000
        }
    }
    
    # Common materials costs (RUB)
    MATERIALS_CATALOG = {
        "electrical": {
            "outlet": 150,
            "switch": 200,
            "circuit_breaker": 500,
            "wire_1m": 80,
            "junction_box": 100,
            "cable_10m": 600,
            "led_lamp": 300
        },
        "plumbing": {
            "pipe_1m": 200,
            "faucet": 1500,
            "valve": 400,
            "sealant": 150
        }
    }
    
    def __init__(self):
        self.min_cost = Decimal(str(settings.MINIMUM_JOB_COST))
        self.max_cost = Decimal(str(settings.MAXIMUM_JOB_COST))
    
    def calculate_job_cost(
        self,
        category: str,
        problem_description: str,
        complexity: str = "medium",
        estimated_hours: float = 1.0,
        required_materials: List[Dict[str, Any]] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate total job cost
        
        Args:
            category: Job category (electrical, plumbing, etc.)
            problem_description: Description of the problem
            complexity: Complexity level (simple, medium, complex)
            estimated_hours: Estimated time to complete
            required_materials: List of required materials
            
        Returns:
            Cost breakdown dictionary
        """
        try:
            # Get base hourly rate
            base_rate = self._get_base_rate(category, complexity)
            
            # Calculate labor cost
            labor_cost = Decimal(str(base_rate * estimated_hours))
            
            # Calculate materials cost
            materials_cost = self._calculate_materials_cost(
                category,
                required_materials or []
            )
            
            # Calculate urgency multiplier
            urgency_multiplier = self._calculate_urgency_multiplier(
                problem_description
            )
            
            # Total cost before adjustments
            subtotal = (labor_cost + materials_cost) * urgency_multiplier
            
            # Apply bounds
            total_cost = max(self.min_cost, min(subtotal, self.max_cost))
            
            # Calculate earnings breakdown
            earnings = self._calculate_earnings_breakdown(total_cost)
            
            return {
                "total_cost": total_cost,
                "labor_cost": labor_cost,
                "materials_cost": materials_cost,
                "urgency_multiplier": urgency_multiplier,
                **earnings
            }
            
        except Exception as e:
            logger.error(f"Error calculating cost: {e}")
            # Return default pricing
            return self._get_default_pricing(category)
    
    def _get_base_rate(self, category: str, complexity: str) -> float:
        """Get base hourly rate for category and complexity"""
        if category not in self.BASE_RATES:
            category = "electrical"  # Default fallback
        
        if complexity not in self.BASE_RATES[category]:
            complexity = "medium"  # Default fallback
        
        return self.BASE_RATES[category][complexity]
    
    def _calculate_materials_cost(
        self,
        category: str,
        materials: List[Dict[str, Any]]
    ) -> Decimal:
        """Calculate total materials cost"""
        total = Decimal("0")
        
        if category not in self.MATERIALS_CATALOG:
            return total
        
        catalog = self.MATERIALS_CATALOG[category]
        
        for material in materials:
            material_name = material.get("name", "").lower()
            quantity = material.get("quantity", 1)
            
            # Try to find material in catalog
            for catalog_item, price in catalog.items():
                if catalog_item in material_name:
                    total += Decimal(str(price * quantity))
                    break
        
        return total
    
    def _calculate_urgency_multiplier(self, description: str) -> Decimal:
        """Calculate urgency multiplier based on problem description"""
        urgency_keywords = {
            "срочно": 1.3,
            "аварийно": 1.5,
            "немедленно": 1.4,
            "сегодня": 1.2,
            "искры": 1.5,
            "запах гари": 1.5,
            "протечка": 1.4,
            "затопление": 1.6
        }
        
        description_lower = description.lower()
        
        for keyword, multiplier in urgency_keywords.items():
            if keyword in description_lower:
                return Decimal(str(multiplier))
        
        return Decimal("1.0")
    
    def _calculate_earnings_breakdown(
        self,
        total_cost: Decimal
    ) -> Dict[str, Decimal]:
        """Calculate earnings breakdown"""
        # Payment gateway fee (2%)
        gateway_fee = total_cost * Decimal("0.02")
        net_amount = total_cost - gateway_fee
        
        # Platform commission (25%)
        platform_commission = net_amount * Decimal(str(settings.PLATFORM_COMMISSION_RATE))
        master_earnings = net_amount - platform_commission
        
        return {
            "gateway_fee": gateway_fee,
            "platform_commission": platform_commission,
            "master_earnings": master_earnings
        }
    
    def _get_default_pricing(self, category: str) -> Dict[str, Decimal]:
        """Get default pricing when calculation fails"""
        default_cost = Decimal("2500")
        
        if category == "plumbing":
            default_cost = Decimal("3000")
        elif category == "appliances":
            default_cost = Decimal("3500")
        
        return {
            "total_cost": default_cost,
            "labor_cost": default_cost * Decimal("0.7"),
            "materials_cost": default_cost * Decimal("0.3"),
            "urgency_multiplier": Decimal("1.0"),
            **self._calculate_earnings_breakdown(default_cost)
        }
    
    def estimate_complexity(self, problem_description: str, category: str) -> str:
        """
        Estimate job complexity based on description
        
        Args:
            problem_description: Problem description
            category: Job category
            
        Returns:
            Complexity level: simple, medium, or complex
        """
        description_lower = problem_description.lower()
        
        # Keywords for different complexity levels
        simple_keywords = [
            "розетка", "выключатель", "лампочка", "патрон",
            "outlet", "switch", "light bulb"
        ]
        
        complex_keywords = [
            "проводка", "щиток", "автомат", "ввод", "кабель",
            "wiring", "panel", "circuit", "main line"
        ]
        
        # Check for simple keywords
        if any(keyword in description_lower for keyword in simple_keywords):
            return "simple"
        
        # Check for complex keywords
        if any(keyword in description_lower for keyword in complex_keywords):
            return "complex"
        
        # Default to medium
        return "medium"
    
    def estimate_duration(
        self,
        complexity: str,
        category: str
    ) -> float:
        """
        Estimate job duration in hours
        
        Args:
            complexity: Job complexity
            category: Job category
            
        Returns:
            Estimated hours
        """
        duration_map = {
            "simple": 1.0,
            "medium": 2.5,
            "complex": 5.0
        }
        
        base_duration = duration_map.get(complexity, 2.0)
        
        # Adjust for category
        if category == "appliances":
            base_duration *= 1.2
        elif category == "renovation":
            base_duration *= 1.5
        
        return base_duration
