"""
Settings dialog for CivilAI Twin
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTabWidget, QWidget, QLineEdit, QComboBox, QCheckBox,
    QGroupBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from loguru import logger

from utils.config import ConfigManager


class SettingsDialog(QDialog):
    """Settings dialog window"""
    
    def __init__(self, config_manager: ConfigManager, parent=None, tab=0):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        
        self._init_ui()
        self.tab_widget.setCurrentIndex(tab)
    
    def _init_ui(self):
        """Initialize user interface"""
        
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # General settings tab
        general_tab = self._create_general_tab()
        self.tab_widget.addTab(general_tab, "General")
        
        # AI configuration tab
        ai_tab = self._create_ai_tab()
        self.tab_widget.addTab(ai_tab, "AI Configuration")
        
        # Analysis settings tab
        analysis_tab = self._create_analysis_tab()
        self.tab_widget.addTab(analysis_tab, "Analysis Settings")
        
        # Visualization settings tab
        viz_tab = self._create_visualization_tab()
        self.tab_widget.addTab(viz_tab, "Visualization")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self._save_settings)
        button_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(button_layout)
    
    def _create_general_tab(self) -> QWidget:
        """Create general settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Application settings
        app_group = QGroupBox("Application")
        app_layout = QFormLayout(app_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        current_theme = self.config_manager.get('application.theme', 'light')
        self.theme_combo.setCurrentText(current_theme.title())
        app_layout.addRow("Theme:", self.theme_combo)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Español", "Français", "中文"])
        app_layout.addRow("Language:", self.language_combo)
        
        layout.addWidget(app_group)
        
        layout.addStretch()
        return widget
    
    def _create_ai_tab(self) -> QWidget:
        """Create AI configuration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # AI Mode
        mode_group = QGroupBox("AI Explanation Mode")
        mode_layout = QVBoxLayout(mode_group)
        
        mode_info = QLabel(
            "Choose how AI explanations work:\n\n"
            "• Built-in Mode: Rule-based explanations using engineering principles (no API required)\n"
            "• API Mode: Enhanced natural language explanations using AI APIs"
        )
        mode_info.setWordWrap(True)
        mode_layout.addWidget(mode_info)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Built-in (No API)", "API-Enhanced"])
        current_mode = self.config_manager.get('ai.mode', 'built-in')
        self.mode_combo.setCurrentIndex(0 if current_mode == 'built-in' else 1)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        
        layout.addWidget(mode_group)
        
        # API Configuration
        self.api_group = QGroupBox("API Configuration")
        api_layout = QFormLayout(self.api_group)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["OpenAI", "Anthropic"])
        current_provider = self.config_manager.get('ai.provider', 'openai')
        self.provider_combo.setCurrentText(current_provider.title())
        api_layout.addRow("Provider:", self.provider_combo)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter your API key")
        
        # Load existing API key if available
        provider = self.provider_combo.currentText().lower()
        existing_key = self.config_manager.get_api_key(provider)
        if existing_key:
            self.api_key_input.setText(existing_key)
        
        api_layout.addRow("API Key:", self.api_key_input)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"])
        current_model = self.config_manager.get('ai.model', 'gpt-4')
        self.model_combo.setCurrentText(current_model)
        api_layout.addRow("Model:", self.model_combo)
        
        # Test connection button
        self.btn_test_api = QPushButton("Test Connection")
        self.btn_test_api.clicked.connect(self._test_api_connection)
        api_layout.addRow("", self.btn_test_api)
        
        layout.addWidget(self.api_group)
        
        # Update visibility based on mode
        self._on_mode_changed()
        
        layout.addStretch()
        return widget
    
    def _create_analysis_tab(self) -> QWidget:
        """Create analysis settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Structural settings
        struct_group = QGroupBox("Structural Analysis")
        struct_layout = QFormLayout(struct_group)
        
        self.safety_factor_input = QLineEdit()
        self.safety_factor_input.setText(
            str(self.config_manager.get('analysis.structural.safety_factor', 1.5))
        )
        struct_layout.addRow("Safety Factor:", self.safety_factor_input)
        
        self.code_combo = QComboBox()
        self.code_combo.addItems(["ACI", "Eurocode", "IS Code", "BS Code"])
        current_code = self.config_manager.get('analysis.structural.code_standard', 'ACI')
        self.code_combo.setCurrentText(current_code)
        struct_layout.addRow("Code Standard:", self.code_combo)
        
        layout.addWidget(struct_group)
        
        # Geotechnical settings
        geo_group = QGroupBox("Geotechnical Analysis")
        geo_layout = QFormLayout(geo_group)
        
        self.soil_class_combo = QComboBox()
        self.soil_class_combo.addItems(["USCS", "AASHTO"])
        current_soil = self.config_manager.get('analysis.geotechnical.soil_classification', 'USCS')
        self.soil_class_combo.setCurrentText(current_soil)
        geo_layout.addRow("Soil Classification:", self.soil_class_combo)
        
        self.settlement_input = QLineEdit()
        self.settlement_input.setText(
            str(self.config_manager.get('analysis.geotechnical.settlement_limit_mm', 25))
        )
        geo_layout.addRow("Settlement Limit (mm):", self.settlement_input)
        
        layout.addWidget(geo_group)
        
        # Materials settings
        mat_group = QGroupBox("Materials")
        mat_layout = QFormLayout(mat_group)
        
        self.concrete_combo = QComboBox()
        self.concrete_combo.addItems(["M20", "M25", "M30", "M35", "M40"])
        current_concrete = self.config_manager.get('analysis.materials.concrete_grade', 'M25')
        self.concrete_combo.setCurrentText(current_concrete)
        mat_layout.addRow("Concrete Grade:", self.concrete_combo)
        
        self.steel_combo = QComboBox()
        self.steel_combo.addItems(["Fe415", "Fe500", "Fe550"])
        current_steel = self.config_manager.get('analysis.materials.steel_grade', 'Fe500')
        self.steel_combo.setCurrentText(current_steel)
        mat_layout.addRow("Steel Grade:", self.steel_combo)
        
        layout.addWidget(mat_group)
        
        layout.addStretch()
        return widget
    
    def _create_visualization_tab(self) -> QWidget:
        """Create visualization settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Render settings
        render_group = QGroupBox("Rendering")
        render_layout = QFormLayout(render_group)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Low", "Medium", "High", "Ultra"])
        current_quality = self.config_manager.get('visualization.render_quality', 'high')
        self.quality_combo.setCurrentText(current_quality.title())
        render_layout.addRow("Quality:", self.quality_combo)
        
        self.show_grid_check = QCheckBox()
        self.show_grid_check.setChecked(
            self.config_manager.get('visualization.show_grid', True)
        )
        render_layout.addRow("Show Grid:", self.show_grid_check)
        
        self.show_axes_check = QCheckBox()
        self.show_axes_check.setChecked(
            self.config_manager.get('visualization.show_axes', True)
        )
        render_layout.addRow("Show Axes:", self.show_axes_check)
        
        layout.addWidget(render_group)
        
        layout.addStretch()
        return widget
    
    def _on_mode_changed(self):
        """Handle AI mode change"""
        is_api_mode = self.mode_combo.currentIndex() == 1
        self.api_group.setEnabled(is_api_mode)
    
    def _test_api_connection(self):
        """Test API connection"""
        api_key = self.api_key_input.text().strip()
        provider = self.provider_combo.currentText().lower()
        
        if not api_key:
            QMessageBox.warning(self, "No API Key", "Please enter an API key first.")
            return
        
        # TODO: Implement actual API test
        QMessageBox.information(
            self,
            "Connection Test",
            f"Testing connection to {provider}...\n\n"
            "API connection test will be implemented here."
        )
    
    def _save_settings(self):
        """Save all settings"""
        try:
            # General settings
            self.config_manager.set('application.theme', self.theme_combo.currentText().lower())
            
            # AI settings
            ai_mode = 'built-in' if self.mode_combo.currentIndex() == 0 else 'api'
            self.config_manager.set('ai.mode', ai_mode)
            self.config_manager.set('ai.provider', self.provider_combo.currentText().lower())
            self.config_manager.set('ai.model', self.model_combo.currentText())
            
            # Save API key if provided
            api_key = self.api_key_input.text().strip()
            if api_key:
                provider = self.provider_combo.currentText().lower()
                self.config_manager.set_api_key(provider, api_key)
            
            # Analysis settings
            self.config_manager.set(
                'analysis.structural.safety_factor',
                float(self.safety_factor_input.text())
            )
            self.config_manager.set(
                'analysis.structural.code_standard',
                self.code_combo.currentText()
            )
            self.config_manager.set(
                'analysis.geotechnical.soil_classification',
                self.soil_class_combo.currentText()
            )
            self.config_manager.set(
                'analysis.geotechnical.settlement_limit_mm',
                float(self.settlement_input.text())
            )
            self.config_manager.set(
                'analysis.materials.concrete_grade',
                self.concrete_combo.currentText()
            )
            self.config_manager.set(
                'analysis.materials.steel_grade',
                self.steel_combo.currentText()
            )
            
            # Visualization settings
            self.config_manager.set(
                'visualization.render_quality',
                self.quality_combo.currentText().lower()
            )
            self.config_manager.set(
                'visualization.show_grid',
                self.show_grid_check.isChecked()
            )
            self.config_manager.set(
                'visualization.show_axes',
                self.show_axes_check.isChecked()
            )
            
            logger.info("Settings saved successfully")
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.accept()
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings:\n{str(e)}")
