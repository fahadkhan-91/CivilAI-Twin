"""
Carbon footprint calculator for CivilAI Twin
Calculates embodied carbon from material quantities
"""

import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass
from loguru import logger


@dataclass
class MaterialCarbon:
    """Material with carbon data"""
    material: str
    quantity: float
    unit: str
    carbon_coefficient: float  # kgCO2e per unit
    category: str  # production, transportation, construction, end_of_life


class CarbonCalculator:
    """Carbon footprint calculator"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.calculation_method = config_manager.get('carbon.calculation_method', 'ICE')
        self.report_units = config_manager.get('carbon.report_units', 'kgCO2e')
        
        # Carbon coefficients (kgCO2e per unit) - ICE Database v3.0
        self.carbon_coefficients = {
            # Concrete
            'concrete_m20': {'unit': 'm³', 'coefficient': 140, 'category': 'material'},
            'concrete_m25': {'unit': 'm³', 'coefficient': 160, 'category': 'material'},
            'concrete_m30': {'unit': 'm³', 'coefficient': 180, 'category': 'material'},
            'concrete_m35': {'unit': 'm³', 'coefficient': 200, 'category': 'material'},
            
            # Steel
            'steel_primary': {'unit': 'tonne', 'coefficient': 2100, 'category': 'material'},
            'steel_recycled': {'unit': 'tonne', 'coefficient': 500, 'category': 'material'},
            'steel_rebar': {'unit': 'kg', 'coefficient': 1.8, 'category': 'material'},
            
            # Cement
            'cement_opc': {'unit': 'tonne', 'coefficient': 900, 'category': 'material'},
            'cement_ppc': {'unit': 'tonne', 'coefficient': 750, 'category': 'material'},
            'cement_ggbs': {'unit': 'tonne', 'coefficient': 150, 'category': 'material'},
            
            # Aggregates
            'aggregate_crushed': {'unit': 'tonne', 'coefficient': 6, 'category': 'material'},
            'aggregate_natural': {'unit': 'tonne', 'coefficient': 4, 'category': 'material'},
            'sand': {'unit': 'tonne', 'coefficient': 5, 'category': 'material'},
            
            # Masonry
            'brick_common': {'unit': 'tonne', 'coefficient': 240, 'category': 'material'},
            'brick_engineering': {'unit': 'tonne', 'coefficient': 280, 'category': 'material'},
            'block_concrete': {'unit': 'm²', 'coefficient': 55, 'category': 'material'},
            
            # Finishes
            'paint': {'unit': 'm²', 'coefficient': 2.5, 'category': 'material'},
            'tiles_ceramic': {'unit': 'm²', 'coefficient': 18, 'category': 'material'},
            'plaster': {'unit': 'm²', 'coefficient': 8, 'category': 'material'},
            
            # Glass & Aluminum
            'glass': {'unit': 'm²', 'coefficient': 50, 'category': 'material'},
            'aluminum': {'unit': 'kg', 'coefficient': 8.5, 'category': 'material'},
            
            # Timber
            'timber_softwood': {'unit': 'm³', 'coefficient': -350, 'category': 'material'},  # Carbon negative
            'timber_hardwood': {'unit': 'm³', 'coefficient': -600, 'category': 'material'},
            
            # Transportation (per tonne-km)
            'transport_truck': {'unit': 'tonne-km', 'coefficient': 0.12, 'category': 'transportation'},
            'transport_rail': {'unit': 'tonne-km', 'coefficient': 0.04, 'category': 'transportation'},
            
            # Construction equipment (per hour)
            'excavator': {'unit': 'hour', 'coefficient': 25, 'category': 'construction'},
            'concrete_pump': {'unit': 'hour', 'coefficient': 15, 'category': 'construction'},
            'crane': {'unit': 'hour', 'coefficient': 30, 'category': 'construction'}
        }
        
        # Industry benchmarks (kgCO2e/m²)
        self.benchmarks = {
            'residential_low_rise': {'min': 400, 'typical': 600, 'max': 800},
            'residential_high_rise': {'min': 500, 'typical': 700, 'max': 900},
            'office': {'min': 600, 'typical': 800, 'max': 1000},
            'industrial': {'min': 300, 'typical': 500, 'max': 700},
            'infrastructure': {'min': 200, 'typical': 400, 'max': 600}
        }
    
    def calculate_carbon(self, materials: List[MaterialCarbon], 
                        project_area: float = None,
                        project_type: str = None) -> Dict[str, Any]:
        """
        Calculate total carbon footprint
        
        Args:
            materials: List of materials with quantities
            project_area: Total project area (m²) for benchmarking
            project_type: Type of project for benchmarking
        
        Returns:
            Carbon calculation results
        """
        
        logger.info(f"Starting carbon footprint calculation for {len(materials)} materials")
        
        results = {
            'summary': {
                'method': self.calculation_method,
                'units': self.report_units,
                'total_materials': len(materials)
            },
            'breakdown': {
                'material_production': 0,
                'transportation': 0,
                'construction': 0,
                'end_of_life': 0
            },
            'by_material': [],
            'reduction_opportunities': [],
            'benchmarking': {},
            'recommendations': []
        }
        
        # Calculate carbon for each material
        total_carbon = 0
        
        for mat in materials:
            try:
                # Get carbon coefficient
                mat_name = getattr(mat, 'material', None)
                if not mat_name:
                    logger.warning(f"Material object missing 'material' attribute, skipping")
                    continue
                    
                if mat_name in self.carbon_coefficients:
                    coef_data = self.carbon_coefficients[mat_name]
                    carbon = mat.quantity * coef_data['coefficient']
                    category = coef_data['category']
                else:
                    # Use provided coefficient if not in database
                    carbon = mat.quantity * mat.carbon_coefficient
                    category = mat.category
                
                total_carbon += carbon
                
                # Ensure category exists in breakdown
                if category not in results['breakdown']:
                    results['breakdown'][category] = 0
                    
                results['breakdown'][category] += carbon
                
                results['by_material'].append({
                    'material': mat_name,
                    'quantity': round(mat.quantity, 2),
                    'unit': mat.unit,
                    'coefficient': mat.carbon_coefficient,
                    'carbon': round(carbon, 2),
                    'percentage': 0  # Will calculate after total known
                })
            except Exception as e:
                logger.error(f"Error processing material {getattr(mat, 'material', 'unknown')}: {e}")
                continue
        
        # Calculate percentages
        for item in results['by_material']:
            item['percentage'] = round((item['carbon'] / total_carbon * 100), 2) if total_carbon != 0 else 0
        
        # Sort by carbon impact
        results['by_material'].sort(key=lambda x: abs(x['carbon']), reverse=True)
        
        results['summary']['total_carbon'] = round(total_carbon, 2)
        
        # Convert to tonnes if appropriate
        if total_carbon > 1000:
            results['summary']['total_carbon_tonnes'] = round(total_carbon / 1000, 2)
        
        # Calculate per area if provided
        if project_area and project_area > 0:
            carbon_per_sqm = total_carbon / project_area
            results['summary']['carbon_per_sqm'] = round(carbon_per_sqm, 2)
            
            # Benchmarking
            if project_type and project_type in self.benchmarks:
                benchmark = self.benchmarks[project_type]
                results['benchmarking'] = {
                    'project_type': project_type,
                    'project_carbon_per_sqm': round(carbon_per_sqm, 2),
                    'industry_min': benchmark['min'],
                    'industry_typical': benchmark['typical'],
                    'industry_max': benchmark['max'],
                    'performance': self._assess_performance(carbon_per_sqm, benchmark)
                }
        
        # Identify reduction opportunities
        results['reduction_opportunities'] = self._identify_reduction_opportunities(results)
        
        # Generate recommendations
        results['recommendations'] = self._generate_carbon_recommendations(results)
        
        logger.info(f"Carbon calculation completed. Total: {total_carbon:,.2f} {self.report_units}")
        
        return results
    
    def _assess_performance(self, value: float, benchmark: Dict[str, float]) -> str:
        """Assess carbon performance against benchmarks"""
        
        if value < benchmark['min']:
            return 'Exceptional'
        elif value < benchmark['typical']:
            return 'Good'
        elif value < benchmark['max']:
            return 'Average'
        else:
            return 'Poor'
    
    def _identify_reduction_opportunities(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify carbon reduction opportunities"""
        
        opportunities = []
        
        # Analyze top carbon contributors
        top_materials = results['by_material'][:5]  # Top 5
        
        for mat in top_materials:
            material = mat['material']
            
            # Concrete reduction opportunities
            if 'concrete' in material:
                opportunities.append({
                    'material': material,
                    'current_carbon': mat['carbon'],
                    'strategy': 'Use supplementary cementitious materials (SCM)',
                    'potential_reduction': '20-30%',
                    'alternative': 'Concrete with GGBS or fly ash replacement'
                })
            
            # Steel reduction opportunities
            if 'steel' in material and 'primary' in material:
                opportunities.append({
                    'material': material,
                    'current_carbon': mat['carbon'],
                    'strategy': 'Use recycled steel content',
                    'potential_reduction': '60-70%',
                    'alternative': 'Specify minimum 90% recycled content'
                })
            
            # Cement reduction opportunities
            if 'cement' in material and 'opc' in material:
                opportunities.append({
                    'material': material,
                    'current_carbon': mat['carbon'],
                    'strategy': 'Switch to low-carbon cement',
                    'potential_reduction': '15-40%',
                    'alternative': 'PPC or GGBS blended cement'
                })
        
        return opportunities
    
    def _generate_carbon_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate carbon reduction recommendations"""
        
        recommendations = []
        
        total = results['summary']['total_carbon']
        breakdown = results['breakdown']
        
        # Material recommendations
        material_pct = (breakdown['material_production'] / total * 100) if total > 0 else 0
        
        if material_pct > 70:
            recommendations.append("Material production is the dominant carbon source (>70%). Focus on material substitution and optimization.")
        
        # Specific recommendations
        recommendations.append("Specify concrete with supplementary cementitious materials (30-50% cement replacement).")
        recommendations.append("Maximize use of recycled steel reinforcement (target 90%+).")
        recommendations.append("Source materials locally to minimize transportation emissions.")
        recommendations.append("Consider timber in lieu of concrete/steel where structurally viable.")
        recommendations.append("Optimize structural design to reduce material quantities.")
        recommendations.append("Implement a carbon budget and track actual embodied carbon during construction.")
        
        # Benchmarking recommendations
        if 'benchmarking' in results and results['benchmarking']:
            performance = results['benchmarking']['performance']
            if performance == 'Poor':
                recommendations.append("CRITICAL: Carbon intensity significantly exceeds industry benchmarks. Major design changes recommended.")
            elif performance == 'Average':
                recommendations.append("Carbon performance is average. Target 20-30% reduction through material optimization.")
        
        return recommendations
    
    def compare_scenarios(self, baseline: List[MaterialCarbon], 
                         alternative: List[MaterialCarbon],
                         scenario_name: str = "Alternative") -> Dict[str, Any]:
        """Compare carbon between baseline and alternative design"""
        
        baseline_results = self.calculate_carbon(baseline)
        alternative_results = self.calculate_carbon(alternative)
        
        baseline_total = baseline_results['summary']['total_carbon']
        alternative_total = alternative_results['summary']['total_carbon']
        
        reduction = baseline_total - alternative_total
        reduction_pct = (reduction / baseline_total * 100) if baseline_total > 0 else 0
        
        return {
            'baseline': {
                'total': baseline_total,
                'details': baseline_results
            },
            'alternative': {
                'name': scenario_name,
                'total': alternative_total,
                'details': alternative_results
            },
            'comparison': {
                'reduction': round(reduction, 2),
                'reduction_percentage': round(reduction_pct, 2),
                'recommendation': scenario_name if reduction > 0 else 'Baseline'
            }
        }
    
    def estimate_from_boq(self, boq_items: List[Dict[str, Any]]) -> List[MaterialCarbon]:
        """Convert BOQ items to materials list for carbon calculation"""
        
        materials = []
        
        for item in boq_items:
            item_code = item.get('item_code', '')
            quantity = item.get('quantity', 0)
            
            if item_code in self.carbon_coefficients:
                coef_data = self.carbon_coefficients[item_code]
                materials.append(MaterialCarbon(
                    material=item_code,
                    quantity=quantity,
                    unit=coef_data['unit'],
                    carbon_coefficient=coef_data['coefficient'],
                    category=coef_data['category']
                ))
        
        return materials
