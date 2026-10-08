import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db, User

SECRET=os.getenv('HIREX_SECRET')
if not SECRET:
    raise RuntimeError('HIREX_SECRET must be set before starting the HireX API.')
ALGORITHM='HS256'; pwd=CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth=OAuth2PasswordBearer(tokenUrl='/api/auth/login')
def hash_password(value): return pwd.hash(value)
def verify_password(value, hashed): return pwd.verify(value, hashed)
def token_for(user): return jwt.encode({'sub':str(user.id),'role':user.role,'exp':datetime.utcnow()+timedelta(hours=12)},SECRET,algorithm=ALGORITHM)
def current_user(token:str=Depends(oauth), db:Session=Depends(get_db)):
    try: uid=int(jwt.decode(token,SECRET,algorithms=[ALGORITHM])['sub'])
    except Exception: raise HTTPException(401,'Invalid or expired session')
    user=db.get(User,uid)
    if not user: raise HTTPException(401,'Invalid session')
    return user
def require_admin(user:User=Depends(current_user)):
    if user.role!='admin': raise HTTPException(403,'Recruiter access required')
    return user
