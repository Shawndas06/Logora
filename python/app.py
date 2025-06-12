from fastapi import FastAPI, HTTPException, Request, Depends, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
import os
from typing import Optional
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, validator
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
from dotenv import load_dotenv
import re
from sqlalchemy import text
from fastapi.responses import HTMLResponse, RedirectResponse

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', 'app.log')
)
logger = logging.getLogger(__name__)

# Создаем приложение
app = FastAPI()

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настраиваем статические файлы и шаблоны
app.mount("/static", StaticFiles(directory="python/static"), name="static")
templates = Jinja2Templates(directory="python/templates")

# Настройка базы данных
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///db/logora.sqlite')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Настройка безопасности
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
EMAIL_CONFIRMATION_EXPIRE_HOURS = 24
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Валидация пароля
def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True

# Модели базы данных
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_verified = Column(Boolean, nullable=False, default=False)
    verification_token = Column(String)

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    number = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active")

class Charge(Base):
    __tablename__ = "charges"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    service = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(String, nullable=False)
    method = Column(String, nullable=False)
    receipt = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False, default="completed")

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

# Функция для миграции базы данных
def migrate_database():
    try:
        # Создаем все таблицы, если они не существуют
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables checked/created successfully")
        
        # Проверяем и добавляем новые колонки, если нужно
        with engine.connect() as conn:
            # Проверяем существование таблицы users
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'"))
            if result.fetchone():
                # Проверяем существование колонок
                result = conn.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result.fetchall()]
                
                # Добавляем отсутствующие колонки
                if 'is_active' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1"))
                if 'created_at' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"))
                if 'is_verified' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT 0"))
                if 'verification_token' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN verification_token TEXT"))
                
                conn.commit()
                logger.info("Added missing columns to users table")
    except Exception as e:
        logger.error(f"Error during database migration: {str(e)}")
        raise

# Выполняем миграцию при запуске
migrate_database()

# Модели для данных
class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str

    @validator('password')
    def password_validation(cls, v):
        if not validate_password(v):
            raise ValueError('Password must be at least 8 characters long and contain uppercase, lowercase, and numbers')
        return v

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @validator('new_password')
    def password_validation(cls, v):
        if not validate_password(v):
            raise ValueError('Password must be at least 8 characters long and contain uppercase, lowercase, and numbers')
        return v

# Функция для работы с базой данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Вспомогательные функции
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_verification_token():
    return secrets.token_urlsafe(32)

def send_verification_email(email: str, token: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = os.getenv('SMTP_USER', 'noreply@smartzhkh.ru')
        msg['To'] = email
        msg['Subject'] = "Подтверждение email адреса"
        
        body = f"""
        Здравствуйте!
        
        Для подтверждения вашего email адреса, пожалуйста, перейдите по ссылке:
        http://localhost:8000/verify-email/{token}
        
        Ссылка действительна в течение {EMAIL_CONFIRMATION_EXPIRE_HOURS} часов.
        
        С уважением,
        Команда Smart ЖКХ
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(os.getenv('SMTP_HOST', 'smtp.gmail.com'), int(os.getenv('SMTP_PORT', 587))) as server:
            server.starttls()
            server.login(os.getenv('SMTP_USER', ''), os.getenv('SMTP_PASSWORD', ''))
            server.send_message(msg)
            logger.info(f"Verification email sent to {email}")
    except Exception as e:
        logger.error(f"Error sending verification email to {email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )

def send_password_reset_email(email: str, token: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = os.getenv('SMTP_USER', 'noreply@smartzhkh.ru')
        msg['To'] = email
        msg['Subject'] = "Сброс пароля"
        
        body = f"""
        Здравствуйте!
        
        Для сброса пароля, пожалуйста, перейдите по ссылке:
        http://localhost:8000/reset-password/{token}
        
        Ссылка действительна в течение 1 часа.
        
        Если вы не запрашивали сброс пароля, проигнорируйте это письмо.
        
        С уважением,
        Команда Smart ЖКХ
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(os.getenv('SMTP_HOST', 'smtp.gmail.com'), int(os.getenv('SMTP_PORT', 587))) as server:
            server.starttls()
            server.login(os.getenv('SMTP_USER', ''), os.getenv('SMTP_PASSWORD', ''))
            server.send_message(msg)
            logger.info(f"Password reset email sent to {email}")
    except Exception as e:
        logger.error(f"Error sending password reset email to {email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password reset email"
        )

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# Функция для получения текущего пользователя (опционально)
async def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except jwt.JWTError:
        return None
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        return None
    return user

# Маршруты
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/articles")
async def get_articles(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    articles = db.query(Article).offset(skip).limit(limit).all()
    return articles

@app.get("/articles/{article_id}")
async def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статья не найдена"
        )
    return article

@app.post("/articles")
async def create_article(
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_article = Article(
        title=title,
        content=content,
        author_id=current_user.id
    )
    try:
        db.add(new_article)
        db.commit()
        db.refresh(new_article)
        return new_article
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating article: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании статьи"
        )

@app.put("/articles/{article_id}")
async def update_article(
    article_id: int,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статья не найдена"
        )
    if article.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав для редактирования этой статьи"
        )
    
    try:
        article.title = title
        article.content = content
        article.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(article)
        return article
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating article: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении статьи"
        )

@app.delete("/articles/{article_id}")
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статья не найдена"
        )
    if article.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав для удаления этой статьи"
        )
    
    try:
        db.delete(article)
        db.commit()
        return {"message": "Статья успешно удалена"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting article: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении статьи"
        )

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Проверяем, существует ли пользователь
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегистрирован"
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(password)
    verification_token = create_verification_token()
    
    new_user = User(
        email=email,
        full_name=full_name,
        password=hashed_password,
        verification_token=verification_token
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Отправляем email для подтверждения
        try:
            send_verification_email(email, verification_token)
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
        
        return {"message": "Пользователь успешно зарегистрирован. Пожалуйста, проверьте вашу почту для подтверждения email."}
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при регистрации пользователя"
        )

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "current_user": current_user
        }
    )

@app.post("/forgot-password")
async def forgot_password(email: EmailStr, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    reset_token = create_verification_token()
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    
    send_password_reset_email(email, reset_token)
    
    return {"message": "Инструкции по сбросу пароля отправлены на ваш email"}

@app.post("/reset-password/{token}")
async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == token).first()
    if not user or datetime.utcnow() > user.reset_token_expires:
        raise HTTPException(status_code=400, detail="Срок действия токена истек")
    
    user.password = get_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {"message": "Пароль успешно изменен"}

@app.post("/api/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(password_change.current_password, current_user.password):
        raise HTTPException(status_code=400, detail="Неверный текущий пароль")
    
    current_user.password = get_password_hash(password_change.new_password)
    db.commit()
    
    return {"message": "Пароль успешно изменен"}

@app.get("/accounts")
async def get_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).all()
    return accounts

@app.post("/accounts")
async def create_account(account_number: str, balance: float, user_id: int, db: Session = Depends(get_db)):
    new_account = Account(
        account_number=account_number,
        balance=balance,
        user_id=user_id
    )
    db.add(new_account)
    db.commit()
    return new_account

@app.get("/team")
async def team_page(request: Request):
    return templates.TemplateResponse("team.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/articles", response_class=HTMLResponse)
async def articles_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    return templates.TemplateResponse(
        "articles.html",
        {
            "request": request,
            "current_user": current_user
        }
    )

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)