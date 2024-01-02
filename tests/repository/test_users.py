import unittest

from unittest.mock import MagicMock, AsyncMock, Mock, patch

from sqlalchemy.ext.asyncio import AsyncSession

import utils.cache
from utils.cache import rc, RedisCache
from src.database.models import Contact, User
from src.schemas.users import UserCreateSchema, UserUpdateSchema
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_password,
    update_avatar
)


class TestAsyncUser(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(username="test_user", email="test_user@gmail.com", password="test1234")
        #self.mock_redis_cache = AsyncMock(spec=RedisCache)

    async def test_get_user_by_email(self):
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_user

        user = await get_user_by_email(self.user.email, self.session)
        self.assertEqual(user, self.user)
        # self.mock_redis_cache.cache.assert_called_once()

    async def test_create_user(self):
        body = UserCreateSchema(username=self.user.username,
                                email=self.user.email,
                                password=self.user.password)

        result = await create_user(body, self.session)

        self.assertEqual(result, self.user)
