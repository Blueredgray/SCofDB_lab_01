import uuid
from typing import Optional, List
from app.domain.user import User
from app.domain.exceptions import EmailAlreadyExistsError, UserNotFoundError
from sqlalchemy.exc import IntegrityError

class UserService:
    def __init__(self, repo):
        self.repo = repo

    async def register(self, email: str, name: str = "") -> User:
        existing = await self.repo.find_by_email(email)
        if existing:
            raise EmailAlreadyExistsError(email)
        user = User(email=email, name=name)
        try:
            return await self.repo.save(user)
        except IntegrityError:
            raise EmailAlreadyExistsError(email)

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        user = await self.repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.repo.find_by_email(email)

    async def list_users(self) -> List[User]:
        return await self.repo.find_all()