import sqlite3
import os
import time
import qrcode
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

DB_PATH = 'report.db'
RECEIPT_DIR = 'receipts'
QRCODE_DIR = 'qrcodes'

# Ensure output directories exist
def prepare_dirs():
    os.makedirs(RECEIPT_DIR, exist_ok=True)
    os.makedirs(QRCODE_DIR, exist_ok=True)

# Fetch row as dict
def fetchone_dict(cursor):
    row = cursor.fetchone()
    return dict(row) if row else None

# Main function to create receipt
def create_receipt(account_id):
    # Setup
    prepare_dirs()

    # Connect to DB
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get account info
    cursor.execute(
        '''SELECT a.id, a.number, a.address, a.area, a.residents, a.management_company,
                  u.full_name, u.email
           FROM accounts a
           JOIN users u ON a.user_id = u.id
           WHERE a.id = ?''',
        (account_id,)
    )
    account = fetchone_dict(cursor)
    if not account:
        raise ValueError(f"Account {account_id} not found")

    # Get latest charge
    cursor.execute(
        '''SELECT service, start_date, end_date, amount
           FROM charges
           WHERE account_id = ?
           ORDER BY start_date DESC
           LIMIT 1''',
        (account_id,)
    )
    charge = fetchone_dict(cursor)

    # Get latest payment
    cursor.execute(
        '''SELECT date AS payment_date, amount AS payment_amount, method, receipt
           FROM payments
           WHERE account_id = ?
           ORDER BY date DESC
           LIMIT 1''',
        (account_id,)
    )
    payment = fetchone_dict(cursor)

    # Close DB
    conn.close()

    # File paths
    receipt_path = os.path.join(RECEIPT_DIR, f"receipt_{account_id}.pdf")
    qr_path = os.path.join(QRCODE_DIR, f"receipt_{account_id}.png")

    # Build PDF
    doc = SimpleDocTemplate(
        receipt_path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'], fontSize=16, spaceAfter=20
    )
    content = []

    # Title
    content.append(Paragraph("Квитанция об оплате", title_style))
    content.append(Spacer(1, 12))

    # Account table
    acct_info = [
        ["Лицевой счет:", account['number']],
        ["ФИО:", account.get('full_name', '-')],
        ["Email:", account.get('email', '-')],
        ["Адрес:", account['address']],
        ["Площадь (м²):", account['area']],
        ["Проживающих:", account['residents']],
        ["УК:", account['management_company']],
        ["Дата формирования:", datetime.now().strftime('%d.%m.%Y')]
    ]
    tbl = Table(acct_info, colWidths=[6*cm, 10*cm])
    tbl.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (0,0), (0,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    content.append(tbl)
    content.append(Spacer(1, 12))

    # Charge section
    if charge:
        content.append(Paragraph("Начисление", styles['Heading2']))
        charge_info = [
            ["Услуга:", charge['service']],
            ["Период:", f"{charge['start_date']} – {charge['end_date']}"],
            ["К оплате (₽):", charge['amount']]
        ]
        ctbl = Table(charge_info, colWidths=[6*cm, 10*cm])
        ctbl.setStyle(tbl._argW)  # reuse style
        content.append(ctbl)
        content.append(Spacer(1, 12))

    # Payment section
    if payment:
        content.append(Paragraph("Оплата", styles['Heading2']))
        pay_info = [
            ["Дата:", payment['payment_date']],
            ["Сумма (₽):", payment['payment_amount']],
            ["Метод:", payment['method']],
            ["Чек:", payment['receipt']]
        ]
        ptbl = Table(pay_info, colWidths=[6*cm, 10*cm])
        ptbl.setStyle(tbl._argW)
        content.append(ptbl)

    doc.build(content)

    # QR code
    qr_data = f"Account: {account['number']} | Amount: {charge['amount'] if charge else 0}" 
    qr = qrcode.make(qr_data)
    qr.save(qr_path)

    return receipt_path, qr_path

