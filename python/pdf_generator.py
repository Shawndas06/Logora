from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import qrcode
import sqlite3
from datetime import datetime
import os

def create_receipt(account_id):
    # Получение данных
    conn = sqlite3.connect("/app/db/logora.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
    account = dict(cursor.fetchone())
    
    # Создание PDF
    os.makedirs("/app/python/receipts", exist_ok=True)
    receipt_path = f"/app/python/receipts/receipt_{account_id}.pdf"
    doc = SimpleDocTemplate(receipt_path, pagesize=A4, margins=[2*cm]*4)
    
    # Содержимое документа
    content = [Paragraph("Квитанция об оплате", getSampleStyleSheet()['Heading1'])]
    
    # Информация о счете
    info = [
        ["Номер счета:", account["number"]],
        ["ФИО:", account["name"]],
        ["Адрес:", account["address"]],
        ["Дата:", datetime.now().strftime("%d.%m.%Y")]
    ]
    
    # Добавление информации о начислении
    cursor.execute("SELECT * FROM charges WHERE account_id = ? ORDER BY start_date DESC LIMIT 1", (account_id,))
    if charge := cursor.fetchone():
        info.extend([
            ["Услуга:", charge["service"]],
            ["Период:", f"{charge['start_date']} - {charge['end_date']}"],
            ["Сумма:", f"{charge['amount']} ₽"]
        ])
    
    # Добавление информации о платеже
    cursor.execute("SELECT * FROM payments WHERE account_id = ? ORDER BY date DESC LIMIT 1", (account_id,))
    if payment := cursor.fetchone():
        info.extend([
            ["Дата оплаты:", payment["date"]],
            ["Сумма оплаты:", f"{payment['amount']} ₽"],
            ["Способ оплаты:", payment["method"]],
            ["Номер чека:", payment["receipt"]]
        ])
    
    # Создание таблицы
    table = Table(info, colWidths=[4*cm, 10*cm])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(table)
    
    # Создание PDF
    doc.build(content)
    
    # Генерация QR-кода
    os.makedirs("/app/python/qrcodes", exist_ok=True)
    qr_path = f"/app/python/qrcodes/receipt_{account_id}.png"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(f"Счет: {account['number']}\nСумма: {payment['amount'] if payment else charge['amount']} ₽")
    qr.make_image().save(qr_path)
    
    return receipt_path, qr_path