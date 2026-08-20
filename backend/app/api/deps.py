from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.config.settings import settings
from app.database.connection import get_db
from app.schemas.user import TokenData
from app.core.security import ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    user = await db["users"].find_one({"email": token_data.email})
    if user is None:
        raise credentials_exception
    
    # Map _id to string id
    user["id"] = str(user["_id"])
    return user

async def get_optional_current_user(token: str = Depends(oauth2_scheme_optional)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        
        db = get_db()
        if db is None:
            return None
            
        user = await db["users"].find_one({"email": email})
        if user:
            user["id"] = str(user["_id"])
            return user
    except Exception:
        return None
    return None
