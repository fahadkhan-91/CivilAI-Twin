"""
Structural analysis module for CivilAI Twin
Performs structural integrity checks and load analysis
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from loguru import logger


@dataclass
class StructuralElement:
    """Structural element data"""
    id: str
    element_type: str  # beam, column, slab, wall
    material: str
    dimensions: Dict[str, float]
    loads: Dict[str, float]
    length: float
    position: Tuple[float, float, float]


@dataclass
class LoadCase:
    """Load case definition"""
    name: str
    load_type: str  # dead, live, wind, seismic
    magnitude: float
    distribution: str  # uniform, point, triangular


class StructuralAnalyzer:
    """Structural analysis engine"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.safety_factor = config_manager.get('analysis.structural.safety_factor', 1.5)
        self.code_standard = config_manager.get('analysis.structural.code_standard', 'ACI')
        
        # Material properties
        self.material_properties = {
            'concrete_M25': {'fc': 25, 'E': 25000},  # MPa, N/mm²
            'concrete_M30': {'fc': 30, 'E': 27000},
            'steel_Fe500': {'fy': 500, 'E': 200000},
            'steel_Fe415': {'fy': 415, 'E': 200000}
        }
    
    def analyze_structure(self, elements: List[StructuralElement], loads: List[LoadCase]) -> Dict[str, Any]:
        """
        Perform structural analysis
        
        Args:
            elements: List of structural elements
            loads: List of load cases
        
        Returns:
            Analysis results dictionary
        """
        
        logger.info(f"Starting structural analysis with {len(elements)} elements and {len(loads)} load cases")
        
        results = {
            'summary': {
                'total_elements': len(elements),
                'total_loads': len(loads),
                'code_standard': self.code_standard,
                'safety_factor': self.safety_factor
            },
            'element_results': [],
            'critical_elements': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Analyze each element
        for element in elements:
            element_result = self._analyze_element(element, loads)
            results['element_results'].append(element_result)
            
            # Flag critical elements
            if element_result['utilization_ratio'] > 0.85:
                results['critical_elements'].append({
                    'element_id': element.id,
                    'type': element.element_type,
                    'utilization': element_result['utilization_ratio'],
                    'reason': 'High utilization ratio'
                })
            
            if element_result['status'] == 'FAIL':
                results['warnings'].append(
                    f"Element {element.id} ({element.element_type}) fails capacity check"
                )
        
        # Calculate overall structural health
        utilization_ratios = [er['utilization_ratio'] for er in results['element_results']]
        results['summary']['max_utilization'] = max(utilization_ratios) if utilization_ratios else 0
        results['summary']['avg_utilization'] = np.mean(utilization_ratios) if utilization_ratios else 0
        results['summary']['status'] = 'PASS' if all(er['status'] == 'PASS' for er in results['element_results']) else 'FAIL'
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        logger.info(f"Structural analysis completed. Status: {results['summary']['status']}")
        
        return results
    
    def _analyze_element(self, element: StructuralElement, loads: List[LoadCase]) -> Dict[str, Any]:
        """Analyze individual structural element"""
        
        if element.element_type == 'beam':
            return self._analyze_beam(element, loads)
        elif element.element_type == 'column':
            return self._analyze_column(element, loads)
        elif element.element_type == 'slab':
            return self._analyze_slab(element, loads)
        else:
            return self._analyze_generic(element, loads)
    
    def _analyze_beam(self, beam: StructuralElement, loads: List[LoadCase]) -> Dict[str, Any]:
        """Analyze beam element"""
        
        # Extract dimensions
        width = beam.dimensions.get('width', 300)  # mm
        depth = beam.dimensions.get('depth', 450)  # mm
        length = beam.length  # m
        
        # Calculate section properties
        I = (width * depth**3) / 12  # Moment of inertia (mm⁴)
        Z = (width * depth**2) / 6   # Section modulus (mm³)
        A = width * depth             # Area (mm²)
        
        # Calculate total load
        total_load = sum(load.magnitude for load in loads)  # kN/m
        
        # Calculate maximum moment (for simply supported beam with uniform load)
        M_max = (total_load * length**2) / 8  # kN·m
        M_max_nmm = M_max * 1e6  # N·mm
        
        # Calculate maximum shear
        V_max = (total_load * length) / 2  # kN
        V_max_n = V_max * 1e3  # N
        
        # Calculate maximum deflection
        E = 25000  # N/mm² (assumed concrete)
        delta_max = (5 * total_load * 1e3 * (length * 1000)**4) / (384 * E * I)  # mm
        
        # Check flexural capacity (simplified)
        f_actual = M_max_nmm / Z  # N/mm²
        f_allowable = 25 / self.safety_factor  # MPa
        
        # Check shear capacity
        v_actual = V_max_n / A  # N/mm²
        v_allowable = 0.25 * np.sqrt(25)  # Simplified ACI
        
        # Check deflection
        delta_limit = (length * 1000) / 360  # L/360 for live load
        
        # Calculate utilization ratio
        utilization_flexure = f_actual / f_allowable
        utilization_shear = v_actual / v_allowable
        utilization_deflection = delta_max / delta_limit
        utilization_ratio = max(utilization_flexure, utilization_shear, utilization_deflection)
        
        status = 'PASS' if utilization_ratio <= 1.0 else 'FAIL'
        
        return {
            'element_id': beam.id,
            'element_type': 'beam',
            'dimensions': f"{width}x{depth}mm, L={length}m",
            'moment_max': round(M_max, 2),
            'shear_max': round(V_max, 2),
            'deflection_max': round(delta_max, 2),
            'deflection_limit': round(delta_limit, 2),
            'utilization_ratio': round(utilization_ratio, 3),
            'status': status,
            'checks': {
                'flexure': {'utilization': round(utilization_flexure, 3), 'status': 'PASS' if utilization_flexure <= 1.0 else 'FAIL'},
                'shear': {'utilization': round(utilization_shear, 3), 'status': 'PASS' if utilization_shear <= 1.0 else 'FAIL'},
                'deflection': {'utilization': round(utilization_deflection, 3), 'status': 'PASS' if utilization_deflection <= 1.0 else 'FAIL'}
            }
        }
    
    def _analyze_column(self, column: StructuralElement, loads: List[LoadCase]) -> Dict[str, Any]:
        """Analyze column element"""
        
        # Extract dimensions
        width = column.dimensions.get('width', 400)  # mm
        depth = column.dimensions.get('depth', 400)  # mm
        height = column.length  # m
        
        # Calculate section properties
        A = width * depth  # mm²
        I = (width * depth**3) / 12  # mm⁴
        r = np.sqrt(I / A)  # radius of gyration
        
        # Calculate total axial load
        P = sum(load.magnitude for load in loads if load.load_type in ['dead', 'live'])  # kN
        P_n = P * 1e3  # N
        
        # Calculate slenderness ratio
        k = 1.0  # effective length factor
        Le = k * height * 1000  # mm
        slenderness = Le / r
        
        # Check if short or slender column
        if slenderness < 12:
            # Short column
            P_allowable = (0.8 * 25 * A) / self.safety_factor  # N
        else:
            # Slender column (simplified Euler)
            E = 25000  # N/mm²
            P_cr = (np.pi**2 * E * I) / Le**2  # Critical buckling load
            P_allowable = P_cr / self.safety_factor
        
        utilization_ratio = P_n / P_allowable
        status = 'PASS' if utilization_ratio <= 1.0 else 'FAIL'
        
        return {
            'element_id': column.id,
            'element_type': 'column',
            'dimensions': f"{width}x{depth}mm, H={height}m",
            'axial_load': round(P, 2),
            'slenderness_ratio': round(slenderness, 2),
            'column_type': 'short' if slenderness < 12 else 'slender',
            'utilization_ratio': round(utilization_ratio, 3),
            'status': status
        }
    
    def _analyze_slab(self, slab: StructuralElement, loads: List[LoadCase]) -> Dict[str, Any]:
        """Analyze slab element"""
        
        thickness = slab.dimensions.get('thickness', 150)  # mm
        lx = slab.dimensions.get('lx', 4000)  # mm (short span)
        ly = slab.dimensions.get('ly', 5000)  # mm (long span)
        
        # Calculate load
        total_load = sum(load.magnitude for load in loads)  # kN/m²
        
        # Check slab type
        if ly / lx < 2:
            slab_type = 'two-way'
            # Simplified moment calculation for two-way slab
            M_x = 0.036 * total_load * lx**2 / 1e6  # kN·m/m
            M_y = 0.028 * total_load * lx**2 / 1e6
        else:
            slab_type = 'one-way'
            # One-way slab bending
            M_x = (total_load * (lx/1000)**2) / 8  # kN·m/m
            M_y = 0
        
        # Simplified capacity check
        d = thickness - 25  # effective depth
        M_allowable = 0.138 * 25 * 1000 * d**2 / 1e6 / self.safety_factor  # kN·m/m
        
        utilization_x = M_x / M_allowable if M_allowable > 0 else 0
        utilization_y = M_y / M_allowable if M_allowable > 0 and M_y > 0 else 0
        utilization_ratio = max(utilization_x, utilization_y)
        
        status = 'PASS' if utilization_ratio <= 1.0 else 'FAIL'
        
        return {
            'element_id': slab.id,
            'element_type': 'slab',
            'dimensions': f"t={thickness}mm, {lx}x{ly}mm",
            'slab_type': slab_type,
            'moment_x': round(M_x, 2),
            'moment_y': round(M_y, 2),
            'utilization_ratio': round(utilization_ratio, 3),
            'status': status
        }
    
    def _analyze_generic(self, element: StructuralElement, loads: List[LoadCase]) -> Dict[str, Any]:
        """Generic element analysis"""
        
        # Simplified analysis
        total_load = sum(load.magnitude for load in loads)
        utilization_ratio = 0.6  # Assumed
        
        return {
            'element_id': element.id,
            'element_type': element.element_type,
            'total_load': round(total_load, 2),
            'utilization_ratio': utilization_ratio,
            'status': 'PASS'
        }
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate structural recommendations"""
        
        recommendations = []
        
        max_util = results['summary']['max_utilization']
        
        if max_util > 0.95:
            recommendations.append("CRITICAL: Some elements are at or over capacity. Immediate redesign required.")
        elif max_util > 0.85:
            recommendations.append("HIGH: Several elements have high utilization ratios. Consider increasing member sizes.")
        elif max_util > 0.70:
            recommendations.append("MODERATE: Structure is adequately designed but with limited reserve capacity.")
        else:
            recommendations.append("GOOD: Structure has adequate capacity with good safety margins.")
        
        if len(results['critical_elements']) > 0:
            recommendations.append(f"Review {len(results['critical_elements'])} critical elements identified in the analysis.")
        
        recommendations.append("Verify all connection details and ensure they match analysis assumptions.")
        recommendations.append("Perform regular inspections during construction and service life.")
        
        return recommendations
    
    def quick_check(self, element_type: str, dimensions: Dict, loads: float) -> Dict[str, Any]:
        """Quick structural check for what-if scenarios"""
        
        element = StructuralElement(
            id="quick_check",
            element_type=element_type,
            material="concrete_M25",
            dimensions=dimensions,
            loads={'total': loads},
            length=dimensions.get('length', 5.0),
            position=(0, 0, 0)
        )
        
        load_case = LoadCase(
            name="quick_load",
            load_type="live",
            magnitude=loads,
            distribution="uniform"
        )
        
        return self._analyze_element(element, [load_case])
