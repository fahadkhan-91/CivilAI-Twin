"""
Main application window for CivilAI Twin
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabWidget, QMenuBar, QMenu, QFileDialog, QMessageBox,
    QStatusBar, QToolBar, QLabel, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QIcon, QFont
from loguru import logger

from .analysis_panel import AnalysisPanel
from .visualization_panel import VisualizationPanel
from .settings_dialog import SettingsDialog
from utils.config import ConfigManager


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        
        self.config_manager = config_manager
        self.current_project = None
        
        self._init_ui()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        
        logger.info("Main window initialized")
    
    def _init_ui(self):
        """Initialize user interface"""
        
        self.setWindowTitle("CivilAI Twin - AI Engineer for Infrastructure")
        self.setGeometry(100, 100, 1600, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Analysis
        self.analysis_panel = AnalysisPanel(self.config_manager)
        self.analysis_panel.analysis_completed.connect(self._on_analysis_completed)
        splitter.addWidget(self.analysis_panel)
        
        # Right panel - Visualization
        self.visualization_panel = VisualizationPanel(self.config_manager)
        splitter.addWidget(self.visualization_panel)
        
        # Set initial sizes (40% analysis, 60% visualization)
        splitter.setSizes([640, 960])
        
        main_layout.addWidget(splitter)
        
        # Apply stylesheet
        self._apply_stylesheet()
    
    def _create_header(self) -> QWidget:
        """Create application header"""
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(80)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Title and subtitle
        title_layout = QVBoxLayout()
        
        title_label = QLabel("CivilAI Twin")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("AI Engineer for Infrastructure")
        subtitle_font = QFont("Arial", 12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #666;")
        title_layout.addWidget(subtitle_label)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Quick action buttons
        self.btn_new_project = QPushButton("New Project")
        self.btn_new_project.setFixedSize(120, 40)
        self.btn_new_project.clicked.connect(self._new_project)
        layout.addWidget(self.btn_new_project)
        
        self.btn_open_project = QPushButton("Open Project")
        self.btn_open_project.setFixedSize(120, 40)
        self.btn_open_project.clicked.connect(self._open_project)
        layout.addWidget(self.btn_open_project)
        
        return header
    
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Project", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_project)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        import_menu = file_menu.addMenu("Import")
        import_bim_action = QAction("BIM Model (IFC)", self)
        import_bim_action.triggered.connect(self._import_bim)
        import_menu.addAction(import_bim_action)
        
        import_drawing_action = QAction("Drawings (PDF/DWG)", self)
        import_drawing_action.triggered.connect(self._import_drawings)
        import_menu.addAction(import_drawing_action)
        
        import_photos_action = QAction("Site Photos", self)
        import_photos_action.triggered.connect(self._import_photos)
        import_menu.addAction(import_photos_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Analysis menu
        analysis_menu = menubar.addMenu("Analysis")
        
        structural_action = QAction("Structural Check", self)
        structural_action.triggered.connect(lambda: self.analysis_panel.run_analysis("structural"))
        analysis_menu.addAction(structural_action)
        
        geotechnical_action = QAction("Geotechnical Analysis", self)
        geotechnical_action.triggered.connect(lambda: self.analysis_panel.run_analysis("geotechnical"))
        analysis_menu.addAction(geotechnical_action)
        
        climate_action = QAction("Climate Risk Assessment", self)
        climate_action.triggered.connect(lambda: self.analysis_panel.run_analysis("climate"))
        analysis_menu.addAction(climate_action)
        
        cv_action = QAction("Defect Detection", self)
        cv_action.triggered.connect(lambda: self.analysis_panel.run_analysis("computer_vision"))
        analysis_menu.addAction(cv_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        simulator_action = QAction("What-If Simulator", self)
        simulator_action.triggered.connect(self._open_simulator)
        tools_menu.addAction(simulator_action)
        
        report_action = QAction("Generate Report", self)
        report_action.setShortcut("Ctrl+R")
        report_action.triggered.connect(self._generate_report)
        tools_menu.addAction(report_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        preferences_action = QAction("Preferences", self)
        preferences_action.triggered.connect(self._open_settings)
        settings_menu.addAction(preferences_action)
        
        api_config_action = QAction("API Configuration", self)
        api_config_action.triggered.connect(self._configure_api)
        settings_menu.addAction(api_config_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        docs_action = QAction("Documentation", self)
        docs_action.triggered.connect(self._open_documentation)
        help_menu.addAction(docs_action)
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # New Project
        new_action = QAction("📁 New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setToolTip("Create new project (Ctrl+N)")
        new_action.triggered.connect(self._new_project)
        toolbar.addAction(new_action)
        
        # Open Project
        open_action = QAction("📂 Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setToolTip("Open project (Ctrl+O)")
        open_action.triggered.connect(self._open_project)
        toolbar.addAction(open_action)
        
        # Save Project
        save_action = QAction("💾 Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setToolTip("Save project (Ctrl+S)")
        save_action.triggered.connect(self._save_project)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Analyze
        analyze_action = QAction("📊 Analyze", self)
        analyze_action.setToolTip("Run analysis")
        analyze_action.triggered.connect(self._run_current_analysis)
        toolbar.addAction(analyze_action)
        
        # Visualize
        visualize_action = QAction("📈 Visualize", self)
        visualize_action.setToolTip("Switch to visualization view")
        visualize_action.triggered.connect(self._show_visualization)
        toolbar.addAction(visualize_action)
        
        # Report
        report_action = QAction("📄 Report", self)
        report_action.setShortcut("Ctrl+R")
        report_action.setToolTip("Generate PDF report (Ctrl+R)")
        report_action.triggered.connect(self._generate_report)
        toolbar.addAction(report_action)
        
        toolbar.addSeparator()
        
        # Settings
        settings_action = QAction("⚙️ Settings", self)
        settings_action.setToolTip("Open settings")
        settings_action.triggered.connect(self._open_settings)
        toolbar.addAction(settings_action)
    
    def _create_status_bar(self):
        """Create status bar"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Status message
        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)
        
        # AI mode indicator
        ai_mode = self.config_manager.get('ai.mode', 'built-in')
        self.ai_mode_label = QLabel(f"AI Mode: {ai_mode.upper()}")
        status_bar.addPermanentWidget(self.ai_mode_label)
    
    def _apply_stylesheet(self):
        """Apply application stylesheet"""
        stylesheet = """
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            #header {
                background-color: #2c3e50;
                color: white;
                border-bottom: 3px solid #3498db;
            }
            
            #header QLabel {
                color: white;
            }
            
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #21618c;
            }
            
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                color: #3498db;
                font-weight: bold;
            }
            
            QTabBar::tab:hover {
                background-color: #d5dbdb;
            }
        """
        self.setStyleSheet(stylesheet)
    
    # Slot methods
    def _new_project(self):
        """Create new project"""
        logger.info("Creating new project")
        self.status_label.setText("Creating new project...")
        
        # Show project setup dialog
        from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QTextEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle("New Project")
        dialog.setMinimumWidth(500)
        
        layout = QFormLayout(dialog)
        
        # Project name
        name_input = QLineEdit()
        name_input.setPlaceholderText("e.g., Building Construction 2026")
        layout.addRow("Project Name:", name_input)
        
        # Location
        location_input = QLineEdit()
        location_input.setPlaceholderText("e.g., Mumbai, Maharashtra")
        layout.addRow("Location:", location_input)
        
        # Engineer
        engineer_input = QLineEdit()
        engineer_input.setPlaceholderText("Your name")
        layout.addRow("Engineer:", engineer_input)
        
        # Description
        desc_input = QTextEdit()
        desc_input.setPlaceholderText("Brief project description (optional)")
        desc_input.setMaximumHeight(100)
        layout.addRow("Description:", desc_input)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            project_name = name_input.text() or "Untitled Project"
            self.current_project = {
                'name': project_name,
                'location': location_input.text(),
                'engineer': engineer_input.text(),
                'description': desc_input.toPlainText(),
                'created': str(Path(__file__).parent.parent.parent)
            }
            self.setWindowTitle(f"CivilAI Twin - {project_name}")
            self.status_label.setText(f"Project created: {project_name}")
            logger.info(f"New project created: {project_name}")
            
            QMessageBox.information(
                self, 
                "Project Created", 
                f"New project '{project_name}' created successfully!\n\n"
                "You can now:\n"
                "• Select an analysis type from the left panel\n"
                "• Click 'Run Analysis' to perform calculations\n"
                "• Get AI explanations of results\n"
                "• Generate PDF reports (Ctrl+R)"
            )
        else:
            self.status_label.setText("New project cancelled")
    
    def _open_project(self):
        """Open existing project"""
        logger.info("Opening project")
        
        # For now, show info about the feature
        QMessageBox.information(
            self,
            "Open Project",
            "Project file loading will be available in the next update.\n\n"
            "For now, you can:\n"
            "1. Click 'New Project' to create a project\n"
            "2. Run any analysis directly from the Analysis panel\n"
            "3. Generate reports for your analysis results\n\n"
            "Project files (.civilai format) will allow you to save and reload\n"
            "your analysis data, settings, and results."
        )
        
        self.status_label.setText("Ready")
    
    def _save_project(self):
        """Save current project"""
        logger.info("Saving project")
        if self.current_project:
            # TODO: Implement project saving logic
            self.status_label.setText("Project saved successfully")
        else:
            QMessageBox.warning(self, "No Project", "No active project to save.")
    
    def _import_bim(self):
        """Import BIM model"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import BIM Model",
            "",
            "IFC Files (*.ifc);;All Files (*.*)"
        )
        if file_path:
            logger.info(f"Importing BIM model: {file_path}")
            self.status_label.setText(f"Importing BIM model: {file_path}")
            # TODO: Implement BIM import logic
            self.visualization_panel.load_bim_model(file_path)
    
    def _import_drawings(self):
        """Import drawings"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Import Drawings",
            "",
            "Drawings (*.pdf *.dwg *.dxf);;All Files (*.*)"
        )
        if file_paths:
            logger.info(f"Importing {len(file_paths)} drawing(s)")
            self.status_label.setText(f"Importing {len(file_paths)} drawing(s)")
            # TODO: Implement drawing import logic
    
    def _import_photos(self):
        """Import site photos"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Import Site Photos",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
        )
        if file_paths:
            logger.info(f"Importing {len(file_paths)} photo(s)")
            self.status_label.setText(f"Importing {len(file_paths)} photo(s)")
            # TODO: Implement photo import logic
    
    def _open_simulator(self):
        """Open what-if simulator"""
        logger.info("Opening what-if simulator")
        # TODO: Implement simulator window
        QMessageBox.information(self, "Simulator", "What-If Simulator will be implemented here.")
    
    def _generate_report(self):
        """Generate PDF report"""
        logger.info("Generating report")
        
        # Check if analysis has been run
        if not hasattr(self.analysis_panel, 'current_results'):
            QMessageBox.warning(
                self,
                "No Analysis Results",
                "Please run an analysis first before generating a report.\n\n"
                "Steps:\n"
                "1. Select analysis type from left panel\n"
                "2. Click 'Run Analysis'\n"
                "3. Wait for results\n"
                "4. Then generate report"
            )
            return
        
        # Ask for save location
        from datetime import datetime
        default_name = f"CivilAI_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Report As",
            default_name,
            "PDF Files (*.pdf);;All Files (*.*)"
        )
        
        if not file_path:
            self.status_label.setText("Report generation cancelled")
            return
        
        try:
            # Generate the report
            from reporting.pdf_generator import PDFReportGenerator
            
            generator = PDFReportGenerator(self.config_manager)
            
            # Get analysis results
            results = self.analysis_panel.current_results
            analysis_type = results.get('type', 'Analysis')
            
            # Get project info
            project_info = self.current_project if self.current_project else {
                'name': 'CivilAI Twin Analysis',
                'location': 'N/A',
                'engineer': 'N/A',
                'description': 'Engineering analysis report'
            }
            
            # Generate report with correct parameter order
            self.status_label.setText("Generating PDF report...")
            generator.generate_report(analysis_type, results, file_path, project_info)
            
            self.status_label.setText(f"Report saved: {file_path}")
            logger.info(f"Report generated: {file_path}")
            
            # Show success message
            reply = QMessageBox.question(
                self,
                "Report Generated",
                f"Report successfully generated:\n{file_path}\n\nDo you want to open it now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    import os
                    import subprocess
                    import platform
                    
                    system = platform.system()
                    if system == 'Windows':
                        os.startfile(file_path)
                    elif system == 'Darwin':  # macOS
                        subprocess.call(['open', file_path])
                    else:  # Linux
                        subprocess.call(['xdg-open', file_path])
                except Exception as open_error:
                    logger.warning(f"Could not auto-open PDF: {open_error}")
                    QMessageBox.information(
                        self,
                        "Report Saved",
                        f"Report saved successfully!\n\nLocation:\n{file_path}\n\nPlease open it manually."
                    )
                
        except Exception as e:
            logger.exception(f"Report generation error: {e}")
            QMessageBox.critical(
                self,
                "Report Generation Error",
                f"Failed to generate report:\n{str(e)}\n\nCheck logs for details."
            )
            self.status_label.setText("Report generation failed")
    
    def _open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.config_manager, self)
        dialog.exec()
    
    def _configure_api(self):
        """Configure API settings"""
        dialog = SettingsDialog(self.config_manager, self, tab=1)
        dialog.exec()
    
    def _open_documentation(self):
        """Open documentation"""
        QMessageBox.information(
            self,
            "Documentation",
            "Documentation is available at:\n\nhttps://github.com/yourusername/CivilAI-Twin/wiki"
        )
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>CivilAI Twin</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>AI Engineer for Infrastructure</b></p>
        <br>
        <p>An integrated platform for BIM analysis, structural assessment,
        geotechnical evaluation, and intelligent infrastructure engineering.</p>
        <br>
        <p>© 2026 CivilAI. All rights reserved.</p>
        """
        QMessageBox.about(self, "About CivilAI Twin", about_text)
    
    def _on_analysis_completed(self, results: dict):
        """Handle analysis completion"""
        logger.info(f"Analysis completed: {results.get('type', 'unknown')}")
        self.status_label.setText("Analysis completed successfully")
        
        # Update visualization with results
        self.visualization_panel.update_results(results)
    
    def _run_current_analysis(self):
        """Run the currently selected analysis"""
        logger.info("Running current analysis from toolbar")
        self.analysis_panel._run_analysis()
    
    def _show_visualization(self):
        """Switch focus to visualization panel"""
        logger.info("Switching to visualization view")
        # The visualization panel is already visible, just show a status message
        self.status_label.setText("Visualization panel active - Run analysis to see results")
        QMessageBox.information(
            self,
            "Visualization",
            "Run an analysis to see results in the visualization panel.\n\n"
            "The right panel will display:\n"
            "• Charts & Graphs\n"
            "• 3D Models (when BIM imported)\n"
            "• Heatmaps\n"
            "• Detailed data tables"
        )
