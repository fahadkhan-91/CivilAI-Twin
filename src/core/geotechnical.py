"""
Geotechnical analysis module for CivilAI Twin
Soil analysis, foundation design, and settlement prediction
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from loguru import logger


@dataclass
class SoilLayer:
    """Soil layer properties"""
    depth_from: float  # m
    depth_to: float    # m
    soil_type: str
    unit_weight: float  # kN/m³
    cohesion: float    # kPa
    friction_angle: float  # degrees
    spt_n: int         # SPT N-value
    moisture_content: float  # %


@dataclass
class FoundationGeometry:
    """Foundation geometry"""
    type: str  # shallow, deep, pile
    width: float   # m
    length: float  # m
    depth: float   # m


class GeotechnicalAnalyzer:
    """Geotechnical analysis engine"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.soil_classification = config_manager.get('analysis.geotechnical.soil_classification', 'USCS')
        self.settlement_limit = config_manager.get('analysis.geotechnical.settlement_limit_mm', 25)
        
        # Bearing capacity factors (Terzaghi)
        self.bearing_factors = {
            0: {'Nc': 5.7, 'Nq': 1.0, 'Ng': 0.0},
            5: {'Nc': 7.3, 'Nq': 1.6, 'Ng': 0.5},
            10: {'Nc': 9.6, 'Nq': 2.7, 'Ng': 1.2},
            15: {'Nc': 12.9, 'Nq': 4.4, 'Ng': 2.5},
            20: {'Nc': 17.7, 'Nq': 7.4, 'Ng': 5.0},
            25: {'Nc': 25.1, 'Nq': 12.7, 'Ng': 9.7},
            30: {'Nc': 37.2, 'Nq': 22.5, 'Ng': 19.7},
            35: {'Nc': 57.8, 'Nq': 41.4, 'Ng': 42.4},
            40: {'Nc': 95.7, 'Nq': 81.3, 'Ng': 100.4},
            45: {'Nc': 172.3, 'Nq': 173.3, 'Ng': 297.5}
        }
    
    def analyze_foundation(self, soil_layers: List[SoilLayer], foundation: FoundationGeometry, 
                          applied_load: float, water_table_depth: float = 10.0) -> Dict[str, Any]:
        """
        Perform foundation analysis
        
        Args:
            soil_layers: List of soil layers
            foundation: Foundation geometry
            applied_load: Applied vertical load (kN)
            water_table_depth: Depth to water table (m)
        
        Returns:
            Analysis results dictionary
        """
        
        logger.info(f"Starting geotechnical analysis for {foundation.type} foundation")
        
        results = {
            'summary': {
                'foundation_type': foundation.type,
                'dimensions': f"{foundation.width}m x {foundation.length}m @ {foundation.depth}m depth",
                'applied_load': applied_load,
                'water_table_depth': water_table_depth
            },
            'bearing_capacity': {},
            'settlement': {},
            'stability': {},
            'recommendations': []
        }
        
        # Find founding layer
        founding_layer = self._get_founding_layer(soil_layers, foundation.depth)
        
        if founding_layer:
            # Calculate bearing capacity
            bearing_results = self._calculate_bearing_capacity(
                founding_layer, foundation, water_table_depth, applied_load
            )
            results['bearing_capacity'] = bearing_results
            
            # Calculate settlement
            settlement_results = self._calculate_settlement(
                soil_layers, foundation, applied_load
            )
            results['settlement'] = settlement_results
            
            # Stability checks
            stability_results = self._check_stability(
                founding_layer, foundation, applied_load, bearing_results['ultimate_capacity']
            )
            results['stability'] = stability_results
            
            # Overall assessment
            results['summary']['status'] = self._determine_status(results)
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results)
        else:
            results['summary']['status'] = 'ERROR'
            results['recommendations'] = ['Unable to determine founding layer properties']
        
        logger.info(f"Geotechnical analysis completed. Status: {results['summary']['status']}")
        
        return results
    
    def _get_founding_layer(self, soil_layers: List[SoilLayer], depth: float) -> SoilLayer:
        """Get soil layer at foundation depth"""
        for layer in soil_layers:
            if layer.depth_from <= depth < layer.depth_to:
                return layer
        return soil_layers[-1] if soil_layers else None
    
    def _calculate_bearing_capacity(self, soil: SoilLayer, foundation: FoundationGeometry, 
                                   water_table_depth: float, applied_load: float = 0) -> Dict[str, Any]:
        """Calculate ultimate and allowable bearing capacity"""
        
        # Get bearing capacity factors
        phi = soil.friction_angle
        factors = self._interpolate_bearing_factors(phi)
        
        # Foundation parameters
        B = foundation.width
        D = foundation.depth
        gamma = soil.unit_weight
        c = soil.cohesion
        
        # Adjust unit weight if below water table
        if D > water_table_depth:
            gamma_eff = gamma - 10  # Submerged unit weight
        else:
            gamma_eff = gamma
        
        # Terzaghi's bearing capacity equation
        q_ult = (c * factors['Nc'] + 
                gamma * D * factors['Nq'] + 
                0.5 * gamma_eff * B * factors['Ng'])
        
        # Factor of safety
        FOS = 3.0
        q_allow = q_ult / FOS
        
        # Applied pressure
        A = foundation.width * foundation.length
        q_applied = (applied_load / A) if A > 0 else 0
        
        # Utilization
        utilization = q_applied / q_allow if q_allow > 0 else 0
        
        return {
            'ultimate_capacity': round(q_ult, 2),
            'allowable_capacity': round(q_allow, 2),
            'applied_pressure': round(q_applied, 2),
            'factor_of_safety': FOS,
            'utilization': round(utilization, 3),
            'status': 'PASS' if utilization <= 1.0 else 'FAIL',
            'bearing_factors': factors
        }
    
    def _interpolate_bearing_factors(self, phi: float) -> Dict[str, float]:
        """Interpolate bearing capacity factors"""
        
        phi_rounded = int(phi / 5) * 5
        phi_rounded = max(0, min(45, phi_rounded))
        
        return self.bearing_factors[phi_rounded]
    
    def _calculate_settlement(self, soil_layers: List[SoilLayer], foundation: FoundationGeometry,
                            load: float) -> Dict[str, Any]:
        """Calculate foundation settlement"""
        
        # Applied stress
        A = foundation.width * foundation.length
        q = load / A if A > 0 else 0
        
        # Simplified elastic settlement (Schmertmann method approximation)
        B = foundation.width
        L = foundation.length
        
        # Influence depth
        z_inf = 2 * B
        
        # Calculate settlement for each layer within influence zone
        total_settlement = 0
        
        for layer in soil_layers:
            if layer.depth_from < foundation.depth + z_inf:
                # Layer thickness within influence zone
                z_top = max(layer.depth_from, foundation.depth)
                z_bottom = min(layer.depth_to, foundation.depth + z_inf)
                dz = z_bottom - z_top
                
                if dz > 0:
                    # Estimate modulus from SPT
                    E_s = self._estimate_modulus(layer)
                    
                    # Stress increase (simplified)
                    z_mid = (z_top + z_bottom) / 2 - foundation.depth
                    I_z = 1 / (1 + (z_mid / B)**2)  # Boussinesq influence factor
                    delta_sigma = q * I_z
                    
                    # Settlement of layer
                    settlement_layer = (delta_sigma * dz * 1000) / E_s  # mm
                    total_settlement += settlement_layer
        
        # Immediate settlement (elastic)
        immediate_settlement = total_settlement
        
        # Consolidation settlement (simplified for cohesive soils)
        consolidation_settlement = 0
        for layer in soil_layers:
            if 'clay' in layer.soil_type.lower() or 'silt' in layer.soil_type.lower():
                consolidation_settlement += immediate_settlement * 0.5  # Rough estimate
        
        total_settlement += consolidation_settlement
        
        # Check against limit
        settlement_ratio = total_settlement / self.settlement_limit
        
        return {
            'immediate_settlement': round(immediate_settlement, 2),
            'consolidation_settlement': round(consolidation_settlement, 2),
            'total_settlement': round(total_settlement, 2),
            'settlement_limit': self.settlement_limit,
            'utilization': round(settlement_ratio, 3),
            'status': 'PASS' if settlement_ratio <= 1.0 else 'FAIL'
        }
    
    def _estimate_modulus(self, layer: SoilLayer) -> float:
        """Estimate soil modulus from SPT N-value"""
        
        # Empirical correlations (kPa)
        if 'sand' in layer.soil_type.lower():
            E_s = 500 * layer.spt_n  # Sandy soils
        elif 'clay' in layer.soil_type.lower():
            E_s = 300 * layer.spt_n  # Clayey soils
        else:
            E_s = 400 * layer.spt_n  # Mixed soils
        
        return max(E_s, 5000)  # Minimum 5 MPa
    
    def _check_stability(self, soil: SoilLayer, foundation: FoundationGeometry,
                        load: float, q_ult: float) -> Dict[str, Any]:
        """Check foundation stability"""
        
        A = foundation.width * foundation.length
        q_applied = load / A if A > 0 else 0
        
        # Bearing capacity check
        FOS_bearing = q_ult / q_applied if q_applied > 0 else 10
        
        # Sliding check (simplified)
        friction_coef = np.tan(np.radians(soil.friction_angle))
        resistance = load * friction_coef + soil.cohesion * A
        lateral_force = load * 0.1  # Assumed 10% lateral force
        FOS_sliding = resistance / lateral_force if lateral_force > 0 else 10
        
        # Overturning check (simplified)
        moment_resisting = load * foundation.width / 2
        moment_overturning = lateral_force * 3  # Assumed height
        FOS_overturning = moment_resisting / moment_overturning if moment_overturning > 0 else 10
        
        return {
            'bearing_fos': round(FOS_bearing, 2),
            'sliding_fos': round(FOS_sliding, 2),
            'overturning_fos': round(FOS_overturning, 2),
            'bearing_status': 'PASS' if FOS_bearing >= 3.0 else 'FAIL',
            'sliding_status': 'PASS' if FOS_sliding >= 1.5 else 'FAIL',
            'overturning_status': 'PASS' if FOS_overturning >= 2.0 else 'FAIL'
        }
    
    def _determine_status(self, results: Dict[str, Any]) -> str:
        """Determine overall foundation status"""
        
        checks = [
            results['bearing_capacity']['status'],
            results['settlement']['status'],
            results['stability']['bearing_status'],
            results['stability']['sliding_status'],
            results['stability']['overturning_status']
        ]
        
        if all(status == 'PASS' for status in checks):
            return 'PASS'
        elif any(status == 'FAIL' for status in checks):
            return 'FAIL'
        else:
            return 'WARNING'
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate geotechnical recommendations"""
        
        recommendations = []
        
        status = results['summary']['status']
        
        if status == 'PASS':
            recommendations.append("Foundation design is adequate for the given soil conditions.")
        elif status == 'FAIL':
            recommendations.append("CRITICAL: Foundation design does not meet safety requirements.")
        
        # Bearing capacity recommendations
        bc_util = results['bearing_capacity']['utilization']
        if bc_util > 1.0:
            recommendations.append("Increase foundation size or improve soil bearing capacity.")
        elif bc_util > 0.85:
            recommendations.append("Consider increasing foundation size for better safety margin.")
        
        # Settlement recommendations
        settlement = results['settlement']['total_settlement']
        if settlement > self.settlement_limit:
            recommendations.append(f"Expected settlement ({settlement:.1f}mm) exceeds limit. Consider deep foundations or ground improvement.")
        elif settlement > self.settlement_limit * 0.8:
            recommendations.append("Settlement is approaching the limit. Monitor during construction.")
        
        # Stability recommendations
        stability = results['stability']
        if stability['sliding_fos'] < 1.5:
            recommendations.append("Improve sliding resistance with keys or larger base.")
        if stability['overturning_fos'] < 2.0:
            recommendations.append("Increase foundation width to prevent overturning.")
        
        # General recommendations
        recommendations.append("Conduct thorough site investigation to verify soil parameters.")
        recommendations.append("Consider seasonal water table variations in final design.")
        recommendations.append("Implement appropriate drainage system around foundation.")
        recommendations.append("Monitor settlement during and after construction.")
        
        return recommendations
    
    def soil_classification(self, grain_size_dist: Dict[str, float]) -> str:
        """Classify soil based on grain size distribution (USCS)"""
        
        gravel = grain_size_dist.get('gravel', 0)
        sand = grain_size_dist.get('sand', 0)
        silt = grain_size_dist.get('silt', 0)
        clay = grain_size_dist.get('clay', 0)
        
        if gravel > 50:
            return "Gravel (G)"
        elif sand > 50:
            return "Sand (S)"
        elif silt > clay:
            return "Silt (M)"
        else:
            return "Clay (C)"
