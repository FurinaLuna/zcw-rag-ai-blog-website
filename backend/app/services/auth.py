from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.models.admin import Admin


async def authenticate_admin(db: AsyncSession, username: str, password: str) -> str | None:
    result = await db.execute(select(Admin).where(Admin.username == username))
    admin = result.scalar_one_or_none()
    if admin is None or not verify_password(password, admin.password_hash):
        return None

    await db.execute(
        update(Admin).where(Admin.id == admin.id).values(last_login_at=datetime.utcnow())
    )
    await db.flush()

    return create_access_token(data={"sub": admin.id, "username": admin.username})


async def get_admin_info(db: AsyncSession, admin_id: int) -> Admin | None:
    result = await db.execute(select(Admin).where(Admin.id == admin_id))
    return result.scalar_one_or_none()
