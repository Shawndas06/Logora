from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, validator
import sqlite3
import jwt
from datetime import datetime, timedelta
import hashlib
import re
from typing import Optional
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create router
router = APIRouter()

# Security settings
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30
EMAIL_CONFIRMATION_EXPIRE_HOURS = 24

# User model
class User(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    password: str
    full_name: str
    is_active: bool = True
    is_verified: bool = False
    verification_token: Optional[str] = None
    created_at: Optional[datetime] = None

# Token models
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshToken(BaseModel):
    refresh_token: str

# Password validation
def validate_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

# Database connection
def get_db():
    conn = sqlite3.connect("/app/db/logora.sqlite")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Password hashing
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    return f"{salt}${hashlib.sha256((password + salt).encode()).hexdigest()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    salt, stored_hash = hashed_password.split('$')
    return hashlib.sha256((plain_password + salt).encode()).hexdigest() == stored_hash

# Token creation
def create_tokens(data: dict) -> dict:
    access_token_expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token_data = data.copy()
    access_token_data.update({"exp": access_token_expire})
    access_token = jwt.encode(access_token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    refresh_token_data = data.copy()
    refresh_token_data.update({"exp": refresh_token_expire, "type": "refresh"})
    refresh_token = jwt.encode(refresh_token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# Email verification
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )

# User registration
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: User):
    conn = next(get_db())
    cursor = conn.cursor()
    
    # Validate password
    if not validate_password(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long and contain uppercase, lowercase, numbers, and special characters"
        )
    
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    if cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    # Create verification token
    verification_token = secrets.token_urlsafe(32)
    
    try:
        # Create user
        cursor.execute(
            """
            INSERT INTO users (email, password, full_name, is_active, is_verified, verification_token, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user.email,
                hash_password(user.password),
                user.full_name,
                True,
                False,
                verification_token,
                datetime.utcnow()
            )
        )
        conn.commit()
        
        # Send verification email
        send_verification_email(user.email, verification_token)
        
        return {"message": "User registered successfully. Please check your email for verification."}
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# User login
@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = next(get_db())
    cursor = conn.cursor()
    
    # Find user
    cursor.execute("SELECT * FROM users WHERE email = ?", (form_data.username,))
    user = cursor.fetchone()
    
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user["is_verified"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your email first"
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )
    
    # Create tokens
    return create_tokens({"sub": user["id"]})

# Token refresh
@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: RefreshToken):
    try:
        payload = jwt.decode(refresh_token.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        return create_tokens({"sub": payload["sub"]})
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

# Email verification
@router.get("/verify-email/{token}")
def verify_email(token: str):
    conn = next(get_db())
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE verification_token = ?", (token,))
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    try:
        cursor.execute(
            "UPDATE users SET is_verified = TRUE, verification_token = NULL WHERE id = ?",
            (user["id"],)
        )
        conn.commit()
        return {"message": "Email verified successfully"}
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
