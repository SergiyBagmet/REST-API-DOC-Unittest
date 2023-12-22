from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request, Form
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from src.database.db import get_db
from src.repository import users as repository_users
from src.schemas.users import UserCreateSchema, TokenSchema, UserResponseSchema, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()
templates = Jinja2Templates(directory="src/services/templates")






@router.post("/signup", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def signup(body: UserCreateSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)

    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url),
                header_msg='Email confirmation', template_name='verify_email.html')

    return {"user": new_user, "detail": "User successfully created, check your email"}


@router.post("/login", response_model=TokenSchema, status_code=status.HTTP_201_CREATED)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account not confirmed. Check email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, bt: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}

    bt.add_task(send_email, user.email, user.username, str(request.base_url),
                header_msg='Email confirmation', template_name='verify_email.html')
    return {"message": "Check your email for confirmation."}


@router.post('/reset_password_send_email')
async def reset_password(body: RequestEmail, bt: BackgroundTasks, request: Request,
                         db: AsyncSession = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        return {"message": "Please, varify your email"}

    bt.add_task(send_email, user.email, user.username, str(request.base_url),
                header_msg='Reset password', template_name='reset_password.html')
    return {"message": "Check your email for reset password."}


@router.get("/reset_password/{token}", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def refresh_password(token: str, request: Request):
    return templates.TemplateResponse("form_reset_password.html", {"request": request, "token": token})


@router.post("/reset_password/response/{token}")
async def refresh_password(token: str,
                           password: str = Form(pattern="[A-Za-z0-9]{6,8}"),
                           confirm_password: str = Form(pattern="[A-Za-z0-9]{6,8}"),
                           db: AsyncSession = Depends(get_db)):

    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if password != confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    password = auth_service.get_password_hash(password)
    await repository_users.update_password(user, password, db)

    return {"message": "Password reset successful"}
