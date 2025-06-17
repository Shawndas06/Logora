import logging
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import qrcode
from database.models import Account, Charge, Payment, Report
from database.connection import get_db
from utils.dirs import get_receipt_path, get_qr_path

logger = logging.getLogger(__name__)

class ReportService:
    @staticmethod
    def generate_report_data(account_id, period):
        """Generate report data (PDF and QR code) for an account within a specific period."""
        if not account_id:
            raise ValueError("Account ID is required")
        
        if not str(period).isdigit() or len(str(period)) != 6:
            raise ValueError("Period must be a valid YYYYMM format (e.g., 202506)")
        
        # Retrieve data from database
        account = Account.get_by_id(account_id)
        if not account:
            logger.error(f"Account ID {account_id} not found")
            raise ValueError(f"Account ID {account_id} not found")
        
        charges = Charge.get_by_account_id(account_id)
        payments = Payment.get_by_account_id(account_id)
        
        # Filter charges by period (assuming period_start is YYYY-MM-01)
        period_start = f"{period[:4]}-{period[4:6]}-01"
        charges = [c for c in charges if c.period_start == period_start]
        
        if not charges:
            logger.warning(f"No charges found for account {account_id} in period {period}")
            raise ValueError(f"No charges found for period {period}")
        
        # Prepare response data
        total_amount = sum(charge.amount for charge in charges)
        services_data = {charge.service_type: charge.amount for charge in charges}
        payments_data = [
            {"date": payment.payment_date, "amount": payment.amount, "method": payment.method}
            for payment in payments
        ]
        
        # Generate file paths
        receipt_path = get_receipt_path(account_id, period)
        qr_path = get_qr_path(account_id, period)
        
        # Generate PDF
        doc = SimpleDocTemplate(receipt_path, pagesize=A4)
        story = ReportService._create_pdf_content(account, charges, payments)
        doc.build(story)
        logger.info(f"PDF generated at {receipt_path} for account {account_id}")
        
        # Generate QR code
        qr_data = f"{account_id}:{total_amount:.2f}"
        ReportService._create_qr_code(qr_data, qr_path)
        logger.info(f"QR code generated at {qr_path} for account {account_id}")
        
        # Save report to database
        report_id = Report.create(
            account_id=account_id,
            period_start=period_start,
            period_end=charges[0].period_end,
            total_amount=total_amount,
            services_data=json.dumps(services_data),
            qr_data=qr_data,
            file_path=receipt_path
        )
        logger.info(f"Report saved to database with ID {report_id}")
        
        # Return structured response
        return {
            "account_id": account_id,
            "period": period,
            "account_number": account.number,
            "address": account.address,
            "total_amount": total_amount,
            "services": services_data,
            "payments": payments_data,
            "receipt_path": receipt_path,
            "qr_path": qr_path
        }
    
    @staticmethod
    def _create_pdf_content(account, charges, payments):
        """Create content for the PDF receipt."""
        styles = getSampleStyleSheet()
        story = []
        
        # Add title
        story.append(Paragraph("Квитанция об оплате", styles['Title']))
        story.append(Spacer(1, 12))
        
        # Account information table
        account_table_data = [
            ["Номер счета", account.number],
            ["Адрес", account.address],
            ["Площадь", f"{account.area} кв.м"],
            ["Жильцы", str(account.residents)],
            ["Управляющая компания", account.management_company]
        ]
        account_table = Table(account_table_data)
        account_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(account_table)
        story.append(Spacer(1, 12))
        
        # Charges table
        charges_table_data = [["Услуга", "Сумма"]] + [
            [charge.service_type.capitalize(), f"{charge.amount:.2f}"] for charge in charges
        ]
        charges_table = Table(charges_table_data)
        charges_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(Paragraph("Начисления", styles['Heading2']))
        story.append(charges_table)
        story.append(Spacer(1, 12))
        
        # Payments table
        payments_table_data = [["Дата", "Сумма", "Метод"]] + [
            [payment.payment_date, f"{payment.amount:.2f}", payment.method] for payment in payments
        ]
        payments_table = Table(payments_table_data)
        payments_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(Paragraph("Платежи", styles['Heading2']))
        story.append(payments_table)
        
        return story
    
    @staticmethod
    def _create_qr_code(qr_data, qr_path):
        """Generate a QR code and save it to qr_path."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(qr_path)