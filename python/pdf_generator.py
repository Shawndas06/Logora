from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import qrcode
import sqlite3
from datetime import datetime
import os

def create_receipt(account_id):
    # Get database connection
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get account information
    cursor.execute('''
        SELECT a.*, u.full_name, u.email
        FROM accounts a
        JOIN users u ON a.user_id = u.id
        WHERE a.id = ?
    ''', (account_id,))
    account = dict(cursor.fetchone())
    
    # Get latest charge
    cursor.execute('''
        SELECT * FROM charges 
        WHERE account_id = ? 
        ORDER BY start_date DESC 
        LIMIT 1
    ''', (account_id,))
    charge = dict(cursor.fetchone()) if cursor.fetchone() else None
    
    # Get latest payment
    cursor.execute('''
        SELECT * FROM payments 
        WHERE account_id = ? 
        ORDER BY date DESC 
        LIMIT 1
    ''', (account_id,))
    payment = dict(cursor.fetchone()) if cursor.fetchone() else None
    
    # Create receipts directory if it doesn't exist
    os.makedirs('receipts', exist_ok=True)
    receipt_path = f'receipts/receipt_{account_id}.pdf'
    
    # Create PDF document
    doc = SimpleDocTemplate(
        receipt_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )
    
    # Create content
    content = []
    
    # Add title
    content.append(Paragraph("Квитанция об оплате", title_style))
    content.append(Spacer(1, 20))
    
    # Add account information
    account_info = [
        ["Номер лицевого счета:", account["number"]],
        ["ФИО:", account["full_name"] or "Не указано"],
        ["Email:", account["email"] or "Не указан"],
        ["Адрес:", account["address"]],
        ["Площадь:", f"{account['area']} м²"],
        ["Количество проживающих:", str(account["residents"])],
        ["Управляющая компания:", account["management_company"]],
        ["Дата формирования:", datetime.now().strftime("%d.%m.%Y")]
    ]
    
    account_table = Table(account_info, colWidths=[6*cm, 10*cm])
    account_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    content.append(account_table)
    content.append(Spacer(1, 20))
    
    # Add charge information if available
    if charge:
        content.append(Paragraph("Информация о начислении", styles['Heading2']))
        charge_info = [
            ["Услуга:", charge["service"]],
            ["Период:", f"{charge['start_date']} - {charge['end_date']}"],
            ["Сумма к оплате:", f"{charge['amount']} ₽"]
        ]
        charge_table = Table(charge_info, colWidths=[6*cm, 10*cm])
        charge_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        content.append(charge_table)
        content.append(Spacer(1, 20))
    
    # Add payment information if available
    if payment:
        content.append(Paragraph("Информация об оплате", styles['Heading2']))
        payment_info = [
            ["Дата оплаты:", payment["date"]],
            ["Сумма оплаты:", f"{payment['amount']} ₽"],
            ["Способ оплаты:", payment["method"]],
            ["Номер чека:", payment["receipt"]]
        ]
        payment_table = Table(payment_info, colWidths=[6*cm, 10*cm])
        payment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        content.append(payment_table)
    
    # Build PDF
    doc.build(content)
    
    # Generate QR code
    os.makedirs('qrcodes', exist_ok=True)
    qr_path = f'qrcodes/receipt_{account_id}.png'
    
    qr_data = f"""
    Лицевой счет: {account['number']}
    Адрес: {account['address']}
    Сумма: {charge['amount'] if charge else '0'} ₽
    Дата: {datetime.now().strftime('%d.%m.%Y')}
    """
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr.make_image().save(qr_path)
    
    conn.close()
    return receipt_path, qr_path