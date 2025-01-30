from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from io import BytesIO
import json
from datetime import datetime

class PDFReportGenerator:
    def __init__(self, report_data):
        self.report_data = report_data
        self.buffer = BytesIO()
        self.styles = getSampleStyleSheet()
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

    def create_header(self):
        elements = []
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        elements.append(Paragraph(self.report_data['report_type'], title_style))
        
        # Date Range
        date_style = ParagraphStyle(
            'DateRange',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.gray
        )
        date_range = f"Period: {self.report_data['start_date']} to {self.report_data['end_date']}"
        elements.append(Paragraph(date_range, date_style))
        elements.append(Spacer(1, 20))
        
        return elements

    def create_summary_table(self):
        # Calculate totals
        total_income = sum(float(t['amount']) for t in self.report_data['transactions'] 
                          if t['transaction_type'] == 'income')
        total_expenses = sum(float(t['amount']) for t in self.report_data['transactions'] 
                           if t['transaction_type'] == 'expense')
        net_amount = total_income - total_expenses

        # Create summary table
        summary_data = [
            ['Summary', 'Amount'],
            ['Total Income', f"${total_income:,.2f}"],
            ['Total Expenses', f"${total_expenses:,.2f}"],
            ['Net Amount', f"${net_amount:,.2f}"]
        ]

        table = Table(summary_data, colWidths=[2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table

    def create_transactions_table(self):
        # Prepare transactions data
        transactions = self.report_data['transactions']
        if not transactions:
            return None

        # Table headers
        headers = ['Date', 'Amount', 'Category', 'Type']
        data = [headers]

        # Add transaction rows
        for t in transactions:
            data.append([
                t['date'],
                f"${float(t['amount']):,.2f}",
                t['category__name'],
                t['transaction_type'].title()
            ])

        # Create table
        table = Table(data, colWidths=[1.5*inch, 1.5*inch, 2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        return table

    def generate(self):
        # Build the document
        elements = []
        
        # Add header
        elements.extend(self.create_header())
        
        # Add summary table
        elements.append(self.create_summary_table())
        elements.append(Spacer(1, 20))
        
        # Add transactions table
        transactions_table = self.create_transactions_table()
        if transactions_table:
            elements.append(Paragraph('Transaction Details', self.styles['Heading2']))
            elements.append(Spacer(1, 10))
            elements.append(transactions_table)
        
        # Build PDF
        self.doc.build(elements)
        
        # Get the value of the BytesIO buffer
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf