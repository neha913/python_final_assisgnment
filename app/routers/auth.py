from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth_service import AuthService
from app.schemas import UserRegister, UserLogin, ForgotPasswordRequest, Token, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user (Doctor or Patient)"""
    auth_service = AuthService(db)
    try:
        user = await auth_service.register(
            email=user_data.email,
            password=user_data.password,
            role=user_data.role.value,
            name=user_data.name
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login and receive JWT token"""
    auth_service = AuthService(db)
    token = await auth_service.login(user_data.email, user_data.password)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"access_token": token, "token_type": "bearer"}


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Mock forgot password flow - returns success if user exists"""
    auth_service = AuthService(db)
    user_exists = await auth_service.forgot_password(request.email)
    
    if user_exists:
        return {
            "message": "If an account with this email exists, a password reset link has been sent."
        }
    else:
        # Don't reveal if user exists for security
        return {
            "message": "If an account with this email exists, a password reset link has been sent."
        }

