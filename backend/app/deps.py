from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.domain.models import User
from app.domain.enums import UserRole
from app.infrastructure.security import decode_token
from app.infrastructure.repositories import UserRepository
from app.application.exceptions import UnauthorizedException, ForbiddenException

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None or payload.get("type") != "access":
        raise UnauthorizedException("Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    user_repo = UserRepository(User, db)
    user = await user_repo.get_by_id(UUID(user_id))

    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive")

    return user


def require_role(*roles: UserRole):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenException(f"Required role: {', '.join(r.value for r in roles)}")
        return current_user
    return role_checker


async def get_facility_scope(
    current_user: User = Depends(get_current_user),
) -> UUID | None:
    if current_user.role == UserRole.ADMIN:
        return None
    return current_user.facility_id
