from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing import Optional
import uuid
from passlib.context import CryptContext


@dataclass
class UserDTO:
    id: str
    name: str
    username: str
    hashed_password: str


class UserRepository(ABC):

    @abstractmethod
    async def get_one(self, username: str) -> Optional[UserDTO]:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, **filters) -> list[UserDTO]:
        raise NotImplementedError

    @abstractmethod
    async def add_one(self, data: UserDTO) -> None:
        raise NotImplementedError


class BaseAuthService(ABC):

    @abstractmethod
    async def login(self, username: str, password: str) -> Optional[UserDTO]:
        raise NotImplementedError

    @abstractmethod
    async def register(self, name: str, username: str, password: str) -> UserDTO:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[UserDTO]:
        raise NotImplementedError


class AuthService(BaseAuthService):

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def login(self, username: str, password: str) -> Optional[UserDTO]:
        users = await self._user_repository.get_all(username=username)
        for user in users:
            if self._verify_password(password, user.hashed_password):
                return user
        return None

    async def register(self, name: str, username: str, password: str) -> UserDTO:
        user_id = str(uuid.uuid4())
        hashed_password = self._hash_password(password)
        user = UserDTO(
            id=user_id, name=name, username=username, hashed_password=hashed_password
        )
        await self._user_repository.add_one(user)
        return user

    async def get_user_by_id(self, user_id: str) -> Optional[UserDTO]:
        return await self._user_repository.get_one(user_id)

    @staticmethod
    def _hash_password(password: str) -> str:
        ctx = CryptContext(schemes=["argon2"], deprecated="auto")
        return ctx.hash(password)

    @staticmethod
    def _verify_password(password: str, hashed_password: str) -> bool:
        ctx = CryptContext(schemes=["argon2"], deprecated="auto")
        return ctx.verify(password, hashed_password)


class InMemoryUserRepository(UserRepository):
    _instance: Optional["InMemoryUserRepository"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._users: list[UserDTO] = []
            self._initialized = True

    async def get_one(self, user_id: str) -> Optional[UserDTO]:
        for user in self._users:
            if user.id == user_id:
                return user
        return None

    async def get_all(self, **filters) -> list[UserDTO]:
        users = []
        for user in self._users:
            is_passed = True
            for filter_key, filter_value in filters.items():
                if getattr(user, filter_key) != filter_value:
                    is_passed = False
            if is_passed:
                users.append(user)
        return users

    async def add_one(self, data: UserDTO) -> UserDTO:
        self._users.append(data)
        return data
