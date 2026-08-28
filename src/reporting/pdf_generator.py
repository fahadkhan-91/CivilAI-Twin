"""
PDF report generator for CivilAI Twin
Creates professional engineering reports with calculations, graphs, and recommendations
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger
import io


class PDFReportGenerator:
    """Generate professional PDF reports"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Heading 1
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#3498db'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Heading 2
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            fontName='Helvetica'
        ))
    
    def generate_report(self, analysis_type: str, results: Dict[str, Any], 
                       output_path: str, project_info: Dict[str, str] = None) -> str:
        """
        Generate comprehensive PDF report
        
        Args:
            analysis_type: Type of analysis
            results: Analysis results dictionary
            output_path: Output file path
            project_info: Project information dictionary
        
        Returns:
            Path to generated PDF file
        """
        
        logger.info(f"Generating PDF report for {analysis_type} analysis")
        
        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build story (content)
        story = []
        
        # Cover page
        story.extend(self._create_cover_page(analysis_type, project_info))
        story.append(PageBreak())
        
        # Table of contents
        story.extend(self._create_toc(analysis_type))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(analysis_type, results))
        story.append(PageBreak())
        
        # Analysis methodology
        story.extend(self._create_methodology_section(analysis_type))
        story.append(PageBreak())
        
        # Detailed results
        story.extend(self._create_results_section(analysis_type, results))
        story.append(PageBreak())
        
        # Recommendations
        story.extend(self._create_recommendations_section(results))
        story.append(PageBreak())
        
        # Appendices
        story.extend(self._create_appendices(analysis_type, results))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"PDF report generated: {output_path}")
        
        return output_path
    
    def _create_cover_page(self, analysis_type: str, project_info: Dict[str, str] = None) -> List:
        """Create cover page"""
        
        story = []
        
        # Spacer
        story.append(Spacer(1, 2*inch))
        
        # Title
        title = Paragraph(f"{analysis_type.title()} Analysis Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        subtitle = Paragraph("CivilAI Twin - AI Engineer for Infrastructure", self.styles['CustomHeading2'])
        story.append(subtitle)
        story.append(Spacer(1, 1.5*inch))
        
        # Project information
        if project_info:
            project_data = [
                ["Project Name:", project_info.get('name', 'N/A')],
                ["Location:", project_info.get('location', 'N/A')],
                ["Client:", project_info.get('client', 'N/A')],
                ["Engineer:", project_info.get('engineer', 'N/A')],
                ["Date:", datetime.now().strftime("%B %d, %Y")]
            ]
        else:
            project_data = [
                ["Analysis Type:", analysis_type.title()],
                ["Report Date:", datetime.now().strftime("%B %d, %Y")],
                ["Generated By:", "CivilAI Twin v1.0.0"]
            ]
        
        project_table = Table(project_data, colWidths=[2*inch, 4*inch])
        project_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(project_table)
        
        return story
    
    def _create_toc(self, analysis_type: str) -> List:
        """Create table of contents"""
        
        story = []
        
        story.append(Paragraph("Table of Contents", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        toc_items = [
            "1. Executive Summary",
            "2. Analysis Methodology",
            "3. Detailed Results",
            "4. Recommendations",
            "5. Appendices"
        ]
        
        for item in toc_items:
            story.append(Paragraph(item, self.styles['CustomBody']))
            story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _create_executive_summary(self, analysis_type: str, results: Dict[str, Any]) -> List:
        """Create executive summary"""
        
        story = []
        
        story.append(Paragraph("1. Executive Summary", self.styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        # Analysis overview
        summary = results.get('summary', {})
        status = summary.get('status', 'UNKNOWN')
        
        # Status box
        status_color = colors.green if status == 'PASS' else colors.red if status == 'FAIL' else colors.orange
        
        status_text = f"""
        <para align=center>
        <font size=14><b>Analysis Status: {status}</b></font>
        </para>
        """
        
        status_para = Paragraph(status_text, self.styles['BodyText'])
        status_table = Table([[status_para]], colWidths=[6*inch])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), status_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        story.append(status_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Key findings
        story.append(Paragraph("Key Findings:", self.styles['CustomHeading2']))
        
        findings_text = f"""
        This {analysis_type} analysis was conducted using industry-standard methods and code requirements.
        The analysis evaluated critical parameters and identified potential areas of concern.
        Detailed results and recommendations are provided in the following sections.
        """
        
        story.append(Paragraph(findings_text, self.styles['CustomBody']))
        
        return story
    
    def _create_methodology_section(self, analysis_type: str) -> List:
        """Create methodology section"""
        
        story = []
        
        story.append(Paragraph("2. Analysis Methodology", self.styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        methodology_text = {
            'structural': """
                The structural analysis was performed following established engineering principles
                and code requirements. The methodology includes:
                <br/><br/>
                • Load analysis and distribution<br/>
                • Member capacity calculations<br/>
                • Deflection and serviceability checks<br/>
                • Code compliance verification<br/>
                • Safety factor application
            """,
            'geotechnical': """
                The geotechnical analysis was conducted using standard soil mechanics principles:
                <br/><br/>
                • Bearing capacity calculation (Terzaghi method)<br/>
                • Settlement analysis (elastic and consolidation)<br/>
                • Stability checks (sliding and overturning)<br/>
                • Factor of safety application<br/>
                • Site-specific soil parameter evaluation
            """,
            'climate': """
                Climate and disaster risk assessment methodology:
                <br/><br/>
                • Historical climate data analysis<br/>
                • Topographic and hydrological evaluation<br/>
                • Flood risk mapping and assessment<br/>
                • Rainfall intensity-duration-frequency curves<br/>
                • Risk level classification and mitigation strategies
            """
        }
        
        text = methodology_text.get(analysis_type.lower(), """
            Standard engineering analysis methodology was applied following
            relevant codes and industry best practices.
        """)
        
        story.append(Paragraph(text, self.styles['CustomBody']))
        
        return story
    
    def _create_results_section(self, analysis_type: str, results: Dict[str, Any]) -> List:
        """Create detailed results section"""
        
        story = []
        
        story.append(Paragraph("3. Detailed Results", self.styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        # Get summary from results
        summary = results.get('summary', {})
        
        # If no summary in expected format, try to extract from top level
        if not summary and results:
            # Try different keys based on analysis type
            if 'bearing_capacity' in results:
                summary = results.get('bearing_capacity', {})
            elif 'carbon_data' in results:
                summary = results.get('carbon_data', {})
            elif 'cost_breakdown' in results:
                summary = results.get('cost_breakdown', {})
            elif 'beam' in results or 'column' in results:
                summary = {'Type': analysis_type, 'Status': results.get('status', 'Complete')}
            else:
                # Use whatever top-level data is available
                summary = results
        
        # Create results table with better formatting
        results_data = [["Parameter", "Value"]]
        
        if summary:
            for key, value in summary.items():
                if isinstance(value, dict):
                    # Skip nested dictionaries
                    continue
                elif isinstance(value, (int, float)):
                    results_data.append([str(key).replace('_', ' ').title(), f"{value:.2f}"])
                elif isinstance(value, list):
                    # Show list length
                    results_data.append([str(key).replace('_', ' ').title(), f"{len(value)} items"])
                else:
                    results_data.append([str(key).replace('_', ' ').title(), str(value)])
        else:
            # If no summary data, show message
            results_data.append(["Status", "Analysis completed"])
            results_data.append(["Note", "Detailed data available in appendices"])
        
        results_table = Table(results_data, colWidths=[3*inch, 3*inch])
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ]))
        
        story.append(results_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Add detailed subsections based on analysis type
        if analysis_type.lower() == 'structural' or 'beam' in results or 'column' in results:
            story.append(Paragraph("Structural Elements:", self.styles['CustomHeading2']))
            
            for element in ['beam', 'column', 'slab']:
                if element in results:
                    elem_data = results[element]
                    story.append(Paragraph(f"<b>{element.title()}:</b>", self.styles['CustomBody']))
                    elem_text = ", ".join([f"{k.replace('_', ' ').title()}: {v}" for k, v in elem_data.items() if not isinstance(v, (dict, list))])
                    story.append(Paragraph(elem_text, self.styles['CustomBody']))
                    story.append(Spacer(1, 0.1*inch))
        
        elif 'bearing_capacity' in results or 'settlement' in results:
            story.append(Paragraph("Geotechnical Parameters:", self.styles['CustomHeading2']))
            
            for section in ['bearing_capacity', 'settlement', 'stability']:
                if section in results:
                    sect_data = results[section]
                    story.append(Paragraph(f"<b>{section.replace('_', ' ').title()}:</b>", self.styles['CustomBody']))
                    sect_text = ", ".join([f"{k.replace('_', ' ').title()}: {v}" for k, v in sect_data.items() if not isinstance(v, (dict, list))])
                    story.append(Paragraph(sect_text, self.styles['CustomBody']))
                    story.append(Spacer(1, 0.1*inch))
        
        elif 'carbon_data' in results:
            story.append(Paragraph("Carbon Breakdown:", self.styles['CustomHeading2']))
            carbon = results.get('carbon_data', {})
            for key, value in carbon.items():
                story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value} kg CO₂e", self.styles['CustomBody']))
        
        elif 'cost_breakdown' in results:
            story.append(Paragraph("Cost Details:", self.styles['CustomHeading2']))
            costs = results.get('cost_breakdown', {})
            for key, value in costs.items():
                story.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> ₹{value:,.2f}", self.styles['CustomBody']))
        
        return story
    
    def _create_recommendations_section(self, results: Dict[str, Any]) -> List:
        """Create recommendations section"""
        
        story = []
        
        story.append(Paragraph("4. Recommendations", self.styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        recommendations = results.get('recommendations', [])
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                rec_text = f"<b>{i}.</b> {rec}"
                story.append(Paragraph(rec_text, self.styles['CustomBody']))
                story.append(Spacer(1, 0.1*inch))
        else:
            story.append(Paragraph("No specific recommendations generated.", self.styles['CustomBody']))
        
        return story
    
    def _create_appendices(self, analysis_type: str, results: Dict[str, Any]) -> List:
        """Create appendices section"""
        
        story = []
        
        story.append(Paragraph("5. Appendices", self.styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
        
        # Appendix A: Assumptions
        story.append(Paragraph("Appendix A: Analysis Assumptions", self.styles['CustomHeading2']))
        
        assumptions_text = """
        • Analysis based on information provided at the time of report generation<br/>
        • Standard material properties assumed unless specified<br/>
        • Load combinations per applicable code requirements<br/>
        • Site conditions assumed to match provided data
        """
        
        story.append(Paragraph(assumptions_text, self.styles['CustomBody']))
        story.append(Spacer(1, 0.2*inch))
        
        # Appendix B: References
        story.append(Paragraph("Appendix B: References", self.styles['CustomHeading2']))
        
        references_text = """
        • Relevant building codes and standards<br/>
        • Engineering textbooks and manuals<br/>
        • Industry best practices<br/>
        • CivilAI Twin Analysis Engine v1.0.0
        """
        
        story.append(Paragraph(references_text, self.styles['CustomBody']))
        
        return story
    
    def quick_report(self, title: str, content: str, output_path: str) -> str:
        """Generate quick simple report"""
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(content, self.styles['CustomBody']))
        
        doc.build(story)
        
        return output_path
