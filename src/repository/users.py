from libgravatar import Gravatar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas.users import UserCreateSchema
from utils.chahe import cache


@cache.redis_cache
async def get_user_by_email(email: str, db: AsyncSession):
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    return user.scalar_one_or_none()


async def create_user(body: UserCreateSchema, db: AsyncSession):
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    user = User(**body.model_dump(exclude_unset=True), avatar=avatar)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_token(user: User, token: str | None, db: AsyncSession):
    user.refresh_token = token
    await db.commit()
    await db.refresh(user)


async def confirmed_email(email: str, db: AsyncSession) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()
    await db.refresh(user)


async def update_password(user: str, password: str, db: AsyncSession):
    user.password = password
    await db.commit()
    await db.refresh(user)


async def update_avatar(email: str, src_url: str, db: AsyncSession):
    user: User = await get_user_by_email(email, db)
    user.avatar = src_url
    await db.commit()
    await db.merge(user)
    cache.updated.send(sender=None, func_name="get_user_by_email", arg=email, value=user)
    return user
