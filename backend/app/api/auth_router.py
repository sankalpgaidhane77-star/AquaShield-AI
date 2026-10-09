from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.models import User
from backend.app.schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from backend.app.auth import verify_password, get_password_hash, create_access_token, get_current_active_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

class QuickLoginRequest(BaseModel):
    role: str # "admin" or "community_user"

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )
    
    hashed = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed,
        role=user_data.role or "community_user"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": user.email, "role": user.role, "id": user.id})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalars().first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    token = create_access_token({"sub": user.email, "role": user.role, "id": user.id})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(user: User = Depends(get_current_active_user)):
    return UserResponse.model_validate(user)

@router.post("/quick-login", response_model=TokenResponse)
async def quick_login(req: QuickLoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Convenience endpoint for judges and testers to switch roles instantly.
    """
    target_email = "admin@aquashield.org" if req.role == "admin" else "citizen@aquashield.org"
    result = await db.execute(select(User).where(User.email == target_email))
    user = result.scalars().first()

    if not user:
        # Create user on the fly if not seeded
        pwd = get_password_hash("password123")
        name = "System Admin" if req.role == "admin" else "Sarah Chen (Local Citizen)"
        user = User(
            email=target_email,
            name=name,
            hashed_password=pwd,
            role=req.role
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    token = create_access_token({"sub": user.email, "role": user.role, "id": user.id})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )
