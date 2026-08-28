"""
Visualization panel for CivilAI Twin
Handles charts, 3D models, and result visualization with Matplotlib
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTabWidget, QTextEdit, QScrollArea
)
from PyQt6.QtCore import Qt
from loguru import logger

from utils.config import ConfigManager

# Import matplotlib for charts
try:
    import matplotlib
    matplotlib.use('QtAgg')
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("Matplotlib not available - charts will not be displayed")


class VisualizationPanel(QWidget):
    """Panel for charts, 3D visualization and detailed results"""
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        
        self.config_manager = config_manager
        self.current_results = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize user interface"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel("Visualization & Results")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title_label)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Charts tab - Real matplotlib charts
        self.charts_tab = self._create_charts_tab()
        self.tab_widget.addTab(self.charts_tab, "📊 Charts & Graphs")
        
        # Heatmap tab - Color-coded heatmaps
        self.heatmap_tab = self._create_heatmap_tab()
        self.tab_widget.addTab(self.heatmap_tab, "🔥 Heatmaps")
        
        # 3D Model tab - 3D visualization
        self.model_tab = self._create_model_tab()
        self.tab_widget.addTab(self.model_tab, "🏗️ 3D Model")
        
        # Detailed Results tab - Text results
        self.results_tab = self._create_results_tab()
        self.tab_widget.addTab(self.results_tab, "📄 Detailed Results")
        
        layout.addWidget(self.tab_widget)
        
        # View controls
        controls_layout = QHBoxLayout()
        
        self.btn_screenshot = QPushButton("📸 Screenshot")
        self.btn_screenshot.clicked.connect(self._take_screenshot)
        controls_layout.addWidget(self.btn_screenshot)
        
        self.btn_export = QPushButton("💾 Export Data")
        self.btn_export.clicked.connect(self._export_data)
        controls_layout.addWidget(self.btn_export)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
    
    def _create_charts_tab(self) -> QWidget:
        """Create charts tab with matplotlib canvas"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        if MATPLOTLIB_AVAILABLE:
            # Create matplotlib figure and canvas
            self.figure = Figure(figsize=(10, 8))
            self.canvas = FigureCanvas(self.figure)
            layout.addWidget(self.canvas)
            
            # Initial message
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, '📊 Run an analysis to generate charts',
                   ha='center', va='center', fontsize=16, color='#7f8c8d')
            ax.axis('off')
            self.canvas.draw()
        else:
            # Fallback if matplotlib not available
            label = QLabel("Matplotlib not available.\nInstall with: pip install matplotlib")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 14px; color: #e74c3c; padding: 50px;")
            layout.addWidget(label)
        
        return widget
    
    def _create_heatmap_tab(self) -> QWidget:
        """Create heatmap tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        if MATPLOTLIB_AVAILABLE:
            # Create matplotlib figure for heatmap
            self.heatmap_figure = Figure(figsize=(10, 8))
            self.heatmap_canvas = FigureCanvas(self.heatmap_figure)
            layout.addWidget(self.heatmap_canvas)
            
            # Initial message
            ax = self.heatmap_figure.add_subplot(111)
            ax.text(0.5, 0.5, '🔥 Run Structural or Risk analysis\nto generate heatmaps',
                   ha='center', va='center', fontsize=16, color='#7f8c8d')
            ax.axis('off')
            self.heatmap_canvas.draw()
        else:
            label = QLabel("Matplotlib required for heatmaps")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
        
        return widget
    
    def _create_model_tab(self) -> QWidget:
        """Create 3D model viewer tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        if MATPLOTLIB_AVAILABLE:
            # Create 3D matplotlib figure
            self.model_figure = Figure(figsize=(10, 8))
            self.model_canvas = FigureCanvas(self.model_figure)
            layout.addWidget(self.model_canvas)
            
            # Initial 3D message
            ax = self.model_figure.add_subplot(111, projection='3d')
            ax.text2D(0.5, 0.5, '🏗️ 3D structural model\nwill appear here after analysis',
                     ha='center', va='center', fontsize=16, color='#7f8c8d',
                     transform=ax.transAxes)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            self.model_canvas.draw()
        else:
            label = QLabel("3D visualization requires matplotlib with mpl_toolkits")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
        
        return widget
    
    def _create_results_tab(self) -> QWidget:
        """Create detailed results tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Scrollable text area for detailed results
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: #2c3e50;
                font-size: 13px;
                border: 1px solid #bdc3c7;
                padding: 10px;
            }
        """)
        layout.addWidget(self.results_text)
        
        # Initial message
        self.results_text.setHtml("""
            <div style="padding: 20px; text-align: center;">
                <h2 style="color: #7f8c8d;">📄 Detailed Results</h2>
                <p style="font-size: 14px; color: #95a5a6;">
                    Run an analysis to see detailed numerical results here.
                </p>
            </div>
        """)
        
        return widget
    
    def _take_screenshot(self):
        """Take screenshot of current view"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            from PyQt6.QtGui import QPixmap
            import os
            
            # Get current tab
            current_widget = self.tab_widget.currentWidget()
            tab_name = self.tab_widget.tabText(self.tab_widget.currentIndex())
            
            # Ask user for save location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Screenshot",
                f"CivilAI_{tab_name}_{logger._core.extra.get('timestamp', 'screenshot')}.png",
                "PNG Image (*.png);;JPEG Image (*.jpg)"
            )
            
            if file_path:
                # Take screenshot
                pixmap = current_widget.grab()
                pixmap.save(file_path)
                logger.info(f"Screenshot saved: {file_path}")
                
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
    
    def _export_data(self):
        """Export visualization data"""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            import json
            
            if not self.current_results:
                QMessageBox.information(self, "No Data", "Run an analysis first to export data.")
                return
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Analysis Data",
                "analysis_data.json",
                "JSON Files (*.json);;CSV Files (*.csv)"
            )
            
            if file_path:
                if file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.current_results, f, indent=2)
                    logger.info(f"Data exported to JSON: {file_path}")
                else:
                    # CSV export - simplified
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write("Analysis Type, Value\n")
                        for key, value in self.current_results.items():
                            f.write(f"{key},{value}\n")
                    logger.info(f"Data exported to CSV: {file_path}")
                
                QMessageBox.information(self, "Export Complete", f"Data exported to:\n{file_path}")
                
        except Exception as e:
            logger.error(f"Export failed: {e}")
    
    def update_results(self, results: dict):
        """Update visualization with analysis results"""
        self.current_results = results
        analysis_type = results.get('type', 'unknown')
        logger.info(f"Updating visualization with results: {analysis_type}")
        
        # Update all tabs
        self._update_charts(results)
        self._update_heatmap(results)
        self._update_3d_model(results)
        self._update_detailed_results(results)
        
        # Switch to charts tab to show results
        self.tab_widget.setCurrentIndex(0)
    
    def _update_charts(self, results: dict):
        """Update charts tab with matplotlib charts"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        analysis_type = results.get('type', '')
        self.figure.clear()
        
        if 'Structural' in analysis_type:
            self._plot_structural_charts(results)
        elif 'Geotechnical' in analysis_type:
            self._plot_geotechnical_charts(results)
        elif 'Cost' in analysis_type:
            self._plot_cost_charts(results)
        elif 'Carbon' in analysis_type:
            self._plot_carbon_charts(results)
        else:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, f'✓ {analysis_type}\nCompleted Successfully',
                   ha='center', va='center', fontsize=16, color='#27ae60')
            ax.axis('off')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def _plot_structural_charts(self, results: dict):
        """Plot structural analysis charts"""
        beam = results.get('beam', {})
        column = results.get('column', {})
        slab = results.get('slab', {})
        
        # Create 2x2 subplot
        ax1 = self.figure.add_subplot(2, 2, 1)
        ax2 = self.figure.add_subplot(2, 2, 2)
        ax3 = self.figure.add_subplot(2, 2, 3)
        ax4 = self.figure.add_subplot(2, 2, 4)
        
        # Beam moment diagram
        x = np.linspace(0, 10, 50)
        moment = beam.get('moment', 150) * np.sin(np.pi * x / 10)
        ax1.plot(x, moment, 'b-', linewidth=2)
        ax1.fill_between(x, moment, alpha=0.3)
        ax1.set_title('Beam Bending Moment', fontweight='bold')
        ax1.set_xlabel('Length (m)')
        ax1.set_ylabel('Moment (kN·m)')
        ax1.grid(True, alpha=0.3)
        
        # Column capacity bar chart
        labels = ['Capacity', 'Applied Load']
        values = [column.get('capacity', 1000), column.get('applied_load', 600)]
        colors = ['#2ecc71', '#3498db']
        ax2.bar(labels, values, color=colors, alpha=0.7)
        ax2.set_title('Column Load Analysis', fontweight='bold')
        ax2.set_ylabel('Load (kN)')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Deflection comparison
        elements = ['Beam', 'Column', 'Slab']
        deflections = [
            beam.get('deflection', 8.5),
            column.get('deflection', 2.3),
            slab.get('deflection', 12.4)
        ]
        allowable = [10, 5, 15]
        
        x_pos = np.arange(len(elements))
        width = 0.35
        ax3.bar(x_pos - width/2, deflections, width, label='Actual', color='#e74c3c', alpha=0.7)
        ax3.bar(x_pos + width/2, allowable, width, label='Allowable', color='#95a5a6', alpha=0.7)
        ax3.set_title('Deflection Comparison', fontweight='bold')
        ax3.set_ylabel('Deflection (mm)')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(elements)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Safety factors pie chart
        ax4.pie(
            [3, 1],
            labels=['Safety Factor', 'Applied'],
            colors=['#27ae60', '#e67e22'],
            autopct='%1.1f',
            startangle=90
        )
        ax4.set_title('Safety Factor', fontweight='bold')
    
    def _plot_geotechnical_charts(self, results: dict):
        """Plot geotechnical analysis charts"""
        bc = results.get('bearing_capacity', {})
        settlement = results.get('settlement', {})
        
        # Create 2x2 subplot
        ax1 = self.figure.add_subplot(2, 2, 1)
        ax2 = self.figure.add_subplot(2, 2, 2)
        ax3 = self.figure.add_subplot(2, 2, 3)
        ax4 = self.figure.add_subplot(2, 2, 4)
        
        # Bearing capacity bar chart
        labels = ['Ultimate', 'Allowable', 'Applied']
        values = [
            bc.get('ultimate', 450),
            bc.get('allowable', 150),
            bc.get('applied', 100)
        ]
        colors = ['#e74c3c', '#f39c12', '#3498db']
        ax1.bar(labels, values, color=colors, alpha=0.7)
        ax1.set_title('Bearing Capacity', fontweight='bold')
        ax1.set_ylabel('Pressure (kPa)')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Settlement vs depth
        depth = np.array([0, 2, 4, 6, 8, 10])
        settle = settlement.get('total', 18) * np.exp(-depth / 5)
        ax2.plot(settle, -depth, 'o-', color='#8e44ad', linewidth=2, markersize=6)
        ax2.set_title('Settlement vs Depth', fontweight='bold')
        ax2.set_xlabel('Settlement (mm)')
        ax2.set_ylabel('Depth (m)')
        ax2.grid(True, alpha=0.3)
        ax2.invert_yaxis()
        
        # Soil layers
        layers = ['Sand', 'Clay', 'Gravel']
        thickness = [3, 5, 4]
        colors_soil = ['#f4e04d', '#a0826d', '#95a5a6']
        ax3.barh(layers, thickness, color=colors_soil, alpha=0.7)
        ax3.set_title('Soil Stratification', fontweight='bold')
        ax3.set_xlabel('Thickness (m)')
        ax3.grid(True, alpha=0.3, axis='x')
        
        # Safety factor gauge
        sf = bc.get('safety_factor', 3.0)
        ax4.barh(['Factor of Safety'], [sf], color='#27ae60', alpha=0.7)
        ax4.axvline(x=3.0, color='r', linestyle='--', label='Minimum (3.0)')
        ax4.set_xlim(0, 5)
        ax4.set_title('Factor of Safety', fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='x')
    
    def _plot_cost_charts(self, results: dict):
        """Plot cost estimation charts"""
        breakdown = results.get('cost_breakdown', {})
        boq = results.get('boq', [])
        
        # Create 2x2 subplot
        ax1 = self.figure.add_subplot(2, 2, 1)
        ax2 = self.figure.add_subplot(2, 2, 2)
        ax3 = self.figure.add_subplot(2, 2, 3)
        ax4 = self.figure.add_subplot(2, 2, 4)
        
        # Cost breakdown pie chart
        labels = ['Materials', 'Labor', 'Equipment']
        sizes = [
            breakdown.get('materials', 45000),
            breakdown.get('labor', 15000),
            breakdown.get('equipment', 5000)
        ]
        colors = ['#3498db', '#e74c3c', '#f39c12']
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Cost Breakdown', fontweight='bold')
        
        # Total cost components
        categories = ['Subtotal', 'Overhead', 'Profit', 'Contingency']
        amounts = [
            breakdown.get('subtotal', 65000),
            breakdown.get('overhead', 9000),
            breakdown.get('profit', 7000),
            breakdown.get('contingency', 8000)
        ]
        ax2.barh(categories, amounts, color='#2ecc71', alpha=0.7)
        ax2.set_title('Cost Components', fontweight='bold')
        ax2.set_xlabel('Amount (₹)')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # BOQ items (top 5)
        if boq and len(boq) > 0:
            items = [item.get('description', 'Item')[:20] for item in boq[:5]]
            costs = [item.get('total_cost', 0) for item in boq[:5]]
            ax3.bar(range(len(items)), costs, color='#9b59b6', alpha=0.7)
            ax3.set_title('Top 5 BOQ Items', fontweight='bold')
            ax3.set_ylabel('Cost (₹)')
            ax3.set_xticks(range(len(items)))
            ax3.set_xticklabels(items, rotation=45, ha='right', fontsize=8)
            ax3.grid(True, alpha=0.3, axis='y')
        
        # Grand total display
        grand_total = breakdown.get('grand_total', 89000)
        ax4.text(0.5, 0.5, f'Grand Total\n₹ {grand_total:,.2f}',
                ha='center', va='center', fontsize=20, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.3))
        ax4.axis('off')
    
    def _plot_carbon_charts(self, results: dict):
        """Plot carbon footprint charts"""
        materials = results.get('materials', [])
        totals = results.get('totals', {})
        
        # Create 2x2 subplot
        ax1 = self.figure.add_subplot(2, 2, 1)
        ax2 = self.figure.add_subplot(2, 2, 2)
        ax3 = self.figure.add_subplot(2, 2, 3)
        ax4 = self.figure.add_subplot(2, 2, 4)
        
        # Emissions by material (pie chart)
        if materials and len(materials) > 0:
            labels = [m.get('material', 'Material')[:15] for m in materials[:6]]
            sizes = [m.get('total_emissions', 0) for m in materials[:6]]
            colors_palette = ['#e74c3c', '#3498db', '#f39c12', '#2ecc71', '#9b59b6', '#1abc9c']
            ax1.pie(sizes, labels=labels, colors=colors_palette, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Emissions by Material', fontweight='bold')
        
        # Total emissions bar
        total_co2 = totals.get('total_co2e', 15000)
        ax2.barh(['Total Emissions'], [total_co2], color='#e67e22', alpha=0.7)
        ax2.set_title('Total Carbon Footprint', fontweight='bold')
        ax2.set_xlabel('kg CO₂e')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Emissions by category
        categories = ['Production', 'Transport', 'Construction']
        emissions = [
            totals.get('production', 12000),
            totals.get('transport', 2000),
            totals.get('construction', 1000)
        ]
        ax3.bar(categories, emissions, color=['#c0392b', '#f39c12', '#16a085'], alpha=0.7)
        ax3.set_title('Emissions by Stage', fontweight='bold')
        ax3.set_ylabel('kg CO₂e')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Benchmark comparison
        project = totals.get('intensity', 350)
        industry = 400
        target = 300
        
        labels_bench = ['Your Project', 'Industry Avg', 'Target']
        values_bench = [project, industry, target]
        colors_bench = ['#3498db', '#95a5a6', '#27ae60']
        ax4.bar(labels_bench, values_bench, color=colors_bench, alpha=0.7)
        ax4.set_title('Carbon Intensity', fontweight='bold')
        ax4.set_ylabel('kg CO₂e/m²')
        ax4.grid(True, alpha=0.3, axis='y')
    
    def _update_heatmap(self, results: dict):
        """Update heatmap tab"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        analysis_type = results.get('type', '')
        self.heatmap_figure.clear()
        
        # Generate heatmap based on analysis type
        if 'Structural' in analysis_type or 'Geotechnical' in analysis_type:
            ax = self.heatmap_figure.add_subplot(111)
            
            # Generate sample stress heatmap
            x = np.linspace(0, 10, 50)
            y = np.linspace(0, 10, 50)
            X, Y = np.meshgrid(x, y)
            Z = np.sin(np.sqrt(X**2 + Y**2)) * 100 + 100
            
            im = ax.contourf(X, Y, Z, levels=20, cmap='RdYlGn_r')
            self.heatmap_figure.colorbar(im, ax=ax, label='Stress (MPa)')
            ax.set_title(f'{analysis_type} - Stress Distribution', fontweight='bold')
            ax.set_xlabel('X Position (m)')
            ax.set_ylabel('Y Position (m)')
            
        elif 'Climate' in analysis_type or 'Risk' in analysis_type:
            ax = self.heatmap_figure.add_subplot(111)
            
            # Generate risk heatmap
            risk_levels = np.random.rand(10, 10) * 100
            im = ax.imshow(risk_levels, cmap='YlOrRd', interpolation='bilinear')
            self.heatmap_figure.colorbar(im, ax=ax, label='Risk Level (%)')
            ax.set_title('Risk Distribution Heatmap', fontweight='bold')
            ax.set_xlabel('Grid X')
            ax.set_ylabel('Grid Y')
            
        else:
            ax = self.heatmap_figure.add_subplot(111)
            ax.text(0.5, 0.5, '🔥 Heatmap available for\nStructural and Risk analyses',
                   ha='center', va='center', fontsize=14, color='#7f8c8d')
            ax.axis('off')
        
        self.heatmap_figure.tight_layout()
        self.heatmap_canvas.draw()
    
    def _update_3d_model(self, results: dict):
        """Update 3D model tab"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        self.model_figure.clear()
        ax = self.model_figure.add_subplot(111, projection='3d')
        
        analysis_type = results.get('type', '')
        
        if 'Structural' in analysis_type:
            # Draw simple 3D structural frame
            # Columns
            for x, y in [(0, 0), (5, 0), (0, 5), (5, 5)]:
                ax.plot([x, x], [y, y], [0, 3], 'b-', linewidth=3, label='Column' if x == 0 and y == 0 else '')
            
            # Beams
            ax.plot([0, 5], [0, 0], [3, 3], 'r-', linewidth=2, label='Beam')
            ax.plot([0, 5], [5, 5], [3, 3], 'r-', linewidth=2)
            ax.plot([0, 0], [0, 5], [3, 3], 'r-', linewidth=2)
            ax.plot([5, 5], [0, 5], [3, 3], 'r-', linewidth=2)
            
            # Slab (top surface)
            xx, yy = np.meshgrid([0, 5], [0, 5])
            zz = np.full_like(xx, 3)
            ax.plot_surface(xx, yy, zz, alpha=0.3, color='gray')
            
            ax.set_title('3D Structural Frame', fontweight='bold')
            
        elif 'Geotechnical' in analysis_type:
            # Draw foundation and soil layers
            # Foundation
            x_found = np.array([0, 3, 3, 0, 0])
            y_found = np.array([0, 0, 3, 3, 0])
            z_found = np.array([0, 0, 0, 0, 0])
            ax.plot(x_found, y_found, z_found, 'k-', linewidth=3, label='Foundation')
            
            # Soil layers
            for z in [-1, -2, -3]:
                xx, yy = np.meshgrid([0, 5], [0, 5])
                zz = np.full_like(xx, z)
                ax.plot_surface(xx, yy, zz, alpha=0.2, color=['#f4e04d', '#a0826d', '#95a5a6'][abs(z)-1])
            
            ax.set_title('3D Foundation Model', fontweight='bold')
            ax.set_zlabel('Depth (m)')
            
        else:
            # Generic 3D visualization
            theta = np.linspace(0, 2*np.pi, 100)
            z = np.linspace(0, 10, 100)
            r = 3
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            ax.plot(x, y, z, 'b-', linewidth=2)
            ax.set_title(f'{analysis_type} - 3D View', fontweight='bold')
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)' if 'Geotechnical' not in analysis_type else 'Height (m)')
        ax.legend()
        
        self.model_figure.tight_layout()
        self.model_canvas.draw()
    
    def _update_detailed_results(self, results: dict):
        """Update detailed results tab with formatted HTML"""
        html = self._format_results_html(results)
        self.results_text.setHtml(html)
    
    def _format_results_html(self, results: dict) -> str:
        """Format results as detailed HTML"""
        analysis_type = results.get('type', 'Unknown')
        status = results.get('status', 'unknown')
        
        html = f"""
        <div style="padding: 20px; font-family: Arial, sans-serif;">
        <h1 style="color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;">
            {analysis_type}
        </h1>
        <p style="font-size: 16px;">
            <b>Status:</b> <span style="color: #27ae60; font-weight: bold;">{status.upper()}</span>
        </p>
        <hr style="border: 1px solid #ecf0f1; margin: 20px 0;">
        """
        
        if 'Structural' in analysis_type:
            beam = results.get('beam', {})
            column = results.get('column', {})
            slab = results.get('slab', {})
            
            html += f"""
            <h2 style="color: #3498db;">📊 Beam Analysis</h2>
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <tr style="background: #ecf0f1;">
                    <th style="padding: 10px; text-align: left; border: 1px solid #bdc3c7;">Parameter</th>
                    <th style="padding: 10px; text-align: right; border: 1px solid #bdc3c7;">Value</th>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Max Bending Moment</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{beam.get('moment', 0):.2f} kN·m</b></td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Max Shear Force</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{beam.get('shear', 0):.2f} kN</b></td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Deflection</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{beam.get('deflection', 0):.2f} mm</b></td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Status</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right; color: #27ae60;"><b>{beam.get('status', 'SAFE')}</b></td>
                </tr>
            </table>
            
            <h2 style="color: #3498db; margin-top: 30px;">🏗️ Column Analysis</h2>
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <tr style="background: #ecf0f1;">
                    <th style="padding: 10px; text-align: left; border: 1px solid #bdc3c7;">Parameter</th>
                    <th style="padding: 10px; text-align: right; border: 1px solid #bdc3c7;">Value</th>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Axial Capacity</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{column.get('capacity', 0):.2f} kN</b></td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Applied Load</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{column.get('applied_load', 0):.2f} kN</b></td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Utilization Ratio</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{column.get('utilization', 0):.2f}</b></td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Status</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right; color: #27ae60;"><b>{column.get('status', 'SAFE')}</b></td>
                </tr>
            </table>
            """
            
        elif 'Geotechnical' in analysis_type:
            bc = results.get('bearing_capacity', {})
            settlement = results.get('settlement', {})
            
            html += f"""
            <h2 style="color: #8B4513;">🏗️ Bearing Capacity</h2>
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <tr style="background: #ecf0f1;">
                    <th style="padding: 10px; text-align: left; border: 1px solid #bdc3c7;">Parameter</th>
                    <th style="padding: 10px; text-align: right; border: 1px solid #bdc3c7;">Value</th>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Ultimate Bearing Capacity</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{bc.get('ultimate', 0):.2f} kPa</b></td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Allowable Bearing Capacity</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{bc.get('allowable', 0):.2f} kPa</b></td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Applied Pressure</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{bc.get('applied', 0):.2f} kPa</b></td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Factor of Safety</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{bc.get('safety_factor', 3.0):.2f}</b></td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Status</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right; color: #27ae60;"><b>{bc.get('status', 'SAFE')}</b></td>
                </tr>
            </table>
            
            <h2 style="color: #8B4513; margin-top: 30px;">📐 Settlement Analysis</h2>
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <tr style="background: #ecf0f1;">
                    <th style="padding: 10px; text-align: left; border: 1px solid #bdc3c7;">Type</th>
                    <th style="padding: 10px; text-align: right; border: 1px solid #bdc3c7;">Value (mm)</th>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Immediate Settlement</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{settlement.get('immediate', 0):.2f}</b></td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Consolidation Settlement</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{settlement.get('consolidation', 0):.2f}</b></td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Total Settlement</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{settlement.get('total', 0):.2f}</b></td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Allowable Settlement</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{settlement.get('allowable', 25):.2f}</b></td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Status</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right; color: #27ae60;"><b>{settlement.get('status', 'ACCEPTABLE')}</b></td>
                </tr>
            </table>
            """
            
        elif 'Cost' in analysis_type:
            breakdown = results.get('cost_breakdown', {})
            boq = results.get('boq', [])
            
            html += f"""
            <h2 style="color: #2ecc71;">💰 Cost Breakdown</h2>
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <tr style="background: #ecf0f1;">
                    <th style="padding: 10px; text-align: left; border: 1px solid #bdc3c7;">Category</th>
                    <th style="padding: 10px; text-align: right; border: 1px solid #bdc3c7;">Amount (₹)</th>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Materials</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{breakdown.get('materials', 0):,.2f}</b></td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Labor</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{breakdown.get('labor', 0):,.2f}</b></td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Equipment</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{breakdown.get('equipment', 0):,.2f}</b></td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Overhead</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{breakdown.get('overhead', 0):,.2f}</b></td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Profit</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{breakdown.get('profit', 0):,.2f}</b></td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; border: 1px solid #ecf0f1;">Contingency</td>
                    <td style="padding: 8px; border: 1px solid #ecf0f1; text-align: right;"><b>{breakdown.get('contingency', 0):,.2f}</b></td>
                </tr>
                <tr style="background: #d5f4e6;">
                    <td style="padding: 10px; border: 1px solid #27ae60; font-weight: bold; font-size: 16px;">GRAND TOTAL</td>
                    <td style="padding: 10px; border: 1px solid #27ae60; text-align: right; font-weight: bold; font-size: 16px; color: #27ae60;"><b>₹ {breakdown.get('grand_total', 0):,.2f}</b></td>
                </tr>
            </table>
            
            <h2 style="color: #2ecc71; margin-top: 30px;">📋 Bill of Quantities (Top 5)</h2>
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 12px;">
                <tr style="background: #ecf0f1;">
                    <th style="padding: 8px; text-align: left; border: 1px solid #bdc3c7;">Description</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid #bdc3c7;">Qty</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid #bdc3c7;">Unit</th>
                    <th style="padding: 8px; text-align: right; border: 1px solid #bdc3c7;">Total (₹)</th>
                </tr>
            """
            
            for i, item in enumerate(boq[:5]):
                bg = '#f9f9f9' if i % 2 else 'white'
                html += f"""
                <tr style="background: {bg};">
                    <td style="padding: 6px; border: 1px solid #ecf0f1;">{item.get('description', 'N/A')}</td>
                    <td style="padding: 6px; border: 1px solid #ecf0f1; text-align: center;">{item.get('quantity', 0):.2f}</td>
                    <td style="padding: 6px; border: 1px solid #ecf0f1; text-align: center;">{item.get('unit', '')}</td>
                    <td style="padding: 6px; border: 1px solid #ecf0f1; text-align: right;"><b>{item.get('total_cost', 0):,.2f}</b></td>
                </tr>
                """
            
            html += "</table>"
            
        elif 'Carbon' in analysis_type:
            materials = results.get('materials', [])
            totals = results.get('totals', {})
            benchmark = results.get('benchmark', {})
            
            html += f"""
            <h2 style="color: #e67e22;">🌍 Carbon Footprint Analysis</h2>
            <div style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 5px solid #f39c12; margin: 20px 0;">
                <h3 style="margin-top: 0;">Total Emissions</h3>
                <p style="font-size: 28px; font-weight: bold; color: #e67e22; margin: 10px 0;">
                    {totals.get('total_co2e', 0):,.2f} kg CO₂e
                </p>
                <p style="color: #7f8c8d;">Carbon Intensity: <b>{benchmark.get('project_intensity', 0):.2f} kg CO₂e/m²</b></p>
            </div>
            
            <h3 style="color: #e67e22;">Material Emissions Breakdown</h3>
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 12px;">
                <tr style="background: #ecf0f1;">
                    <th style="padding: 8px; text-align: left; border: 1px solid #bdc3c7;">Material</th>
                    <th style="padding: 8px; text-align: center; border: 1px solid #bdc3c7;">Quantity</th>
                    <th style="padding: 8px; text-align: right; border: 1px solid #bdc3c7;">Emissions (kg CO₂e)</th>
                </tr>
            """
            
            for i, mat in enumerate(materials[:10]):
                bg = '#f9f9f9' if i % 2 else 'white'
                html += f"""
                <tr style="background: {bg};">
                    <td style="padding: 6px; border: 1px solid #ecf0f1;">{mat.get('material', 'N/A')}</td>
                    <td style="padding: 6px; border: 1px solid #ecf0f1; text-align: center;">{mat.get('quantity', 0):.2f} {mat.get('unit', '')}</td>
                    <td style="padding: 6px; border: 1px solid #ecf0f1; text-align: right;"><b>{mat.get('total_emissions', 0):,.2f}</b></td>
                </tr>
                """
            
            html += f"""
            </table>
            
            <h3 style="color: #27ae60; margin-top: 30px;">Performance Rating</h3>
            <div style="background: #d5f4e6; padding: 15px; border-radius: 8px; border-left: 5px solid #27ae60;">
                <p style="font-size: 18px; font-weight: bold; color: #27ae60; margin: 5px 0;">
                    {benchmark.get('performance', 'Good')}
                </p>
                <p style="color: #2c3e50; margin: 5px 0;">
                    Your project: <b>{benchmark.get('project_intensity', 0):.2f} kg CO₂e/m²</b><br>
                    Industry average: <b>{benchmark.get('industry_average', 400):.2f} kg CO₂e/m²</b>
                </p>
            </div>
            """
        
        else:
            html += f"""
            <div style="text-align: center; padding: 50px;">
                <h2 style="color: #27ae60;">✓ Analysis Completed Successfully</h2>
                <p style="font-size: 16px; color: #7f8c8d;">
                    Detailed results are available in the Analysis Panel.<br>
                    Check the Charts and Heatmaps tabs for visual representation.
                </p>
            </div>
            """
        
        html += """
        <hr style="border: 1px solid #ecf0f1; margin: 30px 0;">
        <div style="background: #ecf0f1; padding: 15px; border-radius: 5px;">
            <h3 style="margin-top: 0;">💡 Next Steps</h3>
            <ul style="line-height: 1.8;">
                <li>📊 View charts and graphs in the <b>Charts & Graphs</b> tab</li>
                <li>🔥 Check stress distribution in the <b>Heatmaps</b> tab</li>
                <li>🏗️ See 3D visualization in the <b>3D Model</b> tab</li>
                <li>📑 Generate PDF report: Press <b>Ctrl+R</b></li>
                <li>🤖 Get AI explanation: Click <b>Get AI Explanation</b> button</li>
            </ul>
        </div>
        </div>
        """
        
        return html
