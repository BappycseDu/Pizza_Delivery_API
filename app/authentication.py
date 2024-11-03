from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .database import async_session
from .models import Admin, User
from .config import settings
from .schema import UserCreate, AdminCreate, AdminResponse
from .authentication import create_access_token, get_current_user
from passlib.context import CryptContext

# Security configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # OAuth2 scheme for token authentication
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

@router.post("/register/admin/", response_model=AdminResponse)
async def register_admin(admin_create: AdminCreate, db: AsyncSession = Depends(async_session)):
    existing_admin = await db.execute(select(Admin).filter(Admin.username == admin_create.username))
    if existing_admin.scalars().first():
        raise HTTPException(status_code=400, detail="Admin username already registered.")
    
    hashed_password = pwd_context.hash(admin_create.password)
    new_admin = Admin(username=admin_create.username, hashed_password=hashed_password)
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    return new_admin

@router.post("/login/")
async def login(user_create: UserCreate, db: AsyncSession = Depends(async_session)):
    user = await db.execute(select(User).filter(User.username == user_create.username))
    user = user.scalars().first()
    
    if not user or not user.verify_password(user_create.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Include other admin routes here as needed


# Function to create access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Function to get current user based on token
async def get_current_user(db: AsyncSession, token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.execute(select(User).filter(User.username == username))
    user = user.scalars().first()
    if user is None:
        raise credentials_exception
         
    return user

# Function to get current admin
async def get_current_admin(db: AsyncSession = Depends(async_session), token: str = Depends(oauth2_scheme)):
    user = await get_current_user(db, token)
    if not isinstance(user, Admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user
