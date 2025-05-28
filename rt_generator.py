import os
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class ReportGenerator:
    """
    Utility class for generating reports
    """
    
    def __init__(self, reports_dir="reports", logo_path=None):
        """Initialize the report generator"""
        self.reports_dir = reports_dir
        self.logo_path = logo_path
        
        # Create reports directory if it doesn't exist
        os.makedirs(reports_dir, exist_ok=True)
        
        # Get styles
        self.styles = getSampleStyleSheet()
        
        # Create custom styles - check if they exist first
        try:
                self.styles.add(ParagraphStyle(
                    name='PSTitle',
                    parent=self.styles['Heading1'],
                    fontSize=18,
                    alignment=1,  # Center
                    spaceAfter=12
                ))
        except KeyError:
            # Style already exists, just use it
            pass
            
        try:
                self.styles.add(ParagraphStyle(
                    name='PSSubtitle',
                    parent=self.styles['Heading2'],
                    fontSize=14,
                    alignment=1,  # Center
                    spaceAfter=10
                ))
        except KeyError:
            # Style already exists, just use it
            pass
            
        try:
                self.styles.add(ParagraphStyle(
                    name='PSSectionTitle',
                    parent=self.styles['Heading3'],
                    fontSize=12,
                    spaceBefore=10,
                    spaceAfter=6
                ))
        except KeyError:
            # Style already exists, just use it
            pass
    
    def generate_shift_report(self, shift_data):
        """
        Generate a shift report PDF
        
        Args:
            shift_data: Dictionary containing shift summary data
            
        Returns:
            The path to the generated PDF
        """
        # Create filename with date and time
        now = datetime.now()
        filename = f"shift_report_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        
        # Create elements list
        elements = []
        
        # Add logo if available
        if self.logo_path and os.path.exists(self.logo_path):
            img = Image(self.logo_path, width=1.5*inch, height=1.5*inch)
            img.hAlign = 'CENTER'
            elements.append(img)
            elements.append(Spacer(1, 0.25*inch))
        
        # Add title
            elements.append(Paragraph("PS Gaming Shop", self.styles['Heading1']))
            elements.append(Paragraph(f"Shift Report - {shift_data['date']}", self.styles['Heading2']))
        elements.append(Spacer(1, 0.25*inch))
        
        # Add summary section
        elements.append(Paragraph("Summary", self.styles['Heading3']))
        
        summary_data = [
            ["Total Customers", str(shift_data['total_customers'])],
            ["Total Gaming Sales", f"KES {shift_data['total_gaming']:.2f}"],
            ["Total Snacks Sales", f"KES {shift_data['total_snacks']:.2f}"],
            ["Total Sales", f"KES {shift_data['total_sales']:.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lavender),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Add payment methods section
        if shift_data['payment_methods']:
            elements.append(Paragraph("Payment Methods", self.styles['Heading3']))
            
            payment_data = [["Method", "Count", "Amount"]]
            for method, details in shift_data['payment_methods'].items():
                payment_data.append([
                    method, 
                    str(details['count']), 
                    f"KES {details['amount']:.2f}"
                ])
            
            payment_table = Table(payment_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            payment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lavender),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(payment_table)
            elements.append(Spacer(1, 0.25*inch))
        
        # Add consoles section
        if shift_data['consoles']:
            elements.append(Paragraph("Consoles", self.styles['Heading3']))
            
            console_data = [["Console", "Count"]]
            for console, count in shift_data['consoles'].items():
                console_data.append([console, str(count)])
            
            console_table = Table(console_data, colWidths=[3*inch, 2*inch])
            console_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lavender),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(console_table)
            elements.append(Spacer(1, 0.25*inch))
        
        # Add game genres section
        if shift_data['game_genres']:
            elements.append(Paragraph("Game Genres", self.styles['Heading3']))
            
            genre_data = [["Genre", "Count"]]
            for genre, count in shift_data['game_genres'].items():
                genre_data.append([genre, str(count)])
            
            genre_table = Table(genre_data, colWidths=[3*inch, 2*inch])
            genre_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lavender),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(genre_table)
        
        # Add footer
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(
            f"Generated on {now.strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Italic']
        ))
        
        # Build PDF
        doc.build(elements)
        
        return filepath
    
    def export_to_excel(self, data, filename=None):
        """
        Export data to Excel
        
        Args:
            data: Dictionary of dataframes to export (sheet_name: dataframe)
            filename: Optional filename, if None a default name will be generated
            
        Returns:
            The path to the generated Excel file
        """
        if filename is None:
            now = datetime.now()
            filename = f"PS_export_{now.strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = os.path.join(self.reports_dir, filename)
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Write each dataframe to a different sheet
            for sheet_name, df in data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return filepath