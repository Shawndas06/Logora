.PHONY: all api_db billing_db payment_db report_db account_db init_dbs clean_dbs

# Главная цель
all: init_dbs

build:
	docker-compose build --no-cache

up:
	docker-compose up

# Создание всех БД
init_dbs: api_db billing_db payment_db report_db account_db
	@echo "✅ Все базы данных созданы и инициализированы"

# Удаление всех БД
clean_dbs:
	@rm -f ./api/api.db ./billing/billing.db ./payment/payment.db ./report/report.db ./account/account.db
	@echo "🧹 Все базы данных удалены"

# API DB
api_db:
	@echo "🛠 Создание БД для API..."
	@sqlite3 ./api/api.db < ./api/schema.sql

# Billing DB
billing_db:
	@echo "🛠 Создание БД для Billing_Service..."
	@sqlite3 ./billing/billing.db < ./billing/schema.sql

# Payment DB
payment_db:
	@echo "🛠 Создание БД для Payment_Service..."
	@sqlite3 ./payment/payment.db < ./payment/schema.sql

# Report DB
report_db:
	@echo "🛠 Создание БД для Report_Service..."
	@sqlite3 ./report/report.db < ./report/schema.sql

# Account DB
account_db:
	@echo "🛠 Создание БД для Account_Service..."
	@sqlite3 ./accounts/account.db < ./accounts/schema.sql
