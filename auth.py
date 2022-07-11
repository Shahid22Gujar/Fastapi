from fastapi import Depends,HTTPException
import models_and_schemas
from jose import jwt
from datetime import datetime,timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

pwd_context=CryptContext(schemes=['bcrypt'])
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")

JWT_SECRET="unsersecretkey"
ALGORITHMUS="HS256"


def create_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password,hash_password):
    return pwd_context.verify(plain_password,hash_password)

def create_access_token(user: models_and_schemas.User):
    claims={
        "sub":user.username,
        "email":user.email,
        "role":user.role,
        "active":user.is_active,
        "exp":datetime.utcnow() + timedelta(minutes=120)
    }

    return jwt.encode(claims=claims,key=JWT_SECRET,algorithm=ALGORITHMUS)

def decode_token(token):
    claims=jwt.decode(token,key=JWT_SECRET)
    return claims

def check_active(token: str = Depends(oauth2_scheme)):
    claims = decode_token(token)
    if claims.get("active"):
        return claims
    
    raise HTTPException(
        status_code=401,
        detail="Deactivaed account",
        headers={"WWW-Authenticate":"Bearer"}
    )

"""Checking if user is admin or not"""
def check_admin(claims: dict = Depends(check_active)):
    role = claims.get("role")
    if role != "admin":
        raise HTTPException(
        status_code=401,
        detail="Only available for admin",
        headers={"WWW-Authenticate":"Bearer"}
    )
    return claims
    
    