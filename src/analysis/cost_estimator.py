"""
Cost estimation and BOQ module for CivilAI Twin
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from loguru import logger


@dataclass
class QuantityItem:
    """Quantity item for BOQ"""
    item_code: str
    description: str
    unit: str
    quantity: float
    unit_rate: float
    material_cost: float = 0.0
    labor_cost: float = 0.0
    equipment_cost: float = 0.0


class CostEstimator:
    """Cost estimation and BOQ generator"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.currency = config_manager.get('cost_estimation.currency', 'USD')
        self.labor_rate = config_manager.get('cost_estimation.labor_rate_per_hour', 25.0)
        self.overhead_pct = config_manager.get('cost_estimation.overhead_percentage', 15.0)
        self.profit_pct = config_manager.get('cost_estimation.profit_margin_percentage', 10.0)
        self.contingency_pct = config_manager.get('cost_estimation.contingency_percentage', 10.0)
        
        # Standard unit rates (example database)
        self.unit_rates = {
            'concrete_m25': {'unit': 'm³', 'rate': 150, 'material': 120, 'labor': 20, 'equipment': 10},
            'concrete_m30': {'unit': 'm³', 'rate': 170, 'material': 135, 'labor': 25, 'equipment': 10},
            'steel_rebar': {'unit': 'kg', 'rate': 1.5, 'material': 1.2, 'labor': 0.2, 'equipment': 0.1},
            'formwork': {'unit': 'm²', 'rate': 25, 'material': 15, 'labor': 8, 'equipment': 2},
            'excavation': {'unit': 'm³', 'rate': 12, 'material': 0, 'labor': 5, 'equipment': 7},
            'brick_masonry': {'unit': 'm²', 'rate': 35, 'material': 25, 'labor': 8, 'equipment': 2},
            'plastering': {'unit': 'm²', 'rate': 15, 'material': 8, 'labor': 6, 'equipment': 1},
            'painting': {'unit': 'm²', 'rate': 8, 'material': 4, 'labor': 3.5, 'equipment': 0.5},
            'flooring_tiles': {'unit': 'm²', 'rate': 40, 'material': 30, 'labor': 8, 'equipment': 2},
            'roofing': {'unit': 'm²', 'rate': 45, 'material': 32, 'labor': 10, 'equipment': 3}
        }
    
    def estimate_costs(self, quantities: List[QuantityItem]) -> Dict[str, Any]:
        """
        Estimate costs from bill of quantities
        
        Args:
            quantities: List of quantity items
        
        Returns:
            Cost estimation results
        """
        
        logger.info(f"Starting cost estimation for {len(quantities)} items")
        
        results = {
            'summary': {
                'currency': self.currency,
                'total_items': len(quantities),
                'date': 'Current'
            },
            'boq': [],
            'cost_breakdown': {},
            'scenarios': {},
            'recommendations': []
        }
        
        # Calculate costs for each item
        total_material = 0
        total_labor = 0
        total_equipment = 0
        
        for item in quantities:
            # Get unit rates
            if item.item_code in self.unit_rates:
                rates = self.unit_rates[item.item_code]
                item.material_cost = item.quantity * rates['material']
                item.labor_cost = item.quantity * rates['labor']
                item.equipment_cost = item.quantity * rates['equipment']
            else:
                # Use provided unit rate
                item.material_cost = item.quantity * item.unit_rate * 0.7
                item.labor_cost = item.quantity * item.unit_rate * 0.2
                item.equipment_cost = item.quantity * item.unit_rate * 0.1
            
            item_total = item.material_cost + item.labor_cost + item.equipment_cost
            
            results['boq'].append({
                'item_code': item.item_code,
                'description': item.description,
                'unit': item.unit,
                'quantity': round(item.quantity, 2),
                'unit_rate': round(item.unit_rate, 2),
                'material_cost': round(item.material_cost, 2),
                'labor_cost': round(item.labor_cost, 2),
                'equipment_cost': round(item.equipment_cost, 2),
                'total_cost': round(item_total, 2)
            })
            
            total_material += item.material_cost
            total_labor += item.labor_cost
            total_equipment += item.equipment_cost
        
        # Calculate totals
        subtotal = total_material + total_labor + total_equipment
        overhead = subtotal * (self.overhead_pct / 100)
        subtotal_with_overhead = subtotal + overhead
        profit = subtotal_with_overhead * (self.profit_pct / 100)
        subtotal_with_profit = subtotal_with_overhead + profit
        contingency = subtotal_with_profit * (self.contingency_pct / 100)
        grand_total = subtotal_with_profit + contingency
        
        results['cost_breakdown'] = {
            'direct_costs': {
                'materials': round(total_material, 2),
                'labor': round(total_labor, 2),
                'equipment': round(total_equipment, 2),
                'subtotal': round(subtotal, 2)
            },
            'indirect_costs': {
                'overhead': round(overhead, 2),
                'overhead_percentage': self.overhead_pct
            },
            'profit': {
                'amount': round(profit, 2),
                'percentage': self.profit_pct
            },
            'contingency': {
                'amount': round(contingency, 2),
                'percentage': self.contingency_pct
            },
            'grand_total': round(grand_total, 2)
        }
        
        # Cost scenarios
        results['scenarios'] = self._generate_scenarios(subtotal)
        
        # Recommendations
        results['recommendations'] = self._generate_cost_recommendations(results)
        
        results['summary']['grand_total'] = round(grand_total, 2)
        results['summary']['cost_per_sqm'] = 'N/A'  # Would need area input
        
        logger.info(f"Cost estimation completed. Total: {self.currency} {grand_total:,.2f}")
        
        return results
    
    def _generate_scenarios(self, base_cost: float) -> Dict[str, Any]:
        """Generate cost scenarios (optimistic, most likely, pessimistic)"""
        
        return {
            'optimistic': {
                'description': 'Favorable conditions, efficient execution',
                'adjustment': -10,
                'total': round(base_cost * 0.9, 2)
            },
            'most_likely': {
                'description': 'Normal conditions, expected performance',
                'adjustment': 0,
                'total': round(base_cost, 2)
            },
            'pessimistic': {
                'description': 'Delays, material escalation, challenges',
                'adjustment': +20,
                'total': round(base_cost * 1.2, 2)
            }
        }
    
    def _generate_cost_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate cost optimization recommendations"""
        
        recommendations = []
        
        breakdown = results['cost_breakdown']
        material_pct = (breakdown['direct_costs']['materials'] / breakdown['grand_total']) * 100
        labor_pct = (breakdown['direct_costs']['labor'] / breakdown['grand_total']) * 100
        
        if material_pct > 60:
            recommendations.append("Materials represent >60% of costs. Consider value engineering and alternative materials.")
        
        if labor_pct > 30:
            recommendations.append("Labor costs are high. Explore modularization or prefabrication opportunities.")
        
        recommendations.append("Lock in material prices early to avoid escalation risks.")
        recommendations.append("Consider local sourcing to reduce transportation costs.")
        recommendations.append("Optimize construction sequence to minimize overhead duration.")
        recommendations.append("Regular cost monitoring and variance analysis recommended.")
        
        return recommendations
    
    def extract_quantities_from_model(self, model_data: Dict[str, Any]) -> List[QuantityItem]:
        """Extract quantities from BIM model or drawings"""
        
        # This is a placeholder - real implementation would parse BIM data
        quantities = []
        
        # Example extraction
        if 'concrete_volume' in model_data:
            quantities.append(QuantityItem(
                item_code='concrete_m25',
                description='M25 Concrete',
                unit='m³',
                quantity=model_data['concrete_volume'],
                unit_rate=150
            ))
        
        if 'steel_weight' in model_data:
            quantities.append(QuantityItem(
                item_code='steel_rebar',
                description='Steel Reinforcement',
                unit='kg',
                quantity=model_data['steel_weight'],
                unit_rate=1.5
            ))
        
        return quantities
    
    def compare_alternatives(self, option_a: List[QuantityItem], 
                           option_b: List[QuantityItem]) -> Dict[str, Any]:
        """Compare cost between two design alternatives"""
        
        cost_a = self.estimate_costs(option_a)
        cost_b = self.estimate_costs(option_b)
        
        total_a = cost_a['cost_breakdown']['grand_total']
        total_b = cost_b['cost_breakdown']['grand_total']
        
        savings = total_a - total_b
        savings_pct = (savings / total_a * 100) if total_a > 0 else 0
        
        return {
            'option_a': {'total': total_a, 'details': cost_a},
            'option_b': {'total': total_b, 'details': cost_b},
            'comparison': {
                'savings': round(savings, 2),
                'savings_percentage': round(savings_pct, 2),
                'recommendation': 'Option B' if savings > 0 else 'Option A'
            }
        }
