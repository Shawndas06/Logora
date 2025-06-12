import os
from qr_and_generator import logora

def test_create_receipt():
    # Создаём тестовую квитанцию
    services = [("Вода", 555), ("Электричество", 555)]
    create_receipt("test_receipt.pdf", "доскиева яха", "ул. хруш, д. 10", services, 2230, "09.06.2025")
    
    # Проверяем, что файл создался
    assert os.path.exists("test_receipt.pdf"), "PDF не создался!"