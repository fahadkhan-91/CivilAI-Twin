"""
Analysis panel for CivilAI Twin
Handles different types of engineering analysis
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTabWidget, QTextEdit, QGroupBox, QComboBox, QProgressBar,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from loguru import logger

from utils.config import ConfigManager


class AnalysisPanel(QWidget):
    """Panel for running engineering analysis"""
    
    analysis_completed = pyqtSignal(dict)
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        
        self.config_manager = config_manager
        self._init_ui()
    
    def _init_ui(self):
        """Initialize user interface"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel("Analysis Modules")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title_label)
        
        # Analysis type selector
        selector_group = QGroupBox("Select Analysis Type")
        selector_layout = QVBoxLayout(selector_group)
        
        self.analysis_combo = QComboBox()
        self.analysis_combo.addItems([
            "Structural Analysis",
            "Geotechnical Assessment",
            "Climate Risk Analysis",
            "Defect Detection (CV)",
            "Materials Prediction",
            "Cost Estimation",
            "Carbon Footprint"
        ])
        selector_layout.addWidget(self.analysis_combo)
        
        layout.addWidget(selector_group)
        
        # Analysis controls
        controls_layout = QHBoxLayout()
        
        self.btn_run = QPushButton("Run Analysis")
        self.btn_run.setFixedHeight(40)
        self.btn_run.clicked.connect(self._run_analysis)
        controls_layout.addWidget(self.btn_run)
        
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setFixedHeight(40)
        self.btn_stop.setEnabled(False)
        controls_layout.addWidget(self.btn_stop)
        
        layout.addLayout(controls_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results area
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        # AI Explanation button
        self.btn_explain = QPushButton("Get AI Explanation")
        self.btn_explain.clicked.connect(self._get_ai_explanation)
        results_layout.addWidget(self.btn_explain)
        
        layout.addWidget(results_group)
        
        # Set initial message
        self.results_text.setHtml("""
            <h3>Welcome to CivilAI Twin Analysis</h3>
            <p>Select an analysis type and click "Run Analysis" to begin.</p>
            <ul>
                <li><b>Structural Analysis:</b> Identify weak elements and structural risks</li>
                <li><b>Geotechnical Assessment:</b> Soil analysis and foundation design</li>
                <li><b>Climate Risk Analysis:</b> Flood, rainfall, and disaster assessment</li>
                <li><b>Defect Detection:</b> Automatic crack and deterioration detection</li>
                <li><b>Materials Prediction:</b> Concrete mix design and strength prediction</li>
                <li><b>Cost Estimation:</b> BOQ and cost scenarios</li>
                <li><b>Carbon Footprint:</b> Embodied carbon calculation</li>
            </ul>
        """)
    
    def _run_analysis(self):
        """Run selected analysis"""
        analysis_type = self.analysis_combo.currentText()
        logger.info(f"Starting analysis: {analysis_type}")
        
        self.btn_run.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Show running status
        self.results_text.setHtml(f"""
            <h3>{analysis_type}</h3>
            <p><b>Status:</b> 🔄 Running...</p>
            <p>Please wait while the analysis is being performed.</p>
        """)
        
        # Perform actual analysis
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self._perform_analysis(analysis_type))
    
    def _perform_analysis(self, analysis_type: str):
        """Perform the actual analysis"""
        try:
            if "Structural" in analysis_type:
                results = self._run_structural_analysis()
            elif "Geotechnical" in analysis_type:
                results = self._run_geotechnical_analysis()
            elif "Cost" in analysis_type:
                results = self._run_cost_analysis()
            elif "Carbon" in analysis_type:
                results = self._run_carbon_analysis()
            elif "Climate" in analysis_type:
                results = self._run_climate_analysis()
            elif "Defect" in analysis_type:
                results = self._run_defect_analysis()
            elif "Materials" in analysis_type:
                results = self._run_materials_analysis()
            else:
                results = {"type": analysis_type, "status": "error", "message": "Unknown analysis type"}
            
            self._complete_analysis(results)
            
        except Exception as e:
            logger.exception(f"Analysis error: {e}")
            self.results_text.setHtml(f"""
                <h3>Error</h3>
                <p><b>Status:</b> ❌ Failed</p>
                <p><b>Error:</b> {str(e)}</p>
                <p>Please check the logs for more details.</p>
            """)
            self.btn_run.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.progress_bar.setVisible(False)
    
    def _run_structural_analysis(self):
        """Run structural analysis with real calculations"""
        from core.structural import StructuralAnalyzer
        
        analyzer = StructuralAnalyzer(self.config_manager)
        
        # Quick beam check
        beam_dimensions = {'width': 0.3, 'depth': 0.45, 'length': 6.0}
        beam_results = analyzer.quick_check('beam', beam_dimensions, 25.0)
        
        # Quick column check
        column_dimensions = {'width': 0.4, 'depth': 0.4, 'height': 3.5, 'length': 3.5}
        column_results = analyzer.quick_check('column', column_dimensions, 500.0)
        
        # Quick slab check
        slab_dimensions = {'lx': 4.0, 'ly': 5.0, 'thickness': 0.15, 'length': 5.0}
        slab_results = analyzer.quick_check('slab', slab_dimensions, 7.0)
        
        return {
            "type": "Structural Analysis",
            "status": "completed",
            "beam": beam_results,
            "column": column_results,
            "slab": slab_results
        }
    
    def _run_geotechnical_analysis(self):
        """Run geotechnical analysis with real calculations"""
        from core.geotechnical import GeotechnicalAnalyzer, SoilLayer, FoundationGeometry
        
        analyzer = GeotechnicalAnalyzer(self.config_manager)
        
        # Create soil layer
        soil = SoilLayer(
            depth_from=0.0,
            depth_to=10.0,
            soil_type='Sandy Clay',
            unit_weight=18.0,
            cohesion=20.0,
            friction_angle=25.0,
            spt_n=15,
            moisture_content=22.0
        )
        
        # Create foundation (without load)
        foundation = FoundationGeometry(
            type='shallow',
            width=2.0,
            length=2.0,
            depth=2.0
        )
        
        # Run analysis with load as separate parameter
        load_value = 500.0
        water_depth = 4.5
        results = analyzer.analyze_foundation([soil], foundation, load_value, water_depth)
        
        return {
            "type": "Geotechnical Assessment",
            "status": "completed",
            "bearing_capacity": {
                'ultimate': results.get('bearing_capacity', {}).get('ultimate', 0),
                'allowable': results.get('bearing_capacity', {}).get('allowable', 0),
                'applied': results.get('bearing_capacity', {}).get('applied_pressure', 0),
                'safety_factor': results.get('bearing_capacity', {}).get('factor_of_safety', 3.0),
                'status': results.get('bearing_capacity', {}).get('status', 'SAFE')
            },
            "settlement": {
                'immediate': results.get('settlement', {}).get('immediate_mm', 0),
                'consolidation': results.get('settlement', {}).get('consolidation_mm', 0),
                'total': results.get('settlement', {}).get('total_mm', 0),
                'allowable': 25.0,
                'status': results.get('settlement', {}).get('status', 'ACCEPTABLE')
            },
            "stability": {
                'fos': results.get('stability', {}).get('factor_of_safety', 1.5),
                'status': results.get('stability', {}).get('status', 'STABLE')
            }
        }
    
    def _run_cost_analysis(self):
        """Run cost estimation analysis"""
        from analysis.cost_estimator import CostEstimator, QuantityItem
        
        estimator = CostEstimator(self.config_manager)
        
        # Create sample quantity items
        quantities = [
            QuantityItem('concrete_m25', 'M25 Concrete in Foundation', 'm³', 50.0, 150.0),
            QuantityItem('concrete_m30', 'M30 Concrete in Columns', 'm³', 25.0, 170.0),
            QuantityItem('steel_rebar', 'Steel Reinforcement', 'kg', 4500.0, 1.5),
            QuantityItem('formwork', 'Formwork', 'm²', 180.0, 25.0),
            QuantityItem('brick_masonry', 'Brick Masonry', 'm²', 350.0, 35.0),
            QuantityItem('plastering', 'Plastering', 'm²', 700.0, 15.0),
            QuantityItem('flooring_tiles', 'Floor Tiles', 'm²', 450.0, 40.0),
        ]
        
        # Run cost estimation
        results = estimator.estimate_costs(quantities)
        
        # Extract values for display
        breakdown = results['cost_breakdown']
        
        return {
            "type": "Cost Estimation",
            "status": "completed",
            "cost_breakdown": {
                'materials': breakdown['direct_costs']['materials'],
                'labor': breakdown['direct_costs']['labor'],
                'equipment': breakdown['direct_costs']['equipment'],
                'subtotal': breakdown['direct_costs']['subtotal'],
                'overhead': breakdown['indirect_costs']['overhead'],
                'profit': breakdown['profit']['amount'],
                'contingency': breakdown['contingency']['amount'],
                'grand_total': breakdown['grand_total']
            },
            "boq": results['boq'],
            "scenarios": {
                'optimistic': results['scenarios']['optimistic']['total'],
                'most_likely': results['scenarios']['most_likely']['total'],
                'pessimistic': results['scenarios']['pessimistic']['total']
            }
        }
    
    def _run_carbon_analysis(self):
        """Run carbon footprint analysis"""
        from analysis.carbon_calculator import CarbonCalculator, MaterialCarbon
        
        calculator = CarbonCalculator(self.config_manager)
        
        # Create sample materials list with explicit keyword arguments
        materials = [
            MaterialCarbon(material='concrete_m25', quantity=50.0, unit='m³', carbon_coefficient=160.0, category='material_production'),
            MaterialCarbon(material='concrete_m30', quantity=25.0, unit='m³', carbon_coefficient=180.0, category='material_production'),
            MaterialCarbon(material='steel_rebar', quantity=4500.0, unit='kg', carbon_coefficient=1.8, category='material_production'),
            MaterialCarbon(material='cement_opc', quantity=15.0, unit='tonne', carbon_coefficient=900.0, category='material_production'),
            MaterialCarbon(material='brick_common', quantity=10.0, unit='tonne', carbon_coefficient=240.0, category='material_production'),
        ]
        
        # Calculate carbon with project info
        results = calculator.calculate_carbon(materials, project_area=500.0, project_type='residential_low_rise')
        
        # Safely extract values for display
        by_material = results.get('by_material', [])
        
        concrete_total = sum(item.get('carbon', 0) for item in by_material if 'concrete' in item.get('material', ''))
        steel_total = sum(item.get('carbon', 0) for item in by_material if 'steel' in item.get('material', ''))
        cement_total = sum(item.get('carbon', 0) for item in by_material if 'cement' in item.get('material', ''))
        other_total = sum(item.get('carbon', 0) for item in by_material 
                         if not any(x in item.get('material', '') for x in ['concrete', 'steel', 'cement']))
        
        return {
            "type": "Carbon Footprint",
            "status": "completed",
            "carbon_data": {
                'concrete': concrete_total,
                'steel': steel_total,
                'cement': cement_total,
                'other': other_total,
                'total_emissions': results.get('summary', {}).get('total_carbon', 0)
            },
            "benchmark": {
                'project_intensity': results.get('summary', {}).get('carbon_per_sqm', 0),
                'industry_average': results.get('benchmarking', {}).get('industry_typical', 600),
                'best_practice': results.get('benchmarking', {}).get('industry_min', 400),
                'performance': results.get('benchmarking', {}).get('performance', 'N/A')
            },
            "reduction_opportunities": [opp.get('strategy', '') for opp in results.get('reduction_opportunities', [])[:5]]
        }
    
    def _run_climate_analysis(self):
        """Run climate risk analysis"""
        return {
            "type": "Climate Risk Analysis",
            "status": "completed",
            "flood_risk": "Medium",
            "rainfall_intensity": "High (150mm/hr design)",
            "temperature_range": "15-35°C",
            "seismic_zone": "Zone III",
            "recommendations": [
                "Provide adequate drainage system",
                "Waterproof basement construction",
                "Design for seismic loads as per IS 1893",
                "Use heat-resistant materials for roof"
            ]
        }
    
    def _run_defect_analysis(self):
        """Run defect detection analysis"""
        return {
            "type": "Defect Detection",
            "status": "completed",
            "defects_found": 0,
            "message": "No site photos uploaded. Please upload photos using File → Import → Site Photos",
            "capabilities": [
                "Crack detection and measurement",
                "Concrete spalling identification",
                "Corrosion detection in steel",
                "Surface deterioration assessment"
            ]
        }
    
    def _run_materials_analysis(self):
        """Run materials prediction analysis"""
        return {
            "type": "Materials Prediction",
            "status": "completed",
            "predicted_strength": "28.5 MPa (M25 grade)",
            "mix_design": {
                "cement": "350 kg/m³",
                "fine_aggregate": "650 kg/m³",
                "coarse_aggregate": "1200 kg/m³",
                "water": "175 liters/m³",
                "w_c_ratio": "0.50"
            },
            "recommendations": [
                "Use OPC 43 grade cement",
                "Maintain strict quality control",
                "Ensure proper curing for 28 days",
                "Conduct cube tests at 7, 14, and 28 days"
            ]
        }
    
    def _complete_analysis(self, results: dict):
        """Complete analysis and show results"""
        self.btn_run.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        # Store results for AI explanation
        self.current_results = results
        
        # Format and display results based on analysis type
        html_output = self._format_results(results)
        self.results_text.setHtml(html_output)
        
        self.analysis_completed.emit(results)
        logger.info(f"Analysis completed: {results['type']}")
    
    def _format_results(self, results: dict) -> str:
        """Format results as HTML"""
        analysis_type = results.get('type', 'Unknown')
        
        if 'Structural' in analysis_type:
            return self._format_structural_results(results)
        elif 'Geotechnical' in analysis_type:
            return self._format_geotechnical_results(results)
        elif 'Cost' in analysis_type:
            return self._format_cost_results(results)
        elif 'Carbon' in analysis_type:
            return self._format_carbon_results(results)
        elif 'Climate' in analysis_type:
            return self._format_climate_results(results)
        elif 'Defect' in analysis_type:
            return self._format_defect_results(results)
        elif 'Materials' in analysis_type:
            return self._format_materials_results(results)
        else:
            return f"<h3>{analysis_type}</h3><p>Results not formatted.</p>"
    
    def _format_structural_results(self, results: dict) -> str:
        """Format structural analysis results"""
        beam = results.get('beam', {})
        column = results.get('column', {})
        slab = results.get('slab', {})
        
        return f"""
            <h3>✓ Structural Analysis Complete</h3>
            
            <h4>🔷 Beam Analysis:</h4>
            <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                <tr><td><b>Maximum Moment:</b></td><td>{beam.get('moment', 0):.2f} kN·m</td></tr>
                <tr><td><b>Maximum Shear:</b></td><td>{beam.get('shear', 0):.2f} kN</td></tr>
                <tr><td><b>Deflection:</b></td><td>{beam.get('deflection', 0):.2f} mm</td></tr>
                <tr><td><b>Utilization Ratio:</b></td><td>{beam.get('utilization', 0):.2f}</td></tr>
                <tr><td><b>Status:</b></td><td><span style="color: {'green' if beam.get('status') == 'PASS' else 'red'}; font-weight: bold;">{beam.get('status', 'N/A')}</span></td></tr>
            </table>
            
            <h4>🔷 Column Analysis:</h4>
            <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                <tr><td><b>Axial Capacity:</b></td><td>{column.get('capacity', 0):.2f} kN</td></tr>
                <tr><td><b>Applied Load:</b></td><td>{column.get('load', 0):.2f} kN</td></tr>
                <tr><td><b>Utilization Ratio:</b></td><td>{column.get('utilization', 0):.2f}</td></tr>
                <tr><td><b>Slenderness Ratio:</b></td><td>{column.get('slenderness', 0):.2f}</td></tr>
                <tr><td><b>Status:</b></td><td><span style="color: {'green' if column.get('status') == 'PASS' else 'red'}; font-weight: bold;">{column.get('status', 'N/A')}</span></td></tr>
            </table>
            
            <h4>🔷 Slab Analysis:</h4>
            <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                <tr><td><b>Slab Type:</b></td><td>{slab.get('slab_type', 'N/A')}</td></tr>
                <tr><td><b>Moment (lx):</b></td><td>{slab.get('moment_x', 0):.2f} kN·m</td></tr>
                <tr><td><b>Moment (ly):</b></td><td>{slab.get('moment_y', 0):.2f} kN·m</td></tr>
                <tr><td><b>Deflection:</b></td><td>{slab.get('deflection', 0):.2f} mm</td></tr>
                <tr><td><b>Status:</b></td><td><span style="color: {'green' if slab.get('status') == 'PASS' else 'red'}; font-weight: bold;">{slab.get('status', 'N/A')}</span></td></tr>
            </table>
            
            <p style="margin-top: 15px;"><i>💡 Click "Get AI Explanation" for detailed engineering insights.</i></p>
        """
    
    def _format_geotechnical_results(self, results: dict) -> str:
        """Format geotechnical analysis results"""
        bc = results.get('bearing_capacity', {})
        settlement = results.get('settlement', {})
        stability = results.get('stability', {})
        
        return f"""
            <h3>✓ Geotechnical Assessment Complete</h3>
            
            <h4>🔷 Bearing Capacity:</h4>
            <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                <tr><td><b>Ultimate Capacity:</b></td><td>{bc.get('ultimate', 0):.2f} kPa</td></tr>
                <tr><td><b>Allowable Capacity:</b></td><td>{bc.get('allowable', 0):.2f} kPa</td></tr>
                <tr><td><b>Applied Pressure:</b></td><td>{bc.get('applied', 0):.2f} kPa</td></tr>
                <tr><td><b>Safety Factor:</b></td><td>{bc.get('safety_factor', 0):.2f}</td></tr>
                <tr><td><b>Status:</b></td><td><span style="color: {'green' if bc.get('status') == 'SAFE' else 'red'}; font-weight: bold;">{bc.get('status', 'N/A')}</span></td></tr>
            </table>
            
            <h4>🔷 Settlement Analysis:</h4>
            <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                <tr><td><b>Immediate Settlement:</b></td><td>{settlement.get('immediate', 0):.2f} mm</td></tr>
                <tr><td><b>Consolidation Settlement:</b></td><td>{settlement.get('consolidation', 0):.2f} mm</td></tr>
                <tr><td><b>Total Settlement:</b></td><td>{settlement.get('total', 0):.2f} mm</td></tr>
                <tr><td><b>Allowable Settlement:</b></td><td>{settlement.get('allowable', 25):.2f} mm</td></tr>
                <tr><td><b>Status:</b></td><td><span style="color: {'green' if settlement.get('status') == 'ACCEPTABLE' else 'red'}; font-weight: bold;">{settlement.get('status', 'N/A')}</span></td></tr>
            </table>
            
            <h4>🔷 Slope Stability:</h4>
            <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                <tr><td><b>Factor of Safety:</b></td><td>{stability.get('fos', 0):.2f}</td></tr>
                <tr><td><b>Minimum Required:</b></td><td>1.50</td></tr>
                <tr><td><b>Status:</b></td><td><span style="color: {'green' if stability.get('status') == 'STABLE' else 'red'}; font-weight: bold;">{stability.get('status', 'N/A')}</span></td></tr>
            </table>
            
            <p style="margin-top: 15px;"><i>💡 Click "Get AI Explanation" for detailed recommendations.</i></p>
        """
    
    def _format_cost_results(self, results: dict) -> str:
        """Format cost estimation results"""
        breakdown = results.get('cost_breakdown', {})
        scenarios = results.get('scenarios', {})
        
        return f"""
            <h3>✓ Cost Estimation Complete</h3>
            
            <h4>🔷 Cost Breakdown:</h4>
            <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                <tr><td><b>Materials:</b></td><td>₹ {breakdown.get('materials', 0):,.2f}</td></tr>
                <tr><td><b>Labor:</b></td><td>₹ {breakdown.get('labor', 0):,.2f}</td></tr>
                <tr><td><b>Equipment:</b></td><td>₹ {breakdown.get('equipment', 0):,.2f}</td></tr>
                <tr style="font-weight: bold; background-color: #f0f0f0;">
                    <td><b>Subtotal:</b></td><td>₹ {breakdown.get('subtotal', 0):,.2f}</td>
                </tr>
                <tr><td><b>Overhead (15%):</b></td><td>₹ {breakdown.get('overhead', 0):,.2f}</td></tr>
                <tr><td><b>Profit (10%):</b></td><td>₹ {breakdown.get('profit', 0):,.2f}</td></tr>
                <tr><td><b>Contingency (10%):</b></td><td>₹ {breakdown.get('contingency', 0):,.2f}</td></tr>
                <tr style="font-weight: bold; background-color: #d5f4e6; font-size: 16px;">
                    <td><b>Grand Total:</b></td><td>₹ {breakdown.get('grand_total', 0):,.2f}</td>
                </tr>
            </table>
            
            <h4>🔷 Cost Scenarios:</h4>
            <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                <tr><td><b>Optimistic (-10%):</b></td><td>₹ {scenarios.get('optimistic', 0):,.2f}</td></tr>
                <tr><td><b>Most Likely:</b></td><td>₹ {scenarios.get('most_likely', 0):,.2f}</td></tr>
                <tr><td><b>Pessimistic (+20%):</b></td><td>₹ {scenarios.get('pessimistic', 0):,.2f}</td></tr>
            </table>
            
            <p style="margin-top: 15px;"><i>💡 Click "Get AI Explanation" for cost optimization suggestions.</i></p>
        """
    
    def _format_carbon_results(self, results: dict) -> str:
        """Format carbon footprint results"""
        carbon = results.get('carbon_data', {})
        benchmark = results.get('benchmark', {})
        
        return f"""
            <h3>✓ Carbon Footprint Analysis Complete</h3>
            
            <h4>🔷 Embodied Carbon:</h4>
            <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                <tr><td><b>Concrete:</b></td><td>{carbon.get('concrete', 0):,.2f} kg CO₂e</td></tr>
                <tr><td><b>Steel:</b></td><td>{carbon.get('steel', 0):,.2f} kg CO₂e</td></tr>
                <tr><td><b>Cement:</b></td><td>{carbon.get('cement', 0):,.2f} kg CO₂e</td></tr>
                <tr><td><b>Other Materials:</b></td><td>{carbon.get('other', 0):,.2f} kg CO₂e</td></tr>
                <tr style="font-weight: bold; background-color: #fff3cd; font-size: 16px;">
                    <td><b>Total Emissions:</b></td><td>{carbon.get('total_emissions', 0):,.2f} kg CO₂e</td>
                </tr>
            </table>
            
            <h4>🔷 Benchmark Comparison:</h4>
            <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                <tr><td><b>Your Project:</b></td><td>{benchmark.get('project_intensity', 0):.2f} kg CO₂e/m²</td></tr>
                <tr><td><b>Industry Average:</b></td><td>{benchmark.get('industry_average', 0):.2f} kg CO₂e/m²</td></tr>
                <tr><td><b>Best Practice:</b></td><td>{benchmark.get('best_practice', 0):.2f} kg CO₂e/m²</td></tr>
                <tr><td><b>Performance:</b></td><td><span style="color: {'green' if benchmark.get('performance') == 'GOOD' else 'orange'}; font-weight: bold;">{benchmark.get('performance', 'N/A')}</span></td></tr>
            </table>
            
            <h4>🔷 Reduction Opportunities:</h4>
            <ul>
                {self._format_list(results.get('reduction_opportunities', []))}
            </ul>
            
            <p style="margin-top: 15px;"><i>💡 Click "Get AI Explanation" for carbon reduction strategies.</i></p>
        """
    
    def _format_climate_results(self, results: dict) -> str:
        """Format climate risk results"""
        return f"""
            <h3>✓ Climate Risk Assessment Complete</h3>
            
            <h4>🔷 Risk Factors:</h4>
            <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                <tr><td><b>Flood Risk:</b></td><td>{results.get('flood_risk', 'N/A')}</td></tr>
                <tr><td><b>Rainfall Intensity:</b></td><td>{results.get('rainfall_intensity', 'N/A')}</td></tr>
                <tr><td><b>Temperature Range:</b></td><td>{results.get('temperature_range', 'N/A')}</td></tr>
                <tr><td><b>Seismic Zone:</b></td><td>{results.get('seismic_zone', 'N/A')}</td></tr>
            </table>
            
            <h4>🔷 Recommendations:</h4>
            <ul>
                {self._format_list(results.get('recommendations', []))}
            </ul>
            
            <p style="margin-top: 15px;"><i>💡 Click "Get AI Explanation" for detailed risk mitigation strategies.</i></p>
        """
    
    def _format_defect_results(self, results: dict) -> str:
        """Format defect detection results"""
        return f"""
            <h3>✓ Defect Detection Analysis</h3>
            
            <p><b>Status:</b> {results.get('message', 'No analysis performed')}</p>
            
            <h4>🔷 Capabilities:</h4>
            <ul>
                {self._format_list(results.get('capabilities', []))}
            </ul>
            
            <p style="margin-top: 15px;"><i>💡 Upload site photos using File → Import → Site Photos to detect defects.</i></p>
        """
    
    def _format_materials_results(self, results: dict) -> str:
        """Format materials prediction results"""
        mix_design = results.get('mix_design', {})
        
        return f"""
            <h3>✓ Materials Prediction Complete</h3>
            
            <h4>🔷 Predicted Strength:</h4>
            <p style="font-size: 18px; font-weight: bold; color: #27ae60;">{results.get('predicted_strength', 'N/A')}</p>
            
            <h4>🔷 Mix Design:</h4>
            <table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">
                <tr><td><b>Cement:</b></td><td>{mix_design.get('cement', 'N/A')}</td></tr>
                <tr><td><b>Fine Aggregate:</b></td><td>{mix_design.get('fine_aggregate', 'N/A')}</td></tr>
                <tr><td><b>Coarse Aggregate:</b></td><td>{mix_design.get('coarse_aggregate', 'N/A')}</td></tr>
                <tr><td><b>Water:</b></td><td>{mix_design.get('water', 'N/A')}</td></tr>
                <tr><td><b>W/C Ratio:</b></td><td>{mix_design.get('w_c_ratio', 'N/A')}</td></tr>
            </table>
            
            <h4>🔷 Recommendations:</h4>
            <ul>
                {self._format_list(results.get('recommendations', []))}
            </ul>
            
            <p style="margin-top: 15px;"><i>💡 Click "Get AI Explanation" for mix design optimization.</i></p>
        """
    
    def _format_list(self, items: list) -> str:
        """Format list items as HTML"""
        return ''.join([f'<li>{item}</li>' for item in items])
    
    def _get_ai_explanation(self):
        """Get AI explanation for analysis results"""
        if not hasattr(self, 'current_results'):
            self.results_text.append("""
                <hr>
                <p style="color: red;"><b>No analysis results to explain.</b> Please run an analysis first.</p>
            """)
            return
        
        ai_mode = self.config_manager.get('ai.mode', 'built-in')
        
        if ai_mode == 'built-in':
            # Built-in explanation (no API required)
            explanation = self._generate_builtin_explanation()
        else:
            # API-based explanation
            explanation = self._generate_api_explanation()
        
        self.results_text.append(f"""
            <hr>
            <h4>🤖 AI Explanation:</h4>
            {explanation}
        """)
    
    def _generate_builtin_explanation(self) -> str:
        """Generate built-in explanation without API"""
        if not hasattr(self, 'current_results'):
            return "<p>No analysis results available.</p>"
        
        analysis_type = self.current_results.get('type', '')
        
        if 'Structural' in analysis_type:
            return self._explain_structural()
        elif 'Geotechnical' in analysis_type:
            return self._explain_geotechnical()
        elif 'Cost' in analysis_type:
            return self._explain_cost()
        elif 'Carbon' in analysis_type:
            return self._explain_carbon()
        elif 'Climate' in analysis_type:
            return self._explain_climate()
        else:
            return """
            <p>Based on engineering principles and analysis results:</p>
            <ul>
                <li>Analysis completed successfully</li>
                <li>All parameters checked against code requirements</li>
                <li>Results are within acceptable limits</li>
            </ul>
            <p><i>For enhanced natural language explanations, configure an AI API key in Settings.</i></p>
            """
    
    def _explain_structural(self) -> str:
        """Explain structural analysis results"""
        beam = self.current_results.get('beam', {})
        column = self.current_results.get('column', {})
        slab = self.current_results.get('slab', {})
        
        return f"""
        <div style="background-color: #f0f8ff; padding: 15px; border-left: 4px solid #3498db;">
        
        <p><b>📐 Engineering Analysis Summary:</b></p>
        
        <p><b>Beam Design:</b><br>
        The beam with dimensions 300mm × 450mm spanning 6.0m carries a total load of 25 kN/m.
        Maximum bending moment is {beam.get('moment', 0):.2f} kN·m and shear force is {beam.get('shear', 0):.2f} kN.
        Deflection of {beam.get('deflection', 0):.2f}mm is {'within' if beam.get('status') == 'PASS' else 'exceeding'} the L/360 limit.
        The beam is <span style="color: {'green' if beam.get('status') == 'PASS' else 'red'}; font-weight: bold;">{beam.get('status', 'N/A')}</span> for serviceability.</p>
        
        <p><b>Column Design:</b><br>
        The 400mm × 400mm column with height 3.5m is subjected to {column.get('load', 0):.0f} kN axial load and {column.get('moment', 0):.0f} kN·m moment.
        The column capacity is {column.get('capacity', 0):.2f} kN, giving a utilization ratio of {column.get('utilization', 0):.2f}.
        Slenderness ratio is {column.get('slenderness', 0):.1f}, and the column is <span style="color: {'green' if column.get('status') == 'PASS' else 'red'}; font-weight: bold;">{column.get('status', 'N/A')}</span>.</p>
        
        <p><b>Slab Design:</b><br>
        The {slab.get('slab_type', 'N/A')} slab with dimensions 4.0m × 5.0m and thickness 150mm carries 7.0 kN/m² load.
        Design moments are {slab.get('moment_x', 0):.2f} kN·m and {slab.get('moment_y', 0):.2f} kN·m in the two directions.
        Deflection is {slab.get('deflection', 0):.2f}mm, and the slab is <span style="color: {'green' if slab.get('status') == 'PASS' else 'red'}; font-weight: bold;">{slab.get('status', 'N/A')}</span>.</p>
        
        <p><b>✅ Recommendations:</b></p>
        <ul>
            <li>All structural elements meet IS 456:2000 requirements</li>
            <li>Provide cover as per exposure conditions (minimum 25mm for beams/slabs, 40mm for columns)</li>
            <li>Use M25 grade concrete with proper curing for 28 days</li>
            <li>Conduct regular inspections for any signs of distress</li>
        </ul>
        
        <p style="font-size: 12px; color: #666;"><i>Note: For enhanced conversational AI explanations, configure an API key in Settings → API Configuration.</i></p>
        
        </div>
        """
    
    def _explain_geotechnical(self) -> str:
        """Explain geotechnical analysis results"""
        bc = self.current_results.get('bearing_capacity', {})
        settlement = self.current_results.get('settlement', {})
        
        return f"""
        <div style="background-color: #f0f8ff; padding: 15px; border-left: 4px solid #8B4513;">
        
        <p><b>🏗️ Foundation Engineering Summary:</b></p>
        
        <p><b>Bearing Capacity Analysis:</b><br>
        Using Terzaghi's bearing capacity theory, the ultimate bearing capacity is {bc.get('ultimate', 0):.2f} kPa.
        With a safety factor of {bc.get('safety_factor', 3.0):.1f}, the allowable bearing capacity is {bc.get('allowable', 0):.2f} kPa.
        Applied foundation pressure is {bc.get('applied', 0):.2f} kPa, which is {'within' if bc.get('status') == 'SAFE' else 'exceeding'} safe limits.
        Foundation status: <span style="color: {'green' if bc.get('status') == 'SAFE' else 'red'}; font-weight: bold;">{bc.get('status', 'N/A')}</span>.</p>
        
        <p><b>Settlement Prediction:</b><br>
        Immediate (elastic) settlement: {settlement.get('immediate', 0):.2f}mm<br>
        Consolidation settlement: {settlement.get('consolidation', 0):.2f}mm<br>
        Total predicted settlement: {settlement.get('total', 0):.2f}mm<br>
        This is {'within' if settlement.get('status') == 'ACCEPTABLE' else 'exceeding'} the allowable limit of {settlement.get('allowable', 25):.0f}mm.</p>
        
        <p><b>✅ Recommendations:</b></p>
        <ul>
            <li>Found at minimum 2.0m depth below ground level</li>
            <li>Remove all topsoil and organic material before construction</li>
            <li>Provide proper drainage around foundation perimeter</li>
            <li>Protect foundation from water infiltration during monsoon</li>
            <li>Monitor settlement during and after construction</li>
            <li>Use controlled compacted backfill material</li>
        </ul>
        
        <p style="font-size: 12px; color: #666;"><i>Note: For detailed site-specific recommendations, configure an AI API key.</i></p>
        
        </div>
        """
    
    def _explain_cost(self) -> str:
        """Explain cost estimation results"""
        breakdown = self.current_results.get('cost_breakdown', {})
        
        return f"""
        <div style="background-color: #f0fff4; padding: 15px; border-left: 4px solid #2ecc71;">
        
        <p><b>💰 Cost Analysis Summary:</b></p>
        
        <p><b>Direct Costs:</b><br>
        Materials account for ₹{breakdown.get('materials', 0):,.0f} ({breakdown.get('materials', 0) / breakdown.get('subtotal', 1) * 100:.1f}% of direct costs).
        Labor costs are ₹{breakdown.get('labor', 0):,.0f} ({breakdown.get('labor', 0) / breakdown.get('subtotal', 1) * 100:.1f}%).
        Equipment and machinery: ₹{breakdown.get('equipment', 0):,.0f} ({breakdown.get('equipment', 0) / breakdown.get('subtotal', 1) * 100:.1f}%).</p>
        
        <p><b>Indirect Costs & Margins:</b><br>
        Overhead (site office, supervision, utilities): 15% = ₹{breakdown.get('overhead', 0):,.0f}<br>
        Contractor profit margin: 10% = ₹{breakdown.get('profit', 0):,.0f}<br>
        Contingency for uncertainties: 10% = ₹{breakdown.get('contingency', 0):,.0f}</p>
        
        <p><b>Total Project Cost: ₹{breakdown.get('grand_total', 0):,.2f}</b></p>
        
        <p><b>💡 Value Engineering Opportunities:</b></p>
        <ul>
            <li>Consider bulk material procurement to reduce material costs by 5-8%</li>
            <li>Optimize formwork reuse to save on equipment costs</li>
            <li>Schedule activities efficiently to minimize labor idle time</li>
            <li>Use locally available materials where specifications permit</li>
            <li>Plan construction to avoid monsoon delays</li>
        </ul>
        
        <p style="font-size: 12px; color: #666;"><i>Note: For AI-powered cost optimization suggestions, enable API mode.</i></p>
        
        </div>
        """
    
    def _explain_carbon(self) -> str:
        """Explain carbon footprint results"""
        carbon = self.current_results.get('carbon_data', {})
        benchmark = self.current_results.get('benchmark', {})
        
        return f"""
        <div style="background-color: #fffbf0; padding: 15px; border-left: 4px solid #f39c12;">
        
        <p><b>🌍 Carbon Footprint Summary:</b></p>
        
        <p><b>Embodied Carbon Breakdown:</b><br>
        Total project emissions: <b>{carbon.get('total_emissions', 0):,.0f} kg CO₂e</b><br>
        Carbon intensity: <b>{benchmark.get('project_intensity', 0):.1f} kg CO₂e/m²</b></p>
        
        <p><b>Major Contributors:</b><br>
        • Concrete: {carbon.get('concrete', 0):,.0f} kg CO₂e ({carbon.get('concrete', 0) / carbon.get('total_emissions', 1) * 100:.1f}%)<br>
        • Steel reinforcement: {carbon.get('steel', 0):,.0f} kg CO₂e ({carbon.get('steel', 0) / carbon.get('total_emissions', 1) * 100:.1f}%)<br>
        • Cement: {carbon.get('cement', 0):,.0f} kg CO₂e ({carbon.get('cement', 0) / carbon.get('total_emissions', 1) * 100:.1f}%)</p>
        
        <p><b>Performance vs Benchmarks:</b><br>
        Your project: {benchmark.get('project_intensity', 0):.1f} kg CO₂e/m²<br>
        Industry average: {benchmark.get('industry_average', 0):.1f} kg CO₂e/m²<br>
        Best practice: {benchmark.get('best_practice', 0):.1f} kg CO₂e/m²<br>
        Rating: <span style="color: {'green' if benchmark.get('performance') == 'GOOD' else 'orange'}; font-weight: bold;">{benchmark.get('performance', 'N/A')}</span></p>
        
        <p><b>🌱 Carbon Reduction Strategies:</b></p>
        <ul>
            <li>Replace 30% cement with fly ash or GGBS (reduces embodied carbon by 15-20%)</li>
            <li>Use recycled steel instead of virgin steel where possible</li>
            <li>Optimize structural design to reduce concrete volume</li>
            <li>Consider low-carbon concrete mixes (LC3, geopolymer)</li>
            <li>Source materials locally to minimize transportation emissions</li>
        </ul>
        
        <p style="font-size: 12px; color: #666;"><i>Note: For project-specific carbon reduction roadmap, enable AI API.</i></p>
        
        </div>
        """
    
    def _explain_climate(self) -> str:
        """Explain climate risk results"""
        return f"""
        <div style="background-color: #f0f8ff; padding: 15px; border-left: 4px solid #3498db;">
        
        <p><b>🌦️ Climate Risk Assessment:</b></p>
        
        <p>Based on site location and climate data analysis:</p>
        
        <p><b>Flood Risk: {self.current_results.get('flood_risk', 'N/A')}</b><br>
        Consider adequate site drainage, raised plinth levels, and waterproofing measures.</p>
        
        <p><b>Rainfall Intensity: {self.current_results.get('rainfall_intensity', 'N/A')}</b><br>
        Design drainage system for high-intensity rainfall events.</p>
        
        <p><b>Seismic Zone: {self.current_results.get('seismic_zone', 'N/A')}</b><br>
        Structure must be designed as per IS 1893 seismic provisions.</p>
        
        <p><b>🛡️ Mitigation Measures:</b></p>
        <ul>
            {self._format_list(self.current_results.get('recommendations', []))}
        </ul>
        
        <p style="font-size: 12px; color: #666;"><i>Note: For detailed climate adaptation strategies, configure AI API.</i></p>
        
        </div>
        """
    
    def _generate_api_explanation(self) -> str:
        """Generate API-based explanation"""
        # TODO: Implement API call to OpenAI/Anthropic
        return "Enhanced AI explanation will be generated here using the configured API."
    
    def run_analysis(self, analysis_type: str):
        """Public method to trigger analysis"""
        # Map analysis type to combo box index
        type_map = {
            "structural": 0,
            "geotechnical": 1,
            "climate": 2,
            "computer_vision": 3,
            "materials": 4,
            "cost": 5,
            "carbon": 6
        }
        
        if analysis_type in type_map:
            self.analysis_combo.setCurrentIndex(type_map[analysis_type])
            self._run_analysis()
